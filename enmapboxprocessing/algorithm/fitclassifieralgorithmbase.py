import inspect
import traceback
from math import ceil
from typing import Dict, Any, List, Tuple, Union

import numpy as np
from osgeo import gdal
from sklearn.base import ClassifierMixin
from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider, QgsProcessingParameterRasterDestination)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape
from enmapboxprocessing.utils import Utils


@typechecked
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_CLASSIFICATION = 'classification'
    P_CODE = 'code'
    P_SAMPLE_SIZE = 'sampleSize'
    P_REPLACE = 'replace'
    P_SAVE_DATA = 'saveData'
    P_RASTERIZE_POINTS = 'rasterizePoints'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_CLASSIFICATION = 'outclassification'
    P_OUTPUT_PROBABILITY = 'outprobability'
    P_OUTPUT_CLASSIFIER = 'outclassifier'

    def displayName(self) -> str:
        raise NotImplementedError()

    def shortDescription(self) -> str:
        raise NotImplementedError()

    def code(cls) -> ClassifierMixin:
        raise NotImplementedError()

    def helpParameterCode(self) -> str:
        raise NotImplementedError()

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, 'Raster with training data features.'),
            (self.P_CLASSIFICATION, 'Classification with training data labels. '
                                    f'{self.helpParameterMapClassification()} '
                                    f'Note that, if required, the classification layer is resampled, reprojected and '
                                    f'rasterized internally to match the raster grid.'),
            (self.P_CODE, self.helpParameterCode()),
            (self.P_SAMPLE_SIZE, 'Use all data for training, if value is "not set", '
                                 'a random subsample with given class size for values greater equal 1, '
                                 'or a random subsample with given class propotion for values between 0 and 1.'),
            (self.P_REPLACE, 'Whether to perform random sampling with replacement.'),
            (self.P_SAVE_DATA, 'Whether to store the training data (X, y) inside the model file.'),
            (self.P_RASTERIZE_POINTS, 'Whether to rasterize points instead of point-wise reading. '
                                      'Only relevant for point geometries. Line and polygon geometries are always '
                                      'rasterized.'),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_OUTPUT_CLASSIFICATION, 'Output Classification'),
            (self.P_OUTPUT_CLASSIFIER, 'Output classifier model destination (*.pkl file). '
                                       'This file can be used for applying the classifier to a raster using '
                                       '<i>Classification / Predict Classification</i> and '
                                       '<i>Classification / Predict Class Probability</i>.')
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterMapLayer(self.P_CLASSIFICATION, 'Label')
        self.addParameterString(self.P_CODE, 'Code', self.defaultCodeAsString(), True, advanced=True)
        self.addParameterFloat(self.P_SAMPLE_SIZE, 'Sample Size', optional=True, minValue=0, advanced=True)
        self.addParameterBoolean(self.P_REPLACE, 'Sample with Replacement', False, advanced=True)
        self.addParameterBoolean(self.P_SAVE_DATA, 'Save Data', defaultValue=False, advanced=True)
        self.addParameterBoolean(self.P_RASTERIZE_POINTS, 'Rasterize Points', defaultValue=False, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_CLASSIFICATION, 'Output Classification', None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_PROBABILITY, 'Output Class Probability', None, True, False)
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterFileDestination(self.P_OUTPUT_CLASSIFIER, 'Output Classifier', 'Model file (*.pkl)')

    def defaultCodeAsString(self):
        lines = [line for line in inspect.getsource(self.code).split('\n')
                 if not line.strip().startswith('def') and line != ''][:-1]
        lines = '\n'.join([line[8:] for line in lines])
        return lines

    def parameterAsClassifier(self, parameters: Dict[str, Any], name, context: QgsProcessingContext) -> ClassifierMixin:
        namespace = dict()
        code = self.parameterAsString(parameters, name, context)
        exec(code, namespace)
        return namespace['classifier']

    def checkParameterCode(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            self.parameterAsClassifier(parameters, self.P_CODE, context)
        except:
            return False, traceback.format_exc()
        return True, ''

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        checks = [
            self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context),
            self.checkParameterCode(parameters, context)
        ]
        for valid, message in checks:
            if not valid:
                return valid, message
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        classification = self.parameterAsLayer(parameters, self.P_CLASSIFICATION, context)
        sampleSize = self.parameterAsDouble(parameters, self.P_SAMPLE_SIZE, context)
        replace = self.parameterAsBoolean(parameters, self.P_REPLACE, context)
        saveData = self.parameterAsBoolean(parameters, self.P_SAVE_DATA, context)
        rasterizePoints = self.parameterAsBoolean(parameters, self.P_RASTERIZE_POINTS, context)
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        filenameClassification = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFICATION, context)
        filenameProbability = self.parameterAsFileOutput(parameters, self.P_OUTPUT_PROBABILITY, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.parameterAsClassifier(parameters, self.P_CODE, context)
        if sampleSize is not None and sampleSize >= 1:
            sampleSize = int(round(sampleSize))

        X, y, categories = self.sampleAny(
            raster, classification, filename, rasterizePoints, maximumMemoryUsage, feedback, context
        )

        if sampleSize:
            X, y = self.subsample(X, y, sampleSize, replace)

        classifier.fit(X, y.ravel())

        if not saveData:
            X = y = None
        Utils.pickleDumpClassifier(classifier, categories, X, y, filename)

        result = {self.P_OUTPUT_CLASSIFIER: filename}

        if filenameClassification is not None:
            alg = PredictClassificationAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_CLASSIFIER: filename,
                alg.P_RASTER: raster,
                alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                alg.P_MAXIMUM_MEMORY_USAGE: maximumMemoryUsage,
                alg.P_OUTPUT_RASTER: filenameClassification
            }
            Processing.runAlgorithm(alg, parameters, None, feedback, context)
            result[self.P_OUTPUT_CLASSIFICATION] = filenameClassification

        if filenameProbability is not None:
            alg = PredictClassPropabilityAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_CLASSIFIER: filename,
                alg.P_RASTER: raster,
                alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                alg.P_MAXIMUM_MEMORY_USAGE: maximumMemoryUsage,
                alg.P_OUTPUT_RASTER: filenameProbability
            }
            Processing.runAlgorithm(alg, parameters, None, feedback, context)
            result[self.P_OUTPUT_PROBABILITY] = filenameProbability

        return result

    @classmethod
    def sampleAny(
            cls, raster: QgsRasterLayer, classification: QgsMapLayer, filename: str, rasterizePoints: bool = False,
            maximumMemoryUsage: int = None, feedback: QgsProcessingFeedback = None, context: QgsProcessingContext = None
    ):

        if isinstance(classification, QgsVectorLayer):
            if not rasterizePoints and Utils.isPointGeometry(classification.geometryType()):
                X, y, categories = cls.samplePoints(raster, classification, feedback)
            else:
                tmpFilename = Utils.tmpFilename(filename, 'classification.tif')
                alg = RasterizeClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: classification,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: tmpFilename
                }
                Processing.runAlgorithm(alg, parameters, None, feedback, context)
                classification = QgsRasterLayer(tmpFilename)
                X, y, categories = cls.samplePixels(raster, classification, maximumMemoryUsage, feedback)
        elif isinstance(classification, QgsRasterLayer):
            isGridMatching = all([raster.crs() == classification.crs(),
                                  raster.extent() == classification.extent(),
                                  raster.width() == classification.width(),
                                  raster.height() == classification.height()])
            if not isGridMatching:
                tmpFilename = Utils.tmpFilename(filename, 'classification.tif')
                alg = TranslateClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: classification,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: alg.VrtProfile,
                    alg.P_OUTPUT_RASTER: tmpFilename
                }
                Processing.runAlgorithm(alg, parameters, None, feedback, context)
                classification = QgsRasterLayer(tmpFilename)
            X, y, categories = cls.samplePixels(raster, classification, maximumMemoryUsage, feedback)
        else:
            raise ValueError(f'invalid layer: {classification}')
        return X, y, categories

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
        feature: QgsFeature
        for feature in classification.getFeatures(featureRequest):
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

        X = np.concatenate(X, axis=1).T[0]
        y = np.expand_dims(np.array(y), 1)
        checkSampleShape(X, y)
        return X, y, categories

    @classmethod
    def subsample(cls, X: SampleX, y: SampleY, size: Union[int, float], replace: bool) -> Tuple[SampleX, SampleY]:
        values, counts = np.unique(y, return_counts=True)
        if 0 <= size < 1:
            counts = [max(1, ceil(count * size)) for count in counts]
        else:
            if replace:
                counts = [size for _ in counts]
            else:
                counts = [min(count, size) for count in counts]
        indices = list()
        for value, count in zip(values, counts):
            iall = np.where(y == value)[0]
            ichoosen = np.random.choice(iall, count, replace=replace)
            indices.extend(ichoosen)
        y = y[indices]
        X = X[indices]
        return X, y
