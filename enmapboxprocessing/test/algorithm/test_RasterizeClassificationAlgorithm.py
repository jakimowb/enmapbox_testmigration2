from qgis._core import QgsRasterLayer, QgsVectorLayer, QgsPalettedRasterRenderer

import numpy as np

from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_polygons_3classes_epsg4326

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterizeClassificationAlgorithm(TestCase):

    def test_numberClassAttribute(self):
        assert 0 # todo

    def test_stringClassAttribute(self):
        alg = RasterizeClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_polygons.tif'
        }
        result = self.runalg(alg, parameters)
        classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
        self.assertIsInstance(classification.renderer(), QgsPalettedRasterRenderer)
        for c1, c2 in zip(
                Utils.categoriesFromCategorizedSymbolRenderer(parameters[alg.P_VECTOR].renderer()),
                Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
        ):
            self.assertEqual((c1[1], c1[2].name()), (c2[1], c2[2].name()))
        self.assertEqual(4832, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_withNoneMatching_crs(self):
        alg = RasterizeClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_polygons.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(1381, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))
