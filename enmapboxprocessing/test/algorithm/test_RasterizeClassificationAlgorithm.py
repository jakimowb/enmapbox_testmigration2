from qgis._core import QgsRasterLayer, QgsVectorLayer

import numpy as np

from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_polygons_3classes_epsg4326

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestRasterizeClassificationAlgorithm(TestCase):

    def test_default(self):
        alg = RasterizeClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_polygons.tif'
        }
        result = self.runalg(alg, parameters)
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
