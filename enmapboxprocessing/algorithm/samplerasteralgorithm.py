from typing import Dict, Any, List, Tuple

import processing
#from processing.algs.qgis.RasterSampling import RasterSampling
from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsFeature, QgsField, QgsProcessingFeatureSourceDefinition, QgsApplication,
                        QgsVectorDataProvider, QgsProcessingOutputLayerDefinition)

from qgis.core.additions.edit import edit

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group, AlgorithmCanceledException
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils


@typechecked
class SampleRasterAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_VECTOR = 'vector'
    P_OUTPUT_SAMPLE = 'outVector'

    def displayName(self) -> str:
        return 'Sample Raster'

    def shortDescription(self) -> str:
        return 'Sample raster with vector geometries (points and polygons).'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, self.helpParameterRaster()),
            (self.P_VECTOR, self.helpParameterVector()),
            (self.P_OUTPUT_SAMPLE, self.helpParameterVectorDestination())
        ]

    def group(self):
        return Group.Test.value + Group.Sampling.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterVectorLayer(self.P_VECTOR, 'Locations')

        # self.addParameterBoolean(self.P_AGGREGATE, 'Aggregate Geometries', False)
        # self.addParameterEnum(
        #    self.P_AGGREGATIONS, 'Additional Aggregation Statistics', self.O_AGGREGATIONS, True, optional=True
        # )
        self.addParameterVectorDestination(self.P_OUTPUT_SAMPLE, 'Output Sample', defaultValue='sample.gpkg')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        vector = self.parameterAsVectorLayer(parameters, self.P_VECTOR, context)
        # aggregate = self.parameterAsBoolean(parameters, self.P_AGGREGATE, context)
        # aggregations = self.parameterAsEnums(parameters, self.P_AGGREGATIONS, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)
            selectedFeaturesOnly = False
            if Utils.isPointGeometry(vector.geometryType()):
                self.samplePoints(filename, raster, vector, selectedFeaturesOnly, feedback, feedback2, context)
            else:
                self.samplePolygons(filename, raster, vector, selectedFeaturesOnly, feedback, feedback2, context)
            result = {self.P_OUTPUT_SAMPLE: filename}
            self.toc(feedback, result)

        return result


    @classmethod
    def samplePoints(
            cls, filename: str, raster: QgsRasterLayer, vector: QgsVectorLayer, selectedFeaturesOnly: bool,
            feedback: QgsProcessingFeedback, feedback2: QgsProcessingFeedback, context: QgsProcessingContext
    ):
        assert Utils.isPointGeometry(vector.geometryType())
        alg = 'qgis:rastersampling'
        parameters = {
            'COLUMN_PREFIX': 'SAMPLE_',
            'INPUT': QgsProcessingFeatureSourceDefinition(vector.source(), selectedFeaturesOnly),
            'OUTPUT': filename,
            'RASTERCOPY': raster
        }
        processing.run(alg, parameters, None, feedback2, context, True)
        result = QgsVectorLayer(filename)
        return result

    @classmethod
    def samplePolygons(
            cls, filename: str, raster: QgsRasterLayer, vector: QgsVectorLayer, selectedFeaturesOnly: bool,
            feedback: ProcessingFeedback, feedback2: ProcessingFeedback, context: QgsProcessingContext
    ):
        assert Utils.isPolygonGeometry(vector.geometryType())

        # create oversampling grid
        alg = CreateGridAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_CRS: raster.crs(),
            alg.P_EXTENT: raster.extent(),
            alg.P_UNIT: alg.PixelUnits,
            alg.P_WIDTH: raster.width() * 10,
            alg.P_HEIGHT: raster.height() * 10,
            alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'grid.x10.vrt')
        }
        result = processing.run(alg, parameters, None, feedback2, context, True)
        x10Grid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])

        if feedback.isCanceled():
            raise AlgorithmCanceledException()

        feedback.pushInfo('Rasterize polygon IDs at x10 finer resolution')
        alg = RasterizeVectorAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_VECTOR: vector,
            alg.P_GRID: x10Grid,
            alg.P_BURN_FID: True,
            alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
            alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'fid.x10.tif'),
        }
        result = processing.run(alg, parameters, None, feedback2, context, True)
        x10FidArray = RasterReader(result[alg.P_OUTPUT_RASTER]).array()[0]

        sampleVectors = list()
        polygonFeature: QgsFeature
        refs = list()  # don't loose your C refs!
        n = vector.featureCount()
        for i, polygonFeature in enumerate(vector.getFeatures()):

            if feedback.isCanceled():
                raise AlgorithmCanceledException()

            feedback.pushInfo(f'Sample polygon [{i + 1}/{n}]')

            fid = polygonFeature.id()
            x10MaskArray = x10FidArray == fid
            percentArray = x10MaskArray.reshape((raster.height(), 10, raster.width(), 10)).sum(axis=3).sum(axis=1)

            driver = Driver(
                Utils.tmpFilename(filename, f'cover{fid}.tif'), 'GTiff', cls.CompressedGTiffCreationOptions, feedback2
            )
            coverRaster = driver.createFromArray([percentArray], raster.extent(), raster.crs())
            coverRaster.setNoDataValue(0)
            coverRaster.close()

            if feedback.isCanceled():
                raise AlgorithmCanceledException()

            # create sample locations with cover > 0%
            alg = QgsApplication.processingRegistry().createAlgorithmById('native:pixelstopoints')
            parameters = {
                'FIELD_NAME': 'COVER',
                'INPUT_RASTER': coverRaster.source(),
                'OUTPUT': Utils.tmpFilename(filename, f'locations{fid}.gpkg'),
                'RASTER_BAND': 1
            }
            result = processing.run(alg, parameters, None, feedback2, context, True)
            locationVector = QgsVectorLayer(result['OUTPUT'])
            refs.append(locationVector)
            nFields = locationVector.fields().count()

            if feedback.isCanceled():
                raise AlgorithmCanceledException()

            # add polygon attributes to each point (extremly redundant, but we want all data in one table)
            provider: QgsVectorDataProvider = locationVector.dataProvider()
            fields = [QgsField(field) for field in vector.fields()]
            refs.append(fields)
            provider.addAttributes(fields)
            locationVector.updateFields()
            polygonFeatureAttributes = polygonFeature.attributes()
            with edit(locationVector):
                pointFeature: QgsFeature
                for pointFeature in locationVector.getFeatures():
                    values = [pointFeature.attribute(i) for i in range(nFields)] + polygonFeatureAttributes
                    pointFeature.setAttributes(values)
                    locationVector.updateFeature(pointFeature)

            if feedback.isCanceled():
                raise AlgorithmCanceledException()

            sampleVectors.append(
                cls.samplePoints(
                    Utils.tmpFilename(filename, f'sample{fid}.gpkg'), raster, locationVector, selectedFeaturesOnly,
                    feedback, feedback2, context
                )
            )

        if feedback.isCanceled():
            raise AlgorithmCanceledException()

        # merge all samples
        alg = QgsApplication.processingRegistry().createAlgorithmById('native:mergevectorlayers')
        parameters = {
            'LAYERS': sampleVectors,
            'CRS': vector.crs(),

            'OUTPUT': filename
        }
        processing.run(alg, parameters, None, feedback, context, True)
        result = QgsVectorLayer(filename)
        return result
