import webbrowser

import processing
from qgis._core import QgsRasterLayer, QgsRasterRenderer, QgsProcessingContext
import numpy as np

from enmapboxprocessing.algorithm.rastermathalgorithm import RasterMathAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, hires
from enmapboxunittestdata import landcover_raster_30m_epsg3035, landcover_raster_30m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterMathAlgorithm(TestCase):

    def test_copy_band(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap],
            alg.P_EXPRESSION: 'A@1',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array(bandList=[1])
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(gold[0].dtype, lead[0].dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))

    def test_copy_raster(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap],
            alg.P_EXPRESSION: 'A',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(np.sum(gold), np.sum(lead))
