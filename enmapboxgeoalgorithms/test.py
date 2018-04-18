from __future__ import absolute_import

import tempfile
from os.path import join

outdir = join(tempfile.gettempdir(), 'eb_test')
outdir = r'c:\_eb_test'
import qgis.PyQt
from qgis.core import *
import hubflow.test_core

# init QGIS
from processing.core.Processing import Processing
from qgis.core import QgsApplication

qgsApp = QgsApplication([], True)
qgsApp.initQgis()


# activate QGIS log in PyCharm
def printQgisLog(tb, error, level):
    print(tb)
QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

# load Enmap-Box TestProvider
from enmapboxgeoalgorithms.algorithms import *

Processing.initialize()


# provider = EnMAPProvider()
# QgsApplication.processingRegistry().addProvider(provider)

class Feedback(QgsProcessingFeedback):
    def pushConsoleInfo(self, info):
        print(info)

    def setProgressText(self, info):
        print(info)


def runalg(alg, io, info=None):
    assert isinstance(alg, EnMAPAlgorithm)
    print('\n##############')
    alg.defineCharacteristics()
    print(alg.__class__.__name__,
          '({} -> {}), {}, {}'.format(alg.group(), alg.displayName(), alg.groupId(), alg.name()))
    print('parameters = {}'.format(repr(io)))
    if info is not None:
        print(info)
    return Processing.runAlgorithm(alg, parameters=io, feedback=Feedback())


import hubflow.test_core
import enmapboxtestdata

enmap = hubflow.test_core.enmap.filename
enmapClassification = hubflow.test_core.enmapClassification.filename
enmapProbability = hubflow.test_core.enmapProbability.filename
enmapMask = hubflow.test_core.enmapMask.filename
vector = hubflow.test_core.vector.filename

enmapUnsupervisedSample = join(outdir, 'enmapUnsupervisedSample.pkl')
hubflow.test_core.enmapUnsupervisedSample.pickle(filename=enmapUnsupervisedSample)

enmapClassificationSample = join(outdir, 'enmapClassificationSample.pkl')
hubflow.test_core.enmapClassificationSample.pickle(filename=enmapClassificationSample)

enmapRegressionSample = join(outdir, 'enmapRegressionSample.pkl')
hubflow.test_core.enmapProbabilitySample.pickle(filename=enmapRegressionSample)

enmapProbabilitySample = join(outdir, 'enmapProbabilitySample.pkl')
hubflow.test_core.enmapProbabilitySample.pickle(filename=enmapProbabilitySample)


def test_ClassDefinitionFromRaster():
    alg = ClassDefinitionFromRaster()
    io = {alg.P_RASTER: enmapClassification}
    runalg(alg=alg, io=io)


def test_Classification():
    alg = ClassificationFromProbability()
    io = {alg.P_PROBABILITY: enmapProbability,
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromProbability.bsq')}
          #alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromProbability.img')}

    runalg(alg=alg, io=io)

    alg = ClassificationFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OVERSAMPLING: 1,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromVectorClassification.bsq')}
    runalg(alg=alg, io=io)


def test_ClassificationPerformance():
    alg = ClassificationPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapClassification,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'ClassificationPerformanceFromClassification.html')}
    runalg(ClassificationPerformanceFromRaster(), io)


def test_ClassificationSample():
    alg = ClassificationSampleFromRasterAndVectorClassification()
    filename = join(outdir, 'ClassificationSampleFromRasterAndVectorClassification.pkl')
    io = {alg.P_RASTER: enmap,
          alg.P_VECTOR: enmapboxtestdata.landcover,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OVERSAMPLING: 1,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}
    runalg(alg=alg, io=io)
    return
    alg = ClassificationSampleFromProbabilitySample()
    filename = join(outdir, 'ClassificationSampleFromProbabilitySample.pkl')
    io = {alg.P_PROBABILITY_SAMPLE: enmapProbabilitySample,
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: filename,
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5}
    runalg(alg=alg, io=io)

    alg = ClassificationSampleFromRasterAndProbability()
    filename = join(outdir, 'ClassificationSampleFromRasterAndProbability.pkl')
    io = {alg.P_RASTER: enmap,
          alg.P_PROBABILITY: enmapProbability,
          alg.P_MASK: enmapMask,
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}
    runalg(alg=alg, io=io)

    alg = ClassificationSampleFromENVISpectralLibrary()
    filename = join(outdir, 'ClassificationSampleFromENVISpectralLibrary.pkl')
    io = {alg.P_ENVI_SPECLIB: enmapboxtestdata.speclib,
          alg.P_CLASSDEFINITIONPREFIX: 'level 2',
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}
    runalg(alg=alg, io=io)

    alg = ClassificationSampleSynthMix()
    filename = join(outdir, 'ClassificationSampleSynthMix.pkl')
    io = {alg.P_CLASSIFICATION_SAMPLE: enmapClassificationSample,
          alg.P_N: 100,
          alg.P_COMPLEXITY2LIKELIHOOD: 1.0,
          alg.P_COMPLEXITY3LIKELIHOOD: 0.0,
          alg.P_CLASSLIKELIHOODS: 0,
          alg.P_OUTPUT_PROBABILITY_SAMPLE: filename}
    runalg(alg=alg, io=io)

    alg = ClassificationSampleFromRasterAndClassification()
    filename = join(outdir, 'ClassificationSampleFromRasterAndClassification.pkl')
    io = {alg.P_RASTER: enmap,
          alg.P_CLASSIFICATION: enmapClassification,
          alg.P_MASK: enmapMask,
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: filename}
    runalg(alg=alg, io=io)


def test_Classifier():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, ClassifierFit):
            continue

        if not algFit.displayName().endswith('RandomForestClassifier'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Classifier{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_CLASSIFICATION_SAMPLE: enmapClassificationSample,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        algPredict = ClassifierPredict()
        filename = join(outdir, 'ClassifierPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredict.P_RASTER: enmap,
              algPredict.P_MASK: enmapMask,
              algPredict.P_CLASSIFIER: filenameEstimator,
              algPredict.P_OUTPUT_RASTER: filename}
        runalg(alg=algPredict, io=io)

        # predict probability
        if not algFit.displayName().endswith('RandomForestClassifier'):
            continue

        algPredictProba = ClassifierPredictProbability()
        filename = join(outdir, 'ClassifierPredictProbability{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredictProba.P_RASTER: enmap,
              algPredictProba.P_MASK: enmapMask,
              algPredictProba.P_CLASSIFIER: filenameEstimator,
              algPredictProba.P_OUTPUT_RASTER: filename}
        runalg(alg=algPredictProba, io=io)


def test_Clusterer():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, ClustererFit):
            continue

        if not algFit.displayName().endswith('KMeans'):
            continue

        filenameEstimator = join(outdir, 'Clusterer{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_UNSUPERVISED_SAMPLE: enmapProbabilitySample,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        alg = ClustererPredict()
        filename = join(outdir, 'ClustererPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {alg.P_RASTER: enmap,
              alg.P_MASK: enmapMask,
              alg.P_CLUSTERER: filenameEstimator,
              alg.P_OUTPUT_RASTER: filename}
        runalg(alg=alg, io=io)


def test_ClusteringPerformance():
    alg = ClusteringPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapClassification,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'ClusteringPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_CreateAdditionalTestdata():
    alg = CreateAdditionalTestdata()
    io = {alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'CreateAdditionalTestdataClassification.bsq'),
          alg.P_OUTPUT_PROBABILITY: join(outdir, 'CreateAdditionalTestdataProbability.bsq'),
          alg.P_OUTPUT_UNSUPERVISED_SAMPLE: join(outdir, 'CreateAdditionalTestdataSample.pkl'),
          alg.P_OUTPUT_CLASSIFICATION_SAMPLE: join(outdir, 'CreateAdditionalTestdataClassificationSample.pkl'),
          alg.P_OUTPUT_REGRESSION_SAMPLE: join(outdir, 'CreateAdditionalTestdataRegressionSample.pkl'),
          alg.P_OUTPUT_PROBABILITY_SAMPLE: join(outdir, 'CreateAdditionalTestdataProbabilitySample.pkl')}
    runalg(alg=alg, io=io)

def test_Mask():
    alg = MaskBuildFromRaster()
    io = {alg.P_RASTER: enmap,
          alg.P_TRUEVALUES: '[]',
          alg.P_TRUERANGES: '[]',
          alg.P_FALSEVALUES: '[]',
          alg.P_FALSERANGES: '[]',
          alg.P_OUTPUT_MASK: join(outdir, 'MaskBuildFromRaster.bsq')}
    runalg(alg=alg, io=io)


def test_Probability():
    alg = ProbabilityFromClassification()
    io = {alg.P_CLASSIFICATION: enmapClassification,
          alg.P_OUTPUT_PROBABILITY: join(outdir, 'ProbabilityFromClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = ProbabilityAsClassColorRGB()
    io = {alg.P_PROBABILITY: enmapProbability,
          alg.P_OUTPUT_RASTER: join(outdir, 'ProbabilityAsClassColorRGB.bsq')}
    runalg(alg=alg, io=io)

    alg = ProbabilityFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MINOVERALLCOVERAGE: 0.,
          alg.P_MINWINNERCOVERAGE: 0.,
          alg.P_OVERSAMPLING: 10,
          alg.P_OUTPUT_PROBABILITY: join(outdir, 'ProbabilityFromVectorClassification.bsq')}
    runalg(alg=alg, io=io)


def test_ProbabilityPerformance():
    alg = ProbabilityPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapProbability,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'ProbabilityPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_ProbabilitySample():
    alg = ProbabilitySampleFromRasterAndVector()
    io = {alg.P_RASTER: enmap,
          alg.P_VECTOR: enmapboxtestdata.landcover,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MINOVERALLCOVERAGE: 0.,
          alg.P_MINWINNERCOVERAGE: 0.,
          alg.P_OVERSAMPLING: 10,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_PROBABILITY_SAMPLE: join(outdir, 'ProbabilitySampleFromRasterAndVector.pkl')}
    runalg(alg=alg, io=io)

    alg = ProbabilitySampleFromClassificationSample()
    io = {alg.P_CLASSIFICATION_SAMPLE: enmapProbabilitySample,#enmapClassificationSample,
          alg.P_OUTPUT_PROBABILITY_SAMPLE: join(outdir, 'ProbabilitySampleFromClassificationSample.pkl')}
    runalg(alg=alg, io=io)
    return
    alg = ProbabilitySampleFromRasterAndClassification()
    io = {alg.P_RASTER: enmap,
          alg.P_CLASSIFICATION: enmapClassification,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_PROBABILITY_SAMPLE: join(outdir, 'ProbabilitySampleFromRasterAndClassification.pkl')}
    runalg(alg=alg, io=io)

    alg = ProbabilitySampleFromRasterAndProbability()
    io = {alg.P_RASTER: enmap,
          alg.P_PROBABILITY: enmapProbability,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_PROBABILITY_SAMPLE: join(outdir, 'ProbabilitySampleFromRasterAndProbability.pkl')}
    runalg(alg=alg, io=io)


def test_Raster():
    alg = RasterApplyMask()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_RASTER: join(outdir, 'RasterApplyMask.bsq')}
    runalg(alg=alg, io=io)

    alg = RasterFromVector()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: enmapboxtestdata.landcover,
          alg.P_INIT_VALUE: 0,
          alg.P_BURN_VALUE: 1,
          alg.P_BURN_ATTRIBUTE: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_ALL_TOUCHED: True,
          alg.P_FILTER_SQL: '',
          alg.P_DATA_TYPE: 3,
          alg.P_NO_DATA_VALUE: 'None',
          alg.P_OUTPUT_RASTER: join(outdir, 'RasterFromVector.bsq')}
    runalg(alg=alg, io=io)


def test_RegressionPerformance():
    alg = RegressionPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapProbability,
          alg.P_REFERENCE: enmapProbability,
          alg.P_OUTPUT_REPORT: join(outdir, 'RegressionPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_RegressionSample():
    alg = RegressionSampleFromRasterAndRegression()
    io = {alg.P_RASTER: enmap,
          alg.P_REGRESSION: enmapProbability,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_REGRESSION_SAMPLE: join(outdir, 'RegressionSampleFromRasterAndRegression.pkl')}
    runalg(alg=alg, io=io)


def test_Regressor():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, RegressorFit):
            continue

        if not algFit.displayName().endswith('RandomForestRegressor'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Regressor{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_REGRESSION_SAMPLE: enmapRegressionSample,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        algPredict = RegressorPredict()
        filename = join(outdir, 'RegressorPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredict.P_RASTER: enmap,
              algPredict.P_MASK: enmapMask,
              algPredict.P_REGRESSOR: filenameEstimator,
              algPredict.P_OUTPUT_RASTER: filename}
        runalg(alg=algPredict, io=io)


def test_TestParameters():
    alg = TestVectorClassification()
    io = {alg.P_VECTOR: vector,
          # alg.P_CLASS_DEFINITION: "ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])",
          alg.P_CLASS_DEFINITION: '',
          alg.P_MINOVERALLCOVERAGE: 0.5,
          alg.P_MINWINNERCOVERAGE: 0.5,
          alg.P_OVERSAMPLING: 1,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID}
    runalg(alg=alg, io=io)

    alg = TestNumber()
    io = {alg.P_INTEGER: 1,
          alg.P_FLOAT: 0.5}
    runalg(alg=alg, io=io)

    alg = TestClassDefinition()
    io = {
        alg.P_CLASS_DEFINITION: "ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])"}
    runalg(alg=alg, io=io)

    alg = TestString()
    io = {alg.P_STRING: 'Hello',
          alg.P_STRING2: None}
    runalg(alg=alg, io=io)

    alg = TestField()
    io = {'vector': vector, 'field': enmapboxtestdata.landcoverAttributes.Level_2_ID}
    runalg(alg=alg, io=io)

    alg = TestOutputRaster()
    io = {alg.P_OUTPUT_RASTER: join(outdir, 'TestOutputRaster.bsq')}
    runalg(alg=alg, io=io)

    alg = TestRaster()
    io = {alg.P_RASTER: join(outdir, enmap),
          alg.P_RASTER2: None,
          alg.P_RASTER3: join(outdir, enmap)}
    runalg(alg=alg, io=io)

    alg = TestOutputReport()
    io = {alg.P_OUTPUT_REPORT: join(outdir, 'TestOutputReport.html')}
    runalg(alg=alg, io=io)

    alg = TestVector()
    io = {alg.P_VECTOR: join(outdir, vector),
          alg.P_VECTOR2: None,
          alg.P_VECTOR3: join(outdir, vector)}
    runalg(alg=alg, io=io)


def test_Transformers():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, TransformerFit):
            continue

        if not algFit.displayName().endswith('PCA'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Transformer{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_UNSUPERVISED_SAMPLE: enmapRegressionSample,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # transform
        algTransform = TransformerTransform()
        filenameTransformation = join(outdir, 'TransformerTransform{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algTransform.P_RASTER: enmap,
              algTransform.P_MASK: enmapMask,
              algTransform.P_TRANSFORMER: filenameEstimator,
              algTransform.P_OUTPUT_RASTER: filenameTransformation}
        runalg(alg=algTransform, io=io)

        # inverse transform
        algInverse = TransformerInverseTransform()
        hasNoInverseTransform = False
        for name in ['Imputer', 'FactorAnalysis', 'Normalizer', 'FeatureAgglomeration']:
            if algTransform.displayName().endswith(name):
                hasNoInverseTransform = True
        if hasNoInverseTransform: continue

        filename = join(outdir, 'TransformerInverseTransform{}.bsq'.format(algInverse.displayName().split()[1]))
        io = {algInverse.P_RASTER: filenameTransformation,
              algInverse.P_MASK: enmapMask,
              algInverse.P_TRANSFORMER: filenameEstimator,
              algInverse.P_OUTPUT_RASTER: filename}
        runalg(alg=algInverse, io=io)


def test_UnsupervisedSample():
    alg = UnsupervisedSampleFromRasterAndMask()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_UNSUPERVISED_SAMPLE: join(outdir, 'UnsupervisedSampleFromRasterAndMask.pkl')}
    runalg(alg=alg, io=io)

    alg = UnsupervisedSampleFromENVISpectralLibrary()
    io = {alg.P_ENVI_SPECLIB: enmapboxtestdata.speclib,
          alg.P_OUTPUT_UNSUPERVISED_SAMPLE: join(outdir, 'UnsupervisedSampleFromENVISpectralLibrary.pkl')}
    runalg(alg=alg, io=io)

    alg = UnsupervisedSampleScaleFeatures()
    io = {alg.P_UNSUPERVISED_SAMPLE: enmapUnsupervisedSample,
          alg.P_SCALE_FACTOR: 1.,
          alg.P_OUTPUT_UNSUPERVISED_SAMPLE: join(outdir, 'UnsupervisedSampleScaleFeatures.pkl')}
    runalg(alg=alg, io=io)


def test_VectorFromRandomPointsFromMask():
    alg = VectorFromRandomPointsFromMask()
    io = {alg.P_MASK: enmapMask,
          alg.P_NUMBER_OF_POINTS: 100,
          alg.P_OUTPUT_VECTOR: join(outdir, 'VectorFromRandomPointsFromMask.gpkg')}
    runalg(alg=alg, io=io)


def test_VectorFromRandomPointsFromClassification():
    alg = VectorFromRandomPointsFromClassification()
    io = {alg.P_CLASSIFICATION: enmapClassification,
          alg.P_NUMBER_OF_POINTS_PER_CLASS: 100,
          alg.P_OUTPUT_VECTOR: join(outdir, 'VectorFromRandomPointsFromClassification.gpkg')}
    runalg(alg=alg, io=io)


def test_VectorUniqueValues():
    alg = VectorUniqueValues()
    io = {alg.P_VECTOR: enmapboxtestdata.landcover,
          alg.P_FIELD: enmapboxtestdata.landcoverAttributes.Level_2}
    runalg(alg=alg, io=io)

def test_help():
    alg = VectorUniqueValues()
    alg.defineCharacteristics()
    print(alg.shortHelpString())


def printMenu():
    menu = dict()
    for alg in ALGORITHMS:
        assert isinstance(alg, EnMAPAlgorithm)
        if alg.group() not in menu:
            menu[alg.group()] = list()
        menu[alg.group()].append((alg.displayName(), alg.__class__.__name__))

    print('')
    for group in sorted(menu):
        print(group)
        for name, className in sorted(menu[group]):
            # print('  {} ({})'.format(name, className))
            print('  {}'.format(name))


if __name__ == '__main__':
    test_TestParameters()
    test_ClassDefinitionFromRaster()
    test_Classification()
    test_ClassificationPerformance()
    test_ClassificationSample()
    test_Classifier()
    test_Clusterer()
    test_ClusteringPerformance()
    test_CreateAdditionalTestdata()
    test_Mask()
    test_Probability()
    test_ProbabilityPerformance()
    test_ProbabilitySample()
    test_Raster()
    test_RegressionPerformance()
    test_RegressionSample()
    test_Regressor()
    test_Transformers()
    test_UnsupervisedSample()
    test_VectorFromRandomPointsFromMask()
    test_VectorFromRandomPointsFromClassification()
    test_VectorUniqueValues()

    #test_help()
    #generateRST()

# printMenu()
print('done!!!')
