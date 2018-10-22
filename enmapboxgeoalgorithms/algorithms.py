import sys
from qgis.core import *
from hubflow.core import *
from enmapboxgeoalgorithms.provider import EnMAPAlgorithm, EnMAPAlgorithmParameterValueError, TESTALGORITHMS, \
    ALGORITHMS, Help, Link
from enmapboxgeoalgorithms.estimators import parseClassifiers, parseClusterers, parseRegressors, parseTransformers
from enmapboxgeoalgorithms.filters.convolution import parseSpatialKernel, parseSpectralKernel
from enmapboxgeoalgorithms.filters.morphology import parseMorphology
from enmapboxgeoalgorithms.filters.other import parseOtherFilter


class ApplierDefaultsSetup(EnMAPAlgorithm):
    def displayName(self):
        return 'HUB Datacube Applier Settings'

    def description(self):
        return 'Various settings used inside an applier processing chain.'

    def group(self):
        return self.GROUP_OPTIONS

    P_X_BLOCK_SIZE = 'xblocksize'
    P_Y_BLOCK_SIZE = 'yblocksize'
    P_NWORKER = 'nworker'

    def defineCharacteristics(self):
        from hubdc.applier import ApplierDefaults
        self.addParameterInteger(name=self.P_X_BLOCK_SIZE, description='Tiled-Processing Block X Size',
                                 defaultValue=ApplierDefaults.blockSize.x(), minValue=1,
                                 help='Specify block x size for tile-based processing.')

        self.addParameterInteger(name=self.P_Y_BLOCK_SIZE, description='Tiled-Processing Block Y Size',
                                 defaultValue=ApplierDefaults.blockSize.y(), minValue=1,
                                 help='Specify block y size for tile-based processing.')

        nworker = 1 if ApplierDefaults.nworker is None else ApplierDefaults.nworker
        self.addParameterInteger(name=self.P_NWORKER, description='Number of Multiprocessing Worker',
                                 defaultValue=nworker, minValue=1,
                                 help='Specify number of multiprocessing worker.')

    def processAlgorithm_(self):
        from hubdc.applier import ApplierDefaults
        ApplierDefaults.blockSize = Size(x=self.getParameterInteger(name=self.P_X_BLOCK_SIZE),
                                         y=self.getParameterInteger(name=self.P_Y_BLOCK_SIZE))
        ApplierDefaults.nworker = self.getParameterInteger(name=self.P_NWORKER)
        return {}

    def postProcess(self, context, feedback):
        from hubdc.applier import ApplierDefaults
        ApplierDefaults.blockSize = Size(x=self.getParameterInteger(name=self.P_X_BLOCK_SIZE),
                                         y=self.getParameterInteger(name=self.P_Y_BLOCK_SIZE))
        ApplierDefaults.nworker = self.getParameterInteger(name=self.P_NWORKER)
        return {}


#ALGORITHMS.append(ApplierDefaultsSetup())

class ClassDefinitionFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'ClassDefinition from Raster'

    def description(self):
        return "Creates a Class Definition string from a classification input raster for the usage in other EnMAP-Box algorithms (e.g. 'Classification from Vector'). See Log window for result."

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster(
            help='Specify raster with defined class definition, e.g. classification or class fraction raster')

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


class ClassificationFromFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification from Fraction'

    def description(self):
        return 'Creates classification from class fraction. Winner class is equal to the class with maximum class fraction.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterFraction()
        self.addParameterMinCoverages()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        fraction = self.getParameterFraction(minOverallCoverage=self.getParameterMinOverallCoverage(),
                                                minDominantCoverage=self.getParameterMinDominantCoverage())
        filename = self.getParameterOutputClassification()
        Classification.fromClassification(filename=filename, classification=fraction, progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ClassificationFromFraction())


class ClassificationStatistics(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification Statistics'

    def description(self):
        return 'This algorithm returns class count statistics. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterClassification()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()
        values = classification.statistics()
        for name, n in zip(classification.classDefinition().names(), values):
            self._progressBar.setText('{}: {}'.format(name, n))
        return {}

ALGORITHMS.append(ClassificationStatistics())


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
        return {self.P_OUTPUT_CLASSIFICATION: classification.filename()}


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
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')

        performance = ClassificationPerformance.fromRaster(prediction=prediction, reference=reference,
                                                           progressBar=self._progressBar,
                                                           grid=prediction.grid())
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(ClassificationPerformanceFromRaster())


class SynthMix(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Sample from synthetically mixed Endmembers'

    def description(self):
        return 'Derives a class fraction sample by synthetically mixing (pure) spectra from a classification sample.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    P_N = 'n'
    P_COMPLEXITY2LIKELIHOOD = 'complexity2Likelihoods'
    P_COMPLEXITY3LIKELIHOOD = 'complexity3Likelihoods'
    P_CLASSLIKELIHOODS = 'classLikelihoods'
    ENUM_CLASSLIKELIHOODS = ['proportional', 'equalized']

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterMask()

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
        self.addParameterOutputRaster()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        classificationSample = ClassificationSample(raster=self.getParameterRaster(),
                                                    classification=self.getParameterClassification(),
                                                    mask=self.getParameterMask())
        mixingComplexities = {2: self.getParameterFloat(self.P_COMPLEXITY2LIKELIHOOD),
                              3: self.getParameterFloat(self.P_COMPLEXITY3LIKELIHOOD)}
        classLikelihoods = self.ENUM_CLASSLIKELIHOODS[self.getParameterEnum(self.P_CLASSLIKELIHOODS)]
        fractionSample = classificationSample.synthMix(filenameFeatures=self.getParameterOutputRaster(),
                                                       filenameFractions=self.getParameterOutputFraction(),
                                                       mixingComplexities=mixingComplexities,
                                                       classLikelihoods=classLikelihoods,
                                                       n=self.getParameterInteger(self.P_N))
        return {self.P_OUTPUT_RASTER: fractionSample.raster().filename(),
                self.P_OUTPUT_FRACTION: fractionSample.fraction().filename()}


ALGORITHMS.append(SynthMix())


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
        estimator._initPickle()
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
        self.addParameterRaster(description='Raster', help='Raster with training data features.')
        self.addParameterClassification(description='Labels', help='Classification with training data labels.')
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputClassifier(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return ClassificationSample(raster=self.getParameterRaster(),
                                    classification=self.getParameterClassification(),
                                    mask=self.getParameterMask())

    def estimator(self, sklEstimator):
        return Classifier(sklEstimator=sklEstimator)


for name, (code, helpAlg, helpCode) in parseClassifiers().items():
    ALGORITHMS.append(ClassifierFit(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode))


class ClustererFit(EstimatorFit):
    def group(self):
        return self.GROUP_CLUSTERING

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputClusterer(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return Sample(raster=self.getParameterRaster(), mask=self.getParameterMask())

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
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ClassifierPredict())


class ClassifierPredictFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Predict Class Probability'

    def description(self):
        return 'Applies a classifier to a raster.'

    def group(self):
        return self.GROUP_CLASSIFICATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterClassifier()
        self.addParameterOutputFraction(description='Probability')

    def processAlgorithm_(self):
        estimator = self.getParameterClassifier()
        raster = self.getParameterRaster()
        mask = self.getParameterMask()
        filename = self.getParameterOutputFraction()
        estimator.predictProbability(filename=filename, raster=raster, mask=mask, progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(ClassifierPredictFraction())


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
        return {self.P_OUTPUT_CLASSIFICATION: filename}


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
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')

        performance = ClusteringPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=self._progressBar,
                                                       grid=prediction.grid())
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

    P_BOOLEAN_ENMAP = 'createEnmap'
    P_BOOLEAN_HYMAP = 'createHymap'
    P_BOOLEAN_LIBRARY = 'createLibrary'
    P_OUTPUT_ENMAP_CLASSIFICATION = 'outEnmapClassification'
    P_OUTPUT_ENMAP_FRACTION = 'outEnmapFraction'
    P_OUTPUT_HYMAP_CLASSIFICATION = 'outHymapClassification'
    P_OUTPUT_HYMAP_FRACTION = 'outHymapFraction'
    P_OUTPUT_LIBRARY = 'outLibrary'

    def defineCharacteristics(self):
        self.addParameterBoolean(name=self.P_BOOLEAN_ENMAP, description='Create 30 m maps', defaultValue=True,
                                 help='Whether or not to create 30 m classification and fraction/regression maps.')
        self.addParameterBoolean(name=self.P_BOOLEAN_HYMAP, description='Create 3.6 m maps', defaultValue=False,
                                 help='Whether or not to create 3.6 m classification and fraction/regression maps.')
        self.addParameterOutputClassification(name=self.P_OUTPUT_ENMAP_CLASSIFICATION,
                                              description='LandCover Classification for 6 classes at 30 m')
        self.addParameterOutputFraction(name=self.P_OUTPUT_ENMAP_FRACTION,
                                        description='LandCover Fraction for 6 classes at 30 m')
        self.addParameterOutputClassification(name=self.P_OUTPUT_HYMAP_CLASSIFICATION,
                                              description='LandCover Classification for 6 classes at 3.6 m')
        self.addParameterOutputFraction(self.P_OUTPUT_HYMAP_FRACTION,
                                        description='LandCover Fraction for 6 classes at 3.6 m')

    def processAlgorithm_(self):
        import enmapboxtestdata
        enmap = Raster(filename=enmapboxtestdata.enmap)
        hymap = Raster(filename=enmapboxtestdata.hymap)
        classDefinitionL2 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                            colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
        vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
                                                    classAttribute=enmapboxtestdata.landcoverAttributes.Level_2_ID,
                                                    classDefinition=classDefinitionL2,
                                                    minDominantCoverage=0.5, minOverallCoverage=0.5,
                                                    oversampling=5)

        result = OrderedDict()
        if self.getParameterBoolean(self.P_BOOLEAN_ENMAP):
            fractionEnmap = Fraction.fromClassification(
                filename=self.getParameterOutputFraction(self.P_OUTPUT_ENMAP_FRACTION),
                classification=vectorClassification, grid=enmap)
            result[self.P_OUTPUT_ENMAP_FRACTION] = fractionEnmap.filename()
            classificationEnmap = Classification.fromClassification(
                filename=self.getParameterOutputClassification(self.P_OUTPUT_ENMAP_CLASSIFICATION),
                classification=fractionEnmap)
            result[self.P_OUTPUT_ENMAP_CLASSIFICATION] = classificationEnmap.filename()

        if self.getParameterBoolean(self.P_BOOLEAN_HYMAP):
            fractionHymap = Fraction.fromClassification(
                filename=self.getParameterOutputFraction(self.P_OUTPUT_HYMAP_FRACTION),
                classification=vectorClassification, grid=hymap)
            result[self.P_OUTPUT_HYMAP_FRACTION] = fractionHymap.filename()
            classificationHymap = Classification.fromClassification(
                filename=self.getParameterOutputClassification(self.P_OUTPUT_HYMAP_CLASSIFICATION),
                classification=fractionHymap)
            result[self.P_OUTPUT_HYMAP_CLASSIFICATION] = classificationHymap.filename()

        return result


ALGORITHMS.append(CreateAdditionalTestdata())


class MaskBuildFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Build Mask from Raster'

    def description(self):
        return 'Builds a mask from a raster based on user defined values and value ranges.'

    def group(self):
        return self.GROUP_MASKING

    P_TRUE = 'true'
    P_FALSE = 'false'

    def defineCharacteristics(self):

        self.addParameterRaster()
        self.addParameterList(self.P_TRUE, 'Foreground values',
                              help='List of values and ranges that are mapped to True, e.g. [1, 2, 5, range(5, 10)].')
        self.addParameterList(self.P_FALSE, 'Background values',
                              help='List of values and ranges that are mapped to False, e.g. [-9999, range(-10, 0)].')
        self.addParameterOutputMask()

    def processAlgorithm_(self):
        filename = self.getParameterOutputMask()
        Mask.fromRaster(filename=filename,
                        raster=self.getParameterRaster(),
                        true=self.getParameterList(self.P_TRUE),
                        false=self.getParameterList(self.P_FALSE),
                        progressBar=self._progressBar)
        return {self.P_OUTPUT_MASK: filename}


ALGORITHMS.append(MaskBuildFromRaster())


class ImportLibrary(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library'

    def description(self):
        return 'Import Library profiles as single line Raster.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        filename = self.getParameterOutputRaster()
        Raster.fromENVISpectralLibrary(filename=filename, library=library)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(ImportLibrary())


class ImportLibraryClassificationAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Classification Attribute'

    def description(self):
        return 'Import Library classification attribute as single line Classification.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_ATTRIBUTE = 'attribute'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTE, description='Classification Attribute',
                                help='Attribute name as specified in the library CSV attribute file.')
        self.addParameterOutputClassification()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        attribute = self.getParameterString(self.P_ATTRIBUTE)

        filename = self.getParameterOutputClassification()
        Classification.fromENVISpectralLibrary(filename=filename, library=library, attribute=attribute)
        return {self.P_OUTPUT_CLASSIFICATION: filename}


ALGORITHMS.append(ImportLibraryClassificationAttribute())


class ImportLibraryRegressionAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Regression Attributes'

    def description(self):
        return 'Import Library regression attributes as single line Regression.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_ATTRIBUTES = 'attributes'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTES, description='Regression Attributes',
                                help='List of attribute names as specified in the library CSV attribute file.')
        self.addParameterOutputRegression()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        attributes = [s.strip() for s in self.getParameterString(self.P_ATTRIBUTES).split(',')]
        filename = self.getParameterOutputRegression()
        Regression.fromENVISpectralLibrary(filename=filename, library=library, attributes=attributes)
        return {self.P_OUTPUT_REGRESSION: filename}


ALGORITHMS.append(ImportLibraryRegressionAttribute())


class ImportLibraryFractionAttribute(EnMAPAlgorithm):
    def displayName(self):
        return 'Import Library Fraction Attributes'

    def description(self):
        return 'Import Library fraction attributes as single line Fraction.'

    def group(self):
        return self.GROUP_AUXILLIARY

    P_ATTRIBUTES = 'attributes'

    def defineCharacteristics(self):
        self.addParameterLibrary()
        self.addParameterString(name=self.P_ATTRIBUTES, description='Fraction Attributes',
                                help='List of attribute names as specified in the library CSV attribute file.')
        self.addParameterOutputFraction()

    def processAlgorithm_(self):

        library = self.getParameterLibrary()
        attributes = [s.strip() for s in self.getParameterString(self.P_ATTRIBUTES).split(',')]
        filename = self.getParameterOutputFraction()
        Regression.fromENVISpectralLibrary(filename=filename, library=library, attributes=attributes)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(ImportLibraryFractionAttribute())


class OpenTestMaps_Toolbox(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return OpenTestMaps_Modeler().displayName()

    def description(self):
        return OpenTestMaps_Modeler().description()

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


ALGORITHMS.append(OpenTestMaps_Toolbox())


class OpenTestLibrary(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return 'Open Test Library'

    def description(self):
        return None

    def defineCharacteristics(self):
        pass

    def processAlgorithm_(self):
        import enmapboxtestdata
        import qgis.utils

        library = ENVISpectralLibrary(filename=enmapboxtestdata.speclib)
        qgis.utils.iface.addRasterLayer(library.raster().filename(), basename(enmapboxtestdata.speclib), 'gdal')
        for level in ['level 1', 'level 2']:
            filename = library.raster().filename().replace('.sli.transposed.vrt',
                                                           '.{}.classification.bsq'.format(level.replace(' ', '')))
            Classification.fromENVISpectralLibrary(filename=filename, library=library, attribute=level)
            qgis.utils.iface.addRasterLayer(filename, basename(filename), 'gdal')

        return {}

    def flags(self):
        return self.FlagHideFromModeler


ALGORITHMS.append(OpenTestLibrary())


class OpenTestMaps_Modeler(EnMAPAlgorithm):
    def group(self):
        return self.GROUP_AUXILLIARY

    def displayName(self):
        return 'Open Test Maps'

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
        self.addParameterOutputRaster('speclib', 'Library as Raster',
                                      help='File name: SpecLib_BerlinUrbanGradient.sli\n'
                                           'Spectral library with 75 spectra (material level, level 2 and level 3 class information)')

    def processAlgorithm_(self):
        import enmapboxtestdata
        library = ENVISpectralLibrary(filename=enmapboxtestdata.speclib)
        return {'enmap': enmapboxtestdata.enmap,
                'hymap': enmapboxtestdata.hymap,
                'landcover': enmapboxtestdata.landcover,
                'speclib': library.raster().filename()}

    def flags(self):
        return self.FlagHideFromToolbox


ALGORITHMS.append(OpenTestMaps_Modeler())


class FractionAsClassColorRGB(EnMAPAlgorithm):
    def displayName(self):
        return 'Fraction as RGB Raster'

    def description(self):
        return 'Creates a RGB representation from given class fractions. ' \
               'The RGB color of a specific pixel is the weighted mean value of the original class colors, ' \
               'where the weights are given by the corresponding class propability.\n'

    def group(self):
        return self.GROUP_POSTPROCESSING

    def defineCharacteristics(self):
        self.addParameterFraction()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        fraction = self.getParameterFraction()
        filename = self.getParameterOutputRaster()
        fraction.asClassColorRGBRaster(filename=filename, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(FractionAsClassColorRGB())


class FractionFromClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Fraction from Classification'

    def description(self):
        return 'Derive (binarized) class fractions from a classification.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterClassification()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        classification = self.getParameterClassification()
        filename = self.getParameterOutputFraction()
        Fraction.fromClassification(filename=filename, classification=classification, progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(FractionFromClassification())


class FractionFromVectorClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Fraction from Vector'

    def description(self):
        return 'Derives class fraction raster from a vector file with sufficient class information.'

    def group(self):
        return self.GROUP_CREATE_RASTER

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterVectorClassification(minCoveragesDefaultValues=(0., 0.), hideMinDominantCoverage=True)
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        filename = self.getParameterOutputFraction()
        Fraction.fromClassification(filename=filename,
                                    classification=self.getParameterVectorClassification(),
                                    grid=self.getParameterGrid(),
                                    oversampling=self.getParameterOversampling(),
                                    progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: filename}


ALGORITHMS.append(FractionFromVectorClassification())


class FractionPerformanceFromRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Fraction Performance'

    def description(self):
        return 'Assesses the performance of class fractions in terms of AUC and ROC curves.'

    def group(self):
        return self.GROUP_ACCURACY_ASSESSMENT

    P_PREDICTION = 'prediction'
    P_REFERENCE = 'reference'

    def defineCharacteristics(self):
        self.addParameterRaster(self.P_PREDICTION, 'Prediction',
                                help='Specify class fraction raster to be evaluated.')
        self.addParameterRaster(self.P_REFERENCE, 'Reference',
                                help='Specify reference classification raster (i.e. ground truth).')
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterFraction('prediction')
        reference = self.getParameterClassification('reference')
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')
        performance = FractionPerformance.fromRaster(prediction=prediction, reference=reference,
                                                     progressBar=self._progressBar)
        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(FractionPerformanceFromRaster())


class RasterApplyMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Apply Mask to Raster'

    def description(self):
        return 'Pixels that are masked out are set to the raster no data value.'

    def group(self):
        return self.GROUP_MASKING

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterInvertableMask(optional=False)
        self.addParameterOutputRaster(description='Masked Raster')

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        filename = self.getParameterOutputRaster()
        raster.applyMask(filename=filename, mask=self.getParameterInvertableMask(), progressBar=self._progressBar)
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


class RasterConvolve(EnMAPAlgorithm):
    def __init__(self, name, code, helpAlg, helpCode, domain):
        assert domain in ['spatial', 'spectral']
        self._name = name
        self._code = code
        self._helpAlg = helpAlg
        self._helpCode = helpCode
        self._domain = domain
        super().__init__()

    def description(self):
        return self._helpAlg

    def group(self):
        return self.GROUP_CONVOLUTION

    def createInstance(self):
        return type(self)(name=self._name, code=self._code, helpAlg=self._helpAlg, helpCode=self._helpCode,
                          domain=self._domain)

    def displayName(self):
        return self._domain.title() + ' Convolution ' + self._name

    def code(self):
        return self._code

    P_CODE = 'code'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True, help=self._helpCode)
        self.addParameterOutputRaster()

    def kernel(self):
        namespace = dict()
        code = self.getParameterString(self.P_CODE)
        exec(code, namespace)
        assert 'kernel' in namespace
        return namespace['kernel']

    def processAlgorithm_(self):
        kernel = self.kernel()
        raster = self.getParameterRaster()
        outraster = raster.convolve(filename=self.getParameterOutputRaster(),
                                    kernel=kernel)
        return {self.P_OUTPUT_RASTER: outraster.filename()}

for name, (code, helpAlg, helpCode) in parseSpatialKernel().items():
    ALGORITHMS.append(RasterConvolve(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode, domain='spatial'))
for name, (code, helpAlg, helpCode) in parseSpectralKernel().items():
    ALGORITHMS.append(RasterConvolve(name=name, code=code, helpAlg=helpAlg, helpCode=helpCode, domain='spectral'))


class RasterApplySpatial(EnMAPAlgorithm):
    def __init__(self, name, name2, code, helpAlg, helpCode):
        self._name = name
        self._name2 = name2
        self._code = code
        self._helpAlg = helpAlg
        self._helpCode = helpCode
        super().__init__()

    def description(self):
        return self._helpAlg

    def group(self):
        return self.GROUP_CONVOLUTION

    def createInstance(self):
        return type(self)(name=self._name, name2=self._name2, code=self._code, helpAlg=self._helpAlg, helpCode=self._helpCode)

    def displayName(self):
        name = self._name.title().replace('_', ' ')
        return 'Spatial {} {}'.format(self._name2, name)

    def code(self):
        return self._code

    P_CODE = 'code'

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterString(self.P_CODE, 'Code', defaultValue=self._code, multiLine=True, help=self._helpCode)
        self.addParameterOutputRaster()

    def function(self):
        namespace = dict()
        code = self.getParameterString(self.P_CODE)
        exec(code, namespace)
        assert 'function' in namespace
        return namespace['function']

    def processAlgorithm_(self):
        function = self.function()
        raster = self.getParameterRaster()
        outraster = raster.applySpatial(filename=self.getParameterOutputRaster(),
                                        function=function)
        return {self.P_OUTPUT_RASTER: outraster.filename()}

for name, (code, helpAlg, helpCode) in parseMorphology().items():
    ALGORITHMS.append(RasterApplySpatial(name=name, name2='Morphological', code=code, helpAlg=helpAlg, helpCode=helpCode))

for name, (code, helpAlg, helpCode) in parseOtherFilter().items():
    ALGORITHMS.append(RasterApplySpatial(name=name, name2='', code=code, helpAlg=helpAlg, helpCode=helpCode))


class RasterUniqueValues(EnMAPAlgorithm):
    def displayName(self):
        return 'Unique Values from Raster Band'

    def description(self):
        return 'This algorithm returns unique values from a raster band as a list. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterBand()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        values = raster.uniqueValues(index=self.getParameterBand() - 1)
        self._progressBar.setText('Unique value: {}'.format(repr(values)))
        return {}


ALGORITHMS.append(RasterUniqueValues())


class RasterStatistics(EnMAPAlgorithm):
    def displayName(self):
        return 'Raster Band Statistics'

    def description(self):
        return 'This algorithm returns raster band statistics. The output will be shown in the log window and can the copied from there accordingly.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterBand()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        values = raster.statistics(bandIndices=[self.getParameterBand()-1],
                   calcPercentiles=True, calcHistogram=True, calcMean=True, calcStd=True,
                   percentiles=[25,50,75])[0]

        self._progressBar.setText('Min: {}'.format(values.min))
        self._progressBar.setText('Max: {}'.format(values.max))
        self._progressBar.setText('Mean: {}'.format(values.mean))
        self._progressBar.setText('StdDev: {}'.format(values.std))
        self._progressBar.setText('p25: {}'.format(values.percentiles[0].value))
        self._progressBar.setText('median: {}'.format(values.percentiles[1].value))
        self._progressBar.setText('p75: {}'.format(values.percentiles[2].value))

        return {}

ALGORITHMS.append(RasterStatistics())


class MapViewMetadata(EnMAPAlgorithm):
    def displayName(self):
        return 'View Map Metadata'

    def description(self):
        return 'Prints all Map metadata to log.'

    def group(self):
        return self.GROUP_AUXILLIARY

    def defineCharacteristics(self):
        self.addParameterMap()

    def processAlgorithm_(self):
        map = self.getParameterMap()

        domainName = lambda key: key if key != '' else '<default>'

        if isinstance(map, Raster):
            for key, value in map.dataset().metadataDict().items():
                self._progressBar.setText(text='\n===============\nDataset Domain: {}'.format(domainName(key)))
                for k, v in value.items():
                    self._progressBar.setText(text='{} = {}'.format(k, v))
            for i, band in enumerate(map.dataset().bands()):
                for key, value in band.metadataDict().items():
                    self._progressBar.setText(text='\n===============\nBand {} Domain: {}'.format(i+1, domainName(key)))
                    for k, v in value.items():
                        self._progressBar.setText(text='{} = {}'.format(k, v))
        elif isinstance(map, Vector):
            for key, value in map.dataset().metadataDict().items():
                self._progressBar.setText(text='\n===============\nLayer Domain: {}'.format(domainName(key)))
                for k, v in value.items():
                    self._progressBar.setText(text='{} = {}'.format(k, v))

        else:
            assert 0
        return {}


ALGORITHMS.append(MapViewMetadata())


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
        self.addParameterInvertableMask()
        self.addParameterOutputReport()

    def processAlgorithm_(self):
        prediction = self.getParameterRegression(self.P_PREDICTION)
        reference = self.getParameterRegression(self.P_REFERENCE)
        mask = self.getParameterInvertableMask()
        if not prediction.grid().equal(reference.grid()):
            raise EnMAPAlgorithmParameterValueError('prediction and reference grid must match')
        performance = RegressionPerformance.fromRaster(prediction=prediction, reference=reference, mask=mask,
                                                       grid=prediction.grid(),
                                                       progressBar=self._progressBar)

        filename = self.getParameterOutputReport()
        performance.report().saveHTML(filename=filename, open=True)
        return {self.P_OUTPUT_REPORT: filename}


ALGORITHMS.append(RegressionPerformanceFromRaster())


class RegressorFit(EstimatorFit):
    def group(self):
        return self.GROUP_REGRESSION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputRegressor(self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return RegressionSample(raster=self.getParameterRaster(),
                                regression=self.getParameterRegression(),
                                mask=self.getParameterMask())

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
        return {self.P_OUTPUT_REGRESSION: filename}


ALGORITHMS.append(RegressorPredict())


class SpatialResamplingRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Raster)'

    def description(self):
        return 'Resamples a Raster into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterRaster()
        self.addParameterGDALResamplingAlg()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        outraster = raster.resample(filename=self.getParameterOutputRaster(),
                                    grid=self.getParameterGrid(),
                                    resampleAlg=self.getParameterGDALResamplingAlg(),
                                    progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename()}


ALGORITHMS.append(SpatialResamplingRaster())


class SpatialResamplingMask(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Mask)'

    def description(self):
        return 'Resamples a Mask into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterMask()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputMask()

    def processAlgorithm_(self):
        mask = self.getParameterMask(minOverallCoverage=self.getParameterMinOverallCoverage())
        outmask = mask.resample(filename=self.getParameterOutputMask(),
                                grid=self.getParameterGrid(),
                                progressBar=self._progressBar)
        return {self.P_OUTPUT_MASK: outmask.filename()}


ALGORITHMS.append(SpatialResamplingMask())


class SpatialResamplingClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Classification)'

    def description(self):
        return 'Resamples a Classification into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterClassification()
        self.addParameterMinCoverages()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        classification = self.getParameterClassification(minOverallCoverage=self.getParameterMinOverallCoverage(),
                                                         minDominantCoverage=self.getParameterMinDominantCoverage())
        outclassification = classification.resample(filename=self.getParameterOutputClassification(),
                                                    grid=self.getParameterGrid(),
                                                    progressBar=self._progressBar)
        return {self.P_OUTPUT_CLASSIFICATION: outclassification.filename()}


ALGORITHMS.append(SpatialResamplingClassification())


class SpatialResamplingRegression(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Regression)'

    def description(self):
        return 'Resamples a Regression into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterRegression()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        regression = self.getParameterRegression(minOverallCoverage=self.getParameterMinOverallCoverage())
        outregression = regression.resample(filename=self.getParameterOutputRegression(),
                                            grid=self.getParameterGrid(),
                                            progressBar=self._progressBar)
        return {self.P_OUTPUT_REGRESSION: outregression.filename()}


ALGORITHMS.append(SpatialResamplingRegression())


class SpatialResamplingFraction(EnMAPAlgorithm):
    def displayName(self):
        return 'Spatial Resampling (Fraction)'

    def description(self):
        return 'Resamples a Fraction into a target grid.'

    def group(self):
        return self.GROUP_RESAMPLING

    def defineCharacteristics(self):
        self.addParameterGrid()
        self.addParameterFraction()
        self.addParameterMinOverallCoverage()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        fraction = self.getParameterFraction(minOverallCoverage=self.getParameterMinOverallCoverage(),
                                             minDominantCoverage=self.getParameterMinDominantCoverage())
        outfraction = fraction.resample(filename=self.getParameterOutputFraction(),
                                        grid=self.getParameterGrid(),
                                        progressBar=self._progressBar)
        return {self.P_OUTPUT_FRACTION: outfraction.filename()}


ALGORITHMS.append(SpatialResamplingFraction())


class SensorDefinitionResampleRaster(EnMAPAlgorithm):
    def displayName(self):
        return 'Spectral Resampling'

    def group(self):
        return self.GROUP_RESAMPLING

    def description(self):
        return 'Spectrally resample a raster.'

    SENSOR_NAMES = ['select sensor'] + SensorDefinition.predefinedSensorNames()
    P_OPTION1 = 'option1'
    P_OPTION2 = 'option2'
    P_OPTION3 = 'option3'

    def defineCharacteristics(self):
        self.addParameterRaster(help='Select raster file which should be resampled.')
        self.addParameterEnum(name=self.P_OPTION1,
                              description='[Options 1] Spectral characteristic from predefined sensor',
                              options=self.SENSOR_NAMES, optional=True)
        self.addParameterRaster(name=self.P_OPTION2, description='[Option 2] Spectral characteristic from Raster',
                                help='Raster with defined wavelength and fwhm',
                                optional=True)
        self.addParameterLibrary(name=self.P_OPTION3,
                                 description='[Option 3] Spectral characteristic from response function files.',
                                 optional=True)
        self.resampleAlgNames = ['Linear Interpolation', 'Response Function Convolution']
        self.resampleAlgOptions = [SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE]
        self.addParameterEnum(description='Resampling Algorithm', options=self.resampleAlgNames, defaultValue=0)
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        raster = self.getParameterRaster()
        option1 = self.getParameterEnum(name=self.P_OPTION1)
        option2 = self.getParameterRaster(name=self.P_OPTION2)
        option3 = self.getParameterLibrary(name=self.P_OPTION3)

        self._progressBar.setText(repr(option1))
        self._progressBar.setText(repr(option2))
        self._progressBar.setText(repr(option3))

        if option1 != 0:
            sensor = SensorDefinition.fromPredefined(name=self.SENSOR_NAMES[option1])
#            library = ENVISpectralLibrary(filename=self.SENSOR_RESPONSES[option1])
#            sensor = SensorDefinition.fromENVISpectralLibrary(library=library)
        elif isinstance(option2, Raster):
            sensor = SensorDefinition.fromRaster(raster=option2)
        elif isinstance(option3, ENVISpectralLibrary):
            sensor = SensorDefinition.fromENVISpectralLibrary(library=option3)
        else:
            raise EnMAPAlgorithmParameterValueError('missing spectral characteristic')

        self._progressBar.setText(repr(sensor))

        filename = self.getParameterOutputRaster()
        resampleAlg = self.resampleAlgOptions[self.getParameterEnum()]
        sensor.resampleRaster(filename=filename, raster=raster, resampleAlg=resampleAlg, progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: filename}


ALGORITHMS.append(SensorDefinitionResampleRaster())


class TransformerFit(EstimatorFit):
    def group(self):
        return self.GROUP_TRANSFORMATION

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterMask()
        self.addParameterCode()
        self.addParameterOutputTransformer(name=self.P_OUTPUT_ESTIMATOR)

    def sample(self):
        return Sample(raster=self.getParameterRaster(),
                      mask=self.getParameterMask())

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

        def funcClassTotals():
            counts = classification.statistics()
            return counts

        n = self.getParameterNumberOfPointsPerClass(classes=classification.classDefinition().classes(), funcClassTotals=funcClassTotals)
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
        self.addParameterInvertableMask(allowVector=False, optional=False)
        self.addParameterNumberOfPoints(defaultValue=100)
        self.addParameterOutputVector()

    def processAlgorithm_(self):
        filename = self.getParameterOutputVector()
        mask = self.getParameterInvertableMask()
        def funcTotal():
            array = mask.array()
            return np.sum(array)


        Vector.fromRandomPointsFromMask(filename=filename,
                                        mask=mask, n=self.getParameterNumberOfPoints(funcTotal=funcTotal),
                                        progressBar=self._progressBar)
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


class ExtractSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract samples from raster and mask'

    def description(self):
        return 'Extract samples from raster and mask.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()

    def processAlgorithm_(self):
        sample = Sample(raster=self.getParameterRaster(),
                        mask=self.getParameterInvertableMask())
        outraster, = sample.extractAsRaster(filenames=[self.getParameterOutputRaster()], progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename()}


ALGORITHMS.append(ExtractSamples())


class ExtractClassificationSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract classification samples from raster and classification'

    def description(self):
        return 'Extract classification samples from raster and classification.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputClassification()

    def processAlgorithm_(self):
        sample = ClassificationSample(raster=self.getParameterRaster(),
                                      classification=self.getParameterClassification(),
                                      mask=self.getParameterInvertableMask())
        outraster, outclassification = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                         self.getParameterOutputClassification()],
                                                              progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_CLASSIFICATION: outclassification.filename()}


ALGORITHMS.append(ExtractClassificationSamples())


class ExtractRegressionSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract regression samples from raster and regression'

    def description(self):
        return 'Extract regression samples from raster and regression.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputRegression()

    def processAlgorithm_(self):
        sample = RegressionSample(raster=self.getParameterRaster(),
                                  regression=self.getParameterRegression(),
                                  mask=self.getParameterInvertableMask())
        outraster, outregression = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                     self.getParameterOutputRegression()],
                                                          progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_REGRESSION: outregression.filename()}

ALGORITHMS.append(ExtractRegressionSamples())


class ExtractFractionSamples(EnMAPAlgorithm):
    def displayName(self):
        return 'Extract fraction samples from raster and fraction'

    def description(self):
        return 'Extract fraction samples from raster and fraction.'

    def group(self): return self.GROUP_CREATE_SAMPLE

    def defineCharacteristics(self):
        self.addParameterRaster()
        self.addParameterFraction()
        self.addParameterInvertableMask()
        self.addParameterOutputRaster()
        self.addParameterOutputFraction()

    def processAlgorithm_(self):
        sample = FractionSample(raster=self.getParameterRaster(),
                                fraction=self.getParameterFraction(),
                                mask=self.getParameterInvertableMask())
        outraster, outfraction = sample.extractAsRaster(filenames=[self.getParameterOutputRaster(),
                                                                   self.getParameterOutputFraction()],
                                                        progressBar=self._progressBar)
        return {self.P_OUTPUT_RASTER: outraster.filename(),
                self.P_OUTPUT_FRACTION: outfraction.filename()}

ALGORITHMS.append(ExtractFractionSamples())


def generateRST():
    global ALGORITHMS

    groups = dict()

    for alg in ALGORITHMS:
        if alg.group() not in groups:
            groups[alg.group()] = dict()
        groups[alg.group()][alg.displayName()] = alg

    text = 'GeoAlgorithms\n'
    text += '#############\n\n'

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

            text += '....\n\n'  # separating line

    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'doc', 'source', 'ga.rst')
    with open(filename, mode='w') as f:
        f.write(text)
    print('created GeoAlgoritms RST file: ', filename)

