import numpy as np
from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.aggregaterasterbandsalgorithm import AggregateRasterBandsAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestAggregateRasterBandsAlgorithm(TestCase):

    def test_default(self):
        alg = AggregateRasterBandsAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_OUTPUT_RASTER: self.filename('aggregations.tif')
        }
        result = self.runalg(alg, parameters)
        reader = RasterReader(result[alg.P_OUTPUT_RASTER])
        array = reader.array()
        self.assertAlmostEqual(4388.7344, np.max(array), 4)

    def test_median(self):
        alg = AggregateRasterBandsAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_FUNCTION: [alg.MedianFunction],
            alg.P_OUTPUT_RASTER: self.filename('aggregations.tif')
        }
        result = self.runalg(alg, parameters)
        reader = RasterReader(result[alg.P_OUTPUT_RASTER])
        array = reader.array()
        self.assertAlmostEqual(4669, np.max(array))

    def test_all(self):
        alg = AggregateRasterBandsAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_FUNCTION: list(range(len(alg.FUNCTIONS))),
            alg.P_OUTPUT_RASTER: self.filename('aggregations.tif')
        }
        result = self.runalg(alg, parameters)
        reader = RasterReader(result[alg.P_OUTPUT_RASTER])
        array = reader.array()
        self.assertEqual(len(alg.FUNCTIONS), len(array))