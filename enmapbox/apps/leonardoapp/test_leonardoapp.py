from enmapboxprocessing.test.algorithm.testcase import TestCase
from leonardoapp import OCPFTGlobalAlgorithm


class TestOCPFTGlobalAlgorithm(TestCase):

    def test_OCPFTGlobalAlgorithm(self):
        alg = OCPFTGlobalAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER1: 'D:\data\sensors\enmap\L2A_Arcachon_3_combined\ENMAP01-____L2A-DT000400126_20170218T110119Z_003_V000204_20200512T142942Z-SPECTRAL_IMAGE.TIF',
            alg.P_OUTPUT_GLOBAL1: 'c:/test/global1.tif',
        }
        self.runalg(alg, parameters)
