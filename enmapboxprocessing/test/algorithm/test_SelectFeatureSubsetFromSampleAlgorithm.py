from enmapboxprocessing.algorithm.selectfeaturesubsetfromsamplealgorithm import SelectFeatureSubsetFromSampleAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import (classifierDumpPkl)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestSelectFeatureSubsetFromSampleAlgorithm(TestCase):

    def test(self):
        alg = SelectFeatureSubsetFromSampleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_FEATURE_LIST: "1, 'Band 011: band 18 (0.508000 Micrometers)', 177",
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((1924, 3), dump.X.shape)
        self.assertListEqual(
            ['Band 001: band 8 (0.460000 Micrometers)', 'Band 011: band 18 (0.508000 Micrometers)',
             'Band 177: band 239 (2.409000 Micrometers)']
            , dump.features
        )
