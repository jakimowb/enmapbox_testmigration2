import webbrowser

import processing
from qgis._core import (QgsRasterLayer, QgsVectorLayer, QgsApplication, QgsProcessingContext)
from enmapboxprocessing.algorithm.sampleclassificationalgorithm import SampleClassificationAlgorithm
from enmapboxprocessing.algorithm.samplerasteralgorithm import SampleRasterAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import landcover_points_singlepart_epsg3035, enmap_uncompressed

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class TestClassifierAlgorithm(TestCase):

    def test_help(self):
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        alg.shortHelpString()
        alg.shortDescription()

    def test_pythonCommand(self):
        raster = QgsRasterLayer(enmap)
        alg = SampleRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample_vectorPolygon.gpkg'
        }
        processing
        cmd = alg.asPythonCommand(parameters, QgsProcessingContext())
        print(cmd)
        eval(cmd)
        webbrowser.open_new(parameters[alg.P_OUTPUT_SAMPLE] + '.log')

    def test_sampleFromVectorPoints(self):
        global c
        alg = SampleRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap),
            alg.P_VECTOR: QgsVectorLayer(landcover_points_singlepart_epsg3035),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample_vectorPoint.gpkg'
        }
        result = self.runalg(alg, parameters)

    def test_sampleFromVectorPolygons(self):
        global c
        alg = SampleRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: QgsRasterLayer(enmap_uncompressed),
            alg.P_VECTOR: QgsVectorLayer(landcover_polygons),
            alg.P_OUTPUT_SAMPLE: c + '/vsimem/sample_vectorPolygons.gpkg'

        }
        result = self.runalg(alg, parameters)
