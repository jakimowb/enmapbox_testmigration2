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

    def test_default(self):
        alg = CreateGridAlgorithm()
        parameters = {
            alg.P_CRS: QgsRasterLayer(enmap).crs(),
            alg.P_EXTENT: QgsRasterLayer(enmap).extent(),
            alg.P_WIDTH: 'array(1,2.)',
            alg.P_OUTPUT_RASTER: c + '/vsimem/grid.tif'
        }
        result = self.runalg(alg, parameters)
