import numpy as np

from enmapbox.exampledata import enmap, landcover_polygons
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import landcover_raster_1m


class TestClassificationToFractionAlgorithm(TestCase):

    def test_vector(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_CATEGORIZED_LAYER: landcover_polygons,
            alg.P_GRID: enmap,
            alg.P_OUTPUT_FRACTION: self.filename('fraction.tif')
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-84958, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_FRACTION]).array()[0])))

    def test_raster(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_CATEGORIZED_LAYER: landcover_raster_1m,
            alg.P_GRID: enmap,
            alg.P_OUTPUT_FRACTION: self.filename('fraction.tif')
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-84958, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_FRACTION]).array()[0])))
