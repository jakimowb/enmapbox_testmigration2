from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer)

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
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
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
                alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'grid.x10.vrt')
            }
            self.runAlg(alg, parameters, None, feedback2, context, True)
            gridOversampled = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])

            # create x10 classification
            if isinstance(map, QgsRasterLayer):
                alg = TranslateCategorizedRasterAlgorithm()
                parameters = {
                    alg.P_CLASSIFICATION: map,
                    alg.P_GRID: gridOversampled,
                    alg.P_MAJORITY_VOTING: False,
                    alg.P_CREATION_PROFILE: alg.VrtProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.x10.vrt')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            elif isinstance(map, QgsVectorLayer):
                alg = RasterizeCategorizedVectorAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: map,
                    alg.P_GRID: gridOversampled,
                    alg.P_MAJORITY_VOTING: False,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.x10.tif')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            else:
                assert 0

            # calculate category fractions
            categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
            x10IdArray = RasterReader(classification).array()[0]
            maskArray = np.full((grid.height(), grid.width()), True, dtype=bool)
            arrays = list()
            for i, category in enumerate(categories):

                if feedback.isCanceled():
                    raise AlgorithmCanceledException()

                feedback.pushInfo(f"Calculate '{category.name}' cover fraction")
                feedback.setProgress(i / len(categories))

                # calculate cover fraction
                x10MaskArray = x10IdArray == category.value
                percentArray = x10MaskArray.reshape(
                    (grid.height(), 10, grid.width(), 10)
                ).sum(axis=3, dtype=np.float32).sum(axis=1, dtype=np.float32)
                percentArray /= 100

                # update global mask
                np.logical_and(maskArray, percentArray == 0, out=maskArray)

                arrays.append(percentArray)

            # apply global mask
            noDataValue = -1
            for array in arrays:
                array[maskArray] = noDataValue

            writer = Driver(filename, format, options).createFromArray(arrays, grid.extent(), grid.crs())
            writer.setNoDataValue(noDataValue)
            for bandNo, category in enumerate(categories, 1):
                writer.setBandName(category.name, bandNo)

            result = {self.P_OUTPUT_FRACTION: filename}
            self.toc(feedback, result)

        return result


def _calculatePurePython(classes, counts, notCovered, oversampling, indexByClass):
    height, width = notCovered.shape
    for y in range(height):
        for x in range(width):
            for y2 in range(oversampling):
                for x2 in range(oversampling):
                    c = classes[y * oversampling + y2, x * oversampling + x2]
                    index = indexByClass[c]
                    if index != -1:
                        counts[index, y, x] += 1
                        notCovered[y, x] = False
