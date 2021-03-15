import inspect
import traceback
from math import ceil
from typing import Dict, Any, List, Tuple
import numpy as np
from osgeo import gdal
from sklearn.base import ClassifierMixin
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape, CreationOptions
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer, QgsMapLayer, QgsWkbTypes, QgsRasterRenderer, Qgis)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class PredictClassPropabilityAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_MASK = 'mask'
    P_CLASSIFIER = 'classification'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outprobability'

    def displayName(self) -> str:
        return 'Predict Class Probabilities'

    def shortDescription(self) -> str:
        return 'Applies a classifier to a raster to predict class probabilities. '

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_RASTER, self.helpParameterRaster()),
            (self.P_CLASSIFIER, self.helpParameterClassifier()),
            (self.P_MASK, self.helpParameterMapMask()),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, 'Raster')
        self.addParameterFile(self.P_CLASSIFIER, 'Classifier', fileFilter='Model file (*.pkl)')
        self.addParameterMapLayer(self.P_MASK, 'Mask', optional=True, advanced=True)
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterCreationProfile(self.P_CREATION_PROFILE, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, 'Output Classification')

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            classifier, categories, *_ = Utils.pickleLoadClassifier(
                self.parameterAsFile(parameters, self.P_CLASSIFIER, context)
            )
        except TypeError:
            return False, 'Invalid classifier file.'
        if not hasattr(classifier, 'predict_proba'):
            return False, 'Classifier does not support probability predictions.'
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        mask = self.parameterAsLayer(parameters, self.P_MASK, context)
        classifier, categories, *_ = Utils.pickleLoadClassifier(
            self.parameterAsFile(parameters, self.P_CLASSIFIER, context)
        )
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        self.processQgis(
            raster, classifier, categories, filename, mask, format, options, maximumMemoryUsage, feedback
        )
        return {self.P_OUTPUT_RASTER: filename}

    @classmethod
    def processQgis(
            cls, raster: QgsRasterLayer, classifier: ClassifierMixin, categories: Categories, filename: str,
            mask: QgsMapLayer = None, format: str = None, options: CreationOptions = None,
            maximumMemoryUsage: int = None, feedback: QgsProcessingFeedback = None
    ):
        if isinstance(mask, QgsVectorLayer):
            assert 0  # todo rasterize as mask
        assert isinstance(mask, (type(None), QgsRasterLayer))

        if maximumMemoryUsage is None:
            maximumMemoryUsage = gdal.GetCacheMax()
        rasterReader = RasterReader(raster)
        if mask is not None:
            maskReader = RasterReader(mask)
            maskBandNo = mask.renderer().usesBands()[0]
            # todo test with same and different crs

        nBands = len(categories)
        dataType = Qgis.Float32
        gdalDataType = Utils.qgisDataTypeToNumpyDataType(dataType)
        writer = Driver(filename, format, options, feedback).createLike(rasterReader, dataType, nBands)
        lineMemoryUsage = rasterReader.lineMemoryUsage() + rasterReader.lineMemoryUsage(nBands, 32//4)
        blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
        blockSizeX = raster.width()
        for block in rasterReader.walkGrid(blockSizeX, blockSizeY, feedback):
            arrayX = rasterReader.arrayFromBlock(block)
            valid = np.all(rasterReader.maskArray(arrayX), axis=0)
            if mask is not None:
                marray = maskReader.arrayFromBlock(block, bandList=[maskBandNo])[0]
                np.logical_and(valid, maskReader.maskArray(marray, bandList=[maskBandNo]), out=valid)
            X = list()
            for a in arrayX:
                X.append(a[valid])
            y = classifier.predict_proba(np.transpose(X))
            arrayY = np.full((nBands, *valid.shape), -1, gdalDataType)
            for i, aY in enumerate(arrayY):
                aY[valid] = y[:, i]
                writer.writeArray2d(aY, i + 1, xOffset=block.xOffset, yOffset=block.yOffset)

        for bandNo, (value, label, color) in enumerate(categories, 1):
            writer.setBandName(label, bandNo)
        writer.setNoDataValue(-1)
