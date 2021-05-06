import webbrowser

import numpy as np
from qgis._core import QgsRasterLayer, QgsVectorLayer

from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm

from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import landcover_polygons
from enmapboxunittestdata import landcover_map_l3

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]

class TestClassificationPerformanceSimpleAlgorithm(TestCase):

    def test(self):
        alg = ClassificationPerformanceSimpleAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_map_l3),
            alg.P_REFERENCE: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_REPORT: c + '/vsimem/report.html',
        }
        self.runalg(alg, parameters)
        webbrowser.open_new(parameters[alg.P_OUTPUT_REPORT])
        #webbrowser.open_new(parameters[alg.P_OUTPUT_REPORT] + '.csv')
