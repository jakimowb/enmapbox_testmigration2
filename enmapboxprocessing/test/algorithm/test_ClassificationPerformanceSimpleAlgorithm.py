import webbrowser
from math import nan, isnan

import numpy as np
from qgis._core import QgsRasterLayer, QgsVectorLayer

from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm

from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import landcover_polygons
from enmapboxunittestdata import landcover_map_l3

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]

class TestClassificationPerformanceSimpleAlgorithm(TestCase):

    def test(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: landcover_map_l3,
            alg.P_REFERENCE: landcover_polygons,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html',
        }
        self.runalg(alg, parameters)

    def test_perfectMap(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: landcover_map_l3,
            alg.P_REFERENCE: landcover_map_l3,
            alg.P_OPEN_REPORT: False,
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html',
        }
        result = self.runalg(alg, parameters)
        stats = Utils.jsonLoad(result[alg.P_OUTPUT_REPORT] + '.json')
        for v in stats['producers_accuracy_se'] + stats['users_accuracy_se']:
            self.assertFalse(isnan(v))
