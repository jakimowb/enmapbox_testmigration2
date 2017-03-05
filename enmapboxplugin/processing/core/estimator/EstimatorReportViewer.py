from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterFile


class EstimatorReportViewer(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'View Report'
        self.group = 'Estimator'
        self.addParameter(ParameterFile('estimator', 'Estimator', optional=False))

    def processAlgorithm(self, progress):

        from enmapbox.processing.types import unpickle
        from enmapboxplugin.processing.SignalsManager import SignalsManager

        estimator = unpickle(self.getParameterValue('estimator'), progress=progress)
        report = estimator.report().saveHTML().filename

        SignalsManager.connectHTMLCreatedToWebBrowser()
        SignalsManager.emitHTMLCreated(report)
