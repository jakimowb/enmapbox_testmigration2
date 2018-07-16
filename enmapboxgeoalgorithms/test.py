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

enmap = hubflow.test_core.enmap.filename()
hymap = hubflow.test_core.hymap.filename()
enmapClassification = hubflow.test_core.enmapClassification.filename()
enmapFraction = hubflow.test_core.enmapFraction.filename()
enmapMask = hubflow.test_core.enmapMask.filename()
vector = hubflow.test_core.vector.filename()

#enmapSample = join(outdir, 'enmapSample.pkl')
#enmapClassificationSample = hubflow.test_core.enmapClassificationSample



def test_ClassDefinitionFromRaster():
    alg = ClassDefinitionFromRaster()
    io = {alg.P_RASTER: enmapClassification}
    runalg(alg=alg, io=io)


def test_Classification():

    alg = ClassificationFromFraction()
    io = {alg.P_FRACTION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromFraction.bsq')}

    runalg(alg=alg, io=io)

    alg = ClassificationFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OVERSAMPLING: 1,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromVectorClassification.bsq')}
    runalg(alg=alg, io=io)


def test_ClassificationPerformance():
    alg = ClassificationPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapClassification,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'ClassificationPerformanceFromClassification.html')}
    runalg(ClassificationPerformanceFromRaster(), io)


def test_Classifier():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, ClassifierFit):
            continue

        if not algFit.displayName().endswith('RandomForestClassifier'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Classifier{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_RASTER: enmap,
              algFit.P_CLASSIFICATION: enmapClassification,
              algFit.P_MASK: vector,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        algPredict = ClassifierPredict()
        filename = join(outdir, 'ClassifierPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredict.P_RASTER: enmap,
              algPredict.P_MASK: enmapMask,
              algPredict.P_CLASSIFIER: filenameEstimator,
              algPredict.P_OUTPUT_CLASSIFICATION: filename}
        runalg(alg=algPredict, io=io)

        # predict probability
        if not algFit.displayName().endswith('RandomForestClassifier'):
            continue

        algPredictProba = ClassifierPredictFraction()
        filename = join(outdir, 'ClassifierPredictFraction{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredictProba.P_RASTER: enmap,
              algPredictProba.P_MASK: enmapMask,
              algPredictProba.P_CLASSIFIER: filenameEstimator,
              algPredictProba.P_OUTPUT_FRACTION: filename}
        runalg(alg=algPredictProba, io=io)


def test_Clusterer():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, ClustererFit):
            continue

        if not algFit.displayName().endswith('KMeans'):
            continue

        filenameEstimator = join(outdir, 'Clusterer{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_RASTER: enmap,
              algFit.P_MASK: enmapMask,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        alg = ClustererPredict()
        filename = join(outdir, 'ClustererPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {alg.P_RASTER: enmap,
              alg.P_MASK: enmapMask,
              alg.P_CLUSTERER: filenameEstimator,
              alg.P_OUTPUT_CLASSIFICATION: filename}
        runalg(alg=alg, io=io)


def test_ClusteringPerformance():
    alg = ClusteringPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapClassification,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'ClusteringPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_CreateAdditionalTestdata():
    alg = CreateAdditionalTestdata()
    io = {alg.P_BOOLEAN_ENMAP: True,
          alg.P_BOOLEAN_HYMAP: True,
          alg.P_BOOLEAN_LIBRARY: True,
          alg.P_OUTPUT_ENMAP_CLASSIFICATION: join(outdir, 'CreateAdditionalTestdataEnmapClassification.bsq'),
          alg.P_OUTPUT_ENMAP_FRACTION: join(outdir, 'CreateAdditionalTestdataEnmapFraction.bsq'),
          alg.P_OUTPUT_HYMAP_CLASSIFICATION: join(outdir, 'CreateAdditionalTestdataHymapClassification.bsq'),
          alg.P_OUTPUT_HYMAP_FRACTION: join(outdir, 'CreateAdditionalTestdataHymapFraction.bsq'),
          alg.P_OUTPUT_LIBRARY: join(outdir, 'CreateAdditionalTestdataLibrary.bsq')}

    runalg(alg=alg, io=io)

def test_ImportLibrary():
    alg = ImportLibrary()
    io = {alg.P_LIBRARY: join(outdir, 'CreateAdditionalTestdataLibrary.bsq'),
          alg.P_IMPORT_PROFILES: True,
          alg.P_CLASSIFICATION_SCHEME_NAME: 'level 2',
          alg.P_REGRESSION_OUTPUT_NAMES: ', '.join(hubflow.test_core.enmapFraction.outputNames()),
          alg.P_FRACTION_OUTPUT_NAMES: ', '.join(hubflow.test_core.enmapFraction.outputNames()),
          alg.P_OUTPUT_RASTER: join(outdir, 'OpenLibraryRaster.bsq'),
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'OpenLibraryClassification.bsq'),
          alg.P_OUTPUT_REGRESSION: join(outdir, 'OpenLibraryRegression.bsq'),
          alg.P_OUTPUT_FRACTION: join(outdir, 'OpenLibraryFraction.bsq')}
    runalg(alg=alg, io=io)


def test_Mask():
    alg = MaskBuildFromRaster()
    io = {alg.P_RASTER: enmap,
          alg.P_TRUE: '[]',
          alg.P_FALSE: '[]',
          alg.P_OUTPUT_MASK: join(outdir, 'MaskBuildFromRaster.bsq')}
    runalg(alg=alg, io=io)


def test_ExtractSamples():
    alg = ExtractSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq')}
    runalg(alg=alg, io=io)


    alg = ExtractClassificationSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_CLASSIFICATION: join(outdir, 'CreateAdditionalTestdataEnmapClassification.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ExtractSamplesClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = ExtractRegressionSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_REGRESSION: join(outdir, 'CreateAdditionalTestdataEnmapFraction.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_REGRESSION: join(outdir, 'ExtractSamplesRegression.bsq')}
    runalg(alg=alg, io=io)

    alg = ExtractFractionSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_FRACTION: join(outdir, 'CreateAdditionalTestdataEnmapFraction.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_FRACTION: join(outdir, 'ExtractSamplesFractions.bsq')}
    runalg(alg=alg, io=io)


def test_Fraction():
    alg = FractionFromClassification()
    io = {alg.P_CLASSIFICATION: enmapClassification,
          alg.P_OUTPUT_FRACTION: join(outdir, 'FractionFromClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = FractionAsClassColorRGB()
    io = {alg.P_FRACTION: enmapFraction,
          alg.P_OUTPUT_RASTER: join(outdir, 'FractionAsClassColorRGB.bsq')}
    runalg(alg=alg, io=io)

    alg = FractionFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIDFIELD: enmapboxtestdata.landcoverAttributes.Level_2_ID,
          alg.P_CLASS_DEFINITION: '',
          alg.P_MIN_OVERALL_COVERAGE: 0.,
          alg.P_MIN_DOMINANT_COVERAGE: 0.,
          alg.P_OVERSAMPLING: 10,
          alg.P_OUTPUT_FRACTION: join(outdir, 'FractionFromVectorClassification.bsq')}
    runalg(alg=alg, io=io)


def test_FractionPerformance():
    alg = FractionPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapFraction,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'FractionPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_Raster():

    for alg in ALGORITHMS:
        if isinstance(alg, RasterApplySpatial):
            io = {alg.P_RASTER: enmap,
                  alg.P_CODE: alg.code(),
                  alg.P_OUTPUT_RASTER: join(outdir, 'RasterApplySpatial'+alg.name())}
            runalg(alg=alg, io=io)
            break

    for alg in ALGORITHMS:
        if isinstance(alg, RasterConvolve):
            io = {alg.P_RASTER: enmap,
                  alg.P_CODE: alg.code(),
                  alg.P_OUTPUT_RASTER: join(outdir, 'RasterConvolve'+alg.name())}
            runalg(alg=alg, io=io)
            break

    alg = RasterViewMetadata()
    io = {alg.P_RASTER: enmap}
    runalg(alg=alg, io=io)

    alg = RasterUniqueValues()
    io = {alg.P_RASTER: enmapClassification,
          alg.P_BAND: 1}
    runalg(alg=alg, io=io)

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
    io = {alg.P_PREDICTION: enmapFraction,
          alg.P_REFERENCE: enmapFraction,
          alg.P_OUTPUT_REPORT: join(outdir, 'RegressionPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_Regressor():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, RegressorFit):
            continue

        if not algFit.displayName().endswith('RandomForestRegressor'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Regressor{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_RASTER: enmap,
              algFit.P_REGRESSION: enmapFraction,
              algFit.P_MASK: enmapMask,
              algFit.P_CODE: algFit.code(),
              algFit.P_OUTPUT_ESTIMATOR: filenameEstimator}
        runalg(alg=algFit, io=io, info=algFit.displayName())

        # predict
        algPredict = RegressorPredict()
        filename = join(outdir, 'RegressorPredict{}.bsq'.format(algFit.displayName().split()[1]))
        io = {algPredict.P_RASTER: enmap,
              algPredict.P_MASK: enmapMask,
              algPredict.P_REGRESSOR: filenameEstimator,
              algPredict.P_OUTPUT_REGRESSION: filename}
        runalg(alg=algPredict, io=io)

def test_Resampling():


    alg = SpatialResamplingRaster()
    io = {alg.P_GRID: enmap,
          alg.P_RASTER: hymap,
          alg.P_GDAL_RESAMPLING_ALG: 0,
          alg.P_OUTPUT_RASTER: join(outdir, 'SpatialResamplingRaster.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingMask()
    io = {alg.P_GRID: hymap,
          alg.P_MASK: enmapMask,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_OUTPUT_MASK: join(outdir, 'SpatialResamplingMask.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingClassification()
    io = {alg.P_GRID: hymap,
          alg.P_CLASSIFICATION: enmapClassification,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'SpatialResamplingClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingRegression()
    io = {alg.P_GRID: hymap,
          alg.P_REGRESSION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_OUTPUT_REGRESSION: join(outdir, 'SpatialResamplingRegression.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingFraction()
    io = {alg.P_GRID: hymap,
          alg.P_FRACTION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_FRACTION: join(outdir, 'SpatialResamplingFraction.bsq')}
    runalg(alg=alg, io=io)


def test_SensorDefinitionResampleRaster():

    alg = SensorDefinitionResampleRaster()
    io = {alg.P_RASTER: enmap,
          alg.P_OPTION1: 0,
          alg.P_OPTION2: hymap,
          alg.P_OPTION3: None,
          alg.P_ENUM: 0,
          alg.P_OUTPUT_RASTER: join(outdir, 'SensorDefinitionResampleRasterOption2.bsq')}
    runalg(alg=alg, io=io)


def test_Transformer():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, TransformerFit):
            continue

        if not algFit.displayName().endswith('PCA'):
            continue

        # fit
        filenameEstimator = join(outdir, 'Transformer{}.pkl'.format(algFit.displayName().replace(' ', '')))
        io = {algFit.P_RASTER: enmap,
              algFit.P_MASK: enmapMask,
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

def test_SynthMix():

    alg = SynthMix()
    filenameRaster = join(outdir, 'SynthMixRaster.bsq')
    filenameFraction = join(outdir, 'SynthMixFraction.bsq')
    io = {alg.P_RASTER: enmap,
          alg.P_CLASSIFICATION: enmapClassification,
          alg.P_MASK: enmapMask,
          alg.P_N: 100,
          alg.P_COMPLEXITY2LIKELIHOOD: 1.0,
          alg.P_COMPLEXITY3LIKELIHOOD: 0.0,
          alg.P_CLASSLIKELIHOODS: 0,
          alg.P_OUTPUT_RASTER: filenameRaster,
          alg.P_OUTPUT_FRACTION: filenameFraction}
    runalg(alg=alg, io=io)


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
    #test_Raster()
    #exit(0)

    test_ClassDefinitionFromRaster()
    test_Classification()
    test_ClassificationPerformance()
    test_Classifier()
    test_Clusterer()
    test_ClusteringPerformance()
    test_CreateAdditionalTestdata()
    test_ExtractSamples()
    test_Fraction()
    test_FractionPerformance()
    test_Mask()
    test_Raster()
    test_RegressionPerformance()
    test_Regressor()
    test_Resampling()
    test_SensorDefinitionResampleRaster()
    test_Transformer()
    test_VectorFromRandomPointsFromMask()
    test_VectorFromRandomPointsFromClassification()
    test_VectorUniqueValues()
    test_ImportLibrary()
    test_SynthMix()
    generateRST()

# printMenu()
print('done!!!')
