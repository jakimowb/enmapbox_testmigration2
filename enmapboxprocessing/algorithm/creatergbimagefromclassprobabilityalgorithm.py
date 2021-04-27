from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from PyQt5.QtGui import QColor
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer, Qgis)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class CreateRgbImageFromClassProbabilityAlgorithm(EnMAPProcessingAlgorithm):
    P_PROBABILITY, _PROBABILITY = 'probability', 'Class probability/fraction layer'
    P_COLORS, _COLORS = 'colors', 'Colors'
    P_COLORS_LAYER, _COLORS_LAYER = 'colorsLayer', 'Colors from categorized layer'
    P_COLORS_FILE, _COLORS_FILE = 'colorsFile', 'Colors from pickle file'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRGBImage', 'Output RGB image'

    def displayName(self):
        return 'Create RGB image from class probability/fraction layer'

    def shortDescription(self):
        return 'Create an RGB image from a class fraction/probability layer.' \
               'The RGB pixel color of a single pixel is given by the weighted mean of the given category colors.' \
               'The weights are given by class fractions/probabilities (i.e. values between 0 and 1).\n' \
               '\nFor example, pure pixels with cover fractions of 1 appear in its pure category color. ' \
               'A mixed-pixel with a 50% fractions in two categories colored in red and green,' \
               'appears in a dull yellow ( 0.5 x (255, 0, 0) + 0.5 x (0, 255, 0) = (127, 127, 0) ).'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._PROBABILITY, 'A class fraction layer or class probability layer used as weights for calculating '
                                'final pixel colors.'),
            (self._COLORS, 'Comma separated list of hex-colors representing (pure) category colors, '
                           'one color for each band in the given class probability/fraction layer.'),
            (self._OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.Postprocessing.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_PROBABILITY, self._PROBABILITY)
        self.addParameterMapLayer(self.P_COLORS_LAYER, self._COLORS_LAYER)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def checkParameterFractionAndStyle(
            self, parameters: Dict[str, Any], context: QgsProcessingContext
    ) -> Tuple[bool, str]:
        fraction = self.parameterAsRasterLayer(parameters, self.P_SCORE, context)
        classification = self.parameterAsLayer(parameters, self.P_STYLE, context)
        if isinstance(classification, QgsVectorLayer):
            categories = Utils.categoriesFromCategorizedSymbolRenderer(classification.renderer())
        elif isinstance(classification, QgsRasterLayer):
            categories = Utils.categoriesFromPalettedRasterRenderer(classification.renderer())
        else:
            return False, f'invalid layer type {classification}'
        valid = fraction.bandCount() == len(categories)
        return valid, 'Number of bands (score) not matching number of categories (style)'

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = self.checkParameterMapClassification(parameters, self.P_STYLE, context)
        if not valid:
            return False, message
        valid, message = self.checkParameterFractionAndStyle(parameters, context)
        if not valid:
            return False, message
        return True, ''

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_SCORE, context)
        style = self.parameterAsLayer(parameters, self.P_STYLE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        maximumMemoryUsage = gdal.GetCacheMax()

        if isinstance(style, QgsVectorLayer):
            categories = Utils.categoriesFromCategorizedSymbolRenderer(style.renderer())
        elif isinstance(style, QgsRasterLayer):
            categories = Utils.categoriesFromPalettedRasterRenderer(style.renderer())
        else:
            raise TypeError(self.P_STYLE)
        colors = [QColor(c[2]).rgb() for c in categories]

        reader = RasterReader(raster)
        driver = Driver(filename, 'GTiff', options=self.TiledAndCompressedGTiffCreationOptions, feedback=feedback)
        writer = driver.createLike(reader, Qgis.Byte, 3)
        lineMemoryUsage = reader.lineMemoryUsage()
        lineMemoryUsage += reader.lineMemoryUsage(3, Qgis.Float32)
        blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
        blockSizeX = raster.width()
        for block in reader.walkGrid(blockSizeX, blockSizeY, feedback):
            arrayRgb = np.zeros((3, block.height, block.width), np.float32)
            for bandNo, color in enumerate(colors, 1):
                arrayScore = np.clip(reader.arrayFromBlock(block, [bandNo])[0], 0, 1)
                np.clip(reader.arrayFromBlock(block, [bandNo])[0], 0, 1, arrayScore)
                for a, v in zip(arrayRgb, color):
                    a[:] += arrayScore * v
            writer.writeArray(arrayRgb, block.xOffset, block.yOffset)

        return {self.P_OUTPUT_RASTER: filename}
