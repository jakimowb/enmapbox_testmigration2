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

        from enmapboxplugin.processing.Signals import Signals

        predicted = Classification(self.getParameterValue('prediction'))
        observed = Classification(self.getParameterValue('observed'))
        report = predicted.assessClassificationPerformance(observed).report().saveHTML().filename

        Signals.emitHTMLCreated(report)