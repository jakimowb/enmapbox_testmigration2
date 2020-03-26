from typing import Dict

from qgis._core import QgsProcessingFeedback, QgsProcessingContext, QgsRasterLayer

from enmapboxprocessing.enmapalgorithm import (EnMAPAlgorithm, Help,
                                               EnMAPProcessingParameterRasterLayer, Group)
from hubdsm.algorithm.categorycounts import categoryCounts
from hubdsm.core.raster import Raster


class ClassificationStatistics(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification Statistics'

    def description(self):
        return 'This algorithm reports class counts.'

    def group(self):
        return Group.Auxilliary.name

    P_RASTER = 'raster'

    def defineCharacteristics(self):
        self.addParameter(
            EnMAPProcessingParameterRasterLayer(
                name=self.P_RASTER, description='Classification',
                help=Help(text='Raster with categories from 1 to n.'))
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        qgsRasterLayer: QgsRasterLayer = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        raster = Raster.open(qgsRasterLayer.source())

        total = 0
        for id, count in categoryCounts(raster=raster).items():
            feedback.pushInfo(f'{id}: {count}')
            total += count
        feedback.pushInfo(f'total: {total}')

        return {}