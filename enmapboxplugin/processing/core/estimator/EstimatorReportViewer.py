from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterFile
from processing.core.outputs import OutputRaster

from enmapbox.processing.types import Image, Mask, unpickle

class EstimatorReportViewer(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'View Report'
        self.group = 'Estimator'
        self.addParameter(ParameterFile('estimator', 'Estimator', optional=False))

    def processAlgorithm(self, progress):

        estimator = unpickle(self.getParameterValue('estimator'), progress=progress)
        estimator.info()