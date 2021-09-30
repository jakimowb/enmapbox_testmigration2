import numpy as np
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapbox.exampledata import enmap, landcover_polygons, landcover_points
from enmapboxtestdata import landcover_raster_30m, classifierDumpPkl

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


class TestPredictClassificationAlgorithm(TestCase):

    def test_default(self):
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_DATASET: classifierDumpPkl,
            algFit.P_CLASSIFIER: algFit.defaultCodeAsString(),
            algFit.P_OUTPUT_CLASSIFIER: 'c:/vsimem/classifier.pkl',
        }
        self.runalg(algFit, parametersFit)

        alg = PredictClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(127249, np.sum(RasterReader(result[alg.P_OUTPUT_CLASSIFICATION]).array()))

    def test_rasterMask(self):
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_DATASET: classifierDumpPkl,
            algFit.P_CLASSIFIER: algFit.defaultCodeAsString(),
            algFit.P_OUTPUT_CLASSIFIER: 'c:/vsimem/classifier.pkl',
        }
        self.runalg(algFit, parametersFit)

        alg = PredictClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            alg.P_MASK: landcover_raster_30m,
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(3277, np.sum(RasterReader(result[alg.P_OUTPUT_CLASSIFICATION]).array()))

    def test_vectorMask(self):
        algFit = FitTestClassifierAlgorithm()
        algFit.initAlgorithm()
        parametersFit = {
            algFit.P_DATASET: classifierDumpPkl,
            algFit.P_CLASSIFIER: algFit.defaultCodeAsString(),
            algFit.P_OUTPUT_CLASSIFIER: 'c:/vsimem/classifier.pkl',
        }
        self.runalg(algFit, parametersFit)

        alg = PredictClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CLASSIFIER: parametersFit[algFit.P_OUTPUT_CLASSIFIER],
            alg.P_MASK: landcover_polygons,
            alg.P_OUTPUT_CLASSIFICATION: c + '/vsimem/classification.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(3277, np.sum(RasterReader(result[alg.P_OUTPUT_CLASSIFICATION]).array()))
