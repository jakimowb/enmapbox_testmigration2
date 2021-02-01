from osgeo import gdal
from qgis._core import QgsRasterLayer, QgsPalettedRasterRenderer
import numpy as np

from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, hires
from enmapboxunittestdata import landcover_raster_30m_epsg3035, landcover_raster_30m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestTranslateRasterAlgorithm(TestCase):

    def test_default(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(gold[0].dtype, lead[0].dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))

    def test_tmpFilesAndVrt(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_GRID: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_BAND_LIST: [5],
            alg.P_CREATION_PROFILE: alg.Vrt,
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.vrt'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(28263893, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_gridWithSameCrs(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(hires),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_BAND_LIST: [1],
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        grid = RasterReader(enmap)
        outraster = RasterReader(result[alg.P_OUTPUT_RASTER])
        self.assertEqual(grid.extent(), outraster.extent())
        self.assertEqual(2939687, np.sum(outraster.array()))

    def test_gridWithDifferentCrs(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(hires),
            alg.P_GRID: QgsRasterLayer(landcover_raster_30m_epsg3035),
            # alg.P_BAND_LIST: [1],
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster3035.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(parameters[alg.P_GRID].extent(), RasterReader(result[alg.P_OUTPUT_RASTER]).extent())
        self.assertEqual(9200302, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_gridWithDifferentCrs_AndBandSubset(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(hires),
            alg.P_GRID: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_BAND_LIST: [1],
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster3035_bandSubset.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(parameters[alg.P_GRID].extent(), RasterReader(result[alg.P_OUTPUT_RASTER]).extent())
        self.assertEqual(2919474, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_dataType(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_BAND_LIST: [1],
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        gold = [1, 3, 2, 5, 4, 6, 7]
        for index, name in enumerate(alg.O_DATA_TYPE):
            parameters[alg.P_DATA_TYPE] = index
            parameters[alg.P_OUTPUT_RASTER] = c + f'/vsimem/raster.{name}.tif'
            result = self.runalg(alg, parameters)
            dataType = RasterReader(result[alg.P_OUTPUT_RASTER]).dataType()
            print(name, dataType)
            self.assertEqual(gold[index], dataType)

    def test_bandList(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif',
            alg.P_BAND_LIST: None
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(RasterReader(enmap).bandCount(), RasterReader(result[alg.P_OUTPUT_RASTER]).bandCount())

        parameters[alg.P_BAND_LIST] = []
        result = self.runalg(alg, parameters)
        self.assertEqual(RasterReader(enmap).bandCount(), RasterReader(result[alg.P_OUTPUT_RASTER]).bandCount())

        parameters[alg.P_BAND_LIST] = [1, 3, 5]
        result = self.runalg(alg, parameters)
        self.assertEqual(3, RasterReader(result[alg.P_OUTPUT_RASTER]).bandCount())

    def test_metadata_forEnviSource_allBands(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_COPY_METADATA: True,
            alg.P_CREATION_PROFILE: alg.EnviBsq,
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmap.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).metadataDomain('')
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).metadataDomain('')
        for key in gold:
            self.assertEqual(gold[key], lead[key])
        gold = RasterReader(enmap).metadataDomain('ENVI')
        gold.pop('file_compression')
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).metadataDomain('ENVI')
        for key in gold:
            self.assertEqual(gold[key], lead[key])

    def test_metadata_forEnviSource_bandSubset(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_BAND_LIST: [3],
            alg.P_COPY_METADATA: True,
            alg.P_CREATION_PROFILE: alg.EnviBsq,
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmap.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).metadataDomain('')
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).metadataDomain('')
        for key in gold:
            if key.startswith('Band_'):
                continue
            self.assertEqual(gold[key], lead[key])
        self.assertEqual(gold['Band_3'], lead['Band_1'])
        gold = RasterReader(enmap).metadataDomain('ENVI')
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).metadataDomain('ENVI')
        for key, value in gold.items():
            if key in ['file_compression']:
                continue
            if key == 'bands':
                value = '1'
            if key in [
                'band names', 'bbl', 'data_gain_values', 'data_offset_values', 'data_reflectance_gain_values',
                'data_reflectance_offset_values', 'fwhm', 'wavelength'
            ]:
                value = [value[bandNo - 1] for bandNo in parameters[alg.P_BAND_LIST]]
            self.assertEqual(value, lead[key])

    def test_clipSourceGrid_byFullExtent(self):
        raster = QgsRasterLayer(enmap)
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: raster,
            alg.P_BAND_LIST: [1],
            alg.P_EXTENT: raster.extent(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmapClipFull.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(raster.extent(), RasterReader(result[alg.P_OUTPUT_RASTER]).extent())

    def test_clipSourceGrid_by1PixelBufferedExtent(self):
        raster = QgsRasterLayer(enmap)
        extent = raster.extent().buffered(-30)

        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: raster,
            alg.P_BAND_LIST: [1],
            alg.P_EXTENT: extent,
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmapClipBuffered.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(extent, RasterReader(result[alg.P_OUTPUT_RASTER]).extent())

    def test_clipSourceGrid_withNonSnappedExtent(self):
        raster = QgsRasterLayer(enmap)
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: raster,
            alg.P_BAND_LIST: [1],
            alg.P_EXTENT: raster.extent().buffered(-20),
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmapClipBuffered.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(raster.extent().buffered(-30), RasterReader(result[alg.P_OUTPUT_RASTER]).extent())
        self.assertEqual(raster.width() - 2, RasterReader(result[alg.P_OUTPUT_RASTER]).width())
        self.assertEqual(raster.height() - 2, RasterReader(result[alg.P_OUTPUT_RASTER]).height())

    def test_clipSourceGrid_withSourceWindow(self):
        raster = QgsRasterLayer(enmap)

        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: raster,
            alg.P_BAND_LIST: [1],
            alg.P_SOURCE_WINDOW: f'1, 1, {raster.width() - 2}, {raster.height() - 2}',
            alg.P_OUTPUT_RASTER: c + '/vsimem/enmapClipSourceWindow.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(raster.extent().buffered(-30), RasterReader(result[alg.P_OUTPUT_RASTER]).extent())
        self.assertEqual(raster.width() - 2, RasterReader(result[alg.P_OUTPUT_RASTER]).width())
        self.assertEqual(raster.height() - 2, RasterReader(result[alg.P_OUTPUT_RASTER]).height())

    def test_resampleAlg(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_BAND_LIST: [1],
        }
        for index, name in enumerate(alg.O_RESAMPLE_ALG):
            print(name)
            parameters[alg.P_RESAMPLE_ALG] = index
            parameters[alg.P_OUTPUT_RASTER] = c + f'/vsimem/raster.{name}.tif'
            self.runalg(alg, parameters)

    def test_copyStyle(self):
        alg = TranslateRasterAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(landcover_raster_30m),
            alg.P_COPY_RENDERER: True,
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover.tif'
        }
        result = self.runalg(alg, parameters)
        inraster =QgsRasterLayer(landcover_raster_30m)
        outraster = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])
        assert isinstance(outraster.renderer(), QgsPalettedRasterRenderer)
        self.assertListEqual(
            Utils.categoriesFromPalettedRasterRenderer(inraster.renderer()),
            Utils.categoriesFromPalettedRasterRenderer(outraster.renderer())
        )

