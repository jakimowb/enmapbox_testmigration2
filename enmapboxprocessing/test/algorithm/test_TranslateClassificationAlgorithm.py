import webbrowser

import numpy as np
import processing
from qgis._core import QgsRasterLayer, QgsProcessingContext

from enmapboxprocessing.algorithm.translatecategorizedrasteralgorithm import TranslateCategorizedRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap
from enmapboxunittestdata import landcover_raster_30m_epsg3035

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestTranslateClassificationAlgorithm(TestCase):

    def test_pythonCommand(self):
        alg = TranslateCategorizedRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CATEGORIZED_RASTER: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_CATEGORIZED_RASTER: c + '/vsimem/landcover.tif'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_CATEGORIZED_RASTER] + '.log')

    def test_default(self):
        alg = TranslateCategorizedRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CATEGORIZED_RASTER: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_CATEGORIZED_RASTER: c + '/vsimem/landcover.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(5126, np.sum(RasterReader(result[alg.P_OUTPUT_CATEGORIZED_RASTER]).array()))
