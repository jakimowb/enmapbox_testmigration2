import webbrowser

import numpy as np
import processing
from qgis._core import QgsProcessingContext
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_points_multipart_epsg3035,
                                  landcover_points_singlepart_epsg3035, landcover_raster_30m,
                                  classificationSampleAsVector, classifierDumpPkl)

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
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_polygons,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_CLASSIFIER] + '.log')

    def test_style(self):
        pass  # do not need to test correct output styling, because we check this internally

    def test_vectorSample(self):
        global c
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: classificationSampleAsVector,
            alg.P_FEATURE_FIELDS: [f'Sample__{i + 1}' for i in range(177)],
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(142169, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(-13052, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_polygonLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_polygons,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(193260, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(-29894, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_polygonLabels_withDifferentCrs_andClassSubset(self):
        global c
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_polygons_3classes_epsg4326,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(113010, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(20632, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_singlePart_pointLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_points_singlepart_epsg3035,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(142058, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(-13052, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_singlePart_pointLabels_rasterized(self):
        global c
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_points_singlepart_epsg3035,
            alg.P_RASTERIZE_POINTS: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)

        # Note that the results differ slightly from the results with direct point reading.
        # The training data is the same in both cases, but the samples are order differently.
        # Different ordering will result in a different RFC model, even with equal random seed.
        # That may be a bit surprising at first :-)
        self.assertEqual(127249, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        # Sums of probabilities are equal!
        self.assertEqual(-13052, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_multiPart_pointLabels(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_points_multipart_epsg3035,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(142058, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(-13052, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_multiPart_pointLabels_rasterized(self):
        pass  # we do not need to test multi-part vector rasterization

    def test_sampleSize_absolute(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
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
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
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
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_SAMPLE_SIZE: 1000,
            alg.P_REPLACE: True,
            alg.P_SAVE_DATA: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories, X, y = Utils.pickleLoadClassifier(result[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual(6000, len(y))

    def test_dumpAsJson(self):
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_DUMP_AS_JSON: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        self.runalg(alg, parameters)
        # check the result manually

    def test_saveData(self):
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_SAVE_DATA: True,
            alg.P_DUMP_AS_JSON: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        self.runalg(alg, parameters)
        dump = Utils.pickleLoad(parameters[alg.P_OUTPUT_CLASSIFIER])
        self.assertEqual((2028, 177), dump['X'].shape)
        self.assertEqual((2028, 1), dump['y'].shape)
        dump = Utils.jsonLoad(parameters[alg.P_OUTPUT_CLASSIFIER] + '.json')
        self.assertEqual((2028, 177), dump['X'].shape)
        self.assertEqual((2028, 1), dump['y'].shape)

    def test_evalTrainPerformance(self):
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_EVAL_TRAIN_PERFORMANCE: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        self.runalg(alg, parameters)
        # check the result manually

    def test_evalCrossPerformance(self):
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_EVAL_CROSS_PERFORMANCE: 3,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        self.runalg(alg, parameters)
        # check the result manually

    def test_evalPermutationFeatureImportance(self):
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: landcover_raster_30m,
            alg.P_EVAL_PERMUTATION_FEATURE_IMPORTANCE: True,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        self.runalg(alg, parameters)
        # check the result manually

    def test_pklSample(self):
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFICATION: classifierDumpPkl,
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif',
            alg.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        self.runalg(alg, parameters)
        self.assertEqual(142169, np.sum(RasterReader(parameters[alg.P_OUTPUT_CLASSIFICATION]).array()))
        self.assertEqual(-13052, np.round(np.sum(RasterReader(parameters[alg.P_OUTPUT_PROBABILITY]).array())))

    def test_classifiers(self):
        algs = [
            FitRandomForestClassifierAlgorithm(), FitGaussianProcessClassifierAlgorithm(), FitLinearSvcAlgorithm(),
            FitSvcAlgorithm(),
        ]
        for alg in algs:
            print(alg.displayName())
            alg.initAlgorithm()
            alg.shortHelpString()
