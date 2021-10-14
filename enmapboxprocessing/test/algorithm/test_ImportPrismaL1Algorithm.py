import numpy as np

from enmapboxprocessing.algorithm.importprismal1algorithm import ImportPrismaL1Algorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestImportPrismaL1Algorithm(TestCase):

    def test(self):
        alg = ImportPrismaL1Algorithm()
        parameters = {
            alg.P_FILE: r'D:\data\sensors\prisma\PRS_L1_STD_OFFL_20201107101404_20201107101408_0001.he5',
            alg.P_OUTPUT_RASTER: self.filename('prismaL1.tif'),
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(3801392558, round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array(bandList=[1]), dtype=float)))

