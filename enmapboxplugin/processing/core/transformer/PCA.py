from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterString
from processing.core.outputs import OutputFile

from enmapbox.processing.estimators import PCA


class PCAFitter(GeoAlgorithm):

    statement = PCA().signature()

    def defineCharacteristics(self):

        self.name = 'PCA'
        self.group = 'Fit Transformer'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('train', 'Mask'))
        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(OutputFile(self.name, self.name, ext='pkl'))

    def processAlgorithm(self, progress):

        from enmapbox.processing.types import Image, Mask
        from enmapboxplugin.processing.SignalsManager import SignalsManager

        image = self.getParameterValue('image')
        train = self.getParameterValue('train')
        classifier = eval(self.getParameterValue('parameters'))
        classifier.fit(Image(image), Mask(train), progress=progress)
        filename = self.getOutputValue(self.name)
        classifier.pickle(filename, progress=progress)

        SignalsManager.emitPickleCreated(filename)

    def help(self):
        return False, 'http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html'
