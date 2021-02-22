from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from PyQt5.QtCore import QVariant
from osgeo import gdal
from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider, QgsCoordinateReferenceSystem, QgsVectorFileWriter,
                        QgsField)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape
from enmapboxprocessing.utils import Utils


@typechecked
class SampleClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_CLASSIFICATION = 'classification'
    P_AGGREGATE = 'aggregate'
    P_AGGREGATIONS = 'aggregations'
    O_AGGREGATIONS = ['Standard Deviation', 'Number of Observations']
    StandardDeviationAggregation, NumberOfObservationsAggregation = range(len(O_AGGREGATIONS))
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_SAMPLE = 'outSample'

    def displayName(self) -> str:
        return 'Sample Classification'

    def shortDescription(self) -> str:
        return 'Sample labeled pixels and store the result as a vector layer.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, 'Raster with features.'),
            (self.P_CLASSIFICATION,
             f'Classification with labels. {self.helpParameterMapClassification()} '
             f'\nRaster and polygon classifications are reprojected, resampled/rasterized at a x10 finer '
             f'resolution and aggregated via majority voting to match the target raster grid, '
             f'resulting in a class decision that is accurate to the percent. '
             f'\nVector points are sampled directly and source attributes are copied.'),
            (self.P_AGGREGATE,
             'Whether to average polygons instead of using pixel-wise samples.'),
            (self.P_AGGREGATIONS,
             'Additional aggregations to be calculated for each polygon.'),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_OUTPUT_SAMPLE, self.helpParameterVectorDestination())
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterMapLayer(self.P_CLASSIFICATION, 'Classification')
        self.addParameterBoolean(self.P_AGGREGATE, 'Aggregate Polygons', False)
        self.addParameterEnum(
            self.P_AGGREGATIONS, 'Additional Polygon Aggregations', self.O_AGGREGATIONS, True, optional=True
        )
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterVectorDestination(self.P_OUTPUT_SAMPLE, 'Output Sample')

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        classification = self.parameterAsLayer(parameters, self.P_CLASSIFICATION, context)
        aggregate = self.parameterAsBoolean(parameters, self.P_AGGREGATE, context)
        aggregations = self.parameterAsEnums(parameters, self.P_AGGREGATIONS, context)
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_SAMPLE, context)

        if isinstance(classification, QgsRasterLayer):
            # translate into target grid if required
            isGridMatching = all([raster.crs() == classification.crs(),
                                  raster.extent() == classification.extent(),
                                  raster.width() == classification.width(),
                                  raster.height() == classification.height()])
            if not isGridMatching:
                alg = TranslateClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: classification,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: alg.VrtProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.vrt')
                }
                classification = QgsRasterLayer(
                    Processing.runAlgorithm(alg, parameters, None, feedback, context)[alg.P_OUTPUT_RASTER]
                )
            X, y, mapX, mapY, categories = self.sampleRaster(raster, classification, maximumMemoryUsage, feedback)
            sourceFields = None
            sourceAttributes = None
        elif isinstance(classification, QgsVectorLayer):
            sourceFields = [QgsField(field) for field in classification.fields()]
            if sourceFields[0].name() == 'fid':
                sourceFields[0].setName('_fid')
            if Utils.isPointGeometry(classification.geometryType()):
                X, y, mapX, mapY, categories, sourceAttributes = self.samplePoints(raster, classification, feedback)
            else:
                # rasterize into target grid
                alg = RasterizeClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: classification,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.tif')
                }
                classification = QgsRasterLayer(
                    Processing.runAlgorithm(alg, parameters, None, feedback, context)[alg.P_OUTPUT_RASTER]
                )
                X, y, mapX, mapY, categories = self.sampleRaster(raster, classification, maximumMemoryUsage, feedback)
                sourceAttributes = [[]] * (X.shape[0] + 1)
                assert 0  # todo use fid and get attributes correctly!!!!!!!!!!!
        else:
            assert 0

        # sample data and write to disk

        self.writeAsVector(
            X, y, mapX, mapY, categories, sourceFields, sourceAttributes, raster.crs(), filename, feedback
        )

        return {self.P_OUTPUT_SAMPLE: filename}

    @classmethod
    def writeAsVector(
            cls, X: SampleX, y: SampleY, mapX: np.ndarray, mapY: np.ndarray, categories: Categories,
            sourceFields: List[QgsField], sourceAttributes: List, crs: QgsCoordinateReferenceSystem, filename: str,
            feedback: QgsProcessingFeedback = None
    ):
        n = len(X)
        assert n == len(X) == len(y) == len(mapX) == len(mapY)
        if sourceFields is not None:
            assert len(sourceAttributes) == n

        # prepare in memory
        uri = f'point?crs={crs.toWkt()}'
        layer = QgsVectorLayer(uri, 'sample', 'memory')
        provider = layer.dataProvider()
        fields = [QgsField('y[0]', QVariant.Int)]
        fields.extend([QgsField(f'X[{i}]', QVariant.Double) for i in range(X.shape[1])])
        if sourceFields is not None:
            fields.extend(sourceFields)
        provider.addAttributes(fields)
        layer.updateFields()
        for i in range(n):
            feature = QgsFeature()
            feature.setGeometry(QgsPoint(mapX[i], mapY[i]))
            values = list(map(float, X[i]))
            if sourceFields is not None:
                values.extend(sourceAttributes[i])
            values.insert(0, int(y[i, 0]))
            feature.setAttributes(values)
            provider.addFeature(feature)
        layer.updateExtents()

        # save to disk
        saveVectorOptions = QgsVectorFileWriter.SaveVectorOptions()
        saveVectorOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        saveVectorOptions.feedback = feedback
        transformContext = QgsProject.instance().transformContext()
        error, message = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer, filename, transformContext, saveVectorOptions
        )
        assert error == QgsVectorFileWriter.NoError, f'Fail error {error}:{message}'

        # set style
        layer = QgsVectorLayer(filename)
        layer.setRenderer(Utils.categorizedSymbolRendererFromCategories(fields[0].name(), categories))
        layer.saveDefaultStyle()

    @classmethod
    def sampleRaster(
            cls, raster: QgsRasterLayer, classification: QgsRasterLayer, maximumMemoryUsage: int = None,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, np.ndarray, np.ndarray, Categories]:
        assert raster.crs() == classification.crs()
        assert raster.extent() == classification.extent()
        assert (raster.width(), raster.height()) == (classification.width(), classification.height())

        renderer = classification.renderer()
        assert isinstance(renderer, QgsPalettedRasterRenderer)
        categories = Utils.categoriesFromPalettedRasterRenderer(renderer)
        if maximumMemoryUsage is None:
            maximumMemoryUsage = gdal.GetCacheMax()
        rasterReader = RasterReader(raster)
        classificationReader = RasterReader(classification)

        lineMemoryUsage = rasterReader.lineMemoryUsage(1)
        lineMemoryUsage += classificationReader.width() * classificationReader.dataTypeSize()
        blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
        blockSizeX = raster.width()

        X = list()
        y = list()
        mapX = list()
        mapY = list()
        for block in rasterReader.walkGrid(blockSizeX, blockSizeY, feedback):
            blockClassification = classificationReader.arrayFromBlock(block, [renderer.band()])[0]
            labeled = np.full_like(blockClassification, False, np.bool)
            for value, label, color in categories:
                np.logical_or(labeled, blockClassification == value, out=labeled)
            blockY = blockClassification[labeled]
            blockX = list()
            for bandNo in range(1, rasterReader.bandCount() + 1):
                blockBand = rasterReader.arrayFromBlock(block, [bandNo])[0]
                blockX.append(blockBand[labeled])
            X.append(blockX)
            y.append(blockY)
            mapX.append(block.xMap()[labeled])
            mapY.append(block.yMap()[labeled])

        X = np.concatenate(X, axis=1).T
        y = np.expand_dims(np.concatenate(y), 1)
        mapX = np.concatenate(mapX)
        mapY = np.concatenate(mapY)
        checkSampleShape(X, y)
        return X, y, mapX, mapY, categories

    @classmethod
    def samplePoints(
            cls, raster: QgsRasterLayer, classification: QgsVectorLayer, feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, np.ndarray, np.ndarray, Categories, List]:
        assert Utils.isPointGeometry(classification.geometryType())
        renderer = classification.renderer()
        assert isinstance(renderer, QgsCategorizedSymbolRenderer)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer)
        classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}
        categories = [(classIdByValue[value], label, color)
                      for i, (value, label, color) in enumerate(categories) if label != '']
        rasterReader = RasterReader(raster)

        featureRequest = QgsFeatureRequest(raster.extent())
        featureRequest.setDestinationCrs = raster.crs()
        featureRequest = QgsFeatureRequest()
        classField = renderer.classAttribute()
        coordinateTransform = QgsCoordinateTransform(classification.sourceCrs(), raster.crs(), QgsProject.instance())
        X = list()
        y = list()
        mapX = list()
        mapY = list()
        attributes = list()
        n = classification.featureCount()
        feature: QgsFeature
        for i, feature in enumerate(classification.getFeatures(featureRequest)):
            feedback.setProgress(i / n * 100)
            yi = classIdByValue.get(feature.attribute(classField), None)
            if yi is None:
                continue
            geometry: QgsGeometry = feature.geometry()
            geometry.transform(coordinateTransform)
            if geometry.isMultipart():
                def points():
                    for point in geometry.parts():
                        yield point
            else:
                def points():
                    pointXY: QgsPointXY = geometry.asPoint()
                    yield QgsPoint(pointXY.x(), pointXY.y())
            for point in points():
                offset: QgsPoint = rasterReader.provider.transformCoordinates(
                    point, QgsRasterDataProvider.TransformLayerToImage
                )
                Xi = rasterReader.gdalDataset.ReadAsArray(int(offset.x()), int(offset.y()), 1, 1)
                X.append(Xi)
                y.append(yi)
                mapX.append(point.x())
                mapY.append(point.y())
                attributes.append(feature.attributes())
        X = np.concatenate(X, axis=1).T[0]
        y = np.expand_dims(np.array(y), 1)
        mapX = np.array(mapX)
        mapY = np.array(mapY)
        checkSampleShape(X, y)
        return X, y, mapX, mapY, categories, attributes

    @classmethod
    def samplePolygons(
            cls, raster: QgsRasterLayer, classification: QgsVectorLayer, feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, np.ndarray, np.ndarray, Categories]:
        assert Utils.isPolygonGeometry(classification.geometryType())
        renderer = classification.renderer()
        assert isinstance(renderer, QgsCategorizedSymbolRenderer)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer)
        classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}
        categories = [(classIdByValue[value], label, color)
                      for i, (value, label, color) in enumerate(categories) if label != '']
        rasterReader = RasterReader(raster)

        featureRequest = QgsFeatureRequest(raster.extent())
        featureRequest.setDestinationCrs = raster.crs()
        featureRequest = QgsFeatureRequest()
        classField = renderer.classAttribute()
        coordinateTransform = QgsCoordinateTransform(classification.sourceCrs(), raster.crs(), QgsProject.instance())
        X = list()
        y = list()
        mapX = list()
        mapY = list()
        n = classification.featureCount()
        feature: QgsFeature
        for i, feature in enumerate(classification.getFeatures(featureRequest)):
            feedback.setProgress(i / n * 100)
            yi = classIdByValue.get(feature.attribute(classField), None)
            if yi is None:
                continue
            geometry: QgsGeometry = feature.geometry()
            geometry.transform(coordinateTransform)

            if geometry.isMultipart():
                def points():
                    for point in geometry.parts():
                        yield point
            else:
                def points():
                    pointXY: QgsPointXY = geometry.asPoint()
                    yield QgsPoint(pointXY.x(), pointXY.y())
            for point in points():
                offset: QgsPoint = rasterReader.provider.transformCoordinates(
                    point, QgsRasterDataProvider.TransformLayerToImage
                )
                Xi = rasterReader.gdalDataset.ReadAsArray(int(offset.x()), int(offset.y()), 1, 1)
                X.append(Xi)
                y.append(yi)
                mapX.append(point.x())
                mapY.append(point.y())

        X = np.concatenate(X, axis=1).T[0]
        y = np.expand_dims(np.array(y), 1)
        mapX = np.array(mapX)
        mapY = np.array(mapY)
        checkSampleShape(X, y)
        return X, y, mapX, mapY, categories
