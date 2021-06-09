from enmapboxprocessing.algorithm.featureclusteringhierarchicalalgorithm import FeatureClusteringHierarchicalAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxunittestdata import classifierDumpPkl

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestFeatureClusteringHierarchicalAlgorithm(TestCase):

    def test(self):
        alg = FeatureClusteringHierarchicalAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_DATASET: classifierDumpPkl,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)
