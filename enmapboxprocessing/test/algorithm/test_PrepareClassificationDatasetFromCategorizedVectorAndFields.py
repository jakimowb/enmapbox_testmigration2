from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvectorandfields import  \
    PrepareClassificationDatasetFromCategorizedVectorAndFields
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsVector

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationDatasetFromVectorAndFields(TestCase):

    def test(self):
        alg = PrepareClassificationDatasetFromCategorizedVectorAndFields()
        parameters = {
            alg.P_CATEGORIZED_VECTOR: classificationSampleAsVector,
            alg.P_FEATURE_FIELDS: [f'Sample__{i + 1}' for i in range(177)],
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((299, 177), dump.X.shape)
        self.assertEqual((299, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertListEqual(parameters[alg.P_FEATURE_FIELDS], dump.features)
        self.assertListEqual([1, 2, 3, 4, 5], [c.value for c in dump.categories])
        self.assertListEqual(
            ['impervious', 'low vegetation', 'tree', 'soil', 'water'], [c.name for c in dump.categories]
        )

