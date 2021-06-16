import numpy as np
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.creatergbimagefromclassprobabilityalgorithm import \
    CreateRgbImageFromClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons, landcover_points
from enmapboxunittestdata import landcover_raster_30m, classifierDumpPkl

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


class TestCreateRgbImageFromClassProbabilityAlgorithm(TestCase):

    def test_colorsFromLayer(self):
        global c
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_DATASET: classifierDumpPkl,
            algFit.P_CLASSIFIER: algFit.defaultCodeAsString(),
            algFit.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        result = self.runalg(algFit, parametersFit)

        algPredict1 = PredictClassificationAlgorithm()
        algPredict1.initAlgorithm()
        parametersPredict1 = {
            algPredict1.P_RASTER: enmap,
            algPredict1.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            algPredict1.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(algPredict1, parametersPredict1)

        algPredict2 = PredictClassPropabilityAlgorithm()
        algPredict2.initAlgorithm()
        parametersPredict2 = {
            algPredict2.P_RASTER: enmap,
            algPredict2.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            algPredict2.P_OUTPUT_PROBABILITY: c + '/vsimem/probability.tif'
        }
        result = self.runalg(algPredict2, parametersPredict2)

        # test colors from layer
        alg = CreateRgbImageFromClassProbabilityAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_PROBABILITY: parametersPredict2[algPredict2.P_OUTPUT_PROBABILITY],
            alg.P_COLORS_LAYER: parametersPredict1[algPredict1.P_OUTPUT_CLASSIFICATION],
            alg.P_OUTPUT_RGB: c + '/vsimem/rgb.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(16826968, np.sum(RasterReader(result[alg.P_OUTPUT_RGB]).array()))

        # test colors from list
        colors = str([c.color for c in ClassifierDump(**Utils.pickleLoad(classifierDumpPkl)).categories])
        parameters = {
            alg.P_PROBABILITY: parametersPredict2[algPredict2.P_OUTPUT_PROBABILITY],
            alg.P_COLORS: colors,
            alg.P_OUTPUT_RGB: c + '/vsimem/rgb.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(16826968, np.sum(RasterReader(result[alg.P_OUTPUT_RGB]).array()))
