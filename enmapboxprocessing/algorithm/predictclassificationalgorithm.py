from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
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
                           'Classifier features and raster bands are matched by name.'),
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
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_CLASSIFICATION, context)
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
            dataType = Utils.smallesUIntDataType(max([c.value for c in dump.categories]))
            writer = Driver(filename, format, options, feedback).createLike(rasterReader, dataType, 1)
            lineMemoryUsage = rasterReader.lineMemoryUsage()
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
