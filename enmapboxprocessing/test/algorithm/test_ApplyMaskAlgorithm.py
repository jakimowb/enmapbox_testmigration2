import numpy as np

from enmapboxprocessing.algorithm.applymaskalgorithm import ApplyMaskAlgorithm
from enmapboxprocessing.algorithm.layertomaskalgorithm import LayerToMaskAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons


class TestLayerToMaskAlgorithm(TestCase):

    def test_raster(self):
        alg = ApplyMaskAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_MASK: landcover_polygons,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/masked.tif',
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-7549619, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array(bandList=[1])))