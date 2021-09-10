import numpy as np
from qgis._core import QgsRasterLayer, QgsVectorLayer

from enmapboxprocessing.algorithm.randompointsfromcategorizedrasteralgorithm import \
    RandomPointsFromCategorizedRasterAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxunittestdata import landcover_map_l3

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRandomPointsFromCategorizedRasterAlgorithm(TestCase):

    def test(self):
        global c
        alg = RandomPointsFromCategorizedRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_STRATIFICATION: QgsRasterLayer(landcover_map_l3),
            alg.P_N: 100000000,
            alg.P_DISTANCE_GLOBAL: 0,
            alg.P_DISTANCE_STRATUM: 45,
            alg.P_SEED: 42,
            alg.P_OUTPUT_POINTS: c + '/vsimem/points.gpkg',
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(26317, QgsVectorLayer(parameters[alg.P_OUTPUT_POINTS]).featureCount())
        # webbrowser.open_new(parameters[alg.P_OUTPUT_REPORT] + '.log')

    def test_kernel(self):
        self.assertTrue(np.alltrue(np.equal([[0]], RandomPointsFromCategorizedRasterAlgorithm.makeKernel(30, 30, 0))))
        self.assertTrue(np.alltrue(np.equal([[0]], RandomPointsFromCategorizedRasterAlgorithm.makeKernel(30, 30, 15))))
        self.assertTrue(np.alltrue(np.equal(
            [[1, 1, 1], [1, 0, 1], [1, 1, 1]], RandomPointsFromCategorizedRasterAlgorithm.makeKernel(30, 30, 16)
        )))
        self.assertTrue(np.alltrue(np.equal(
            [[1, 0, 1], [0, 0, 0], [1, 0, 1]], RandomPointsFromCategorizedRasterAlgorithm.makeKernel(30, 30, 30)
        )))
        self.assertTrue(np.alltrue(np.equal(
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]], RandomPointsFromCategorizedRasterAlgorithm.makeKernel(30, 30, 45)
        )))
