import numpy as np

from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_raster_1m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestClassificationToFractionAlgorithm(TestCase):

    def test_vector(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: landcover_polygons,
            alg.P_GRID: enmap,
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-84958, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0])))

    def test_raster(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: landcover_raster_1m,
            alg.P_GRID: enmap,
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-84958, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0])))