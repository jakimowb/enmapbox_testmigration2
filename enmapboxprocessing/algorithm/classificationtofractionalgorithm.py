from typing import Dict, Any, List, Tuple
from warnings import warn

import numpy as np

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer,
                        QgsPalettedRasterRenderer)

from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group, AlgorithmCanceledException


@typechecked
class ClassificationToFractionAlgorithm(EnMAPProcessingAlgorithm):
    P_MAP = 'map'
    P_GRID = 'grid'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outRaster'

    def displayName(self):
        return 'Classification to fraction'

    def shortDescription(self):
        return 'Converts a classification (raster or vector) into a multiband class cover fraction raster. ' \
               'Output band order and naming are given by the renderer categories.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_MAP, self.helpParameterMapClassification()),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMapLayer(self.P_MAP, 'Classification')
        self.addParameterRasterLayer(self.P_GRID, 'Grid')
        self.addParameterCreationProfile(self.P_CREATION_PROFILE)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterMapClassification(parameters, self.P_MAP, context)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        map = self.parameterAsLayer(parameters, self.P_MAP, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        format, options = self.parameterAsCreationProfile(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

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
                alg = TranslateClassificationAlgorithm()
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
                alg = VectorToClassificationAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_VECTOR: map,
                    alg.P_GRID: gridOversampled,
                    alg.P_MAJORITY_VOTING: False,
                    alg.P_CREATION_PROFILE: self.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.x10.tif')
                }
                self.runAlg(alg, parameters, None, feedback2, context, True)
                classification = QgsRasterLayer(parameters[alg.P_OUTPUT_RASTER])
            else:
                assert 0

            # calculate category fractions
            categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
            x10IdArray = RasterReader(classification).array()[0]
            maskArray = np.full((grid.height(), grid.width()), True, dtype=np.bool)
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

            result = {self.P_OUTPUT_RASTER: filename}
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
