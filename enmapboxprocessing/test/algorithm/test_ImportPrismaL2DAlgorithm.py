import numpy as np

from enmapboxprocessing.algorithm.importenmapl2aalgorithm import ImportEnmapL2AAlgorithm
from enmapboxprocessing.algorithm.importprismal2dalgorithm import ImportPrismaL2DAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestImportPrismaL2DAlgorithm(TestCase):

    def test(self):
        alg = ImportPrismaL2DAlgorithm()
        parameters = {
            alg.P_FILE: r'D:\data\sensors\prisma\PRS_L2D_STD_20201107101404_20201107101408_0001.he5',
            alg.P_OUTPUT_RASTER: 'c:/vsimem/prismaL2D.tif',
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-889622826, round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array(bandList=[1]))))