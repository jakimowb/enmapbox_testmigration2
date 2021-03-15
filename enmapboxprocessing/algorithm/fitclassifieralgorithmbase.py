import inspect
import traceback
from collections import OrderedDict
from math import ceil
from typing import Dict, Any, List, Tuple, Union

import numpy as np
from osgeo import gdal
from sklearn.base import ClassifierMixin
from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.processingfeedback import ProcessingFeedback
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsCategorizedSymbolRenderer,
                        QgsFeatureRequest, QgsFeature, QgsCoordinateTransform, QgsProject, QgsGeometry, QgsPointXY,
                        QgsPoint, QgsRasterDataProvider, QgsProcessingParameterRasterDestination,
                        QgsProcessingParameterField)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape, Category
from enmapboxprocessing.utils import Utils


@typechecked
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_CLASSIFICATION = 'classification'
    P_FEATURE_FIELDS = 'featureFields'
    P_CODE = 'code'
    P_SAMPLE_SIZE = 'sampleSize'
    P_REPLACE = 'replace'
    P_SAVE_DATA = 'saveData'
    P_RASTERIZE_POINTS = 'rasterizePoints'
    P_DUMP_AS_JSON = 'dumpAsJson'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_CLASSIFICATION = 'outClassification'
    P_OUTPUT_PROBABILITY = 'outProbability'
    P_OUTPUT_CLASSIFIER = 'outClassifier'

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
            (self.P_CLASSIFICATION, 'Training data labels. '
                                    f'{self.helpParameterMapClassification()} '
                                    f'The classification layer is resampled, reprojected and rasterized internally to '
                                    f'match the raster grid, if required. '
                                    f'\nNote: you can safely ignore the <i>"Could not load layer/table. '
                                    f'Dependent field could not be populated."</i> warning, when selecting a raster '
                                    f'layer.'),
            (self.P_FEATURE_FIELDS, 'Use selected fields as training data features (instead of sampling the Raster).'),
            (self.P_CODE, self.helpParameterCode()),
            (self.P_SAMPLE_SIZE, 'Use all data for training, if value is "not set", '
                                 'a random subsample with given class size for values greater equal 1, '
                                 'or a random subsample with given class propotion for values between 0 and 1.'),
            (self.P_REPLACE, 'Whether to perform random sampling with replacement.'),
            (self.P_SAVE_DATA, 'Whether to store the training data inside the model file.'),
            (self.P_RASTERIZE_POINTS, 'Whether to rasterize points instead of point-wise reading. '
                                      'Only relevant for point geometries. Line and polygon geometries are always '
                                      'rasterized.'),
            (self.P_DUMP_AS_JSON, 'Whether to additionally store the model as a human-readable JSON sidecar '
                                  '*.pkl.json file.'),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_OUTPUT_CLASSIFICATION, 'Specify an output classification destination to apply the model to the '
                                           'given Raster.'),
            (self.P_OUTPUT_PROBABILITY, 'Specify an output class probability destination to apply the model to the '
                                        'given Raster.'),
            (self.P_OUTPUT_CLASSIFIER, 'Output classifier model destination *.pkl file.'
                                       'This file can be used for applying the model to a raster using '
                                       '"EnMAP-Box/Classification/Predict classification" and '
                                       '"EnMAP-Box/Classification/Predict class probability"')
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster', optional=True)
        self.addParameterMapLayer(self.P_CLASSIFICATION, 'Labels')
        self.addParameterField(
            self.P_FEATURE_FIELDS, 'Features', None, self.P_CLASSIFICATION, QgsProcessingParameterField.Numeric, True,
            optional=True, advanced=True
        )
        self.addParameterString(self.P_CODE, 'Code', self.defaultCodeAsString(), True, advanced=True)
        self.addParameterFloat(self.P_SAMPLE_SIZE, 'Sample size', optional=True, minValue=0, advanced=True)
        self.addParameterBoolean(self.P_REPLACE, 'Sample with replacement', False, advanced=True)
        self.addParameterBoolean(self.P_SAVE_DATA, 'Save training data', defaultValue=False, advanced=True)
        self.addParameterBoolean(self.P_RASTERIZE_POINTS, 'Rasterize points', defaultValue=False, advanced=True)
        self.addParameterBoolean(self.P_DUMP_AS_JSON, 'Save model as JSON', False, False, True)
        self.addParameterRasterDestination(self.P_OUTPUT_CLASSIFICATION, 'Output classification', None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_PROBABILITY, 'Output class probability', None, True, False)
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterFileDestination(self.P_OUTPUT_CLASSIFIER, 'Output classifier', 'Model file (*.pkl)')

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

    def checkParameterFeatures(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        fields = self.parameterAsFields(parameters, self.P_FEATURE_FIELDS, context)

        if raster is None and fields is None:
            return False, 'Select either a raster layer (Raster) or a list of fields (Feature fields) used as ' \
                          'training data features.'
        if raster is not None and fields is not None:
            if raster.bandCount() != len(fields):
                return False, 'Number of bands (Raster) must match number of selected fields (Feature fields).'
        return True, ''

    def checkParameterRaster(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        if self.parameterAsRasterLayer(parameters, self.P_RASTER, context) is None:
            if self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFICATION, context) is not None:
                return False, 'Missing parameter value: (Raster)'
            if self.parameterAsFileOutput(parameters, self.P_OUTPUT_PROBABILITY, context) is not None:
                return False, 'Missing parameter value: (Raster)'
        return True, ''

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        checks = [
            self.checkParameterRaster(parameters, context),
            self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context),
            self.checkParameterFeatures(parameters, context),
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
        featureFields = self.parameterAsFields(parameters, self.P_FEATURE_FIELDS, context)
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

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            feedback.pushInfo('Sample training data')
            if featureFields is None:
                X, y, categories = self.sampleAny(
                    raster, classification, filename, rasterizePoints, maximumMemoryUsage, feedback, context
                )
            else:
                assert isinstance(classification, QgsVectorLayer)
                X, y, categories = self.sampleFromFields(featureFields, classification, feedback)

            if sampleSize:
                X, y = self.subsample(X, y, sampleSize, replace)

            feedback.pushInfo('Fit classifier')
            classifier.fit(X, y.ravel())

            if not saveData:
                X = y = None
            Utils.pickleDumpClassifier(classifier, categories, X, y, filename)

            if self.parameterAsBoolean(parameters, self.P_DUMP_AS_JSON, context):
                Utils.jsonDump(OrderedDict([
                    ('classifier',classifier),
                    ('categories', categories),
                    ('training samples X', X),
                    ('training samples y', y)
                ]), filename + '.json')

            result = {self.P_OUTPUT_CLASSIFIER: filename}

            if filenameClassification is not None:
                feedback.pushInfo('Predict classification')
                alg = PredictClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFIER: filename,
                    alg.P_RASTER: raster,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                    alg.P_MAXIMUM_MEMORY_USAGE: maximumMemoryUsage,
                    alg.P_OUTPUT_RASTER: filenameClassification
                }
                Processing.runAlgorithm(alg, parameters, None, feedback2, context)
                result[self.P_OUTPUT_CLASSIFICATION] = filenameClassification

            if filenameProbability is not None:
                feedback.pushInfo('Predict class probabilities')
                alg = PredictClassPropabilityAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CLASSIFIER: filename,
                    alg.P_RASTER: raster,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiffProfile,
                    alg.P_MAXIMUM_MEMORY_USAGE: maximumMemoryUsage,
                    alg.P_OUTPUT_RASTER: filenameProbability
                }
                Processing.runAlgorithm(alg, parameters, None, feedback2, context)
                result[self.P_OUTPUT_PROBABILITY] = filenameProbability

            self.toc(feedback, result)

        return result


    @classmethod
    def sampleFromFields(
            cls, featureFields: List[str], classification: QgsVectorLayer, feedback: ProcessingFeedback
    ) -> Tuple[SampleX, SampleY, Categories]:
        renderer = classification.renderer()
        assert isinstance(renderer, QgsCategorizedSymbolRenderer)
        categories = Utils.categoriesFromCategorizedSymbolRenderer(renderer)
        classIdByValue = {value: i + 1 for i, (value, label, color) in enumerate(categories) if label != ''}
        categories = [Category(classIdByValue[value], label, color)
                      for i, (value, label, color) in enumerate(categories) if label != '']
        classField = renderer.classAttribute()

        n = classification.featureCount()
        X = np.zeros(shape=(n, len(featureFields)), dtype=np.float32)
        y = np.zeros(shape=(n, 1), dtype=np.float32)
        feature: QgsFeature
        for i, feature in enumerate(classification.getFeatures()):
            feedback.setProgress(i / n * 100)
            yi = classIdByValue.get(feature.attribute(classField), np.nan)
            y[i, 0] = yi
            for k, featureField in enumerate(featureFields):
                Xik = feature.attribute(featureField)
                if Xik is None:
                    Xik = np.nan
                X[i, k] = Xik

        checkSampleShape(X, y)
        return X, y, categories

    @classmethod
    def sampleAny(
            cls, raster: QgsRasterLayer, classification: QgsMapLayer, filename: str, rasterizePoints: bool = False,
            maximumMemoryUsage: int = None, feedback: ProcessingFeedback = None, context: QgsProcessingContext = None
    ) -> Tuple[SampleX, SampleY, Categories]:
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
