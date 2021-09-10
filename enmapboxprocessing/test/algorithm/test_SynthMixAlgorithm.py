from enmapboxprocessing.algorithm.synthmixalgorithm import SynthMixAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxunittestdata import (classifierDumpPkl)


class TestFitClassifierAlgorithm(TestCase):

    def test(self):
        alg = SynthMixAlgorithm()
        parameters = {
            alg.P_DATASET: classifierDumpPkl,
            alg.P_N: 10,
            alg.P_INCLUDE_ENDMEMBER: False,
            alg.P_OUTPUT_DATASET: 'c:/vsimem/synthmix.pkl',
        }
        self.runalg(alg, parameters)
