from hubdsm.algorithm.changemap import changeMap
from hubdsm.core.category import Category
from hubdsm.core.raster import Raster
from hubdsm.processing.enmapalgorithm import *


class ChangeMap(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Change Map'

    def description(self):
        return 'Create a change map from two classifications.'

    def group(self):
        return Group.Classification.value

    P_CLASSIFICATION1 = 'classification1'
    P_CLASSIFICATION2 = 'classification2'
    P_OUTRASTER = 'outraster'

    def defineCharacteristics(self):

        self.addParameter(
            EnMAPProcessingParameterPalettedRasterLayer(
                name=self.P_CLASSIFICATION1, description='Classification 1'
            )
        )

        self.addParameter(
            EnMAPProcessingParameterPalettedRasterLayer(
                name=self.P_CLASSIFICATION2, description='Classification 2'
            )
        )

        self.addParameter(
            EnMAPProcessingParameterRasterDestination(
                name=self.P_OUTRASTER, description='Output Raster'
            )
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):

        layer1: QgsRasterLayer = self.parameter(parameters, self.P_CLASSIFICATION1, context)
        layer2: QgsRasterLayer = self.parameter(parameters, self.P_CLASSIFICATION2, context)
        filename = self.parameter(parameters, self.P_OUTRASTER, context)

        categories1 = Category.fromQgsPalettedRasterRenderer(renderer=layer1.renderer())
        categories2 = Category.fromQgsPalettedRasterRenderer(renderer=layer2.renderer())

        changeMap(
            band1=Raster.open(layer1.source()).band(1),
            band2=Raster.open(layer2.source()).band(1),
            categories1=categories1,
            categories2=categories2,
            filename=filename
        )

        return {self.P_OUTRASTER: filename}
