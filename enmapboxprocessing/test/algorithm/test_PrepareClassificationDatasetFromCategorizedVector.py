from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvector import \
    PrepareClassificationDatasetFromCategorizedVector
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons, landcover_points

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestPrepareClassificationSampleFromCategorizedVector(TestCase):

    def test_styled_poly(self):
        alg = PrepareClassificationDatasetFromCategorizedVector()
        parameters = {
            alg.P_FEATURE_RASTER: enmap,
            alg.P_CATEGORIZED_VECTOR: landcover_polygons,
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((2028, 177), dump.X.shape)
        self.assertEqual((2028, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertEqual(['band 8 (0.460000 Micrometers)', 'band 9 (0.465000 Micrometers)'], dump.features[:2])
        self.assertListEqual([1, 2, 3, 4, 5, 6], [c.value for c in dump.categories])
        self.assertListEqual(
            ['roof', 'pavement', 'low vegetation', 'tree', 'soil', 'water'], [c.name for c in dump.categories]
        )

    def test_styled_point(self):
        alg = PrepareClassificationDatasetFromCategorizedVector()
        parameters = {
            alg.P_FEATURE_RASTER: enmap,
            alg.P_CATEGORIZED_VECTOR: landcover_points,
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((58, 177), dump.X.shape)
        self.assertEqual((58, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertEqual(['band 8 (0.460000 Micrometers)', 'band 9 (0.465000 Micrometers)'], dump.features[:2])
        self.assertListEqual([1, 2, 3, 4, 5], [c.value for c in dump.categories])
        self.assertListEqual(
            ['impervious', 'low vegetation', 'tree', 'soil', 'water'], [c.name for c in dump.categories]
        )

    def test_field_poly(self):
        alg = PrepareClassificationDatasetFromCategorizedVector()
        parameters = {
            alg.P_FEATURE_RASTER: enmap,
            alg.P_CATEGORIZED_VECTOR: landcover_polygons,
            alg.P_CATEGORY_FIELD: 'level_3',
            alg.P_OUTPUT_DATASET: c + '/vsimem/sample.pkl'
        }
        self.runalg(alg, parameters)
        dump = ClassifierDump(**Utils.pickleLoad(parameters[alg.P_OUTPUT_DATASET]))
        self.assertEqual((1924, 177), dump.X.shape)
        self.assertEqual((1924, 1), dump.y.shape)
        self.assertEqual(177, len(dump.features))
        self.assertEqual(['band 8 (0.460000 Micrometers)', 'band 9 (0.465000 Micrometers)'], dump.features[:2])
        self.assertListEqual([1, 2, 3, 4, 5, 6], [c.value for c in dump.categories])
        self.assertListEqual(
            ['low vegetation', 'pavement', 'roof', 'soil', 'tree', 'water'],
            [c.name for c in dump.categories]
        )
