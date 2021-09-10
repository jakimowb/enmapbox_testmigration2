import numpy as np

from enmapboxprocessing.algorithm.spectralresamplingbyresponsefunctionlibraryalgorithm import \
    SpectralResamplingByResponseFunctionLibraryAlgorithm
from enmapboxprocessing.algorithm.spectralresamplingtolandsat8algorithm import SpectralResamplingToLandsat8Algorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, enmap_srf_library
from enmapboxunittestdata import landsat8_sectralResponseFunctionLibrary


class TestSpectralResamplingByResponseFunctionLibraryAlgorithmBase(TestCase):

    def test(self):
        alg = SpectralResamplingByResponseFunctionLibraryAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_LIBRARY: enmap_srf_library,
            alg.P_OUTPUT_RASTER: 'C:/vsimem/resampled.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(14908146678, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array(), dtype=float))
