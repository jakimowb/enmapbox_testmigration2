import webbrowser

import processing
from qgis._core import (QgsRasterLayer, QgsVectorLayer, QgsProcessingContext)
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_points_singlepart_epsg3035, enmap_uncompressed

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestSampleRasterValuesAlgorithm(TestCase):

    def test_sampleFromVectorPoints(self):
        global c
        alg = SampleRasterValuesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_points_singlepart_epsg3035),
            alg.P_OUTPUT_POINTS: c + '/vsimem/sample_vectorPoint.gpkg'
        }
        result = self.runalg(alg, parameters)

    def test_sampleFromVectorPolygons(self):
        global c
        alg = SampleRasterValuesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap_uncompressed),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_POINTS: c + '/vsimem/sample_vectorPolygons.gpkg'

        }
        result = self.runalg(alg, parameters)

    def test_coverageRange(self):
        global c
        alg = SampleRasterValuesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap_uncompressed),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_COVERAGE_RANGE: [70, 100],
            alg.P_OUTPUT_POINTS: c + '/vsimem/sample_70p_pure.gpkg'

        }
        result = self.runalg(alg, parameters)

