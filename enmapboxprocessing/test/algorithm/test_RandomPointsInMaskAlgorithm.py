from qgis._core import QgsRasterLayer, QgsVectorLayer

from enmapboxprocessing.algorithm.randompointsfrommaskrasteralgorithm import RandomPointsFromMaskRasterAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRandomPointsInMaskAlgorithm(TestCase):

    def test(self):
        global c
        alg =  RandomPointsFromMaskRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_MASK: QgsRasterLayer(enmap),
            alg.P_N: 100000000,
            alg.P_DISTANCE: 300,
            alg.P_SEED: 42,
            alg.P_OUTPUT_POINTS: c + '/vsimem/points.gpkg',
        }
        self.runalg(alg, parameters)
        #self.assertEqual(26317, QgsVectorLayer(parameters[alg.P_OUTPUT_VECTOR]).featureCount())
