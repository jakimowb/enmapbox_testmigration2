from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster, ParameterString
from processing.core.outputs import OutputFile


from enmapbox.processing.estimators import RandomForestClassifier


class RandomForestClassifierFitter(GeoAlgorithm):

    statement = RandomForestClassifier().signature()

    def defineCharacteristics(self):

        self.name = 'RandomForestClassifier'
        self.group = 'Fit Classifier'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('train', 'Classification'))
        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(OutputFile(self.name, self.name, ext='pkl'))

    def processAlgorithm(self, progress):

        from enmapbox.processing.types import Image, Classification
        image = self.getParameterValue('image')
        train = self.getParameterValue('train')
        classifier = eval(self.getParameterValue('parameters'))
        classifier.fit(Image(image), Classification(train), progress=progress)
        filename = self.getOutputValue(self.name)
        classifier.pickle(filename, progress=progress)

