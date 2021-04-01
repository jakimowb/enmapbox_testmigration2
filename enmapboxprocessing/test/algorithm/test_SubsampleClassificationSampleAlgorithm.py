from enmapboxprocessing.algorithm.subsampleclassificationsamplealgorithm import SubsampleClassificationSampleAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import (classifierDumpPkl)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestSubsampleClassificationSampleAlgorithm(TestCase):

    def test_N(self):
        alg = SubsampleClassificationSampleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_N: 100,
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        self.assertEqual(482, len(Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE])['X']))

    def test_N_withReplacemant(self):
        alg = SubsampleClassificationSampleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_N: 100,
            alg.P_REPLACE: True,
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        self.assertEqual(600, len(Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE])['X']))

    def test_P(self):
        alg = SubsampleClassificationSampleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_N: 10,
            alg.P_PROPORTIONAL: True,
            alg.P_REPLACE: True,
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        self.assertEqual(193, len(Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE])['X']))
