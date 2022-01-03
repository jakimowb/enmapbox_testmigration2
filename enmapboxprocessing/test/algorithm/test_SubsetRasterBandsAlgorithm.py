import numpy as np
from qgis._core import QgsRasterLayer

from enmapbox.exampledata import enmap, hires
from enmapboxprocessing.algorithm.saverasterlayerasalgorithm import SaveRasterAsAlgorithm
from enmapboxprocessing.algorithm.subsetrasterbandsalgorithm import SubsetRasterBandsAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase


class TestSubsetRasterBandsAlgorithm(TestCase):

    def test_default(self):
        alg = SubsetRasterBandsAlgorithm()
        parameters = {
            alg.P_RASTER: enmap,
            alg.P_BAND_LIST: [1, 11, 21],
            alg.P_OUTPUT_RASTER: self.filename('raster.vrt')
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array(bandList=[1, 11, 21])
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(gold[0].dtype, lead[0].dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))
