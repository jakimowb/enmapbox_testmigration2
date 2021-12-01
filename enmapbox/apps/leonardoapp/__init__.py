from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu
from qgis._core import QgsRasterLayer

import inspect
import traceback
from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, Qgis)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


from enmapbox.gui.applications import EnMAPBoxApplication


def enmapboxApplicationFactory(enmapBox):
    return [TemplateApp(enmapBox)]


class TemplateApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = TemplateApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def processingAlgorithms(self):
        return [TemplateAlgorithm()]

@typechecked
class TemplateAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRaster', 'Output raster layer'

    def displayName(self) -> str:
        return 'The name ...'

    def shortDescription(self) -> str:
        return 'The description ...'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'Raster layer.'),
            (self._OUTPUT_RASTER, 'Raster file destination.')
        ]

    def group(self):
        return 'Water analysis'

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # call the algorithm that creates the result file


            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
