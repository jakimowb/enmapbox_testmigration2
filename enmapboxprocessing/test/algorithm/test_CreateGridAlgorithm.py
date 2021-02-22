from osgeo import gdal
from qgis._core import QgsRasterLayer, QgsPalettedRasterRenderer
import numpy as np

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, hires
from enmapboxunittestdata import landcover_raster_30m_epsg3035, landcover_raster_30m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestCreateGridAlgorithm(TestCase):

    def test_pixelUnits(self):
        raster = QgsRasterLayer(enmap)
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.PixelUnits,
            alg.P_WIDTH: raster.width(),
            alg.P_HEIGHT: raster.height(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/gridPixelUnits.tif'
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])
        for gold, lead in [
            (raster.crs(), grid.crs()), (raster.extent(), grid.extent()),(raster.width(), grid.width()),
            (raster.height(), grid.height())
        ]:
            self.assertEqual(gold, lead)

    def test_georeferencedUnits(self):
        raster = QgsRasterLayer(enmap)
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.GeoreferencedUnits,
            alg.P_WIDTH: raster.rasterUnitsPerPixelX(),
            alg.P_HEIGHT: raster.rasterUnitsPerPixelY(),
            alg.P_OUTPUT_RASTER: c + '/vsimem/gridGeoreferencedUnits.tif'
        }
        result = self.runalg(alg, parameters)
        grid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])
        for gold, lead in [
            (raster.crs(), grid.crs()), (raster.extent(), grid.extent()),(raster.width(), grid.width()),
            (raster.height(), grid.height())
        ]:
            self.assertEqual(gold, lead)
