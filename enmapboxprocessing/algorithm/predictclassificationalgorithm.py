from math import ceil
from typing import Dict, Any, List, Tuple
import numpy as np
from osgeo import gdal

from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked
from qgis._core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class PredictClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER = 'raster'
    P_MASK = 'mask'
    P_CLASSIFIER = 'classification'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outClassification'

    def displayName(self) -> str:
        return 'Predict classification'

    def shortDescription(self) -> str:
        return 'Applies a classifier to a raster to predict class labels. ' \
               '\nUsed in the Cookbook Recipes: <a href="' \
               'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html' \
               '">Classification</a>, <a href="' \
               'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html' \
               '">Graphical Modeler</a> for information on different parameters.'

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
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, 'Output classification')

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
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

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
                    alg.P_CREATION_PROFILE: self.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'mask.tif')
                }
                mask = QgsRasterLayer(self.runAlg(alg, parameters, None, feedback2, context, True)[alg.P_OUTPUT_RASTER])
            assert isinstance(mask, (type(None), QgsRasterLayer))

            if maximumMemoryUsage is None:
                maximumMemoryUsage = gdal.GetCacheMax()
            rasterReader = RasterReader(raster)
            if mask is not None:
                maskReader = RasterReader(mask)
            dataType = Utils.smallesUIntDataType(max([c[0] for c in dump.categories]))
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

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
