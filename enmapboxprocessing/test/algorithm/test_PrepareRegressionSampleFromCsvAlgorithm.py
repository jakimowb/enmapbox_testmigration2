from enmapboxprocessing.algorithm.prepareclassificationdatasetfromfilesalgorithm import PrepareClassificationDatasetFromFilesAlgorithm
from enmapboxprocessing.algorithm.prepareregressionsamplefromcsv import PrepareRegressionSampleFromCsv
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsCsv

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareRegressionSampleFromTable(TestCase):

    def test(self):
        alg = PrepareClassificationDatasetFromFilesAlgorithm()
        parameters = {
            alg.P_FEATURE_FILE: classificationSampleAsCsv[0],
            alg.P_VALUE_FILE: classificationSampleAsCsv[1],
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((15000, 20), dump.X.shape)
        self.assertEqual((15000, 1), dump.y.shape)
        self.assertEqual(20, len(dump.features))
        self.assertEqual(6, len(dump.categories))
