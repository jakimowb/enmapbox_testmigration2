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
        return [OCPFTGlobalAlgorithm(), OCPFTRegionalAlgorithm()]

@typechecked
class OCPFTGlobalAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER1, _RASTER1 = 'SPECTRAL_IMAGE', 'SPECTRAL IMAGER'
    P_RASTER2, _RASTER2 = 'QL_PIXELMASK', 'QL_PIXELMASK'
    P_RASTER3, _RASTER3 = 'raster3', 'Raster layer'
    P_RASTER4, _RASTER4 = 'raster4', 'Raster layer'
    P_RASTER5, _RASTER5 = 'raster5', 'Raster layer'
    P_RASTER6, _RASTER6 = 'raster6', 'Raster layer'
    P_RASTER7, _RASTER7 = 'raster7', 'Raster layer'
    P_RASTER8, _RASTER8 = 'raster8', 'Raster layer'

    P_PFT_TYPE, _PFT_TYPE = 'pftType', 'PFT Type'
    O_PFT_TYPE = ['Global', 'Regional']

    P_OUTPUT_GLOBAL1, _OUTPUT_GLOBAL1 = 'outputGlobal1', 'Output global diatoms file destination.'
    P_OUTPUT_GLOBAL2, _OUTPUT_GLOBAL2 = 'outputGlobal2', 'Output global ... file destination.'
    P_OUTPUT_GLOBAL3, _OUTPUT_GLOBAL3 = 'outputGlobal3', 'Output global ... file destination.'
    P_OUTPUT_GLOBAL4, _OUTPUT_GLOBAL4 = 'outputGlobal4', 'Output global diatoms file destination.'
    P_OUTPUT_GLOBAL5, _OUTPUT_GLOBAL5 = 'outputGlobal5', 'Output global diatoms file destination.'
    P_OUTPUT_GLOBAL6, _OUTPUT_GLOBAL6 = 'outputGlobal6', 'Output global diatoms file destination.'
    P_OUTPUT_GLOBAL7, _OUTPUT_GLOBAL7 = 'outputGlobal7', 'Output global diatoms file destination.'

    def displayName(self) -> str:
        return 'OC-PFT (global)'

    def shortDescription(self) -> str:
        return 'The description ...'

    def helpParameters(self) -> List[Tuple[str, str]]:
        # todo add the descriptions here
        return [
            (self._RASTER1, 'Spectral image TIF file.'),
            (self._RASTER2, 'Pixel mask TIF file.'),
            (self._OUTPUT_GLOBAL1, 'describe me')
        ]

    def group(self):
        return 'Water analysis'

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER1, self._RASTER1)
        self.addParameterRasterLayer(self.P_RASTER2, self._RASTER2, None, True)
        self.addParameterRasterLayer(self.P_RASTER3, self._RASTER3, None, True)
        self.addParameterRasterLayer(self.P_RASTER4, self._RASTER4, None, True)
        self.addParameterRasterLayer(self.P_RASTER5, self._RASTER5, None, True)
        self.addParameterRasterLayer(self.P_RASTER6, self._RASTER6, None, True)
        self.addParameterRasterLayer(self.P_RASTER7, self._RASTER7, None, True)
        self.addParameterRasterLayer(self.P_RASTER8, self._RASTER8, None, True)

        # 7 global results
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL1, self._OUTPUT_GLOBAL1, None)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL2, self._OUTPUT_GLOBAL2, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL3, self._OUTPUT_GLOBAL3, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL4, self._OUTPUT_GLOBAL4, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL5, self._OUTPUT_GLOBAL5, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL6, self._OUTPUT_GLOBAL6, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_GLOBAL7, self._OUTPUT_GLOBAL7, None, True, False)


    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster1 = self.parameterAsRasterLayer(parameters, self.P_RASTER1, context)
        raster2 = self.parameterAsRasterLayer(parameters, self.P_RASTER2, context)
        raster3 = self.parameterAsRasterLayer(parameters, self.P_RASTER3, context)
        raster4 = self.parameterAsRasterLayer(parameters, self.P_RASTER4, context)
        raster5 = self.parameterAsRasterLayer(parameters, self.P_RASTER5, context)
        raster6 = self.parameterAsRasterLayer(parameters, self.P_RASTER6, context)
        raster7 = self.parameterAsRasterLayer(parameters, self.P_RASTER7, context)

        filename1 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL1, context)
        filename2 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL2, context)
        filename3 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL3, context)
        filename4 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL4, context)
        filename5 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL5, context)
        filename6 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL6, context)
        filename7 = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_GLOBAL7, context)

        with open(filename1 + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # call the algorithm that creates the result file
            raster1Filename = raster1.source()

            from leonardoapp.core import myAlgo
            myAlgo(raster1Filename, filename1)

            result = {self.P_OUTPUT_GLOBAL1: filename1,
                      self.P_OUTPUT_GLOBAL2: filename2,
                      self.P_OUTPUT_GLOBAL3: filename3,
                      self.P_OUTPUT_GLOBAL4: filename4,
                      self.P_OUTPUT_GLOBAL5: filename5,
                      self.P_OUTPUT_GLOBAL6: filename6,
                      self.P_OUTPUT_GLOBAL7: filename7}
            self.toc(feedback, result)

        return result

@typechecked
class OCPFTRegionalAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER1, _RASTER1 = 'SPECTRAL_IMAGE', 'SPECTRAL IMAGER'
    P_RASTER2, _RASTER2 = 'QL_PIXELMASK', 'QL_PIXELMASK'
    P_RASTER3, _RASTER3 = 'raster3', 'Raster layer'
    P_RASTER4, _RASTER4 = 'raster4', 'Raster layer'
    P_RASTER5, _RASTER5 = 'raster5', 'Raster layer'
    P_RASTER6, _RASTER6 = 'raster6', 'Raster layer'
    P_RASTER7, _RASTER7 = 'raster7', 'Raster layer'
    P_RASTER8, _RASTER8 = 'raster8', 'Raster layer'

    P_OUTPUT_REGIONAL1, _OUTPUT_REGIONAL1 = 'outputRegional1', 'Output REGIONAL diatoms file destination.'
    P_OUTPUT_REGIONAL2, _OUTPUT_REGIONAL2 = 'outputRegional2', 'Output REGIONAL ... file destination.'
    P_OUTPUT_REGIONAL3, _OUTPUT_REGIONAL3 = 'outputRegional3', 'Output REGIONAL ... file destination.'
    P_OUTPUT_REGIONAL4, _OUTPUT_REGIONAL4 = 'outputRegional4', 'Output REGIONAL diatoms file destination.'

    def displayName(self) -> str:
        return 'OC-PFT (regional)'

    def shortDescription(self) -> str:
        return 'The description ...'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER1, 'Spectral image TIF file.'),
            (self._RASTER2, 'Pixel mask TIF file.'),
            (self._OUTPUT_GLOBAL1, 'describe me')
        ]

    def group(self):
        return 'Water analysis'

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER1, self._RASTER1)
        self.addParameterRasterLayer(self.P_RASTER2, self._RASTER2, None, True)
        self.addParameterRasterLayer(self.P_RASTER3, self._RASTER3, None, True)
        self.addParameterRasterLayer(self.P_RASTER4, self._RASTER4, None, True)
        self.addParameterRasterLayer(self.P_RASTER5, self._RASTER5, None, True)
        self.addParameterRasterLayer(self.P_RASTER6, self._RASTER6, None, True)
        self.addParameterRasterLayer(self.P_RASTER7, self._RASTER7, None, True)
        self.addParameterRasterLayer(self.P_RASTER8, self._RASTER8, None, True)

        self.addParameterEnum(self.P_PFT_TYPE, self._PFT_TYPE, self.O_PFT_TYPE)

        # 4 regional results
        self.addParameterRasterDestination(self.P_OUTPUT_REGIONAL1, self._OUTPUT_REGIONAL1, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_REGIONAL2, self._OUTPUT_REGIONAL2, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_REGIONAL3, self._OUTPUT_REGIONAL3, None, True, False)
        self.addParameterRasterDestination(self.P_OUTPUT_REGIONAL4, self._OUTPUT_REGIONAL4, None, True, False)

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
