from enmapboxprocessing.algorithm.prepareclassificationsamplefromtable import PrepareClassificationSampleFromTable
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import classificationSampleAsTable

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationSampleFromTable(TestCase):

    def test_minimallySpecified(self):
        alg = PrepareClassificationSampleFromTable()
        parameters = {
            alg.P_TABLE: classificationSampleAsTable,
            alg.P_FEATURES: [f'Band_{i + 1}' for i in range(177)],
            alg.P_LABELS: 'level_1_id',
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((58, 177), dump.X.shape)
        self.assertEqual((58, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertEqual(parameters[alg.P_FEATURES], dump.features)


    def test_fullySpecified(self):
        alg = PrepareClassificationSampleFromTable()
        parameters = {
            alg.P_TABLE: classificationSampleAsTable,
            alg.P_FEATURES: [f'Band_{i + 1}' for i in range(177)],
            alg.P_LABELS: 'level_1_id',
            alg.P_NAMES: 'level_1',
            alg.P_COLORS: 'colors',
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_SAMPLE]))
        self.assertEqual((58, 177), dump.X.shape)
        self.assertEqual((58, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertEqual(parameters[alg.P_FEATURES], dump.features)
        self.assertEqual(
            "[Category(value='1', name='impervious', color='#004242'), Category(value='2', name='vegetation', color='#00ff00'), Category(value='3', name='soil', color='#eeae02'), Category(value='4', name='water', color='#0000ff')]",
            str(dump.categories)
        )
