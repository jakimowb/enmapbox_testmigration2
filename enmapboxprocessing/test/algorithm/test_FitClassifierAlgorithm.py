import webbrowser

import numpy as np
import processing
from qgis._core import QgsRasterLayer, QgsVectorLayer, QgsProcessingContext
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_points_multipart_epsg3035,
                                  landcover_points_singlepart_epsg3035, landcover_raster_30m, landcover_raster_1m,
                                  landcover_raster_1m_epsg3035, sample)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class FitTestClassifierAlgorithm(FitClassifierAlgorithmBase):

    def displayName(self) -> str:
        return ''

    def shortDescription(self) -> str:
        return ''

    def helpParameterCode(self) -> str:
        return ''

    def code(self) -> ClassifierMixin:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators=10, oob_score=True, random_state=42)
        return classifier


class TestFitClassifierAlgorithm(TestCase):

    def test_pythonCommand(self):
        alg = FitRandomForestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_CLASSIFIER] + '.log')

    def test_vectorSample(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(sample),
            alg.P_FEATURE_FIELDS: [f'Sample__{i + 1}' for i in range(177)],
            alg.P_SAVE_DATA: True,
            alg.P_DUMP_AS_JSON: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        #webbrowser.open_new(parameters[alg.P_OUTPUT_CLASSIFIER] + '.json')

    def test_polygonLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertListEqual([1, 2, 3, 4, 5, 6], [c[0] for c in categories])
        self.assertListEqual(
            ['roof', 'pavement', 'low vegetation', 'tree', 'soil', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#0064ff'],
            [c[2] for c in categories])

    def test_polygonLabels_withDifferentCrs_andClassSubset(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        assert isinstance(classifier, ClassifierMixin)
        self.assertListEqual(
            ['roof', 'tree', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#267300', '#0064ff'],
            [c[2] for c in categories])

    def test_singlePart_pointLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_points_singlepart_epsg3035),
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(58, len(y))
        self.assertEqual(152, np.sum(y))
        self.assertEqual(16336431, np.sum(X))

    def test_singlePart_pointLabels_rasterized(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_points_singlepart_epsg3035),
            alg.P_RASTERIZE_POINTS: True,
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(58, len(y))
        self.assertEqual(152, np.sum(y))
        self.assertEqual(16336431, np.sum(X))

    def test_multiPart_pointLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_points_multipart_epsg3035),
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(58, len(y))
        self.assertEqual(152, np.sum(y))
        self.assertEqual(16336431, np.sum(X))

    def test_multiPart_pointLabels_rasterized(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_points_multipart_epsg3035),
            alg.P_SAVE_DATA: True,
            alg.P_RASTERIZE_POINTS: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(58, len(y))
        self.assertEqual(152, np.sum(y))
        self.assertEqual(16336431, np.sum(X))

    def test_rasterLabels_withMatchingGrid(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(2028, len(y))
        self.assertEqual(5260, np.sum(y))
        self.assertEqual(417748998, np.sum(X))

    def test_rasterLabels_withNonMatchingResolution(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_1m),
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(1922, len(y))
        self.assertEqual(4835, np.sum(y))
        self.assertEqual(396655550, np.sum(X))

    def test_rasterLabels_withNonMatchingCrs(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_1m_epsg3035),
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(1911, len(y))
        self.assertEqual(4837, np.sum(y))
        self.assertEqual(394330702, np.sum(X))

    def test_sampleSize_absolute(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_SAMPLE_SIZE: 5,
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(30, len(y))
        self.assertEqual(105, np.sum(y))

    def test_sampleSize_relative(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_SAMPLE_SIZE: 0.5,
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(1016, len(y))

    def test_sampleSize_withReplacement(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_SAMPLE_SIZE: 1000,
            alg.P_REPLACE: True,
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(6000, len(y))

    def test_predictClassification(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/classPropability.tif',
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)

    def test_dumpAsJson(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_DUMP_AS_JSON: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)

    def test_classifiers(self):
        algs = [FitRandomForestClassifierAlgorithm()]
        for alg in algs:
            alg.initAlgorithm()
            alg.shortHelpString()
