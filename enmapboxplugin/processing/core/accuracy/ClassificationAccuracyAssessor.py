from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster

from enmapbox.processing.types import Classification

class ClassificationAccuracyAssessor(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classification Accuracy Assessment'
        self.group = 'Accuracy Assessment'
        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('observed', 'Observation'))

    def processAlgorithm(self, progress):
        predicted = Classification(self.getParameterValue('prediction'))
        observed = Classification(self.getParameterValue('observed'))
        predicted.assessClassificationPerformance(observed).info()
