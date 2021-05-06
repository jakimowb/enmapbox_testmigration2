from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedlibrary import \
    PrepareClassificationDatasetFromCategorizedLibrary
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvectorandfields import  \
    PrepareClassificationDatasetFromCategorizedVectorAndFields
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import library

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationDatasetFromCategorizedLibrary(TestCase):

    def test_default(self):
        alg = PrepareClassificationDatasetFromCategorizedLibrary()
        parameters = {
            alg.P_CATEGORIZED_LIBRARY: library,
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((58, 177), dump.X.shape)
        self.assertEqual((58, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))

    def test_selectBinaryField(self):
        alg = PrepareClassificationDatasetFromCategorizedLibrary()
        parameters = {
            alg.P_CATEGORIZED_LIBRARY: library,
            alg.P_FIELD: 'values',
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((58, 177), dump.X.shape)
        self.assertEqual((58, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
