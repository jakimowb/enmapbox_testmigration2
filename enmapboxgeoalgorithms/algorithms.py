import sys
from qgis.core import *
from hubflow.core import *
from enmapboxgeoalgorithms.provider import EnMAPAlgorithm, EnMAPAlgorithmParameterValueError, TESTALGORITHMS, \
    ALGORITHMS, Help, Link
from enmapboxgeoalgorithms.estimators import parseClassifiers, parseClusterers, parseRegressors, parseTransformers


class TestRaster(EnMAPAlgorithm):
    P_RASTER2 = 'raster2'
    P_RASTER3 = 'raster3'

    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Raster'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRaster(name=self.P_RASTER2, optional=True)
        import enmapboxtestdata
        self.addParameterRaster(name=self.P_RASTER3, defaultValue=enmapboxtestdata.enmap)

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        raster2 = self.getParameterRaster(name=self.P_RASTER2)
        raster3 = self.getParameterRaster(name=self.P_RASTER3)

        return {}


TESTALGORITHMS.append(TestRaster())


class TestVector(EnMAPAlgorithm):
    P_VECTOR2 = 'vector2'
    P_VECTOR3 = 'vector3'

    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Vector'

    def defineCharacteristics(self):
        self.addParameterVector()
        self.addParameterVector(name=self.P_VECTOR2, optional=True)
        import enmapboxtestdata
        self.addParameterVector(name=self.P_VECTOR3, defaultValue=enmapboxtestdata.landcover)

    def processAlgorithm_(self):
        vector = self.getParameterRaster()
        vector2 = self.getParameterRaster(name=self.P_VECTOR2)
        vector3 = self.getParameterRaster(name=self.P_VECTOR3)
        return {}


TESTALGORITHMS.append(TestVector())


class TestVectorClassification(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'VectorClassification'

    def defineCharacteristics(self):
        self.addParameterVectorClassification()

    def processAlgorithm_(self):
        vectorClassification = self.getParameterVectorClassification()
        self._progressBar.setText(repr(vectorClassification))
        return {}


TESTALGORITHMS.append(TestVectorClassification())


class TestClassDefinition(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'ClassDefinition'

    def defineCharacteristics(self):
        self.addParameterClassDefinition()

    def processAlgorithm_(self):
        classDefinition = self.getParameterClassDefinition()
        self._progressBar.setText(repr(classDefinition))
        return {}


TESTALGORITHMS.append(TestClassDefinition())


class TestField(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Field'

    def defineCharacteristics(self):
        self.addParameterVector()
        self.addParameterField()

    def processAlgorithm_(self):
        field = self.getParameterField()
        return {self.P_FIELD: field}


TESTALGORITHMS.append(TestField())


class TestString(EnMAPAlgorithm):
    P_STRING2 = 'string2'

    def group(self): return self.GROUP_TEST

    def displayName(self): return 'String'

    def defineCharacteristics(self):
        self.addParameterString()
        self.addParameterString(name=self.P_STRING2, optional=True)

    def processAlgorithm_(self):
        string1 = self.getParameterString()
        string2 = self.getParameterString(name=self.P_STRING2)
        self._progressBar.setText(string1)
        self._progressBar.setText(string2)
        return {}


TESTALGORITHMS.append(TestString())


class TestNumber(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Number'

    def defineCharacteristics(self):
        self.addParameterInteger()
        self.addParameterFloat()

    def processAlgorithm_(self):
        number1 = self.getParameterInteger()
        number2 = self.getParameterFloat()
        self._progressBar.setText(number1)
        self._progressBar.setText(number2)
        return {}


TESTALGORITHMS.append(TestNumber())


class TestOutputRaster(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Raster'

    def defineCharacteristics(self):
        self.addParameterOutputRaster()  # note that defaultValue and optional arguments are not working

    def processAlgorithm_(self):
        filename = self.getParameterOutputRaster()
        return {self.P_OUTPUT_RASTER: filename}


TESTALGORITHMS.append(TestOutputRaster())


class TestOutputReport(EnMAPAlgorithm):
    def group(self): return self.GROUP_TEST

    def displayName(self): return 'Report'

    def defineCharacteristics(self):
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        filename = self.getParameterOutputReport()
        report = Report(title='Test Report')
        report.saveHTML(filename)
        return {self.P_OUTPUT_REPORT: filename}


TESTALGORITHMS.append(TestOutputReport())


class ClassDefinitionFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassDefinition from Raster'

    def description(self):
        return "Creates a Class Definition string from a classification input raster for the usage in other EnMAP-Box algorithms (e.g. 'Classification from Vector'). See Log window for result."

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster(help='Specify raster with defined class definition, e.g. classification or class probability raster')

    def processAlgorithm_(self):

        raster = self.getParameterRaster()
        try:
            classDefinition = ClassDefinition.fromENVIClassification(raster)
        except:
            try:
                classDefinition = ClassDefinition.fromGDALMeta(raster)
            except:
                raise EnMAPAlgorithmParameterValueError('insufficient metadata to derive ClassDefinition')

        self._progressBar.setText('Class definition: {}'.format(repr(classDefinition)))
        return {}


ALGORITHMS.append(ClassDefinitionFromRaster())


class ClassificationFromProbability(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification from ClassProbability'

    def description(self):
        return 'Creates classification from class probability. Winner class is equal to the class with maximum class probability.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterProbability()
        self.addParameterMinCoverages()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        probability = self.getParameterProbability(minOverallCoverage=self.getParameterMinOverallCoverage(),
                                                   minWinnerCoverage=self.getParameterMinWinnerCoverage())
        filename = self.getParameterOutputClassification()
        Classification.fromClassification(filename=filename, classification=probability, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ClassificationFromProbability())


class ClassificationFromVectorClassification(EnMAPAlgorithm):
    def group(self): return self.GROUP_CREATE_RASTER

    def displayName(self): return 'Classification from Vector'

    def description(self):
        return 'Creates a classification from a vector field with class ids.'

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVectorClassification()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        classification = Classification.fromClassification(filename=self.getParameterOutputClassification(),
                                                           classification=self.getParameterVectorClassification(),
                                                           grid=self.getParameterGrid(),
                                                           progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: classification.filename}


ALGORITHMS.append(ClassificationFromVectorClassification())


class ClassificationPerformanceFromRaster(EnMAPAlgorithm):
    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def group(self): return self.GROUP_ACCURACY_ASSESSMENT

    def displayName(self): return 'Classification Performance'

    def description(self):
        return 'Assesses the performance of a classification.'

    def defineCharacteristics(self):
        self.addParameterClassification(self.P_PREDICTION, 'Prediction',
                                        help='Specify classification raster be evaluated')
        self.addParameterClassification(self.P_REFERENCE, 'Reference',
                                        help='Specify reference classification raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterClassification(self.P_PREDICTION)
        reference = self.getParameterClassification(self.P_REFERENCE)
        performance = ClassificationPerformance.fromRaster(prediction=prediction, reference=reference,
                                                           progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(ClassificationPerformanceFromRaster())


class ClassificationSampleFromENVISpectralLibrary(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassificationSample from ENVI Spectral Library'

    def description(self):
        return 'Derive ClassificationSample from ENVI Spectral Library.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    P_CLASSDEFINITIONPREFIX = 'classDefinitionPrefix'

    def defineCharacteristics(self):
        import enmapboxtestdata
        self.addParameterEnviSpeclib()
        self.addParameterString(self.P_CLASSDEFINITIONPREFIX, 'ClassDefinition prefix', optional=True,
                                help=Help("Class definition prefixes allow the selection of a specific class definition "
                                          "(i.e. 'class names' and 'class lookup') and class mapping (i.e. 'class spectra names') "
                                          "stored in the spectral library .hdr file).\n"
                                          "For example, inside the {}, the prefixes 'level 1' and 'level 2' are defined.",
                                          links=[Link(url='file:///'+enmapboxtestdata.speclib.replace('.sli', '.hdr'),
                                                      name='EnMAP-Box testdata spectral library')]))
        self.addParameterOutputClassificationSample()

    def processAlgorithm_(self):
        unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterEnviSpeclib())
        prefix = self.getParameterString(self.P_CLASSDEFINITIONPREFIX)
        if not prefix.endswith(' '):
            prefix = prefix + ' '
        for key in ['class names', 'class lookup', 'class spectra names']:
            key = prefix + key
            if not key in unsupervisedSample.metadata:
                raise EnMAPAlgorithmParameterValueError('missing metatdata: ' + key)
        names = unsupervisedSample.metadata[prefix + 'class names'][1:]
        colors = [int(v) for v in unsupervisedSample.metadata[prefix + 'class lookup'][3:]]
        classDefinition = ClassDefinition(names=names, colors=colors)
        classificationSample = unsupervisedSample.classifyByName(
            names=unsupervisedSample.metadata[prefix + 'class spectra names'],
            classDefinition=classDefinition)

        filename = self.getParameterOutputClassificationSample()
        classificationSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleFromENVISpectralLibrary())


class ClassificationSampleFromProbabilitySample(EnMAPAlgorithm):
    def group(self): return self.GROUP_CREATE_SAMPLE

    def displayName(self):
        return 'ClassificationSample from ClassProbabilitySample'

    def description(self):
        return 'Derive ClassificationSample from ClassProbabilitySample. Winner class is selected by the maximum probability decision.'

    def defineCharacteristics(self):
        self.addParameterProbabilitySample()
        self.addParameterMinCoverages()
        self.addParameterOutputClassificationSample()

    def processAlgorithm_(self):
        probabilitySample = self.getParameterProbabilitySample()
        filename = self.getParameterOutputClassificationSample()
        classificationSample = ClassificationSample.fromProbabilitySample(sample=probabilitySample,
                                                                          minOverallCoverage=self.getParameterMinOverallCoverage(),
                                                                          minWinnerCoverage=self.getParameterMinWinnerCoverage())
        classificationSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleFromProbabilitySample())


class ClassificationSampleFromRasterAndProbability(EnMAPAlgorithm):
    def group(self): return self.GROUP_CREATE_SAMPLE

    def displayName(self):
        return 'ClassificationSample from Raster and ClassProbability'

    def description(self):
        return 'Derives classification sample from raster and class probability raster.'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterProbability()
        self.addParameterMask()
        self.addParameterMinCoverages()
        self.addParameterOutputClassificationSample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        probability = self.getParameterProbability()
        mask = self.getParameterMask()
        minOverallCoverage = self.getParameterMinOverallCoverage()
        minWinnerCoverage = self.getParameterMinWinnerCoverage()
        filename = self.getParameterOutputClassificationSample()
        classificationSample = ClassificationSample.fromRasterAndProbability(raster=raster, probability=probability,
                                                                             grid=raster, mask=mask,
                                                                             minOverallCoverage=minOverallCoverage,
                                                                             minWinnerCoverage=minWinnerCoverage,
                                                                             progressBar=self._progressBar)
        classificationSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleFromRasterAndProbability())


class ClassificationSampleFromRasterAndVectorClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassificationSample from Raster and Vector'

    def description(self):
        return 'Derives classification sample from raster and vector.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterVectorClassification()
        self.addParameterMask()
        self.addParameterOutputClassificationSample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        classification = self.getParameterVectorClassification()
        mask = self.getParameterMask()
        classificationSample = ClassificationSample.fromRasterAndClassification(raster=raster,
                                                                                classification=classification,
                                                                                grid=raster, masks=mask,
                                                                                progressBar=self._progressBar)
        filename = self.getParameterOutputClassificationSample()
        classificationSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleFromRasterAndVectorClassification())


class ClassificationSampleSynthMix(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbabilitySample from synthetically mixed ClassificationSample'

    def description(self):
        return 'Derives a class probability sample by synthetically mixing (pure) spectra from a ClassificationSample.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    P_N = 'n'
    P_COMPLEXITY2LIKELIHOOD = 'complexity2Likelihoods'
    P_COMPLEXITY3LIKELIHOOD = 'complexity3Likelihoods'
    P_CLASSLIKELIHOODS = 'classLikelihoods'
    ENUM_CLASSLIKELIHOODS = ['proportional', 'equalized']

    def defineCharacteristics(self):
        self.addParameterClassificationSample()
        self.addParameterInteger(self.P_N, 'n', defaultValue=1000,
                                 help='Total number of samples to be generated.')
        self.addParameterFloat(self.P_COMPLEXITY2LIKELIHOOD, 'Likelihood for mixing complexity 2', defaultValue=1.0,
                               help='Specifies the probability of mixing spectra from 2 classes.')
        self.addParameterFloat(self.P_COMPLEXITY3LIKELIHOOD, 'Likelihood for mixing complexity 3', defaultValue=0.0,
                               help='Specifies the probability of mixing spectra from 3 classes.')
        self.addParameterEnum(self.P_CLASSLIKELIHOODS, 'Class likelihoods', options=self.ENUM_CLASSLIKELIHOODS,
                              defaultValue=0,
                              help='Specifies the likelihoods for drawing spectra from individual classes.\n'
                                   "In case of 'equalized', all classes have the same likelihhod to be drawn from.\n"
                                   "In case of 'proportional', class likelihoods scale with their sizes.")
        self.addParameterOutputProbabilitySample()

    def processAlgorithm_(self):
        classificationSample = self.getParameterClassificationSample()
        mixingComplexities = {2: self.getParameterFloat(self.P_COMPLEXITY2LIKELIHOOD),
                              3: self.getParameterFloat(self.P_COMPLEXITY3LIKELIHOOD)}
        classLikelihoods = self.ENUM_CLASSLIKELIHOODS[self.getParameterEnum(self.P_CLASSLIKELIHOODS)]
        probabilitySample = classificationSample.synthMix(mixingComplexities=mixingComplexities,
                                                          classLikelihoods=classLikelihoods,
                                                          n=self.getParameterInteger(self.P_N))
        filename = self.getParameterOutputProbabilitySample()
        probabilitySample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleSynthMix())


class ClassificationSampleFromRasterAndClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassificationSample from Raster and Classification'

    def description(self):
        return 'Derives a classification sample from raster (defines the grid) and classification.'

    def group(self):
        return 'Create Sample'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterMask()
        self.addParameterMinCoverages()
        self.addParameterOutputClassificationSample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        classification = self.getParameterClassification(minOverallCoverage=self.getParameterMinWinnerCoverage(),
                                                         minWinnerCoverage=self.getParameterMinWinnerCoverage())
        mask = self.getParameterMask()
        classificationSample = ClassificationSample.fromRasterAndClassification(raster, classification=classification,
                                                                                grid=raster, mask=mask,
                                                                                progressBar=self._progressBar)
        filename = self.getParameterOutputClassificationSample()
        classificationSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}


ALGORITHMS.append(ClassificationSampleFromRasterAndClassification())


class EstimatorFit(EnMAPAlgorithm):
    def __init__(self, name, code, helpAlg, helpCode):
        self._name = name
        self._code = code
        self._helpAlg = helpAlg
        self._helpCode = helpCode
        super().__init__()

    def description(self):
        return self._helpAlg

    def createInstance(self):
        return type(self)(name=self._name, code=self._code, helpAlg=self._helpAlg, helpCode=self._helpCode)

    def displayName(self):
        return 'Fit ' + self._name

    def code(self):
        return self._code

    P_CODE = 'code'

    def addParameterCode(self):
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True, help=self._helpCode)

    def sklEstimator(self):
        namespace = dict()
        code = self.getParameterString(self.P_CODE)
        exec(code, namespace)
        assert 'estimator' in namespace
        sklEstimator = namespace['estimator']
        return sklEstimator

    def processAlgorithm_(self):
        estimator = self.estimator(sklEstimator=self.sklEstimator())
        estimator.fit(sample=self.sample())
        filename = self.getParameterOutputEstimator()
        estimator.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_ESTIMATOR: filename}

    def sample(self):
        pass

    def estimator(self, sklEstimator):
        pass


class ClassifierFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLASSIFICATION

    def defineCharacteristics(self):
        self.addParameterClassificationSample()
        self.addParameterCode()
        self.addParameterOutputClassifier()

    def sample(self):
        return self.getParameterClassificationSample()

    def estimator(self, sklEstimator):
        return Classifier(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode) in parseClassifiers().items():
    ALGORITHMS.append(ClassifierFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode))


class ClustererFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLUSTERING

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterCode()
        self.addParameterOutputClusterer()

    def sample(self):
        return self.getParameterUnsupervisedSample()

    def estimator(self, sklEstimator):
        return Clusterer(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode) in parseClusterers().items():
    ALGORITHMS.append(ClustererFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode))


class ClassifierPredict(EnMAPAlgorithm):

    def displayName(self):
        return 'Predict Classification'

    def group(self):
        return self.GROUP_CLASSIFICATION

    def description(self):
        return 'Applies a classifier to a raster.'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be classified.')
        self.addParameterMask()
        self.addParameterClassifier()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        estimator = self.getParameterClassifier()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputClassification()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}

ALGORITHMS.append(ClassifierPredict())


class ClassifierPredictProbability(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict ClassProbability'

    def description(self):
        return 'Applies a classifier to a raster.'

    def group(self):
        return self.GROUP_CLASSIFICATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterClassifier()
        self.addParameterOutputRaster(description='Prediction')

    def processAlgorithm_(self):
        estimator = self.getParameterClassifier()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.predictProbability(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}

ALGORITHMS.append(ClassifierPredictProbability())


class ClustererPredict(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict Clustering'

    def description(self):
        return 'Applies a clusterer to a raster.'

    def group(self):
        return self.GROUP_CLUSTERING

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be clustered.')
        self.addParameterMask()
        self.addParameterClusterer()
        self.addParameterOutputClassification(description='Clustering')

    def processAlgorithm_(self):
        estimator = self.getParameterClusterer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputClassification()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(ClustererPredict())


class ClusteringPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Clustering Performance'

    def description(self):
        return 'Assesses the performance of a clusterer.'
    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterClassification(self.P_PREDICTION, 'Prediction',
                                        help='Specify clustering raster to be evaluated.')
        self.addParameterClassification(self.P_REFERENCE, 'Reference',
                                        help='Specify reference clustering raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterClassification(self.P_PREDICTION)
        reference = self.getParameterClassification(self.P_REFERENCE)
        performance = ClusteringPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(ClusteringPerformanceFromRaster())


class CreateAdditionalTestdata(EnMAPAlgorithm):
    def displayName(self):
        return 'Create additional Testdata'

    def description(self):
        return 'Based on the testdata additional datasets will be created using existing EnMAP-Box algorithms with predefined settings.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterOutputClassification(description='LandCover L2 Classification',
                                              help='Specify output path for LandCover L2 Classification.')
        self.addParameterOutputProbability(description='LandCover L2 ClassProbability',
                                           help='Specify output path for LandCover L2 ClassProbability.')
        self.addParameterOutputUnsupervisedSample()
        self.addParameterOutputClassificationSample()
        self.addParameterOutputProbabilitySample()
        self.addParameterOutputRegressionSample()

    def processAlgorithm_(self):
        import enmapboxtestdata
        enmap = Raster(filename=enmapboxtestdata.enmap)
        classDefinitionL2 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                            colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
        vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
                                                    nameAttribute=enmapboxtestdata.landcoverAttributes.Level_2,
                                                    classDefinition=classDefinitionL2,
                                                    minWinnerCoverage=0.5, minOverallCoverage=0.5,
                                                    oversampling=5)
        probability = Probability.fromClassification(filename=self.getParameterOutputProbability(),
                                                     classification=vectorClassification, grid=enmap)
        classification = Classification.fromClassification(filename=self.getParameterOutputClassification(),
                                                           classification=probability)
        psample = ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=probability, grid=enmap)
        csample = ClassificationSample.fromProbabilitySample(sample=psample)
        rsample = RegressionSample.fromProbabilitySample(sample=psample)
        usample = UnsupervisedSample.fromSample(sample=psample)

        usample.pickle(filename=self.getParameterOutputUnsupervisedSample(), progressBar=self._progressBar)
        csample.pickle(filename=self.getParameterOutputClassificationSample(), progressBar=self._progressBar)
        psample.pickle(filename=self.getParameterOutputProbabilitySample(), progressBar=self._progressBar)
        rsample.pickle(filename=self.getParameterOutputRegressionSample(), progressBar=self._progressBar)

        return {self.P_OUTPUT_CLASSIFICATION: classification.filename,
                self.P_OUTPUT_PROBABILITY: probability.filename,
                self.P_OUTPUT_UNSUPERVISED_SAMPLE: self.getParameterOutputUnsupervisedSample(),
                self.P_OUTPUT_CLASSIFICATION_SAMPLE: self.getParameterOutputClassificationSample(),
                self.P_OUTPUT_REGRESSION_SAMPLE: self.getParameterOutputRegressionSample(),
                self.P_OUTPUT_PROBABILITY_SAMPLE: self.getParameterOutputProbabilitySample()}


ALGORITHMS.append(CreateAdditionalTestdata())


class MaskBuildFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Build Mask from Raster'

    def description(self):
        return 'Builds a mask from a raster based on user defined values and value ranges.'

    def group(self):
        return self.GROUP_MASKING

    P_TRUEVALUES = 'trueValues'
    P_TRUERANGES = 'trueRanges'
    P_FALSEVALUES = 'falseValues'
    P_FALSERANGES = 'falseRanges'

    def defineCharacteristics(self):
        self.doc = 'Create a binary mask from given forground/background values and ranges.'
        self.addParameterRaster('raster', 'Raster')
        self.addParameterList(self.P_TRUEVALUES, 'Foreground values',
                              help='List of values that are mapped to True, e.g. [1, 2, 5].')
        self.addParameterList(self.P_TRUERANGES, 'Foreground ranges',
                              help='List of [min, max] ranges, e.g. [[1, 3], [5, 7]]. Values inside those ranges are mapped to True.')
        self.addParameterList(self.P_FALSEVALUES, 'Background values',
                              help='List of values that are mapped to False, e.g. [1, 2, 5].')
        self.addParameterList(self.P_FALSERANGES, 'Background ranges',
                              help='List of [min, max] ranges, e.g. [[-999, 0], [10, 255]]. Values inside those ranges are mapped to False.')
        self.addParameterOutputMask()

    def processAlgorithm_(self):
        filename = self.getParameterOutputMask()
        Mask.fromRaster(filename=filename,
                        raster=self.getParameterRaster(),
                        trueValues=self.getParameterList(self.P_TRUEVALUES),
                        trueRanges=self.getParameterList(self.P_TRUERANGES),
                        falseValues=self.getParameterList(self.P_FALSEVALUES),
                        falseRanges=self.getParameterList(self.P_FALSERANGES),
                        progressBar=self._progressBar)
        return {self.P_OUTPUT_MASK: filename}


ALGORITHMS.append(MaskBuildFromRaster())


class OpenTestdata_Toolbox(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return OpenTestdata_Modeler().displayName()

    def description(self):
        return OpenTestdata_Modeler().description()

    def defineCharacteristics(self):
        pass

    def processAlgorithm_(self):
        import enmapboxtestdata
        import qgis.utils

        qgis.utils.iface.addRasterLayer(enmapboxtestdata.enmap, basename(enmapboxtestdata.enmap), 'gdal')
        qgis.utils.iface.addRasterLayer(enmapboxtestdata.hymap, basename(enmapboxtestdata.hymap), 'gdal')
        qgis.utils.iface.addVectorLayer(enmapboxtestdata.landcover, None,
                                        'ogr')  # QGIS 3 bug when setting the name, e.g. basename(enmapboxtestdata.landcover)
        return {}

    def flags(self):
        return self.FlagHideFromModeler


ALGORITHMS.append(OpenTestdata_Toolbox())


class OpenTestdata_Modeler(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return 'Open Testdata'

    def description(self):
        return 'Opens testdata into current QGIS project (LandCov_BerlinUrbanGradient.shp, HighResolution_BerlinUrbanGradient.bsq, EnMAP_BerlinUrbanGradient.bsq, SpecLib_BerlinUrbanGradient.sli).'

    def name(self):
        return 'OpenTestdataForModel'

    def defineCharacteristics(self):
        self.addParameterOutputRaster('enmap', 'EnMAP (30m; 177 bands)',
                                      help='File name: EnMAP_BerlinUrbanGradient.bsq\n'
                                           'Simulated EnMAP data (based on 3.6m HyMap imagery) acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). It has a spectral resolution of 177 bands and a spatial resolution of 30m.')
        self.addParameterOutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)',
                                      help='File name: HighResolution_BerlinUrbanGradient.bsq\n'
                                           'HyMap image acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). This dataset was reduced to 4 bands (0.483, 0.558, 0.646 and 0.804 micrometers). The spatial resolution is 3.6m.')
        self.addParameterOutputVector('landcover', 'LandCover Layer',
                                      help='File name: LandCov_BerlinUrbanGradient.shp\n'
                                           'Polygon shapefile containing land cover information on two classification levels. Derived from very high resolution aerial imagery and cadastral datasets.\n'
                                           'Level 1 classes: Impervious; Other; Vegetation; Soil\n'
                                           'Level 2 classes: Roof; Low vegetation; Other; Pavement; Tree; Soil')
        self.addParameterOutputFile('speclib', 'ENVI Spectral Library',
                                    help='File name: SpecLib_BerlinUrbanGradient.sli\n'
                                         'Spectral library with 75 spectra (material level, level 2 and level 3 class information)')

    def processAlgorithm_(self):
        import enmapboxtestdata
        return {'enmap': enmapboxtestdata.enmap,
                'hymap': enmapboxtestdata.hymap,
                'landcover': enmapboxtestdata.landcover,
                'speclib': enmapboxtestdata.speclib}

    def flags(self):
        return self.FlagHideFromToolbox


ALGORITHMS.append(OpenTestdata_Modeler())


class ProbabilityAsClassColorRGB(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbability as RGB Raster'

    def description(self):
        return 'Creates a RGB representation from given class probabilities. ' \
               'The RGB color of a specific pixel is the weighted mean value of the original class colors, ' \
               'where the weights are given by the corresponding class propability.\n' \

    def group(self):
        return self.GROUP_POSTPROCESSING

    def defineCharacteristics(self):
        self.addParameterProbability()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        probability = self.getParameterProbability()
        filename = self.getParameterOutputRaster()
        probability.asClassColorRGBRaster(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(ProbabilityAsClassColorRGB())


class ProbabilityFromClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbability from Classification'

    def description(self):
        return 'Derive (binarized) class probabilities from a classification.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterClassification()
        self.addParameterOutputProbability()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()
        filename = self.getParameterOutputProbability()
        Probability.fromClassification(filename=filename, classification=classification, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY: filename}


ALGORITHMS.append(ProbabilityFromClassification())


class ProbabilityFromVectorClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbability from Vector'

    def description(self):
        return 'Derives class probability raster from a vector file with sufficient class information.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVectorClassification(minCoveragesDefaultValues=(0., 0.))
        self.addParameterOutputProbability()

    def processAlgorithm_(self):
        filename = self.getParameterOutputProbability()
        Probability.fromClassification(filename=filename,
                                       classification=self.getParameterVectorClassification(),
                                       grid=self.getParameterGrid(),
                                       oversampling=self.getParameterOversampling(),
                                       progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY: filename}


ALGORITHMS.append(ProbabilityFromVectorClassification())


class ProbabilityPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbability Performance'

    def description(self):
        return 'Assesses the performance of class probabilities in terms of AUC and ROC curves.'

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRaster(self.P_PREDICTION, 'Prediction',
                                help='Specify class probability raster to be evaluated.')
        self.addParameterRaster(self.P_REFERENCE, 'Reference',
                                help='Specify reference classification raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterProbability('prediction')
        reference = self.getParameterClassification('reference')
        performance = ProbabilityPerformance.fromRaster(prediction=prediction, reference=reference,
                                                        progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(ProbabilityPerformanceFromRaster())


class ProbabilitySampleFromClassificationSample(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbabilitySample from ClassificationSample'

    def description(self):
        return 'Derives a class probability sample from a classification sample.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterClassificationSample()
        self.addParameterOutputProbabilitySample()

    def processAlgorithm_(self):
        classificationSample = self.getParameterClassificationSample()
        probabilitySample = ProbabilitySample.fromClassificationSample(sample=classificationSample)
        filename = self.getParameterOutputProbabilitySample()
        probabilitySample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY_SAMPLE: filename}


ALGORITHMS.append(ProbabilitySampleFromClassificationSample())


class ProbabilitySampleFromRasterAndClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbabilitySample from Raster and Classification'

    def description(self):
        return 'Derives a class probability sample from raster and classification.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterMask()
        self.addParameterOutputProbabilitySample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        classification = self.getParameterClassification()
        mask = self.getParameterMask()
        probabilitySample = ProbabilitySample.fromRasterAndClassification(raster=raster, classification=classification,
                                                                          grid=raster, mask=mask,
                                                                          progressBar=self._progressBar)
        filename = self.getParameterOutputProbabilitySample()
        probabilitySample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY_SAMPLE: filename}


ALGORITHMS.append(ProbabilitySampleFromRasterAndClassification())


class ProbabilitySampleFromRasterAndProbability(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbabilitySample from Raster and ClassProbability'

    def description(self):
        return 'Derives class probability sample from raster and class probability.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterProbability()
        self.addParameterMask()
        self.addParameterOutputProbabilitySample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        probability = self.getParameterProbability()
        mask = self.getParameterMask()
        probabilitySample = ProbabilitySample.fromRasterAndProbability(raster=raster, probability=probability,
                                                                       grid=raster, mask=mask,
                                                                       progressBar=self._progressBar)
        filename = self.getParameterOutputProbabilitySample()
        probabilitySample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY_SAMPLE: filename}


ALGORITHMS.append(ProbabilitySampleFromRasterAndProbability())


class ProbabilitySampleFromRasterAndVector(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassProbabilitySample from Raster and Vector'

    def description(self):
        return 'Derives class probability sample from raster and vector.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterVectorClassification(minCoveragesDefaultValues=(0., 0.))
        self.addParameterMask()
        self.addParameterOutputProbabilitySample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        classification = self.getParameterVectorClassification()
        mask = self.getParameterMask()
        probabilitySample = ProbabilitySample.fromRasterAndClassification(raster=raster, classification=classification,
                                                                          grid=raster, mask=mask,
                                                                          progressBar=self._progressBar)
        filename = self.getParameterOutputProbabilitySample()
        probabilitySample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_PROBABILITY_SAMPLE: filename}


ALGORITHMS.append(ProbabilitySampleFromRasterAndVector())


class RasterApplyMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Apply Mask to Raster. Pixels that are masked out are set to the raster no data value.'

    def description(self):
        return ''

    def group(self):
        return self.GROUP_MASKING

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterOutputRaster(description='Masked Raster')

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        filename = self.getParameterOutputRaster()
        raster.applyMask(filename=filename, mask=self.getParameterMask(), progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(RasterApplyMask())


class RasterFromVector(EnMAPAlgorithm):
    def displayName(self):
        return 'Raster from Vector'

    def description(self):
        return Help(text='Converts vector to raster (using {}).',
                    links=[Link(url='http://gdal.org/python/osgeo.gdal-module.html#RasterizeOptions',
                                name='gdal rasterize')])

    def group(self):
        return self.GROUP_CREATE_RASTER

    P_INIT_VALUE = 'initValue'
    P_BURN_VALUE = 'burnValue'
    P_BURN_ATTRIBUTE = 'burnAttribute'
    P_ALL_TOUCHED = 'allTouched'
    P_FILTER_SQL = 'filterSQL'

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVector()
        self.addParameterFloat(self.P_INIT_VALUE, 'Init Value', defaultValue=0,
                               help='Pre-initialization value for the output raster before burning. Note that this value is not marked as the nodata value in the output raster.')
        self.addParameterFloat(self.P_BURN_VALUE, 'Burn Value', defaultValue=1,
                               help='Fixed value to burn into each pixel, which is covered by a feature (point, line or polygon).')
        self.addParameterField(self.P_BURN_ATTRIBUTE, 'Burn Attribute', type=QgsProcessingParameterField.Numeric,
                               parentLayerParameterName=self.P_VECTOR, optional=True,
                               help='Specify numeric vector field to use as burn values.')
        self.addParameterBoolean(self.P_ALL_TOUCHED, 'All touched', defaultValue=False,
                                 help='Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.')
        self.addParameterString(self.P_FILTER_SQL, 'Filter SQL', defaultValue='', optional=True,
                                help='Create SQL based feature selection, so that only selected features will be used for burning.\n'
                                     "Example: Level_2 = 'Roof' will only burn geometries where the Level_2 attribute value is equal to 'Roof', others will be ignored. This allows you to subset the vector dataset on-the-fly.")
        self.addParameterDataType()
        self.addParameterNoDataValue(optional=True)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        grid = self.getParameterGrid()
        filterSQL = self.getParameterString(self.P_FILTER_SQL)
        if filterSQL == '':
            filterSQL = None
        vector = self.getParameterVector(initValue=self.getParameterFloat(self.P_INIT_VALUE),
                                         burnValue=self.getParameterFloat(self.P_BURN_VALUE),
                                         burnAttribute=self.getParameterField(self.P_BURN_ATTRIBUTE),
                                         allTouched=self.getParameterBoolean(self.P_ALL_TOUCHED),
                                         filterSQL=filterSQL,
                                         dtype=self.getParameterDataType())

        filename = self.getParameterOutputRaster()
        Raster.fromVector(filename=filename, vector=vector, grid=grid, noDataValue=self.getParameterNoDataValue(),
                          progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(RasterFromVector())


class RegressionPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Regression Performance'

    def description(self):
        return 'Assesses the performance of a regression.'

    def group(self):
        return 'Accuracy Assessment'

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRegression(self.P_PREDICTION, 'Prediction',
                                    help='Specify regression raster to be evaluated.')
        self.addParameterRegression(self.P_REFERENCE, 'Reference',
                                    help='Specify reference regression raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterRegression(self.P_PREDICTION)
        reference = self.getParameterRegression(self.P_REFERENCE)
        performance = RegressionPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(RegressionPerformanceFromRaster())


class RegressionSampleFromRasterAndRegression(EnMAPAlgorithm):
    def displayName(self):
        return 'RegressionSample from Raster and Regression'

    def description(self):
        return 'Derives Regression sample from raster and regression.'

    def group(self):
        return 'Create Sample'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterMask()
        self.addParameterOutputRegressionSample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        regression = self.getParameterRegression()
        mask = self.getParameterMask()
        regressionSample = RegressionSample.fromRasterAndRegression(raster=raster, regression=regression,
                                                                    grid=raster, mask=mask,
                                                                    progressBar=self._progressBar)
        filename = self.getParameterOutputRegressionSample()
        regressionSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_REGRESSION_SAMPLE: filename}


ALGORITHMS.append(RegressionSampleFromRasterAndRegression())


class RegressorFit(EstimatorFit):
    def group(self):
        return self.GROUP_REGRESSION

    def defineCharacteristics(self):
        self.addParameterRegressionSample()
        self.addParameterCode()
        self.addParameterOutputRegressor()

    def sample(self):
        return self.getParameterRegressionSample()

    def estimator(self, sklEstimator):
        return Regressor(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode) in parseRegressors().items():
    ALGORITHMS.append(RegressorFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode))


class RegressorPredict(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict Regression'

    def group(self):
        return self.GROUP_REGRESSION

    def description(self):
        return 'Applies a regressor to an raster.'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be regressed.')
        self.addParameterMask()
        self.addParameterRegressor()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        estimator = self.getParameterRegressor()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRegression()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(RegressorPredict())


class TransformerFit(EstimatorFit):
    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterCode()
        self.addParameterOutputTransformer()

    def sample(self):
        return self.getParameterUnsupervisedSample()

    def estimator(self, sklEstimator):
        return Transformer(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode) in parseTransformers().items():
    ALGORITHMS.append(TransformerFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode))


class TransformerTransform(EnMAPAlgorithm):
    def displayName(self):
        return 'Transform Raster'

    def group(self):
        return self.GROUP_TRANSFORMATION

    def description(self):
        return 'Applies a transformer to an raster.'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be regressed.')
        self.addParameterMask()
        self.addParameterTransformer()
        self.addParameterOutputRaster(description='Transformation')

    def processAlgorithm_(self):
        estimator = self.getParameterTransformer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.transform(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(TransformerTransform())


class TransformerInverseTransform(EnMAPAlgorithm):
    def displayName(self):
        return 'InverseTransform Raster'

    def description(self):
        return "Performs an inverse transformation on an previously transformed raster (i.e. output of 'Transformation -> Transform Raster'). " \
               "Works only for transformers that have an 'inverse_transform(X)' method. See scikit-learn documentations."

    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterTransformer()
        self.addParameterOutputRaster(description='Inverse Transformation')

    def processAlgorithm_(self):
        estimator = self.getParameterTransformer()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.inverseTransform(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(TransformerInverseTransform())


class UnsupervisedSampleFromENVISpectralLibrary(EnMAPAlgorithm):
    def displayName(self):
        return 'UnsupervisedSample from ENVI Spectral Library'

    def description(self):
        return 'Derives unsupervised sample from ENVI spectral library.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterEnviSpeclib()
        self.addParameterOutputUnsupervisedSample()

    def processAlgorithm_(self):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterEnviSpeclib())
        filename = self.getParameterOutputUnsupervisedSample()
        sample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_UNSUPERVISED_SAMPLE: filename}


ALGORITHMS.append(UnsupervisedSampleFromENVISpectralLibrary())


class UnsupervisedSampleFromRasterAndMask(EnMAPAlgorithm):
    def displayName(self):
        return 'UnsupervisedSample from raster and mask'

    def description(self):
        return 'Derives unsupervised sample from raster and mask.'

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterOutputUnsupervisedSample()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        unsupervisedSample = UnsupervisedSample.fromRasterAndMask(raster=raster, grid=raster, mask=mask,
                                                                  progressBar=self._progressBar)
        filename = self.getParameterOutputUnsupervisedSample()
        unsupervisedSample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_UNSUPERVISED_SAMPLE: filename}


ALGORITHMS.append(UnsupervisedSampleFromRasterAndMask())


class UnsupervisedSampleScaleFeatures(EnMAPAlgorithm):
    def displayName(self):
        return 'Scale Sample Features'

    def description(self):
        return 'Scales the features of a sample by a user defined factor (can be used for matching datasets).\n'\
               'Use case: A sample from a spectral library should be used for classifying a raster. The spectral library sample has ' \
               'float surface reflectance values between 0 and 1 and the raster integer surface reflectances between 0 and 1000. In order ' \
               'to match the datasets, you can rescale the sample by a factor of 1000.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_SCALE_FACTOR = 'scaleFactor'

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterFloat(self.P_SCALE_FACTOR, 'Scale factor', defaultValue=1.,
                               help='Scale factor that is applied to all features.')
        self.addParameterOutputUnsupervisedSample()

    def processAlgorithm_(self):
        sample = self.getParameterUnsupervisedSample()
        sample.scaleFeaturesInplace(factor=self.getParameterFloat(self.P_SCALE_FACTOR))
        filename = self.getParameterOutputUnsupervisedSample()
        sample.pickle(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_UNSUPERVISED_SAMPLE: filename}


ALGORITHMS.append(UnsupervisedSampleScaleFeatures())


class VectorFromRandomPointsFromClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Random Points from Classification'

    def description(self):
        return 'Randomly samples a user defined amount of points/pixels from a classification raster and returns them as a vector dataset.'

    def group(self):
        return self.GROUP_RANDOM

    def defineCharacteristics(self):
        self.addParameterClassification()
        self.addParameterNumberOfPointsPerClass()
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()
        n = self.getParameterNumberOfPointsPerClass(classification=classification)
        filename = self.getParameterOutputVector()
        Vector.fromRandomPointsFromClassification(filename=filename, classification=classification, n=n,
                                                  progressBar=self._progressBar)
        return {self.P_OUTPUT_VECTOR: filename}


ALGORITHMS.append(VectorFromRandomPointsFromClassification())


class VectorFromRandomPointsFromMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Random Points from Mask'

    def description(self):
        return 'Randomly draws defined number of points from Mask and returns them as vector dataset.'

    def group(self):
        return self.GROUP_RANDOM

    P_N = 'n'

    def defineCharacteristics(self):
        self.addParameterMask()

        self.addParameterNumberOfPoints(defaultValue=100)
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        filename = self.getParameterOutputVector()
        Vector.fromRandomPointsFromMask(filename=filename,
                                        mask=self.getParameterMask(), n=self.getParameterNumberOfPoints())
        return {self.P_OUTPUT_VECTOR: filename}


ALGORITHMS.append(VectorFromRandomPointsFromMask())


class VectorUniqueValues(EnMAPAlgorithm):
    def displayName(self):
        return 'Unique Values from Vector Attribute '

    def description(self):
        return 'This algorithm returns unique values from vector attributes as a list, which is also usable as Class Definition in other algorithms. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterVector()
        self.addParameterField()

    def processAlgorithm_(self):
        vector = self.getParameterVector()
        values = vector.uniqueValues(attribute=self.getParameterField())
        self._progressBar.setText('Unique value: {}'.format(repr(values)))
        return {}


ALGORITHMS.append(VectorUniqueValues())


def generateRST():
    global ALGORITHMS

    groups = dict()

    for alg in ALGORITHMS:
        if alg.group() not in groups:
            groups[alg.group()] = dict()
        groups[alg.group()][alg.displayName()] = alg

    text = '=============\n'
    text += 'GeoAlgotithms\n'
    text += '=============\n\n'

    for gkey in sorted(groups.keys()):

        text += gkey + '\n'
        text += '=' * len(gkey) + '\n\n'

        for akey in groups[gkey]:
            alg = groups[gkey][akey]
            assert isinstance(alg, EnMAPAlgorithm)
            alg.defineCharacteristics()

            text += alg.displayName() + '\n'
            text += '-' * len(alg.displayName()) + '\n\n'

            if isinstance(alg.description(), str):
                text += alg.description() + '\n\n'
            if isinstance(alg.description(), Help):
                text += alg.description().rst() + '\n\n'

            for pd in alg.parameterDefinitions():
                assert isinstance(pd, QgsProcessingParameterDefinition)
                text += pd.description() + '\n'
                text += '~' * len(pd.description()) + '\n\n'
                if isinstance(pd._help, str):
                    text += pd._help + '\n\n'
                if isinstance(pd._help, Help):
                    text += pd._help.rst() + '\n\n'

            text += '<hr />'
        text += '<hr />'

    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'doc', 'source', 'ga.rst')
    with open(filename, mode='w') as f:
        f.write(text)
    print('created GeoAlgoritms RST file: ', filename)
