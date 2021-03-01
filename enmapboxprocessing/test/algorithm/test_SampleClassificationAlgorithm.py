import numpy as np
from qgis._core import QgsRasterLayer, QgsVectorLayer, QgsVectorDataProvider, QgsFeature
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.sampleclassificationalgorithm import SampleClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_points_multipart_epsg3035,
                                  landcover_points_singlepart_epsg3035, landcover_raster_30m, landcover_raster_1m,
                                  landcover_raster_1m_epsg3035, landcover_raster_30m_epsg3035)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]

assert 0 # todo do we need this anymore?

class TestClassifierAlgorithm(TestCase):

    def test_sampleFromRaster_withMatchingGrid(self):
        global c
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sampleClassification_raster30m.gpkg'
        }
        result = self.runalg(alg, parameters)
        vector = QgsVectorLayer(result[alg.P_OUTPUT_SAMPLE])
        categories = Utils.categoriesFromCategorizedSymbolRenderer(
            vector.renderer()
        )
        self.assertListEqual([1, 2, 3, 4, 5, 6], [int(c[0]) for c in categories])
        self.assertListEqual(
            ['roof', 'pavement', 'low vegetation', 'tree', 'soil', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#0064ff'],
            [c[2] for c in categories])

    def test_sampleFromRaster_withNonMatchingGrid(self):
        global c
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsRasterLayer(landcover_raster_30m_epsg3035),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sampleClassification_raster30m_nonmatching.gpkg'
        }
        result = self.runalg(alg, parameters)
        vector = QgsVectorLayer(result[alg.P_OUTPUT_SAMPLE])
        categories = Utils.categoriesFromCategorizedSymbolRenderer(
            vector.renderer()
        )
        self.assertListEqual([1, 2, 3, 4, 5, 6], [int(c[0]) for c in categories])
        self.assertListEqual(
            ['roof', 'pavement', 'low vegetation', 'tree', 'soil', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#0064ff'],
            [c[2] for c in categories])

        array = np.array([f.attributes() for f in vector.getFeatures()])
        self.assertEqual((1971, 1 + 1 + 177), array.shape)  # FID, y, X[177]
        self.assertEqual(5126, np.sum(array[:, 1]))
        self.assertEqual(404148244, np.sum(array[:, 2:]))

    def test_sampleFromVectorPolygon_allPixel(self):
        global c
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sampleClassification_vectorPolygon_allPixel.gpkg'
        }
        result = self.runalg(alg, parameters)
        vector = QgsVectorLayer(result[alg.P_OUTPUT_SAMPLE])
        categories = Utils.categoriesFromCategorizedSymbolRenderer(
            vector.renderer()
        )

        self.assertListEqual([1, 2, 3], [int(c[0]) for c in categories])
        self.assertListEqual(
            ['roof', 'tree', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#267300', '#0064ff'],
            [c[2] for c in categories]
        )

        array = np.array([f.attributes() for f in vector.getFeatures()])
        self.assertEqual((898, 1 + 1 + 177), array.shape)  # FID, y, X[177]
        self.assertEqual(1381, np.sum(array[:, 1]))
        self.assertEqual(173790367, np.sum(array[:, 2:]))

    def test_sampleFromVectorPolygon_allPixel(self):
        global c
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sampleClassification_vectorPolygon_allPixel.gpkg'
        }
        result = self.runalg(alg, parameters)
        vector = QgsVectorLayer(result[alg.P_OUTPUT_SAMPLE])
        categories = Utils.categoriesFromCategorizedSymbolRenderer(
            vector.renderer()
        )

        self.assertListEqual([1, 2, 3], [int(c[0]) for c in categories])
        self.assertListEqual(
            ['roof', 'tree', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#267300', '#0064ff'],
            [c[2] for c in categories]
        )

        array = np.array([f.attributes() for f in vector.getFeatures()])
        self.assertEqual((898, 1 + 1 + 177), array.shape)  # FID, y, X[177]
        self.assertEqual(1381, np.sum(array[:, 1]))
        self.assertEqual(173790367, np.sum(array[:, 2:]))

    def test_sampleFromVectorPoints(self):
        global c
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_CLASSIFICATION: QgsVectorLayer(landcover_points_multipart_epsg3035),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sampleClassification_vectorPoint.gpkg'
        }
        result = self.runalg(alg, parameters)
        vector = QgsVectorLayer(result[alg.P_OUTPUT_SAMPLE])
        categories = Utils.categoriesFromCategorizedSymbolRenderer(
            vector.renderer()
        )
        self.assertListEqual([1, 2, 3, 4, 5], [int(c[0]) for c in categories])
        self.assertListEqual(
            ['impervious', 'low vegetation', 'tree', 'soil', 'water'],
            [c[1] for c in categories]
        )
        self.assertListEqual(
            ['#e60000', '#98e600', '#267300', '#a87000', '#0064ff'],
            [c[2] for c in categories])

        array = np.array([f.attributes() for f in vector.getFeatures()])
        self.assertEqual((58, 1 + 1 + 177), array.shape)  # FID, y, X[177]
        self.assertEqual(152, np.sum(array[:, 1]))
        self.assertEqual(16336431, np.sum(array[:, 2:]))

