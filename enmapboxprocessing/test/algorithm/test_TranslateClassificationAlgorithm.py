import webbrowser

import processing
from qgis._core import QgsPalettedRasterRenderer, QgsRasterLayer, QgsProcessingContext
import numpy as np

from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateCategorizedRasterAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, hires
from enmapboxunittestdata import landcover_raster_30m_epsg3035, landcover_raster_30m, landcover_raster_1m

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestTranslateClassificationAlgorithm(TestCase):

    def test_pythonCommand(self):
        alg = TranslateCategorizedRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover.tif'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_RASTER] + '.log')

    def test_default(self):
        alg = TranslateCategorizedRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(5126, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))
