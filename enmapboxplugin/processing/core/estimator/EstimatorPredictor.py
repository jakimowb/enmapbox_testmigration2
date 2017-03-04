from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterFile
from processing.core.outputs import OutputRaster


class EstimatorPredictor(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'Prediction'
        self.group = 'Estimator'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(ParameterFile('estimator', 'Estimator', optional=False))
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progress):

        from enmapbox.processing.types import Image, Mask, unpickle
        from enmapboxplugin.processing.SignalsManager import SignalsManager

        image = self.getParameterValue('image')
        mask = self.getParameterValue('mask')
        filename = self.getParameterValue('estimator')
        estimator = unpickle(filename, progress=progress)
        estimation = estimator.predict(image=Image(image),
                                       mask=Mask(mask) if mask is not None else None,
                                       filename=self.getOutputValue('prediction'), progress=progress)

        SignalsManager.emitImageCreated(estimation.filename)
