from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from PyQt5.QtGui import QColor
from osgeo import gdal
from enmapboxprocessing.driver import Driver
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer, Qgis)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils


@typechecked
class ColorizeClassProbabilityAlgorithm(EnMAPProcessingAlgorithm):
    P_SCORE = 'score'
    P_STYLE = 'style'
    P_MAXIMUM_MEMORY_USAGE = 'maximumMemoryUsage'
    P_OUTPUT_RGB = 'outrgb'

    def displayName(self):
        return 'Colorize Class Scores'

    def shortDescription(self):
        return 'Converts multiband class scores (e.g. class cover fractions or probabilies) ' \
               'into a RGB visualization concidering all classes at ones. ' \
               'The RGB color is the weighted mean of class colors given by the style, ' \
               'and weights are given by class scores.  ' \
               '\nFor example, pure pixels with score of 1 (e.g. class cover fraction equal 100%) ' \
               'appear in its pure class color. ' \
               'A two class mixture pixel with 50% of class red (255, 0, 0) and 50% of class green (0, 255, 0) ' \
               'appears in a dull yellow (127, 127, 0).'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_SCORE, 'Source raster layer with bands matching categories given by style.'),
            (self.P_STYLE, self.helpParameterMapClassification()),
            (self.P_MAXIMUM_MEMORY_USAGE, self.helpParameterMaximumMemoryUsage()),
            (self.P_OUTPUT_RGB, self.helpParameterRasterDestination())
        ]

    def group(self):
        return Group.Test.value + Group.Postprocessing.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_SCORE, 'Score')
        self.addParameterMapLayer(self.P_STYLE, 'Style')
        self.addParameterMaximumMemoryUsage(self.P_MAXIMUM_MEMORY_USAGE, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RGB, 'Output RGB')

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
        return valid, 'Number of bands (Score) not matching number of categories (Style)'

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = self.checkParameterMapClassification(parameters, self.P_CLASSIFICATION, context)
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
        maximumMemoryUsage = self.parameterAsInt(parameters, self.P_MAXIMUM_MEMORY_USAGE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RGB, context)

        if isinstance(style, QgsVectorLayer):
            categories = Utils.categoriesFromCategorizedSymbolRenderer(style.renderer())
        elif isinstance(style, QgsRasterLayer):
            categories = Utils.categoriesFromPalettedRasterRenderer(style.renderer())
        else:
            raise TypeError(self.P_STYLE)
        colors = [QColor(c[2]).rgb() for c in categories]

        if maximumMemoryUsage is None:
            maximumMemoryUsage = gdal.GetCacheMax()
        reader = RasterReader(raster)
        driver = Driver(filename, 'GTiff', options=self.TiledAndCompressedGTiff, feedback=feedback)
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

        return {self.P_OUTPUT_RGB: filename}
