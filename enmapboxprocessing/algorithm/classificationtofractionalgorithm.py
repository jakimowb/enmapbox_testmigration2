from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer, Qgis)

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.translatecategorizedrasteralgorithm import TranslateCategorizedRasterAlgorithm
from enmapboxprocessing.algorithm.rasterizecategorizedvectoralgorithm import RasterizeCategorizedVectorAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group, AlgorithmCanceledException
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class ClassificationToFractionAlgorithm(EnMAPProcessingAlgorithm):
    P_CATEGORIZED_LAYER, _CATEGORIZED_LAYER = 'categorizedLayer', 'Categorized layer'
    P_GRID, _GRID = 'grid', 'Grid'
    P_OUTPUT_FRACTION, _OUTPUT_FRACTION = 'outputClassFraction', 'Output class fraction layer'

    def displayName(self):
        return 'Categorized layer to class fraction layer'

    def shortDescription(self):
        return 'Aggregates a (single-band) categorized layer into a (multiband) class fraction raster, ' \
               'by resampling into the given grid. ' \
               'Output band order and naming are given by the renderer categories.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CATEGORIZED_LAYER, 'A categorized layer with categories to be aggregated into fractions.'),
            (self._GRID, 'The target grid.'),
            (self._OUTPUT_FRACTION, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMapLayer(self.P_CATEGORIZED_LAYER, self._CATEGORIZED_LAYER)
        self.addParameterRasterLayer(self.P_GRID, self._GRID)
        self.addParameterRasterDestination(self.P_OUTPUT_FRACTION, self._OUTPUT_FRACTION)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterMapClassification(parameters, self.P_CATEGORIZED_LAYER, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        map = self.parameterAsLayer(parameters, self.P_CATEGORIZED_LAYER, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        format, options = self.GTiffFormat, self.DefaultGTiffCreationOptions
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_FRACTION, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # create x10 grid
            alg = CreateGridAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_CRS: grid.crs(),
                alg.P_EXTENT: grid.extent(),
                alg.P_UNIT: alg.PixelUnits,
                alg.P_WIDTH: grid.width() * 10,
                alg.P_HEIGHT: grid.height() * 10,
                alg.P_OUTPUT_GRID: Utils.tmpFilename(filename, 'grid.x10.vrt')
            }
            self.runAlg(alg, parameters, None, feedback2, context, True)
            gridOversampled = QgsRasterLayer(parameters[alg.P_OUTPUT_GRID])

            # create x10 classification
            if isinstance(map, QgsRasterLayer):
                alg = TranslateCategorizedRasterAlgorithm()
                parameters = {
                    alg.P_CATEGORIZED_RASTER: map,
                    alg.P_GRID: gridOversampled,
                    alg.P_MAJORITY_VOTING: False,
                    alg.P_OUTPUT_CATEGORIZED_RASTER: Utils.tmpFilename(filename, 'classification.x10.vrt')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_CATEGORIZED_RASTER])
            elif isinstance(map, QgsVectorLayer):
                alg = RasterizeCategorizedVectorAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CATEGORIZED_VECTOR: map,
                    alg.P_GRID: gridOversampled,
                    alg.P_MAJORITY_VOTING: False,
                    alg.P_OUTPUT_CATEGORIZED_RASTER: Utils.tmpFilename(filename, 'classification.x10.tif')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_CATEGORIZED_RASTER])
            else:
                assert 0

            # calculate category fractions
            categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
            reader = RasterReader(classification)
            driver = Driver(filename, format, options, feedback)
            writer = driver.createLike(RasterReader(grid), Qgis.Float32, len(categories))
            lineMemoryUsage = reader.lineMemoryUsage() * 2
            blockSizeY = min(reader.height(), ceil(Utils.maximumMemoryUsage() / lineMemoryUsage))
            blockSizeY = max(10, blockSizeY)
            blockSizeY = ceil(blockSizeY / 10) * 10  # need to ensure factors of 10!
            blockSizeX = reader.width()
            for block in reader.walkGrid(blockSizeX, blockSizeY, feedback):

                feedback.setProgress(block.yOffset / gridOversampled.height() * 100)

                x10IdArray = reader.arrayFromBlock(block)[0]
                maskArray = np.full((block.height // 10, block.width //10), True, dtype=bool)

                arrays = list()
                for i, category in enumerate(categories):

                    if feedback.isCanceled():
                        raise AlgorithmCanceledException()

                    # calculate cover fraction
                    x10MaskArray = np.equal(x10IdArray, category.value)
                    percentArray = x10MaskArray.reshape(
                        (block.height // 10, 10, block.width // 10, 10)
                    ).sum(axis=3, dtype=np.float32).sum(axis=1, dtype=np.float32)
                    percentArray /= 100

                    # update global mask
                    np.logical_and(maskArray, percentArray == 0, out=maskArray)

                    arrays.append(percentArray)

                # apply global mask
                noDataValue = -1
                for array in arrays:
                    array[maskArray] = noDataValue

                writer.writeArray(arrays, block.xOffset // 10, block.yOffset // 10)

            writer.setNoDataValue(noDataValue)
            for bandNo, category in enumerate(categories, 1):
                writer.setBandName(category.name, bandNo)

            result = {self.P_OUTPUT_FRACTION: filename}
            self.toc(feedback, result)

        return result
