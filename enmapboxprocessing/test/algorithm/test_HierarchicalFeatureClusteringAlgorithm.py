from enmapboxprocessing.algorithm.hierarchicalfeatureclusteringalgorithm import HierarchicalFeatureClusteringAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxunittestdata import classifierDumpPkl

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestHierarchicalFeatureClusteringAlgorithm(TestCase):

    def test_reportOnly(self):
        alg = HierarchicalFeatureClusteringAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)

    def test_withSubsetting(self):
        alg = HierarchicalFeatureClusteringAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_N: 10,
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl',
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)

    def test_david(self):
        alg = HierarchicalFeatureClusteringAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: 'C:\\Users\\janzandr\\Downloads\\ALL\\all_sample.pkl',
            alg.P_NO_PLOT: not True,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)

    def test_david2(self):
        alg = HierarchicalFeatureClusteringAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_SAMPLE: 'C:\\Users\\janzandr\\Downloads\\berlin\\sample.pkl',
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)
