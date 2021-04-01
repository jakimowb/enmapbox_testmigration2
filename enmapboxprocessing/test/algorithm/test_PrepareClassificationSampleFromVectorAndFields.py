from enmapboxprocessing.algorithm.prepareclassificationsamplefromvectorandfields import \
    PrepareClassificationSampleFromVectorAndFields
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsVector

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationSampleFromVectorAndFields(TestCase):

    def test(self):
        alg = PrepareClassificationSampleFromVectorAndFields()
        parameters = {
            alg.P_VECTOR: classificationSampleAsVector,
            alg.P_FIELDS: [f'Sample__{i + 1}' for i in range(177)],
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((299, 177), dump.X.shape)
        self.assertEqual((299, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))

        print(dump.features)
        print(dump.categories)
        self.assertEqual(parameters[alg.P_FIELDS], dump.features)
        self.assertEqual(
            "[Category(value=1, name='impervious', color='#e60000'), Category(value=2, name='low vegetation', color='#98e600'), Category(value=3, name='tree', color='#267300'), Category(value=4, name='soil', color='#a87000'), Category(value=5, name='water', color='#0064ff')]",
            str(dump.categories)
        )
