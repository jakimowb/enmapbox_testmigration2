import sys
from qgis.core import *
from hubflow.core import *
from enmapboxgeoalgorithms.provider import EnMAPAlgorithm, EnMAPAlgorithmParameterValueError, TESTALGORITHMS, \
    ALGORITHMS
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

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()

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
        return 'Classification from Probability'

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

    def defineCharacteristics(self):
        self.addParameterClassification(self.P_PREDICTION, 'Prediction')
        self.addParameterClassification(self.P_REFERENCE, 'Reference')
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

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    P_CLASSDEFINITIONPREFIX = 'classDefinitionPrefix'

    def defineCharacteristics(self):
        self.addParameterEnviSpeclib()
        self.addParameterString(self.P_CLASSDEFINITIONPREFIX, 'ClassDefinition prefix')
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

    def displayName(self): return 'ClassificationSample from ClassProbabilitySample'

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

    def displayName(self): return 'ClassificationSample from Raster and Probability'

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

    def group(self):
        return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterVectorClassification()
        self.addParameterMask()
        #self.addParameterNumberOfPointsPerClass(optional=True)
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
    def displayName(self): return 'ClassProbabilitySample from synthetically mixed ClassificationSample'

    def group(self): return self.GROUP_CREATE_SAMPLE

    P_N = 'n'
    P_COMPLEXITY2LIKELIHOOD = 'complexity2Likelihoods'
    P_COMPLEXITY3LIKELIHOOD = 'complexity3Likelihoods'
    P_CLASSLIKELIHOODS = 'classLikelihoods'
    ENUM_CLASSLIKELIHOODS = ['proportional', 'equalized']

    def defineCharacteristics(self):
        self.addParameterClassificationSample()
        self.addParameterInteger(self.P_N, 'n', defaultValue=1000)
        self.addParameterFloat(self.P_COMPLEXITY2LIKELIHOOD, 'Likelihood for mixing complexity 2', defaultValue=1.0)
        self.addParameterFloat(self.P_COMPLEXITY3LIKELIHOOD, 'Likelihood for mixing complexity 3', defaultValue=0.0)
        self.addParameterEnum(self.P_CLASSLIKELIHOODS, 'Class likelihoods', options=self.ENUM_CLASSLIKELIHOODS,
                              defaultValue=0)
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
    def displayName(self): return 'ClassificationSample from Raster and Classification'

    def group(self): return 'Create Sample'

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
    def __init__(self, name, code):
        self._name = name
        self._code = code
        super().__init__()

    def createInstance(self):
        return type(self)(name=self._name, code=self._code)

    def displayName(self):
        return 'Fit ' + self._name

    def code(self):
        return self._code

    P_CODE = 'code'

    def addParameterCode(self):
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True)

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
        self.addParameterOutputEstimator()

    def sample(self):
        return self.getParameterClassificationSample()

    def estimator(self, sklEstimator):
        return Classifier(sklEstimator=sklEstimator)


for name, code in parseClassifiers().items():
    ALGORITHMS.append(ClassifierFit(name=name, code=code))


class ClustererFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLUSTERING

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterCode()
        self.addParameterOutputEstimator()

    def sample(self):
        return self.getParameterUnsupervisedSample()

    def estimator(self, sklEstimator):
        return Clusterer(sklEstimator=sklEstimator)


for name, code in parseClusterers().items():
    ALGORITHMS.append(ClustererFit(name=name, code=code))


class EstimatorPredict(EnMAPAlgorithm):
    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addEstimator()
        self.addParameterOutputRaster(description='Prediction')

    def processAlgorithm_(self):
        estimator = self.getEstimator()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputRaster()
        estimator.predict(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}

    def addEstimator(self):
        assert 0

    def getEstimator(self):
        assert 0


class ClassifierPredict(EstimatorPredict):
    def displayName(self):
        return 'Predict Classification'

    def group(self):
        return self.GROUP_CLASSIFICATION

    def addEstimator(self):
        self.addParameterClassifier()

    def getEstimator(self):
        return self.getParameterClassifier()


ALGORITHMS.append(ClassifierPredict())


class ClassifierPredictProbability(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict ClassProbability'

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


class ClustererPredict(EstimatorPredict):
    def displayName(self):
        return 'Predict Clustering'

    def group(self):
        return self.GROUP_CLUSTERING

    def addEstimator(self):
        self.addParameterClusterer()

    def getEstimator(self):
        return self.getParameterClusterer()


ALGORITHMS.append(ClustererPredict())


class ClusteringPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Clustering Performance'

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterClassification(self.P_PREDICTION, 'Prediction')
        self.addParameterClassification(self.P_REFERENCE, 'Reference')
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

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterOutputClassification(description='LandCover L2 Classification')
        self.addParameterOutputProbability(description='LandCover L2 ClassProbability')
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
        return 'Open Testdata'

    def defineCharacteristics(self):
        pass

    def processAlgorithm_(self):
        import enmapboxtestdata
        import qgis.utils

        qgis.utils.iface.addRasterLayer(enmapboxtestdata.enmap, basename(enmapboxtestdata.enmap), 'gdal')
        qgis.utils.iface.addRasterLayer(enmapboxtestdata.hymap, basename(enmapboxtestdata.hymap), 'gdal')
        qgis.utils.iface.addVectorLayer(enmapboxtestdata.landcover, None, 'ogr') # QGIS 3 bug when setting the name, e.g. basename(enmapboxtestdata.landcover)
        return {}

    def flags(self):
        return self.FlagHideFromModeler

ALGORITHMS.append(OpenTestdata_Toolbox())


class OpenTestdata_Modeler(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return 'Open Testdata'

    def name(self):
        return 'OpenTestdataForModel'

    def defineCharacteristics(self):
        # self.doc = 'Open EnMAP-Box Testdata'
        self.addParameterOutputRaster('enmap', 'EnMAP (30m; 177 bands)')
        self.addParameterOutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)')
        self.addParameterOutputVector('landcover', 'LandCover Layer')
        self.addParameterOutputFile('speclib', 'ENVI Spectral Library')

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

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRaster(self.P_PREDICTION, 'Prediction (Probabiliy)')
        self.addParameterRaster(self.P_REFERENCE, 'Reference (Classification)')
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
        return 'Apply Mask to Raster'

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
        self.addParameterFloat(self.P_INIT_VALUE, 'Init Value', defaultValue=0)
        self.addParameterFloat(self.P_BURN_VALUE, 'Burn Value', defaultValue=1)
        self.addParameterField(self.P_BURN_ATTRIBUTE, 'Burn Attribute', type=QgsProcessingParameterField.Numeric,
                               parentLayerParameterName=self.P_VECTOR, optional=True)
        self.addParameterBoolean(self.P_ALL_TOUCHED, 'All touched', defaultValue=False)
        self.addParameterString(self.P_FILTER_SQL, 'Filter SQL', defaultValue='', optional=True)
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

    def group(self):
        return 'Accuracy Assessment'

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRegression(self.P_PREDICTION, 'Prediction')
        self.addParameterRegression(self.P_REFERENCE, 'Reference')
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
        self.addParameterOutputEstimator()

    def sample(self):
        return self.getParameterRegressionSample()

    def estimator(self, sklEstimator):
        return Regressor(sklEstimator=sklEstimator)


for name, code in parseRegressors().items():
    ALGORITHMS.append(RegressorFit(name=name, code=code))


class RegressorPredict(EstimatorPredict):
    def displayName(self):
        return 'Predict Regression'

    def group(self):
        return self.GROUP_REGRESSION

    def addEstimator(self):
        self.addParameterRegressor()

    def getEstimator(self):
        return self.getParameterRegressor()


ALGORITHMS.append(RegressorPredict())


class TransformerFit(EstimatorFit):
    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterCode()
        self.addParameterOutputEstimator()

    def sample(self):
        return self.getParameterUnsupervisedSample()

    def estimator(self, sklEstimator):
        return Transformer(sklEstimator=sklEstimator)


for name, code in parseTransformers().items():
    ALGORITHMS.append(TransformerFit(name=name, code=code))


class TransformerTransform(EnMAPAlgorithm):
    def displayName(self):
        return 'Transform Raster'

    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterRaster()
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
        return 'UnsupervisedSample from Raster and Mask'

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

    def group(self):
        return self.GROUP_AUXILLIARY

    P_SCALE_FACTOR = 'scaleFactor'

    def defineCharacteristics(self):
        self.addParameterUnsupervisedSample()
        self.addParameterFloat(self.P_SCALE_FACTOR, 'Scale factor', defaultValue=1.)
        self.addParameterOutputUnsupervisedSample(description='Scaled Sample')

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

    def group(self):
        return self.GROUP_RANDOM

    def defineCharacteristics(self):
        self.addParameterClassification()
        self.addParameterNumberOfPointsPerClass()
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()
        n = self.getParameterNumberOfPointsPerClass(classDefinition=classification.classDefinition)
        filename = self.getParameterOutputVector()
        Vector.fromRandomPointsFromClassification(filename=filename, classification=classification, n=n,
                                                  progressBar=self._progressBar)
        return {self.P_OUTPUT_VECTOR: filename}


ALGORITHMS.append(VectorFromRandomPointsFromClassification())


class VectorFromRandomPointsFromMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Random Points from Mask'

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

    text =  '=============\n'
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

            text += alg.description() + '\n\n'

            for pd in alg.parameterDefinitions():
                assert isinstance(pd, QgsProcessingParameterDefinition)
                text += pd.description() + '\n'
                text += '~' * len(pd.description()) + '\n\n'
                text += pd._helpString + '\n\n'

    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'doc', 'source', 'ga.rst')
    with open(filename, mode='w') as f:
        f.write(text)
    print('created GeoAlgoritms RST file: ', filename)