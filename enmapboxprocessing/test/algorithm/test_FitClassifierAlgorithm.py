import numpy as np
from qgis._core import QgsRasterLayer, QgsVectorLayer
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons

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


class TestClassifierAlgorithm(TestCase):

    def test_default(self):
        global c
        alg = FitTestClassifierAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl'
        }
        result = self.runalg(alg, parameters)
        classifier, categories = Utils.pickleLoad(result[alg.P_OUTPUT_CLASSIFIER])
        assert isinstance(classifier, ClassifierMixin)
        self.assertListEqual([1, 2, 3, 4, 5, 6], [c[0] for c in categories])
        self.assertListEqual(
            ['roof', 'pavement', 'low vegetation', 'tree', 'soil', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#0064ff'],
            [c[2].name() for c in categories])

        alg2 = PredictClassificationAlgorithm()
        alg2.initAlgorithm()
        parameters2 = {
            alg2.P_RASTER: QgsRasterLayer(enmap),
            alg2.P_CLASSIFIER: result[alg.P_OUTPUT_CLASSIFIER],
            alg2.P_OUTPUT_RASTER: c + '/vsimem/classification.tif'
        }
        result2 = self.runalg(alg2, parameters2)
        self.assertEqual(193260, RasterReader(result2[alg2.P_OUTPUT_RASTER]).array()[0].sum())

        alg3 = PredictClassPropabilityAlgorithm()
        alg3.initAlgorithm()
        parameters3 = {
            alg3.P_RASTER: QgsRasterLayer(enmap),
            alg3.P_CLASSIFIER: result[alg.P_OUTPUT_CLASSIFIER],
            alg3.P_OUTPUT_RASTER: c + '/vsimem/probability.tif'
        }
        result3 = self.runalg(alg3, parameters3)
        return
        self.assertEqual(193721, np.sum(RasterReader(result3[alg2.P_OUTPUT_RASTER]).array()))
