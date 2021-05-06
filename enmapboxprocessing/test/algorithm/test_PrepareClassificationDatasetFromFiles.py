from enmapboxprocessing.algorithm.prepareclassificationdatasetfromfiles import PrepareClassificationDatasetFromFiles
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsCsv

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationDatasetFromFiles(TestCase):

    def test(self):
        alg = PrepareClassificationDatasetFromFiles()
        parameters = {
            alg.P_FEATURE_FILE: classificationSampleAsCsv[0],
            alg.P_VALUE_FILE: classificationSampleAsCsv[1],
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((15000, 20), dump.X.shape)
        self.assertEqual((15000, 1), dump.y.shape)
        self.assertEqual(20, len(dump.features))
        self.assertEqual(6, len(dump.categories))
        self.assertEqual(['feature 1', 'feature 2'], dump.features[:2])
        self.assertListEqual([1, 2, 3, 4, 5, 6], [c.value for c in dump.categories])
        self.assertListEqual(['1', '2', '3', '4', '5', '6'], [c.name for c in dump.categories])

    def _test_david(self):
        alg = PrepareClassificationDatasetFromFiles()
        parameters = {
            alg.P_FEATURES: r'C:\Users\janzandr\Downloads\ALL\all_features.txt',
            alg.P_LABELS: r'C:\Users\janzandr\Downloads\ALL\all_response.txt',
            alg.P_OUTPUT_SAMPLE: r'C:\Users\janzandr\Downloads\ALL\all_sample.pkl'
        }
        self.runalg(alg, parameters)

    def _test_david2(self):
        alg = PrepareClassificationDatasetFromFiles()
        parameters = {
            alg.P_FEATURES: r'C:\Users\janzandr\Downloads\berlin\features.txt',
            alg.P_LABELS: r'C:\Users\janzandr\Downloads\berlin\response.txt',
            alg.P_OUTPUT_SAMPLE: r'C:\Users\janzandr\Downloads\berlin\sample.pkl'
        }
        self.runalg(alg, parameters)
