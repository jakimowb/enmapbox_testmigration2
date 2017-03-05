from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterString
from processing.core.outputs import OutputFile

from enmapbox.processing.estimators import RandomForestRegressor


class RandomForestRegressorFitter(GeoAlgorithm):

    statement = RandomForestRegressor().signature()

    def defineCharacteristics(self):

        self.name = 'RandomForestRegressor'
        self.group = 'Fit Regressor'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('train', 'Regression'))
        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(OutputFile(self.name, self.name, ext='pkl'))

    def processAlgorithm(self, progress):

        from enmapbox.processing.types import Image, Regression
        from enmapboxplugin.processing.SignalsManager import SignalsManager

        image = self.getParameterValue('image')
        train = self.getParameterValue('train')
        classifier = eval(self.getParameterValue('parameters'))
        classifier.fit(Image(image), Regression(train), progress=progress)
        filename = self.getOutputValue(self.name)
        classifier.pickle(filename, progress=progress)

        SignalsManager.emitPickleCreated(filename)

    def help(self):
        return False, 'http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html'
