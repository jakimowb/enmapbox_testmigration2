from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterFile


from enmapbox.processing.types import unpickle

class EstimatorReportViewer(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'View Report'
        self.group = 'Estimator'
        self.addParameter(ParameterFile('estimator', 'Estimator', optional=False))

    def processAlgorithm(self, progress):

        from enmapboxplugin.processing.SignalsManager import SignalsManager

        estimator = unpickle(self.getParameterValue('estimator'), progress=progress)
        report = estimator.report().saveHTML().filename

        SignalsManager.emitHTMLCreated(report)