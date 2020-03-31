from typing import Dict

from qgis._core import QgsProcessingFeedback, QgsProcessingContext, QgsRasterLayer

from hubdsm.processing.enmapalgorithm import (EnMAPAlgorithm, Help,
                                              EnMAPProcessingParameterRasterLayer, Group, EnMAPProcessingParameterBand)
from hubdsm.algorithm.uniquebandvaluecounts import uniqueBandValueCounts
from hubdsm.core.raster import Raster


class UniqueBandValueCounts(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification Statistics'

    def description(self):
        return 'This algorithm reports class counts.'

    def group(self):
        return Group.Auxilliary.name

    P_RASTER = 'raster'
    P_BAND = 'band'

    def defineCharacteristics(self):
        self.addParameter(
            EnMAPProcessingParameterRasterLayer(
                name=self.P_RASTER, description='Classification',
                help=Help(text='Classification Raster.'))
        )

        self.addParameter(
            EnMAPProcessingParameterBand(
                name=self.P_BAND, description='Band', parentLayerParameterName=self.P_RASTER, defaultValue=1,
                help=Help(text='Raster band.'))
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        qgsRasterLayer: QgsRasterLayer = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        raster = Raster.open(qgsRasterLayer.source())
        band = raster.band(number=self.parameterAsInt(parameters, self.P_BAND, context))
        total = 0
        for id, count in uniqueBandValueCounts(band=band).items():
            feedback.pushInfo(f'{id}: {count}')
            total += count
        feedback.pushInfo(f'total: {total}')
        return {}