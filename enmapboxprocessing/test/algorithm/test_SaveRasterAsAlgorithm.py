from os.path import exists

import numpy as np
from qgis._core import QgsRasterLayer, QgsRasterRenderer

from enmapbox.exampledata import enmap, hires
from enmapboxprocessing.algorithm.saverasterlayerasalgorithm import SaveRasterAsAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import landcover_raster_30m_epsg3035

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestTranslateAlgorithm(TestCase):

    def test_default(self):
        alg = SaveRasterAsAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/raster.tif'
        }
        result = self.runalg(alg, parameters)
        gold = RasterReader(enmap).array()
        lead = RasterReader(result[alg.P_OUTPUT_RASTER]).array()
        self.assertEqual(gold[0].dtype, lead[0].dtype)
        self.assertEqual(np.sum(gold), np.sum(lead))
