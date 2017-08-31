import numpy
from collections import OrderedDict
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *
from processing.core.outputs import *
from hubflow.types import *
from enmapboxgeoalgorithms.estimators import parseClassifiers, parseRegressors

def parseList(text, dtype=str):
    for c in "'[]{}()":
        text = text.replace(c,'')
    result = [dtype(value.strip()) for value in text.split(',') if value.strip() != '']
    if len(result) == 0:
        result = None
    return result

DTYPE = OrderedDict()
DTYPE['int16'] = numpy.int16, 'Integer 16 Bit'
DTYPE['int32'] = numpy.int32,'Integer 32 Bit'
DTYPE['int64'] = numpy.int64,'Integer 64 Bit'
DTYPE['uint8'] = numpy.uint8,'Unsigned Integer 8 Bit'
DTYPE['uint16'] = numpy.uint16,'Unsigned Integer 16 Bit'
DTYPE['uint32'] = numpy.uint32,'Unsigned Integer 32 Bit'
DTYPE['uint64'] = numpy.uint64,'Unsigned Integer 64 Bit'
DTYPE['float32'] = numpy.float32,'Single Precision Float 32 Bit'
DTYPE['float64'] = numpy.float64,'Double precision float 64 Bit'

class EnMAPGeoAlgorithm(GeoAlgorithm):
    pass

ALGORITHMS = list()

class ClassificationAssessClassificationPerformance(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classification Performance'
        self.group = 'Accuracy Assessment'

        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('reference', 'Reference'))
        self.addOutput(OutputFile('report', 'HTML Report', ext='.html'))

    def processAlgorithm(self, progressBar):
        prediction = Classification(filename=self.getParameterValue('prediction'))
        reference = Classification(filename=self.getParameterValue('reference'))
        prediction.assessClassificationPerformance(classification=reference, progressBar=progressBar).report().saveHTML(filename=self.getOutputValue('report'), open=True)

    def help(self):
        return True, 'Returns an accuracy assessment report.'
ALGORITHMS.append(ClassificationAssessClassificationPerformance())

class ClassificationSampleFromENVISpectralLibrary(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'ClassificationSample from ENVI Spectral Library'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addParameter(ParameterString('prefix', 'ClassDefinition prefix', default=''))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('classificationSample', 'ClassificationSample', ext='pkl'))

    def processAlgorithm(self, progressBar):
        unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
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

        classificationSample.pickle(filename=self.getOutputValue('classificationSample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns an ClassificationSample imported from an ENVI Spectral Library.'
ALGORITHMS.append(ClassificationSampleFromENVISpectralLibrary())

class ClassificationSampleSynthMix(EnMAPGeoAlgorithm):
    options = ['proportional', 'equalized']
    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from synthetically mixed ClassificationSample'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('classificationSample', 'ClassificationSample', optional=False))
        self.addParameter(ParameterNumber('n', 'n', default=1000))
        self.addParameter(ParameterNumber('complex2', 'Likelihood for mixing complexity 2', default=1.0))
        self.addParameter(ParameterNumber('complex3', 'Likelihood for mixing complexity 3', default=0.0))
        self.addParameter(ParameterSelection('option', 'Class likelihoods', options=self.options, default=0))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('probabilitySample', 'ClassProbabilitySample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        classificationSample = ClassificationSample.unpickle(filename=self.getParameterValue('classificationSample'))
        mixingComplexities = {2:self.getParameterValue('complex2'), 3:self.getParameterValue('complex3')}
        probabilitySample = classificationSample.synthMix(mixingComplexities=mixingComplexities,
                                                          classLikelihoods=self.options[self.getParameterValue('option')],
                                                          n=self.getParameterValue('n'))
        probabilitySample.pickle(filename=self.getOutputValue('probabilitySample'))
        if self.getParameterValue('view'):
            probabilitySample.browse()

    def help(self):
        return True, 'Returns a synthetically mixed ClassProbabilitySample.'
ALGORITHMS.append(ClassificationSampleSynthMix())

class EstimatorFit(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Fit '+TMP_NAME
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
            #sklEstimator = eval(self.getParameterValue('parameters'))
            exec self.getParameterValue('parameters')
            sklEstimator = eval('estimator')
            estimator = Regressor(sklEstimator=sklEstimator)
        elif self.group == CLASSIFIERS_GROUP:
            sample = ClassificationSample.unpickle(filename=self.getParameterValue('sample'))
            #sklEstimator = eval(self.getParameterValue('parameters'))
            exec self.getParameterValue('estimator')
            sklEstimator = eval('classifier')

            estimator = Classifier(sklEstimator=sklEstimator)
        else:
            assert 0
        estimator.fit(sample=sample, progressBar=progressBar)
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

class EstimatorPredict(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'Predict ' + TMP_GROUP
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
        estimator.predict(predictionFilename=self.getOutputValue('prediction'), image=image, mask=mask, progressBar=progressBar)

    def help(self):
        if self.group == REGRESSORS_GROUP:
            return True, 'Returns a Regression.'
        elif self.group == CLASSIFIERS_GROUP:
            return True, 'Returns a Classifier.'
        else:
            assert 0

CLASSIFIERS = parseClassifiers()
REGRESSORS = parseRegressors()
CLASSIFIERS_GA = dict()
REGRESSORS_GA = dict()
CLASSIFIERS_GROUP, REGRESSORS_GROUP = 'Classification', 'Regression'
for TMP_GROUP, TMP_ESTIMATORS in [(CLASSIFIERS_GROUP, CLASSIFIERS), (REGRESSORS_GROUP, REGRESSORS)]:
    for TMP_NAME, TMP_ESTIMATOR in TMP_ESTIMATORS.items():
        ALGORITHMS.append(EstimatorFit())
        if TMP_GROUP==CLASSIFIERS_GROUP: CLASSIFIERS_GA[TMP_NAME] = ALGORITHMS[-1]
        if TMP_GROUP==REGRESSORS_GROUP: REGRESSORS_GA[TMP_NAME] = ALGORITHMS[-1]
    ALGORITHMS.append(EstimatorPredict())

class ImageSampleByClassification(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'ClassificationSample from Image'
        self.group = 'Create Sample'
        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('classification', 'Classification'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('minWinnerCoverage', 'Minimal winner class coverage', minValue=0., maxValue=1., default=0.5))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('classificationSample', 'ClassificationSample'))

    def processAlgorithm(self, progressBar):
        image = Image(filename=self.getParameterValue('image'))
        classification = Classification(filename=self.getParameterValue('classification'))
        mask = Mask(filename=self.getParameterValue('mask'))
        probabilitySample = image.sampleByClassification(classification=classification, mask=mask, progressBar=progressBar)
        classificationSample = probabilitySample.classifyByProbability(minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                   minWinnerCoverage=self.getParameterValue('minWinnerCoverage'),
                                                   progressBar=progressBar)
        classificationSample.pickle(filename=self.getOutputValue('classificationSample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns a ClassificationSample.'
ALGORITHMS.append(ImageSampleByClassification())

class OpenTestdata(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Open Testdata (small dataset)'
        self.group = 'Auxilliary'
        self.addOutput(OutputRaster('enmap', 'EnMAP (30m; 177 bands)'))
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

class OpenTestdataRaw(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Open Testdata (small dataset with bad bands)'
        self.group = 'Auxilliary'
        self.addOutput(OutputRaster('enmap', 'EnMAP (30m; 244 bands)'))
        self.addOutput(OutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)'))
        self.addOutput(OutputVector('landcover', 'LandCover Layer'))
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm(self, progress):

        import enmapboxtestdata_raw
        self.setOutputValue('enmap', enmapboxtestdata_raw.enmap)
        self.setOutputValue('hymap', enmapboxtestdata_raw.hymap)
        self.setOutputValue('landcover', enmapboxtestdata_raw.landcover)
        self.setOutputValue('speclib', enmapboxtestdata_raw.speclib)

    def help(self):
        return True, 'Open EnMAP-Box Testdata'
ALGORITHMS.append(OpenTestdataRaw())

class OpenTestdataFull(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Open Testdata (full dataset)'
        self.group = 'Auxilliary'
        self.addOutput(OutputRaster('enmap', 'EnMAP (30m; 177 bands)'))
        self.addOutput(OutputVector('landcover', 'LandCover Layer'))
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm(self, progress):

        import enmapboxtestdata_full
        self.setOutputValue('enmap', enmapboxtestdata_full.enmap)
        self.setOutputValue('landcover', enmapboxtestdata_full.landcover)
        self.setOutputValue('speclib', enmapboxtestdata_full.speclib)

    def help(self):
        return True, 'Open EnMAP-Box Testdata'
ALGORITHMS.append(OpenTestdataFull())


class ProbabilityAsClassColorRGB(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'ClassProbability as RGB Image'
        self.group = 'Post-Processing'

        self.addParameter(ParameterRaster('probability', 'ClassProbability'))
        self.addParameter(ParameterString('filterById', 'Filter classes by id', optional=True))
        self.addParameter(ParameterString('filterByName', 'Filter classes by names', optional=True))
        self.addOutput(OutputRaster('image', 'RGB Image'))

    def processAlgorithm(self, progressBar):

        probability = Probability(filename=self.getParameterValue('probability'))
        probability.asClassColorRGBImage(imageFilename=self.getOutputValue('image'),
                                         filterById=parseList(self.getParameterValue('filterById'), dtype=int),
                                         filterByName=parseList(self.getParameterValue('filterByName')),
                                         progressBar=progressBar)

    def help(self):
        return True, 'Returns a RGB Image.'
ALGORITHMS.append(ProbabilityAsClassColorRGB())

class ProbabilitySampleClassify(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'ClassificationSample from ClassProbabilitySample'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('probabilitySample', 'ClassProbabilitySample', optional=False))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('minWinnerCoverage', 'Minimal winner class coverage', minValue=0., maxValue=1., default=0.5))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('classificationSample', 'ClassificationSample', ext='pkl'))

    def processAlgorithm(self, progressBar):
        probabilitySample = ProbabilitySample.unpickle(filename=self.getParameterValue('probabilitySample'))
        classificationSample = probabilitySample.classifyByProbability(minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                                       minWinnerCoverage=self.getParameterValue('minWinnerCoverage'))
        classificationSample.pickle(filename=self.getOutputValue('classificationSample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns a ClassificationSample.'
ALGORITHMS.append(ProbabilitySampleClassify())

class ProbabilitySampleSubsetClassesByClassName(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Subset ClassProbabilitySample (by Class)'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('probabilitySample', 'ClassProbabilitySample', optional=False))
        self.addParameter(ParameterString('names', 'Class names', default=''))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('probabilitySample2', 'ClassProbabilitySample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        probabilitySample = ProbabilitySample.unpickle(filename=self.getParameterValue('probabilitySample'))
        names = parseList(self.getParameterValue('names'))
        probabilitySample = probabilitySample.subsetClassesByName(names=names)
        probabilitySample.pickle(filename=self.getOutputValue('probabilitySample2'))
        if self.getParameterValue('view'):
            probabilitySample.browse()


    def help(self):
        return True, 'Returns a ClassProbabilitySample with subsetted classes.'
ALGORITHMS.append(ProbabilitySampleSubsetClassesByClassName())

class RegressionAssessRegressionPerformance(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Regression Performance'
        self.group = 'Accuracy Assessment'

        self.addParameter(ParameterRaster('prediction', 'Prediction'))
        self.addParameter(ParameterRaster('reference', 'Reference'))
        self.addOutput(OutputFile('report', 'HTML Report', ext='.html'))

    def processAlgorithm(self, progressBar):
        prediction = Regression(filename=self.getParameterValue('prediction'))
        reference = Regression(filename=self.getParameterValue('reference'))
        prediction.assessRegressionPerformance(regression=reference, progressBar=progressBar).report().saveHTML(filename=self.getOutputValue('report'), open=True)

    def help(self):
        return True, 'Returns an accuracy assessment report.'
ALGORITHMS.append(RegressionAssessRegressionPerformance())

class UnsupervisedSampleFromENVISpectralLibrary(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'UnsupervisedSample from ENVI Spectral Library'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('unsupervisedSample', 'UnsupervisedSample', ext='pkl'))

    def processAlgorithm(self, progressBar):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
        sample.pickle(filename=self.getOutputValue('unsupervisedSample'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns an UnsupervisedSample imported from an ENVI Spectral Library file.'
ALGORITHMS.append(UnsupervisedSampleFromENVISpectralLibrary())

class UnsupervisedSampleScaleFeatures(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Scale Sample Features'
        self.group = 'Auxilliary'

        self.addParameter(ParameterFile('unsupervisedSample', 'Sample', optional=False))
        self.addParameter(ParameterNumber('factor', 'Scale factor', default=1.))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('unsupervisedSample2', 'Scaled Sample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        sample = UnsupervisedSample.unpickle(filename=self.getParameterValue('unsupervisedSample'))
        sample.scaleFeaturesInplace(factor=self.getParameterValue('factor'))
        sample.pickle(filename=self.getOutputValue('unsupervisedSample2'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns a Sample with scaled features.'
ALGORITHMS.append(UnsupervisedSampleScaleFeatures())

class VectorRasterize(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Rasterize Vector'
        self.group = 'Vector'

        self.addParameter(ParameterRaster('image', 'Image (defining the PixelGrid)'))
        self.addParameter(ParameterVector('vector', 'Vector'))
        self.addParameter(ParameterNumber('initValue', 'Init Value', default=0))
        self.addParameter(ParameterNumber('burnValue', 'Burn Value', default=1))
        self.addParameter(ParameterTableField('burnAttribute', 'Burn Attribute', datatype=ParameterTableField.DATA_TYPE_NUMBER, parent='vector', optional=True))
        self.addParameter(ParameterBoolean('allTouched', 'All touched', default=False))
        self.addParameter(ParameterString('filterSQL', 'Filter SQL', default='', optional=True))
        self.addParameter(ParameterSelection('dtype', 'Data Type', options=DTYPE.keys(), default=DTYPE.keys().index('uint8')))
        self.addOutput(OutputRaster('image2', 'Image'))

    def processAlgorithm(self, progressBar):

        image = Image(filename=self.getParameterValue('image'))
        vector = Vector(filename=self.getParameterValue('vector'),
                        initValue=self.getParameterValue('initValue'),
                        burnValue=self.getParameterValue('burnValue'),
                        burnAttribute=self.getParameterValue('burnAttribute'),
                        allTouched=self.getParameterValue('allTouched'),
                        filterSQL=self.getParameterValue('filterSQL') if self.getParameterValue('filterSQL')!='' else None,
                        dtype=DTYPE.values()[self.getParameterValue('dtype')][0])
        vector.rasterize(imageFilename=self.getOutputValue('image2'), grid=image.pixelGrid, progressBar=progressBar)

    def help(self):
        return True, 'Returns an Image.'
ALGORITHMS.append(VectorRasterize())

class VectorClassificationRasterizeAsClassification(EnMAPGeoAlgorithm):

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
                                                       grid=image.pixelGrid, oversampling=self.getParameterValue('oversampling'),
                                                       progressBar=progressBar)

    def help(self):
        return True, 'Returns a Classification.'
ALGORITHMS.append(VectorClassificationRasterizeAsClassification())

class VectorClassificationRasterizeAsProbability(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Rasterize Vector as ClassProbability'
        self.group = 'Vector'

        self.addParameter(ParameterRaster('image', 'Image (defining the PixelGrid)'))
        self.addParameter(ParameterVector('vector', 'Vector'))
        self.addParameter(ParameterTableField('idAttribute', 'Class id attribute', datatype=ParameterTableField.DATA_TYPE_NUMBER,
                                              parent='vector'))
        self.addParameter(ParameterString('names', 'Class names', optional=True))
        self.addParameter(ParameterString('lookup', 'Class colors', optional=True))
        self.addParameter(ParameterNumber('minOverallCoverage', 'Minimal overall coverage', minValue=0., maxValue=1., default=1.))
        self.addParameter(ParameterNumber('oversampling', 'Oversampling factor', minValue=1, maxValue=10, default=10))
        self.addOutput(OutputRaster('probability', 'ClassProbability'))

    def processAlgorithm(self, progressBar):

        classes = None
        names = parseList(self.getParameterValue('names'))
        if names is None:
            classes = numpy.max(Vector(filename=self.getParameterValue('vector')).uniqueValues(attribute=self.getParameterValue('idAttribute')))
        lookup = parseList(self.getParameterValue('lookup'), dtype=int)
        classDefinition = ClassDefinition(classes=classes, names=names, lookup=lookup)


        image = Image(filename=self.getParameterValue('image'))
        vectorClassification = VectorClassification(filename=self.getParameterValue('vector'),
                                                    idAttribute=self.getParameterValue('idAttribute'),
                                                    minOverallCoverage=self.getParameterValue('minOverallCoverage'),
                                                    classDefinition=classDefinition)
        vectorClassification.rasterizeAsProbability(probabilityFilename=self.getOutputValue('probability'),
                                                    grid=image.pixelGrid, oversampling=self.getParameterValue('oversampling'),
                                                    progressBar=progressBar)

    def help(self):
        return True, 'Returns a ClassProbability.'
ALGORITHMS.append(VectorClassificationRasterizeAsProbability())

# todo
#Create Sample
#  RegressionSample from Image
#  UnsupervisedSample from Image#
#  Subset ClassificationSample (by Class)
#  Subset RegressionSample (by Output)
