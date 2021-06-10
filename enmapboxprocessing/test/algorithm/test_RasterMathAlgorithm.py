import numpy as np

from enmapboxprocessing.algorithm.rastermathalgorithm import RasterMathAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterMathAlgorithm(TestCase):

    def test_copy_band(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap],
            alg.P_EXPRESSION: 'np.add(A@1, A@2)',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array(bandList=[1, 2])
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

    def test_build_stack(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap, enmap, enmap],
            alg.P_EXPRESSION: 'list(A) + list(B) + list(C)',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = 3 * RasterReader(enmap).bandCount()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).bandCount()
        self.assertEqual(gold, lead)

    def test_multiline(self):
        alg = RasterMathAlgorithm()
        parameters = {
            alg.P_RASTER_LIST: [enmap],
            alg.P_EXPRESSION: 'nir = np.float32(A@4)\nred = np.float32(A@3)\nndvi = (nir - red) / (nir + red)\nndvi',
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(np.sum(gold), np.sum(lead))
