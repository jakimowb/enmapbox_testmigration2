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
from enmapboxtestdata import enmap, landcover_polygons, landcover_points
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_points_multipart_epsg3035,
                                  landcover_points_singlepart_epsg3035, landcover_raster_30m, landcover_raster_1m,
                                  landcover_raster_1m_epsg3035, sample, landcover_raster_30m_epsg3035)

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
        assert 0
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

    def test_default(self):
        global c
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_RASTER: QgsRasterLayer(enmap),
            algFit.P_CLASSIFICATION: QgsVectorLayer(landcover_points),
            algFit.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        self.runalg(algFit, parametersFit)

        alg = PredictClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(142058, np.sum(RasterReader(result[alg.P_OUTPUT_CLASSIFICATION]).array()))

    def test_rasterMask(self):
        global c
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_RASTER: QgsRasterLayer(enmap),
            algFit.P_CLASSIFICATION: QgsVectorLayer(landcover_points),
            algFit.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        self.runalg(algFit, parametersFit)

        alg = PredictClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            alg.P_MASK: QgsRasterLayer(landcover_raster_30m),
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(142058, np.sum(RasterReader(result[alg.P_OUTPUT_CLASSIFICATION]).array()))
