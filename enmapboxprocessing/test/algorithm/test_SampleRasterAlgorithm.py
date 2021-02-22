import numpy as np
from qgis._core import (QgsRasterLayer, QgsVectorLayer, QgsVectorDataProvider, QgsFeature, QgsApplication,
                        QgsProcessingRegistry)
from sklearn.base import ClassifierMixin

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.sampleclassificationalgorithm import SampleClassificationAlgorithm
from enmapboxprocessing.algorithm.samplerasteralgorithm import SampleRasterAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.utils import Utils
from enmapboxtestdata import enmap, landcover_polygons
from enmapboxunittestdata import (landcover_polygons_3classes_epsg4326, landcover_points_multipart_epsg3035,
                                  landcover_points_singlepart_epsg3035, landcover_raster_30m, landcover_raster_1m,
                                  landcover_raster_1m_epsg3035, landcover_raster_30m_epsg3035, enmap_uncompressed)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


#from enmapbox.testing import start_app
#qgsApp = start_app()


class TestClassifierAlgorithm(TestCase):

    def test_help(self):
        alg = SampleClassificationAlgorithm()
        alg.initAlgorithm()
        alg.shortHelpString()
        alg.shortDescription()

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
            alg.P_OUTPUT_SAMPLE: 'sample.gpkg'  #  c + '/vsimem/sample_vectorPolygons.gpkg'

        }
        result = self.runalg(alg, parameters)
