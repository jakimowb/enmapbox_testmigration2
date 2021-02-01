from qgis._core import QgsPalettedRasterRenderer, QgsRasterLayer
import numpy as np

from enmapboxprocessing.algorithm.translateclassification import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, hires
from enmapboxunittestdata import landcover_raster_30m_epsg3035, landcover_raster_30m, landcover_raster_1m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestTranslateClassificationAlgorithm(TestCase):

    def test_default(self):
        alg = TranslateClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_1m),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(4835, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))
