import webbrowser

import processing
from qgis._core import QgsRasterLayer, QgsVectorLayer, Qgis, QgsProcessingContext

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_polygons_3classes_epsg4326

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterizeAlgorithm(TestCase):

    def test_pythonCommand(self):
        alg = RasterizeVectorAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_RASTER: c + '/vsimem/mask.tif'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        #webbrowser.open_new(parameters[alg.P_OUTPUT_RASTER] + '.log')

    def test_default(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_RASTER: c + '/vsimem/mask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(Qgis.Float32, RasterReader(result[alg.P_OUTPUT_RASTER]).dataType())
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_tmpFileAndVrt(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_OUTPUT_RASTER: c + '/vsimem/mask.vrt'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_differentCrs(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_OUTPUT_RASTER: c + '/vsimem/mask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_initAndBurnValue(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_INIT_VALUE: 1,
            alg.P_BURN_VALUE: 0,
            alg.P_OUTPUT_RASTER: c + '/vsimem/invertedMask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(85972, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_burnAttribute(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_BURN_ATTRIBUTE: 'level_1_id',
            alg.P_OUTPUT_RASTER: c + '/vsimem/classes.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(3100, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_modeAggregation(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_RESAMPLE_ALG: alg.ModeResampleAlg,
            alg.P_OUTPUT_RASTER: c + '/vsimem/mode.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2026, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_averageAggregation(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_RESAMPLE_ALG: alg.AverageResampleAlg,
            alg.P_OUTPUT_RASTER: c + '/vsimem/average.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum().round())

    def test_minAggregation(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_RESAMPLE_ALG: alg.MinResampleAlg,
            alg.P_OUTPUT_RASTER: c + '/vsimem/min.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(1481, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_allTouched(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_ALL_TOUCHED: True,
            alg.P_DATA_TYPE: alg.Byte,
            alg.P_OUTPUT_RASTER: c + '/vsimem/allTouched.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2721, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())
        self.assertEqual(Qgis.Byte, RasterReader(result[alg.P_OUTPUT_RASTER]).dataType())

    def test_addValue(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_ADD_VALUE: True,
            alg.P_OUTPUT_RASTER: c + '/vsimem/addValue.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2031, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_burnFid(self):
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_BURN_FID: True,
            alg.P_OUTPUT_RASTER: c + '/vsimem/fid.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-81902, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())
