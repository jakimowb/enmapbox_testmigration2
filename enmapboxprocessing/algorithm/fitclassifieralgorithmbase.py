import inspect
import traceback
from math import ceil
from typing import Dict, Any, List, Tuple
import numpy as np
from osgeo import gdal
from sklearn.base import ClassifierMixin
from processing.core.Processing import Processing
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsWkbTypes)


from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class FitClassifierAlgorithmBase(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_CLASSIFICATION = 'classification'
    P_CODE = 'code'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_CLASSIFIER = 'classifier'

    def displayName(self) -> str:
        raise NotImplementedError()

    def shortDescription(self) -> str:
        raise NotImplementedError()

    def helpParameterCode(self) -> str:
        raise NotImplementedError()

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, 'Raster with training data features.'),
            (self.P_CLASSIFICATION, 'Classification with training data labels. '
                                    f'{self.helpParameterMapClassification()} '
                                    f'Note that the classification layer is resampled/reprojected/rasterized '
                                    f'internally to match the raster grid.'),
            (self.P_CODE, self.helpParameterCode()),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_OUTPUT_MODEL, 'Output classifier destination (*.pkl file). '
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
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterFileDestination(
            self.P_OUTPUT_CLASSIFIER, 'Output Classifier', 'Model file (*.pkl)', f'{self.P_OUTPUT_CLASSIFIER}')

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
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFIER, context)
        classifier = self.parameterAsClassifier(parameters, self.P_CODE, context)

        self.processQgis(
            raster, classification, classifier, filename, maximumMemoryUsage, feedback, context
        )
        return {self.P_OUTPUT_CLASSIFIER: filename}

    @classmethod
    def processQgis(
            cls, raster: QgsRasterLayer, classification: QgsMapLayer, classifier: ClassifierMixin, filename: str,
            maximumMemoryUsage: int = None, feedback: QgsProcessingFeedback = None, context: QgsProcessingContext = None
    ):
        if isinstance(classification, QgsVectorLayer):
            if classification.geometryType() == QgsWkbTypes.Point:
                assert 0
                features, labels = cls.samplePoints(raster, classification, )
            elif classification.geometryType() in [QgsWkbTypes.LineString, QgsWkbTypes.Polygon]:
                tmpFilename = Utils.tmpFilename(filename, 'classification.tif')

                alg = RasterizeClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: classification,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: alg.TiledAndCompressedGTiff,
                    alg.P_OUTPUT_RASTER: tmpFilename
                }
                Processing.runAlgorithm(alg, parameters, None, feedback, context)
                exit()

                #writer, categories = RasterizeClassificationAlgorithm.processQgis(
                #    classification, raster.extent(), raster.width(), raster.height(), raster.crs(), 10,
                #    tmpFilename, cls.GTiffFormat, cls.TiledAndCompressedGTiffCreationOptions, feedback
                #)
                classification = QgsRasterLayer(tmpFilename)
                categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
                X, y, categories = cls.samplePixels(raster, classification, categories, maximumMemoryUsage, feedback)
            else:
                assert 0
        elif isinstance(classification, QgsRasterLayer):
            tmpFilename = ''
            assert 0
            # case 1: grids do match -> do nothing
            # case 2: grids don't match -> translate classification
        else:
            assert 0

        classifier.fit(X, y.ravel())

        Utils.pickleDumpClassifier(classifier, categories, filename)
        exit()

    @classmethod
    def samplePixels(
            cls, raster: QgsRasterLayer, classification: QgsRasterLayer, categories: Categories = None,
            maximumMemoryUsage: int = None, feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY, Categories]:
        renderer = classification.renderer()
        assert isinstance(renderer, QgsPalettedRasterRenderer)
        if categories is None:
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
