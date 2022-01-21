import numpy as np

from enmapboxprocessing.algorithm.importprismal2dalgorithm import ImportPrismaL2DAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestImportPrismaL2DAlgorithm(TestCase):

    def test(self):
        if not self.sensorProductsFolderExists():
            return

        alg = ImportPrismaL2DAlgorithm()
        parameters = {
            alg.P_FILE: r'D:\data\sensors\prisma\PRS_L2D_STD_20201107101404_20201107101408_0001.he5',
            alg.P_OUTPUT_SPECTRAL_CUBE: self.filename('prismaL2D_SPECTRAL.tif'),
            alg.P_OUTPUT_SPECTRAL_GEOLOCATION: self.filename('prismaL2D_SPECTRAL_GEOLOCATION.vrt'),
            alg.P_OUTPUT_SPECTRAL_GEOMETRIC: self.filename('prismaL2D_SPECTRAL_GEOMETRIC.vrt'),
            alg.P_OUTPUT_SPECTRAL_ERROR: self.filename('prismaL2D_SPECTRAL_ERROR.tif'),

            alg.P_OUTPUT_PAN_CUBE: self.filename('prismaL2D_PAN.vrt'),
            alg.P_OUTPUT_PAN_GEOLOCATION: self.filename('prismaL2D_PAN_GEOLOCATION.vrt'),
            alg.P_OUTPUT_PAN_ERROR: self.filename('prismaL2D_PAN_ERROR.vrt'),

        }
        result = self.runalg(alg, parameters)
        #self.assertEqual(24335132, round(np.sum(RasterReader(result[alg.P_OUTPUT_SPECTRAL_CUBE]).array())))
