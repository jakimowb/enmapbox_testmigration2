from enmapbox.exampledata import enmap
from enmapboxprocessing.algorithm.rasterlayerzonalaggregationalgorithm import RasterLayerZonalAggregationAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import landcover_map_l3


class TestCreateMaskAlgorithm(TestCase):

    def test(self):
        alg = RasterLayerZonalAggregationAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_CATEGORIZED_RASTER: landcover_map_l3,
            alg.P_OUTPUT_TABLE: self.filename('table.csv'),
        }
        result = self.runalg(alg, parameters)
        # self.assertEqual(6286415, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))
