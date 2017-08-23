from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *
from processing.core.outputs import *
import numpy
from hubflow.types import *
from enmapboxgeoalgorithms.estimators import *

def parseList(text, dtype=str):
    result = [dtype(value.strip()) for value in text.split(',') if value.strip() != '']
    if len(result) == 0:
        result = None
    return result

ALGORITHMS = list()
class OpenTestdata(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Open Testdata'
        self.group = 'Open'

        self.addOutput(OutputRaster('enmap', 'EnMAP (30m; 244 bands)'))
        self.addOutput(OutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)'))
        self.addOutput(OutputVector('landcover', 'LandCover Layer'))
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm(self, progress):

        import enmapboxtestdata
        self.setOutputValue('enmap', enmapboxtestdata.enmap)
        self.setOutputValue('hymap', enmapboxtestdata.hymap)
        self.setOutputValue('landcover', enmapboxtestdata.landcover)
        self.setOutputValue('speclib', enmapboxtestdata.speclib)

    def help(self):
        return True, 'Open EnMAP-Box Testdata'
ALGORITHMS.append(OpenTestdata())

class UnsupervisedSampleFromENVISpectralLibrary(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Import ENVI Spectral Library'
        self.group = 'Import'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('sample', 'UnsupervisedSample', ext='pkl'))

    def processAlgorithm(self, progressBar):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
        sample.pickle(filename=self.getOutputValue('sample'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns an UnsupervisedSample imported from an ENVI Spectral Library file.'
ALGORITHMS.append(UnsupervisedSampleFromENVISpectralLibrary())

class UnsupervisedSampleClassifyByClassName(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classify Sample By Class Name'
        self.group = 'Sample'

        self.addParameter(ParameterFile('sample', 'Sample', optional=False))
        self.addParameter(ParameterString('prefix', 'ClassDefinition prefix', default=''))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('csample', 'ClassificationSample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        unsupervisedSample = UnsupervisedSample.unpickle(filename=self.getParameterValue('sample'))
        prefix = self.getParameterValue('prefix')
        if not prefix.endswith(' '):
            prefix = prefix+' '
        for key in ['class names', 'class lookup', 'class spectra names']:
            key = prefix+key
            if not key in unsupervisedSample.metadata:
                progressBar.setInfo(msg='missing metatdata: '+key, error=True)
                raise Exception('missing metatdata: '+key)

        classDefinition = ClassDefinition(names=unsupervisedSample.metadata[prefix+'class names'][1:],
                                          lookup=unsupervisedSample.metadata[prefix+'class lookup'][3:])
        classificationSample = unsupervisedSample.classifyByClassName(names=unsupervisedSample.metadata[prefix+'class spectra names'],
                                                                      classDefinition=classDefinition)

        classificationSample.pickle(filename=self.getOutputValue('csample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns a ClassificationSample. The input Sample is classified by using a ClassDefinition that must be provided inside the Sample metatdata'+\
                     '(i.e. <i>prefix</i> class names, <i>prefix</i> class lookup, <i>prefix</i> class names, <i>prefix</i> class spectra names).'
ALGORITHMS.append(UnsupervisedSampleClassifyByClassName())

#        classificationSample.scaleFeaturesInplace(factor=10000.)

class UnsupervisedSampleScaleFeatures(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Scale Sample Features'
        self.group = 'Sample'

        self.addParameter(ParameterFile('sample', 'Sample', optional=False))
        self.addParameter(ParameterNumber('factor', 'Scale factor', default=1.))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('outsample', 'Scaled Sample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        sample = UnsupervisedSample.unpickle(filename=self.getParameterValue('sample'))
        sample.scaleFeaturesInplace(factor=self.getParameterValue('factor'))
        sample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns a Sample with scaled features.'
ALGORITHMS.append(UnsupervisedSampleScaleFeatures())

class ClassificationSampleSynthMix(GeoAlgorithm):
    options = ['proportional', 'equalized']
    def defineCharacteristics(self):
        self.name = 'Generate synthetically mixed ProbabilitySample'
        self.group = 'Sample'

        self.addParameter(ParameterFile('csample', 'ClassificationSample', optional=False))
        self.addParameter(ParameterNumber('n', 'n', default=1000))
        self.addParameter(ParameterNumber('complex2', 'Likelihood for mixing complexity 2', default=1.0))
        self.addParameter(ParameterNumber('complex3', 'Likelihood for mixing complexity 3', default=0.0))
        self.addParameter(ParameterSelection('option', 'Class likelihoods', options=self.options, default=0))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('outsample', 'ProbabilitySample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        classificationSample = ClassificationSample.unpickle(filename=self.getParameterValue('csample'))
        mixingComplexities = {2:self.getParameterValue('complex2'), 3:self.getParameterValue('complex3')}
        probabilitySample = classificationSample.synthMix(mixingComplexities=mixingComplexities,
                                                          classLikelihoods=self.options[self.getParameterValue('option')],
                                                          n=self.getParameterValue('n'))
        probabilitySample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            probabilitySample.browse()

    def help(self):
        return True, 'Returns a synthetically mixed ProbabilitySample.'
ALGORITHMS.append(ClassificationSampleSynthMix())

class ProbabilitySampleSubsetClassesByClassName(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Subset ProbabilitySample Classes'
        self.group = 'Sample'

        self.addParameter(ParameterFile('sample', 'ProbabilitySample', optional=False))
        self.addParameter(ParameterString('names', 'Class names', default=''))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('outsample', 'ProbabilitySample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        probabilitySample = ProbabilitySample.unpickle(filename=self.getParameterValue('sample'))
        names = self.getParameterValue('names')
        for c in '{[( )]}':
            names = names.replace(c, ' ').strip()
        names = [name.strip() for name in names.split(' ')]
        probabilitySample = probabilitySample.subsetClassesByNames(names=names)
        probabilitySample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            probabilitySample.browse()


    def help(self):
        return True, 'Returns a ProbabilitySample with subsetted classes.'
ALGORITHMS.append(ProbabilitySampleSubsetClassesByClassName())

class ProbabilitySampleClassify(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classify ProbabilitySample'
        self.group = 'Sample'

        self.addParameter(ParameterFile('probabilitySample', 'ProbabilitySample', optional=False))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('minWinnerCoverage', 'Minimal winner class coverage', minValue=0., maxValue=1., default=0.5))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('outsample', 'ClassificationSample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        probabilitySample = ProbabilitySample.unpickle(filename=self.getParameterValue('probabilitySample'))
        classificationSample = probabilitySample.classifyByProbability(minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                                       minWinnerCoverage=self.getParameterValue('minWinnerCoverage'))
        classificationSample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns a ClassificationSample.'
ALGORITHMS.append(ProbabilitySampleClassify())

class EstimatorFit(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = TMP_NAME + ' Fit'
        self.group = TMP_GROUP

        if self.group == REGRESSORS_GROUP:
            self.addParameter(ParameterFile('sample', 'RegressionSample', optional=False))
        elif self.group == CLASSIFIERS_GROUP:
            self.addParameter(ParameterFile('sample', 'ClassificationSample', optional=False))
        else:
            assert 0
        self.addParameter(ParameterString('parameters', 'Parameters', TMP_ESTIMATOR, multiline=True))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('model', 'Fitted Model', ext='pkl'))

    def processAlgorithm(self, progressBar):
        if self.group == REGRESSORS_GROUP:
            sample = RegressionSample.unpickle(filename=self.getParameterValue('sample'))
            sklEstimator = eval(self.getParameterValue('parameters'))
            estimator = Regressor(sklEstimator=sklEstimator)
        elif self.group == CLASSIFIERS_GROUP:
            sample = ClassificationSample.unpickle(filename=self.getParameterValue('sample'))
            sklEstimator = eval(self.getParameterValue('parameters'))
            estimator = Classifier(sklEstimator=sklEstimator)
        else:
            assert 0
        estimator.fit(sample=sample)
        estimator.pickle(filename=self.getOutputValue('model'))
        if self.getParameterValue('view'):
            estimator.browse()

    def help(self):
        if self.group == REGRESSORS_GROUP:
            return True, 'Returns a Regressor fittet on a RegressionSample.'
        elif self.group == CLASSIFIERS_GROUP:
            return True, 'Returns a Classifier fittet on a ClassificationSample.'
        else:
            assert 0

class EstimatorPredict(GeoAlgorithm):

    def defineCharacteristics(self):

        self.name = TMP_GROUP[:-1] + ' Predict'
        self.group = TMP_GROUP

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        if self.group == REGRESSORS_GROUP:
            self.addParameter(ParameterFile('model', 'Regressor', optional=False))
        elif self.group == CLASSIFIERS_GROUP:
            self.addParameter(ParameterFile('model', 'Classifier', optional=False))
        else:
            assert 0
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progressBar):
        if self.group == REGRESSORS_GROUP:
            estimator = Regressor.unpickle(filename=self.getParameterValue('model'))
        elif self.group == CLASSIFIERS_GROUP:
            estimator = Classifier.unpickle(filename=self.getParameterValue('model'))
        else:
            assert 0
        image = Image(filename=self.getParameterValue('image'))
        mask = Mask(filename=self.getParameterValue('mask'))
        estimator.predict(predictionFilename=self.getOutputValue('prediction'), image=image, mask=mask)

    def help(self):
        if self.group == REGRESSORS_GROUP:
            return True, 'Returns a Regression.'
        elif self.group == CLASSIFIERS_GROUP:
            return True, 'Returns a Classifier.'
        else:
            assert 0

CLASSIFIERS_GROUP, REGRESSORS_GROUP = 'Classifiers', 'Regressors'
for TMP_GROUP, TMP_ESTIMATORS in [(CLASSIFIERS_GROUP, CLASSIFIERS), (REGRESSORS_GROUP, REGRESSORS)]:
    for TMP_NAME, TMP_ESTIMATOR in TMP_ESTIMATORS.items():
        ALGORITHMS.append(EstimatorFit())
    ALGORITHMS.append(EstimatorPredict())

class VectorClassificationRasterizeAsClassification(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Rasterize Vector as Classification'
        self.group = 'Vector'

        self.addParameter(ParameterRaster('image', 'Image (defining the PixelGrid)'))
        self.addParameter(ParameterVector('vector', 'Vector'))
        self.addParameter(ParameterTableField('idAttribute', 'Class id attribute', datatype=ParameterTableField.DATA_TYPE_NUMBER,
                                              parent='vector'))
        self.addParameter(ParameterString('names', 'Class names', optional=True))
        self.addParameter(ParameterString('lookup', 'Class colors', optional=True))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('minWinnerCoverage', 'Minimal winner class coverage', minValue=0., maxValue=1., default=0.5))

        self.addParameter(ParameterNumber('oversampling', 'Oversampling factor', minValue=1, maxValue=10, default=10))

        self.addOutput(OutputRaster('classification', 'Classification'))

    def processAlgorithm(self, progressBar):

        classes = None
        names = parseList(self.getParameterValue('names'))
        if names is None:
            classes = numpy.max(Vector(filename=self.getParameterValue('vector')).uniqueValues(attribute=self.getParameterValue('idAttribute')))
        lookup = parseList(self.getParameterValue('lookup'))
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)

        image = Image(filename=self.getParameterValue('image'))
        vectorClassification = VectorClassification(filename=self.getParameterValue('vector'),
                                                    idAttribute=self.getParameterValue('idAttribute'),
                                                    minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                    minWinnerCoverage=self.getParameterValue('minWinnerCoverage'),
                                                    classDefinition=classDefinition)
        vectorClassification.rasterizeAsClassification(classificationFilename=self.getOutputValue('classification'),
                                                       grid=image.pixelGrid,
                                                       oversampling=self.getParameterValue('oversampling'))

    def help(self):
        return True, 'Returns a Classification.'
ALGORITHMS.append(VectorClassificationRasterizeAsClassification())

class VectorClassificationRasterizeAsProbability(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Rasterize Vector as Probability'
        self.group = 'Vector'

        self.addParameter(ParameterRaster('image', 'Image (defining the PixelGrid)'))
        self.addParameter(ParameterVector('vector', 'Vector'))
        self.addParameter(ParameterTableField('idAttribute', 'Class id attribute', datatype=ParameterTableField.DATA_TYPE_NUMBER,
                                              parent='vector'))
        self.addParameter(ParameterString('names', 'Class names', optional=True))
        self.addParameter(ParameterString('lookup', 'Class colors', optional=True))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('oversampling', 'Oversampling factor', minValue=1, maxValue=10, default=10))
        self.addOutput(OutputRaster('probability', 'Probability'))

    def processAlgorithm(self, progressBar):

        classes = None
        names = parseList(self.getParameterValue('names'))
        if names is None:
            classes = numpy.max(Vector(filename=self.getParameterValue('vector')).uniqueValues(attribute=self.getParameterValue('idAttribute')))
        lookup = parseList(self.getParameterValue('lookup'))
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)


        image = Image(filename=self.getParameterValue('image'))
        vectorClassification = VectorClassification(filename=self.getParameterValue('vector'),
                                                    idAttribute=self.getParameterValue('idAttribute'),
                                                    minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                    classDefinition=classDefinition)
        vectorClassification.rasterizeAsProbability(probabilityFilename=self.getOutputValue('probability'),
                                                       grid=image.pixelGrid,
                                                       oversampling=self.getParameterValue('oversampling'))

    def help(self):
        return True, 'Returns a Probability.'
ALGORITHMS.append(VectorClassificationRasterizeAsProbability())

class ProbabilityAsClassColorRGB(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Probability as RGB Image'
        self.group = 'Probability'

        self.addParameter(ParameterRaster('probability', 'Probability'))
        self.addParameter(ParameterString('filterById', 'Filter classes by id', optional=True))
        self.addParameter(ParameterString('filterByName', 'Filter classes by names', optional=True))
        self.addOutput(OutputRaster('image', 'RGB Image'))

    def processAlgorithm(self, progressBar):

        probability = Probability(filename=self.getParameterValue('probability'))
        probability.asClassColorRGBImage(imageFilename=self.getOutputValue('image'),
                                         filterById=parseList(self.getParameterValue('filterById'), dtype=int),
                                         filterByName=parseList(self.getParameterValue('filterByName')))

    def help(self):
        return True, 'Returns a RGB Image.'
ALGORITHMS.append(ProbabilityAsClassColorRGB())

class ClassificationAssessClassificationPerformance(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Assess Classification performance'
        self.group = 'Classification'

        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('reference', 'Reference'))
        self.addOutput(OutputFile('report', 'HTML Report', ext='.html'))

    def processAlgorithm(self, progressBar):
        prediction = Classification(filename=self.getParameterValue('prediction'))
        reference = Classification(filename=self.getParameterValue('reference'))
        prediction.assessClassificationPerformance(classification=reference).report().saveHTML(filename=self.getOutputValue('report'), open=True)

    def help(self):
        return True, 'Returns an accuracy assessment report.'
ALGORITHMS.append(ClassificationAssessClassificationPerformance())

class RegressionAssessRegressionPerformance(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Assess Regression performance'
        self.group = 'Regression'

        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('reference', 'Reference'))
        self.addOutput(OutputFile('report', 'HTML Report', ext='.html'))

    def processAlgorithm(self, progressBar):
        prediction = Regression(filename=self.getParameterValue('prediction'))
        reference = Regression(filename=self.getParameterValue('reference'))
        prediction.assessRegressionPerformance(regression=reference).report().saveHTML(filename=self.getOutputValue('report'), open=True)

    def help(self):
        return True, 'Returns an accuracy assessment report.'
ALGORITHMS.append(RegressionAssessRegressionPerformance())

class ImageSampleByClassification(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Sample Image by Classification'
        self.group = 'Image'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('classification', 'Classification'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('probabilitySample', 'ProbabilitySample'))

    def processAlgorithm(self, progressBar):
        image = Image(filename=self.getParameterValue('image'))
        classification = Classification(filename=self.getParameterValue('classification'))
        mask = Mask(filename=self.getParameterValue('mask'))
        probabilitySample = image.sampleByClassification(classification=classification, mask=mask)
        probabilitySample.pickle(filename=self.getOutputValue('probabilitySample'))
        if self.getParameterValue('view'):
            probabilitySample.browse()


    def help(self):
        return True, 'Returns a ProbabilitySample.'
ALGORITHMS.append(ImageSampleByClassification())