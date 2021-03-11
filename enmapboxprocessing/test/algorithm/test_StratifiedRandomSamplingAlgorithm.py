import json

import numpy as np
import webbrowser
from math import ceil

from qgis._core import QgsRasterLayer, QgsVectorLayer
from sklearn.ensemble import RandomForestClassifier

from enmapboxprocessing.algorithm.stratifiedrandomsampling import StratifiedRandomSamplingAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import landcover_points, landcover_polygons
from enmapboxunittestdata import landcover_map_l2, landcover_map_l3

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestClassificationPerformanceAlgorithm(TestCase):

    def test(self):
        global c
        alg = StratifiedRandomSamplingAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_STRATIFICATION: QgsRasterLayer(landcover_map_l3),
            alg.P_N: 100000000,
            alg.P_DISTANCE_GLOBAL: 0,
            alg.P_DISTANCE_STRATUM: 45,
            alg.P_SEED: 1,
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample.gpkg',
        }
        result = self.runalg(alg, parameters)
        # webbrowser.open_new(parameters[alg.P_OUTPUT_REPORT] + '.log')

    def test_kernel(self):
        self.assertTrue(np.alltrue(np.equal([[0]], StratifiedRandomSamplingAlgorithm.makeKernel(30, 30, 0))))
        self.assertTrue(np.alltrue(np.equal([[0]], StratifiedRandomSamplingAlgorithm.makeKernel(30, 30, 15))))
        self.assertTrue(np.alltrue(np.equal(
            [[1, 1, 1], [1, 0, 1], [1, 1, 1]], StratifiedRandomSamplingAlgorithm.makeKernel(30, 30, 16)
        )))
        self.assertTrue(np.alltrue(np.equal(
            [[1, 0, 1], [0, 0, 0], [1, 0, 1]], StratifiedRandomSamplingAlgorithm.makeKernel(30, 30, 30)
        )))
        self.assertTrue(np.alltrue(np.equal(
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]], StratifiedRandomSamplingAlgorithm.makeKernel(30, 30, 45)
        )))

    def test_a(self):
        rf = RandomForestClassifier()
        print(json.dumps(rf, default=lambda x: x.__dict__, indent=2))