from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer, QgsPalettedRasterRenderer)

from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import SampleX, SampleY, Categories, checkSampleShape, ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class PrepareClassificationDatasetFromCategorizedRaster(EnMAPProcessingAlgorithm):
    P_CATEGORIZED_RASTER, _CATEGORIZED_RASTER = 'categorizedRaster', 'Categorized raster layer'
    P_FEATURE_RASTER, _FEATURE_RASTER = 'featureRaster', 'Raster layer with features'
    P_CATEGORY_BAND, _CATEGORY_BAND = 'categoryBand', 'Band with class values'
    P_OUTPUT_DATASET, _OUTPUT_DATASET = 'outputClassificationDataset', 'Output dataset'

    @classmethod
    def displayName(cls) -> str:
        return 'Prepare classification dataset (from categorized raster layer and feature raster)'

    def shortDescription(self) -> str:
        return 'Sample data for pixels that match the given categories and store the result as a pickle file. \n' \
               'If the layer is not categorized, or the band with class values is selected manually, ' \
               'categories are derived from sampled data itself. ' \
               'To be more precise: ' \
               'i) category values are derived from unique raster band values (after excluding no data or zero data pixel), ' \
               'ii) category names are set equal to the category values, ' \
               'and iii) category colors are picked randomly.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CATEGORIZED_RASTER,
             f'Categorized raster layer specifying sample locations and target data y. '
             f'If required, the layer is reprojected and resampled internally to match the feature raster grid.\n'),
            (self._FEATURE_RASTER, 'Raster layer used for sampling feature data X.'),
            (self._CATEGORY_BAND, 'Band with class values. '
                                  'If not selected, the band defined by the renderer is used. '
                                  'If that is also not specified, the first band is used.'),
            (self._OUTPUT_DATASET, self.PickleFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.DatasetPreparation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_CATEGORIZED_RASTER, self._CATEGORIZED_RASTER)
        self.addParameterRasterLayer(self.P_FEATURE_RASTER, self._FEATURE_RASTER)
        self.addParameterBand(
            self.P_CATEGORY_BAND, self._CATEGORY_BAND, None, self.P_CATEGORIZED_RASTER, True, False, True
        )
        self.addParameterFileDestination(self.P_OUTPUT_DATASET, self._OUTPUT_DATASET, self.PickleFileFilter)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CATEGORIZED_RASTER, context)
        raster = self.parameterAsRasterLayer(parameters, self.P_FEATURE_RASTER, context)
        classBandIndex = self.parameterAsInt(parameters, self.P_CATEGORY_BAND, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_DATASET, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # derive classification scheme
            renderer = classification.renderer()
            if classBandIndex is None:
                if isinstance(renderer, QgsPalettedRasterRenderer):
                    categories = Utils.categoriesFromPalettedRasterRenderer(renderer)
                    feedback.pushInfo(f'Use categories from style: {categories}')
                    classBandNo = renderer.band()
                else:
                    classBandNo = 1
                    categories = Utils.categoriesFromRasterBand(classification, classBandNo)
                    feedback.pushInfo(f'Derive categories from first band: {categories}')
            else:
                classBandNo = classBandIndex + 1
                categories = Utils.categoriesFromRasterBand(classification, classBandNo)
                feedback.pushInfo(f'Derive categories from selected band: {categories}')

            # resample classification and set renderer
            alg = TranslateClassificationAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_CLASSIFICATION: classification,
                alg.P_GRID: raster,
                alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.tif')
            }
            self.runAlg(alg, parameters, None, feedback2, context, True)
            classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            renderer = Utils.palettedRasterRendererFromCategories(classification.dataProvider(), 1, categories)
            classification.setRenderer(renderer)
            classification.saveDefaultStyle()

            X, y = self.sampleData(raster, classification, classBandNo, categories, feedback2)
            features = [RasterReader(raster).bandName(i + 1) for i in range(raster.bandCount())]
            feedback.pushInfo(f'Sampled data: X=array{list(X.shape)} y=array{list(y.shape)}')

            dump = ClassifierDump(categories=categories, features=features, X=X, y=y)
            dumpDict = dump._asdict()
            Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_DATASET: filename}
            self.toc(feedback, result)
        return result

    @classmethod
    def sampleData(
            cls, raster: QgsRasterLayer, classification: QgsRasterLayer, classBandNo: int, categories: Categories,
            feedback: QgsProcessingFeedback = None
    ) -> Tuple[SampleX, SampleY]:
        assert raster.crs() == classification.crs()
        assert raster.extent() == classification.extent()
        assert (raster.width(), raster.height()) == (classification.width(), classification.height())

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
            blockClassification = classificationReader.arrayFromBlock(block, [classBandNo])[0]
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
        return X, y
