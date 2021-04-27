from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        Qgis)

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PredictClassPropabilityAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer with features'
    P_CLASSIFIER, _CLASSIFIER = 'classifier', 'Classifier'
    P_MASK, _MASK = 'mask', 'Mask layer'
    P_OUTPUT_PROBABILITY, _OUTPUT_PROBABILITY = 'outputProbability', 'Output class probability layer'

    def displayName(self) -> str:
        return 'Predict class probability layer'

    def shortDescription(self) -> str:
        return 'Uses a fitted classifier to predict class probability layer from a raster layer with features.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'A raster layer with bands used as features. '
                           'Classifier features and raster bands are matched by name.'),
            (self._CLASSIFIER, 'A fitted classifier.'),
            (self._MASK, 'A mask layer.'),
            (self._OUTPUT_PROBABILITY, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterFile(self.P_CLASSIFIER, self._CLASSIFIER, fileFilter='Model file (*.pkl)')
        self.addParameterMapLayer(self.P_MASK, self._MASK, optional=True, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_PROBABILITY, self._OUTPUT_PROBABILITY)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            dump = ClassifierDump(**Utils.pickleLoad(self.parameterAsFile(parameters, self.P_CLASSIFIER, context)))
        except TypeError:
            return False, 'Invalid classifier file.'
        if not hasattr(dump.classifier, 'predict_proba'):
            return False, 'Classifier does not support probability predictions.'
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        mask = self.parameterAsLayer(parameters, self.P_MASK, context)
        dump = ClassifierDump(**Utils.pickleLoad(self.parameterAsFile(parameters, self.P_CLASSIFIER, context)))
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        maximumMemoryUsage = gdal.GetCacheMax()

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            if isinstance(mask, QgsRasterLayer):
                feedback.pushInfo('Prepare mask')
                alg = TranslateRasterAlgorithm()
                parameters = {
                    alg.P_RASTER: mask,
                    alg.P_GRID: raster,
                    alg.P_CREATION_PROFILE: self.VrtProfile,
                    alg.P_BAND_LIST: [mask.renderer().usesBands()[0]],
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'mask.vrt')
                }
                mask = QgsRasterLayer(self.runAlg(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER])
            if isinstance(mask, QgsVectorLayer):
                feedback.pushInfo('Prepare mask')
                alg = RasterizeVectorAlgorithm()
                parameters = {
                    alg.P_VECTOR: mask,
                    alg.P_GRID: raster,
                    alg.P_INIT_VALUE: 0,
                    alg.P_BURN_VALUE: 1,
                    alg.P_DATA_TYPE: self.Byte,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'mask.tif')
                }
                mask = QgsRasterLayer(self.runAlg(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER])
            assert isinstance(mask, (type(None), QgsRasterLayer))

            rasterReader = RasterReader(raster)
            if mask is not None:
                maskReader = RasterReader(mask)
            nBands = len(dump.categories)
            dataType = Qgis.Float32
            gdalDataType = Utils.qgisDataTypeToNumpyDataType(dataType)
            writer = Driver(filename, format, options, feedback).createLike(rasterReader, dataType, nBands)
            lineMemoryUsage = rasterReader.lineMemoryUsage() + rasterReader.lineMemoryUsage(nBands, 32 // 4)
            blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
            blockSizeX = raster.width()
            for block in rasterReader.walkGrid(blockSizeX, blockSizeY, feedback):
                arrayX = rasterReader.arrayFromBlock(block)
                valid = np.all(rasterReader.maskArray(arrayX), axis=0)
                if mask is not None:
                    marray = maskReader.arrayFromBlock(block)
                    np.logical_and(valid, maskReader.maskArray(marray, defaultNoDataValue=0.)[0], out=valid)
                X = list()
                for a in arrayX:
                    X.append(a[valid])
                y = dump.classifier.predict_proba(np.transpose(X))
                arrayY = np.full((nBands, *valid.shape), -1, gdalDataType)
                for i, aY in enumerate(arrayY):
                    aY[valid] = y[:, i]
                    writer.writeArray2d(aY, i + 1, xOffset=block.xOffset, yOffset=block.yOffset)

            for bandNo, (value, label, color) in enumerate(dump.categories, 1):
                writer.setBandName(label, bandNo)
            writer.setNoDataValue(-1)

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
