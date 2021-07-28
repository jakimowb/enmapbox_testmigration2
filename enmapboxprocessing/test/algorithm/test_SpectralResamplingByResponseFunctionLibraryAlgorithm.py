import numpy as np

from enmapboxprocessing.algorithm.spectralresamplingbyresponsefunctionlibraryalgorithm import \
    SpectralResamplingByResponseFunctionLibraryAlgorithm
from enmapboxprocessing.algorithm.spectralresamplingtolandsat8algorithm import SpectralResamplingToLandsat8Algorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap
from enmapboxunittestdata import landsat8_sectralResponseFunctionLibrary


class TestSpectralResamplingByResponseFunctionLibraryAlgorithmBase(TestCase):

    def test(self):
        alg = SpectralResamplingByResponseFunctionLibraryAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            #alg.P_LIBRARY: landsat8_sectralResponseFunctionLibrary,
            alg.P_LIBRARY: r'C:\Users\Andreas\Desktop\srf.gpkg',
            alg.P_OUTPUT_RASTER: 'C:/vsimem/resampled.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertTrue(np.all(RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0] == -99))
        self.assertEqual(30542976, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()[1])))

