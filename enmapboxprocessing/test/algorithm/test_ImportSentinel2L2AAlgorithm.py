import numpy as np

from enmapboxprocessing.algorithm.importenmapl2aalgorithm import ImportEnmapL2AAlgorithm
from enmapboxprocessing.algorithm.importsentinel2l2aalgorithm import ImportSentinel2L2AAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestImportSentinel2L2AAlgorithm(TestCase):

    def test(self):
        alg = ImportSentinel2L2AAlgorithm()
        parameters = {
            alg.P_FILE: r'D:\data\sensors\sentinel2\S2A_MSIL2A_20200816T101031_N0214_R022_T32UQD_20200816T130108.SAFE\MTD_MSIL2A.xml',
            #alg.P_BAND_LIST: [1],
            alg.P_OUTPUT_RASTER: 'c:/vsimem/sentinel2L2A.vrt',
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(
            8774,
            round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array(5000, 5000, 1, 1), dtype=float))
        )