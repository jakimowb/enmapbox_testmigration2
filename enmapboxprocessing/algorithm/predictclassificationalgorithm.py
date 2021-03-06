from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer,
                        QgsProcessingException, QgsMapLayer)

from enmapboxprocessing.algorithm.layertomaskalgorithm import LayerToMaskAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PredictClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer with features'
    P_CLASSIFIER, _CLASSIFIER = 'classifier', 'Classifier'
    P_MASK, _MASK = 'mask', 'Mask layer'
    P_OUTPUT_CLASSIFICATION, _OUTPUT_CLASSIFICATION = 'outputClassification', 'Output classification layer'

    def displayName(self) -> str:
        return 'Predict classification layer'

    def shortDescription(self) -> str:
        return 'Uses a fitted classifier to predict a classification layer from a raster layer with features. \n' \
               'Used in the Cookbook Recipes: <a href="' \
               'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html' \
               '">Classification</a>, <a href="' \
               'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html' \
               '">Graphical Modeler</a> for information on different parameters.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'A raster layer with bands used as features. '
                           'Classifier features and raster bands are matched by name to allow for classifiers trained '
                           'on a subset of the raster bands. If raster bands and classifier features are not matching by name, '
                           'but overall number of bands and features do match, raster bands are used in original order.'),
            (self._CLASSIFIER, 'A fitted classifier.'),
            (self._MASK, 'A mask layer.'),
            (self._OUTPUT_CLASSIFICATION, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.Classification.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterMapLayer(self.P_MASK, self._MASK, optional=True, advanced=True)
        self.addParameterFile(self.P_CLASSIFIER, self._CLASSIFIER, fileFilter='Model file (*.pkl)')
        self.addParameterRasterDestination(self.P_OUTPUT_CLASSIFICATION, self._OUTPUT_CLASSIFICATION)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        try:
            ClassifierDump(**Utils.pickleLoad(self.parameterAsFile(parameters, self.P_CLASSIFIER, context)))
        except TypeError:
            return False, 'Invalid classifier file.'
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        mask = self.parameterAsLayer(parameters, self.P_MASK, context)
        dump = ClassifierDump(**Utils.pickleLoad(self.parameterAsFile(parameters, self.P_CLASSIFIER, context)))
        format, options = self.GTiffFormat, self.DefaultGTiffCreationOptions
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_CLASSIFICATION, context)
        maximumMemoryUsage = Utils.maximumMemoryUsage()

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            if isinstance(mask, QgsMapLayer):
                feedback.pushInfo('Prepare mask')
                alg = LayerToMaskAlgorithm()
                parameters = {
                    alg.P_LAYER: mask,
                    alg.P_GRID: raster,
                    alg.P_OUTPUT_MASK: Utils.tmpFilename(filename, 'mask.tif')
                }
                mask = QgsRasterLayer(self.runAlg(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_MASK])

            assert isinstance(mask, (type(None), QgsRasterLayer))

            rasterReader = RasterReader(raster)
            bandNames = [rasterReader.bandName(i + 1) for i in range(rasterReader.bandCount())]

            # match classifier features with raster band names
            try:  # try to find matching bands ...
                bandList = [bandNames.index(feature) + 1 for feature in dump.features]
            except ValueError:
                bandList = None

            # ... if not possible, use original bands, if overall number of bands and features do match
            if bandList is None and len(bandNames) != len(dump.features):
                message = f'classifier features ({dump.features}) not matching raster bands ({bandNames})'
                feedback.reportError(message, fatalError=True)
                raise QgsProcessingException(message)

            if mask is not None:
                maskReader = RasterReader(mask)
            dataType = Utils.smallesUIntDataType(max([c.value for c in dump.categories]))
            writer = Driver(filename, format, options, feedback).createLike(rasterReader, dataType, 1)
            lineMemoryUsage = rasterReader.lineMemoryUsage()
            blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
            blockSizeX = raster.width()
            for block in rasterReader.walkGrid(blockSizeX, blockSizeY, feedback):
                arrayX = rasterReader.arrayFromBlock(block, bandList)
                valid = np.all(rasterReader.maskArray(arrayX, bandList), axis=0)
                if mask is not None:
                    marray = maskReader.arrayFromBlock(block)
                    np.logical_and(valid, maskReader.maskArray(marray, defaultNoDataValue=0.)[0], out=valid)
                X = list()
                for a in arrayX:
                    X.append(a[valid])
                y = dump.classifier.predict(np.transpose(X))
                arrayY = np.zeros_like(valid, Utils.qgisDataTypeToNumpyDataType(dataType))
                arrayY[valid] = y
                writer.writeArray2d(arrayY, 1, xOffset=block.xOffset, yOffset=block.yOffset)

            writer.close()
            outraster = QgsRasterLayer(filename)
            renderer = Utils.palettedRasterRendererFromCategories(outraster.dataProvider(), 1, dump.categories)
            outraster.setRenderer(renderer)
            outraster.saveDefaultStyle()

            result = {self.P_OUTPUT_CLASSIFICATION: filename}
            self.toc(feedback, result)

        return result
