from qgis._core import QgsRasterLayer, QgsVectorLayer, Qgis

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_polygons_3classes_epsg4326


class TestRasterizeAlgorithm(TestCase):

    def test_default(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/mask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_tmpFileAndVrt(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons_3classes_epsg4326)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_CREATION_PROFILE: alg.Vrt,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/mask.vrt'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_differentCrs(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons_3classes_epsg4326)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/mask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_initAndBurnValue(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_INIT_VALUE: 1,
            alg.P_BURN_VALUE: 0,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/invertedMask.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(85972, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_burnAttribute(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_BURN_ATTRIBUTE: 'level_1_id',
            alg.P_OUTPUT_RASTER: 'c:/vsimem/classes.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(3100, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_modeAggregation(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_RESAMPLE_ALG: alg.ModeResampleAlg,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/mode.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2026, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_averageAggregation(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_RESAMPLE_ALG: alg.AverageResampleAlg,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/average.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2028, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum().round())

    def test_minAggregation(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_RESAMPLE_ALG: alg.MinResampleAlg,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/min.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(1481, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())

    def test_allTouched(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_ALL_TOUCHED: True,
            alg.P_DATA_TYPE: alg.Byte,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/allTouched.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2721, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())
        self.assertEqual(Qgis.Byte, RasterReader(result[alg.P_OUTPUT_RASTER]).dataType())

    def test_addValue(self):
        raster = QgsRasterLayer(enmap)
        vector = QgsVectorLayer(landcover_polygons)
        alg = RasterizeVectorAlgorithm()
        parameters = {
            alg.P_GRID: raster,
            alg.P_VECTOR: vector,
            alg.P_ADD_VALUE: True,
            alg.P_OUTPUT_RASTER: 'c:/vsimem/addValue.tif'
        }
        result = self.runalg(alg, parameters)
        self.assertEqual(2031, RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0].sum())
