from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster

from enmapbox.processing.types import Regression

class RegressionAccuracyAssessor(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Regression Accuracy Assessment'
        self.group = 'Accuracy Assessment'
        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('observation', 'Observation'))

    def processAlgorithm(self, progress):

        from enmapboxplugin.processing.Signals import Signals

        observation = Regression(self.getParameterValue('observation'))
        prediction = Regression(self.getParameterValue('prediction'))
        report = prediction.assessRegressionPerformance(observation).report().saveHTML().filename

        Signals.emitHTMLCreated(report)