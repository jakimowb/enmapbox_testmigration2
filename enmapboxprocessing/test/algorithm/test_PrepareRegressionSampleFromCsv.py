from enmapboxprocessing.algorithm.prepareclassificationsamplefromcsv import PrepareClassificationSampleFromCsv
from enmapboxprocessing.algorithm.prepareregressionsamplefromcsv import PrepareRegressionSampleFromCsv
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsCsv

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareRegressionSampleFromTable(TestCase):

    def test(self):
        alg = PrepareClassificationSampleFromCsv()
        parameters = {
            alg.P_FEATURES: classificationSampleAsCsv[0],
            alg.P_LABELS: classificationSampleAsCsv[1],
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((15000, 20), dump.X.shape)
        self.assertEqual((15000, 1), dump.y.shape)
        self.assertEqual(20, len(dump.features))
        self.assertEqual(6, len(dump.categories))

    def test_david(self):
        alg = PrepareRegressionSampleFromCsv()
        parameters = {
            alg.P_FEATURES: r'C:\Users\janzandr\Downloads\ALL\all_features.txt',
            alg.P_LABELS: r'C:\Users\janzandr\Downloads\ALL\all_response.txt',
            alg.P_OUTPUT_SAMPLE: r'C:\Users\janzandr\Downloads\ALL\all_sample.pkl'
        }
        self.runalg(alg, parameters)

    def test_david2(self):
        alg = PrepareClassificationSampleFromCsv()
        parameters = {
            alg.P_FEATURES: r'C:\Users\janzandr\Downloads\berlin\features.txt',
            alg.P_LABELS: r'C:\Users\janzandr\Downloads\berlin\response.txt',
            alg.P_OUTPUT_SAMPLE: r'C:\Users\janzandr\Downloads\berlin\sample.pkl'
        }
        self.runalg(alg, parameters)
