from qgis._core import QgsRasterLayer

from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.awesomespectralindexstackalgorithm import AwesomeSpectralIndexStackAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestAwesomeSpectralIndexAlgorithm(TestCase):

    def test_all(self):
        alg = AwesomeSpectralIndexStackAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            #alg.P_SCALE: 1e4,
            alg.P_OUTPUT_VRT: self.filename('allIndices.vrt'),
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(96, QgsRasterLayer(result[alg.P_OUTPUT_VRT]).bandCount())

    def test_vegetation(self):
        alg = AwesomeSpectralIndexStackAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_TYPE_LIST: [alg.Vegetation],
            alg.P_SCALE: 1e4,
            alg.P_OUTPUT_VRT: self.filename('vegetationIndices.vrt'),
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(72, QgsRasterLayer(result[alg.P_OUTPUT_VRT]).bandCount())
