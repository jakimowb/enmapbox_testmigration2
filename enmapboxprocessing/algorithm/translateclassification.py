from typing import Dict, Any, List, Tuple

from processing.core.Processing import Processing

from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from typeguard import typechecked
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer)

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group


@typechecked
class TranslateClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFICATION = 'classification'
    P_GRID = 'grid'
    P_CREATION_PROFILE = 'creationProfile'
    P_OUTPUT_RASTER = 'outraster'

    def displayName(self):
        return 'Translate/Warp Classification'

    def shortDescription(self):
        return 'Resample classification into target grid by applying majority voting.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_CLASSIFICATION, self.helpParameterClassification()),
            (self.P_GRID, self.helpParameterGrid()),
            (self.P_CREATION_PROFILE, self.helpParameterCreationProfile()),
            (self.P_OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterRasterClassification(parameters, self.P_CLASSIFICATION, context)

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_CLASSIFICATION, 'Classification')
        self.addParameterRasterLayer(self.P_GRID, 'Grid')
        self.addParameterCreationProfile(self.P_CREATION_PROFILE, allowVrt=True, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CLASSIFICATION, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        creationProfile = self.parameterAsEnum(parameters, self.P_CREATION_PROFILE, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        alg = TranslateRasterAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: classification,
            alg.P_GRID: grid,
            alg.P_RESAMPLE_ALG: alg.ModeResampleAlg,
            alg.P_COPY_RENDERER: True,
            alg.P_CREATION_PROFILE: creationProfile,
            alg.P_OUTPUT_RASTER: filename
        }
        Processing.runAlgorithm(alg, parameters, None, feedback, context)
        return {self.P_OUTPUT_RASTER: filename}
