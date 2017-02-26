from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterFile
from processing.core.outputs import OutputRaster

from enmapbox.processing.types import Image, Mask, unpickle

class EstimatorProbabilityPredictor(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'Probability Prediction'
        self.group = 'Estimator'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(ParameterFile('estimator', 'Estimator', optional=False))
        self.addOutput(OutputRaster('prediction', 'Probability Prediction'))

    def processAlgorithm(self, progress):

        image = self.getParameterValue('image')
        mask = self.getParameterValue('mask')
        filename = self.getParameterValue('estimator')
        estimator = unpickle(filename, progress=progress)
        estimation = estimator.predictProbability(image=Image(image),
                                                  mask=Mask(mask) if mask is not None else None,
                                                  filename=self.getOutputValue('prediction'), progress=progress)
