from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider)

from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape, Category, ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PrepareClassificationSampleFromMapAndRaster(EnMAPProcessingAlgorithm):
    P_MAP, _MAP = 'map', 'Categorized layer'
    P_RASTER, _RASTER = 'raster', 'Raster layer with features'
    P_BAND_LIST, _BAND_LIST = 'bandList', 'Selected bands/features'
    P_CLASS_FIELD, _CLASS_FIELD = 'classField', 'Field with class label'
    P_CLASS_BAND, _CLASS_BAND = 'classBand', 'Band with class label'
    P_OUTPUT_DATASET, _OUTPUT_DATASET = 'outputClassificationDataset', 'Output dataset'

    @classmethod
    def displayName(cls) -> str:
        return 'Prepare classification dataset (from categorized layer and feature raster)'

    def shortDescription(self) -> str:
        return 'Sample all labeled pixels and store the result as a pickle file.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._MAP,
             f'Locations with categorical labels. {self.helpParameterMapClassification()} '
             f'The layer is resampled, reprojected and rasterized internally to match the raster grid, if required.\n'),
            (self._RASTER, 'Raster used for sampling feature values.'),
            (self._BAND_LIST, 'Bands to subset and rearrange. '
                              'An empty selection defaults to all bands in native order.'),
            (self._OUTPUT_DATASET, 'Output dataset destination pickle file.')
        ]

    def group(self):
        return Group.Test.value + Group.DatasetPreparation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMapLayer(self.P_MAP, self._MAP)
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterBandList(
            self.P_BAND_LIST, self._BAND_LIST, parentLayerParameterName=self.P_RASTER, optional=True
        )
        self.addParameterFileDestination(self.P_OUTPUT_DATASET, self._OUTPUT_DATASET, self.PickleFileFilter)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = self.checkParameterMapClassification(parameters, self.P_MAP, context)
        if not valid:
            return valid, message
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsLayer(parameters, self.P_MAP, context)
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        bandList = self.parameterAsInts(parameters, self.P_BAND_LIST, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_DATASET, context)
        maximumMemoryUsage = None

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            feedback.pushInfo('Sample data')
            if isinstance(classification, QgsVectorLayer):
                if Utils.isPointGeometry(classification.geometryType()):
                    X, y, categories = self.samplePoints(raster, classification, feedback2)
                else:
                    tmpFilename = Utils.tmpFilename(filename, 'classification.tif')
                    alg = VectorToClassificationAlgorithm()
                    alg.initAlgorithm()
                    parameters = {
                        alg.P_VECTOR: classification,
                        alg.P_GRID: raster,
                        alg.P_OUTPUT_RASTER: tmpFilename
                    }
                    self.runAlg(alg, parameters, None, feedback2, context, True)
                    classification = QgsRasterLayer(tmpFilename)
                    X, y, categories = self.samplePixels(raster, classification, maximumMemoryUsage, feedback2)
            elif isinstance(classification, QgsRasterLayer):
                alg = TranslateClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: classification,
                    alg.P_GRID: raster,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.tif')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
                X, y, categories = self.samplePixels(raster, classification, maximumMemoryUsage, feedback2)
            else:
                assert 0

            features = [raster.bandName(i + 1) for i in range(raster.bandCount())]

            dump = ClassifierDump(categories=categories, features=features, X=X, y=y)
            dumpDict = dump._asdict()
            Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_DATASET: filename}
            self.toc(feedback, result)
        return result

    @classmethod
    def samplePixels(
            cls, raster: QgsRasterLayer, classification: QgsRasterLayer, maximumMemoryUsage: int = None,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, Categories]:
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
        for block in rasterReader.walkGrid(blockSizeX, blockSizeY, feedback):
            blockClassification = classificationReader.arrayFromBlock(block, [renderer.band()])[0]
            labeled = np.full_like(blockClassification, False, bool)
            for value, label, color in categories:
                np.logical_or(labeled, blockClassification == value, out=labeled)
            blockY = blockClassification[labeled]
            blockX = list()
            for bandNo in range(1, rasterReader.bandCount() + 1):
                blockBand = rasterReader.arrayFromBlock(block, [bandNo])[0]
                blockX.append(blockBand[labeled])
            X.append(blockX)
            y.append(blockY)
        X = np.concatenate(X, axis=1).T
        y = np.expand_dims(np.concatenate(y), 1)
        checkSampleShape(X, y)
        return X, y, categories

    @classmethod
    def samplePoints(
            cls, raster: QgsRasterLayer, classification: QgsVectorLayer, feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, Categories]:
        renderer = classification.renderer()
        assert isinstance(renderer, QgsCategorizedSymbolRenderer)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer)
        classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}
        categories = [Category(classIdByValue[value], label, color)
                      for i, (value, label, color) in enumerate(categories) if label != '']
        rasterReader = RasterReader(raster)

        featureRequest = QgsFeatureRequest(raster.extent())
        featureRequest.setDestinationCrs = raster.crs()
        featureRequest = QgsFeatureRequest()
        classField = renderer.classAttribute()
        coordinateTransform = QgsCoordinateTransform(classification.sourceCrs(), raster.crs(), QgsProject.instance())
        X = list()
        y = list()
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
                    for part in geometry.parts():
                        yield part
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

        X = np.concatenate(X, axis=1).T[0]
        y = np.expand_dims(np.array(y), 1)
        checkSampleShape(X, y)
        return X, y, categories
