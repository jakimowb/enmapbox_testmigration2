import webbrowser

import processing
from qgis._core import QgsRasterLayer, QgsVectorLayer, QgsPalettedRasterRenderer, QgsProcessingContext

import numpy as np

from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_polygons_3classes_id,
                                  landcover_points_multipart_epsg3035)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestVectorToClassificationAlgorithm(TestCase):

    def test_pythonCommand(self):
        alg = VectorToClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_id),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_polygons.tif'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_RASTER] + '.log')

    def test_numberClassAttribute(self):
        alg = VectorToClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_id),
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
            self.assertEqual((c1[1], c1[2]), (c2[1], c2[2]))

        self.assertEqual(1381, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_stringClassAttribute(self):
        alg = VectorToClassificationAlgorithm()
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
            self.assertEqual((c1[1], c1[2]), (c2[1], c2[2]))
        self.assertEqual(4832, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_withNoneMatching_crs(self):
        alg = VectorToClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_polygons.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(1381, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_pointVector(self):
        alg = VectorToClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_points_multipart_epsg3035),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/landcover_points.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(152, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_minimalCoverage(self):
        alg = VectorToClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_COVERAGE: 100,
            alg.P_OUTPUT_RASTER: c + '/vsimem/classification_fullcoverage.tif'
        }

        result = self.runalg(alg, parameters)
        self.assertEqual(3816, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))
