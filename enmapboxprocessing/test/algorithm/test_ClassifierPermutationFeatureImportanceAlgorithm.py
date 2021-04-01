from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.classifierpermutationfeatureimportancealgorithm import \
    ClassifierPermutationFeatureImportanceAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxunittestdata import (classifierDumpPkl)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestClassifierPerformanceAlgorithm(TestCase):

    def test(self):
        alg = ClassifierPermutationFeatureImportanceAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFIER: classifierDumpPkl,
            alg.P_SAMPLE: classifierDumpPkl,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html'
        }
        self.runalg(alg, parameters)
