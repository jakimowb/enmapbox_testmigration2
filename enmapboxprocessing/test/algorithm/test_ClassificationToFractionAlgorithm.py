from qgis._core import QgsRasterLayer, QgsVectorLayer
import numpy as np

from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_l3_1m, landcover_polygons_l3_1m_3classes,
                                  landcover_polygons_3classes, landcover_polygons_3classes_epsg4326)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]

class TestClassificationToFractionAlgorithm(TestCase):

    def test_defaultVector(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: QgsVectorLayer(landcover_polygons),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(21835742, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_defaultRaster(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: QgsVectorLayer(landcover_polygons),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(21835742, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())


    def test_raster_withNonMatching_crs(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: QgsRasterLayer(landcover_polygons_l3_1m_3classes),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(21885796, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_vector_withNonMatching_crs(self):
        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: QgsVectorLayer(landcover_polygons_3classes_epsg4326),
            alg.P_GRID: QgsRasterLayer(enmap),
            alg.P_OUTPUT_RASTER: c + '/vsimem/fraction.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(21835742, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_vectorSource_floatPrecision(self):
        vector = QgsVectorLayer(landcover_polygons)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()
        alg.initAlgorithm()
        print(alg.shortHelpString())

        parameters = {
            alg.P_MAP: vector,
            alg.P_GRID: grid,
            alg.P_OVERSAMPLING: 15,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-309699.0, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array())))

    def test_rasterSource_default(self):
        raster = QgsRasterLayer(landcover_polygons_l3_1m)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()

        parameters = {
            alg.P_MAP: raster,
            alg.P_GRID: grid,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(130931945, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_rasterSource_floatPrecision(self):
        raster = QgsRasterLayer(landcover_polygons_l3_1m)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()

        parameters = {
            alg.P_MAP: raster,
            alg.P_GRID: grid,
            alg.P_OVERSAMPLING: 15,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(-309789.0, np.round(np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array())))

    def test_rasterSource_nonConsecutiveClasses(self):
        raster = QgsRasterLayer(landcover_polygons_l3_1m_3classes)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()

        parameters = {
            alg.P_MAP: raster,
            alg.P_GRID: grid,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(65618715, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_vectorSource_nonConsecutiveClasses(self):
        vector = QgsVectorLayer(landcover_polygons_3classes)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()

        parameters = {
            alg.P_MAP: vector,
            alg.P_GRID: grid,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(65615019, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))

    def test_vectorSource_nonConsecutiveClasses_nonMatchingCrs(self):
        vector = QgsVectorLayer(landcover_polygons_3classes_epsg4326)
        grid = QgsRasterLayer(enmap)

        alg = ClassificationToFractionAlgorithm()
        parameters = {
            alg.P_MAP: vector,
            alg.P_GRID: grid,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/fraction'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(65615019, np.sum(RasterReader(result[alg.P_OUTPUT_RASTER]).array()))


# todo block-wise IO
# on-the-fly-resampling?

    P_GRID = 'grid'
    P_PRECISION = 'precision'
