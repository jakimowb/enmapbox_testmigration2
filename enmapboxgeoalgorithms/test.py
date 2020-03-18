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
enmapClassification = hubflow.test_core.enmapClassification.filename()
enmapFraction = hubflow.test_core.enmapFraction.filename()
enmapMask = hubflow.test_core.enmapMask.filename()
vector = hubflow.test_core.vector.filename()


# enmapSample = join(outdir, 'enmapSample.pkl')
# enmapClassificationSample = hubflow.test_core.enmapClassificationSample


# def test_ClassDefinitionFromRaster():
#    alg = ClassDefinitionFromRaster()
#    io = {alg.P_RASTER: enmapClassification}
#    runalg(alg=alg, io=io)


def test_Classification():
    alg = ClassificationStatistics()
    io = {alg.P_CLASSIFICATION: enmapClassification}
    runalg(alg=alg, io=io)

    alg = ClassificationFromFraction()
    io = {alg.P_FRACTION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ClassificationFromFraction.bsq')}
    runalg(alg=alg, io=io)

    alg = ClassificationFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIFICATION_ATTRIBUTE: 'level_2_id',
          # alg.P_CLASS_DEFINITION: '',
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

        # cross-val perf
        algPCV = ClassifierPerformanceCrossValidation()
        io = {algPCV.P_CLASSIFIER: filenameEstimator,
              algPCV.P_NFOLD: 10,
              algPCV.P_OUTPUT_REPORT: join(outdir, 'ClassifierPerformanceCrossValidation.html')}
        runalg(alg=algPCV, io=io)

        # training perf
        algPT = ClassifierPerformanceTraining()
        io = {algPT.P_CLASSIFIER: filenameEstimator,
              algPT.P_OUTPUT_REPORT: join(outdir, 'ClassifierPerformanceTraining.html')}
        runalg(alg=algPT, io=io)


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


def test_CreateTestdata():
    alg = CreateTestClassification()
    io = {alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'CreateTestdataClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = CreateTestFraction()
    io = {alg.P_OUTPUT_FRACTION: join(outdir, 'CreateTestdataFraction.bsq')}
    runalg(alg=alg, io=io)

    alg = CreateTestClassifier()
    io = {alg.P_OUTPUT_CLASSIFIER: join(outdir, 'CreateTestdataClassifier.pkl')}
    runalg(alg=alg, io=io)

    alg = CreateTestClusterer()
    io = {alg.P_OUTPUT_CLUSTERER: join(outdir, 'CreateTestdataClusterer.pkl')}
    runalg(alg=alg, io=io)

    alg = CreateTestTransformer()
    io = {alg.P_OUTPUT_TRANSFORMER: join(outdir, 'CreateTestdataTransformer.pkl')}
    runalg(alg=alg, io=io)

    alg = CreateTestRegressor()
    io = {alg.P_OUTPUT_REGRESSOR: join(outdir, 'CreateTestdataRegressor.pkl')}
    runalg(alg=alg, io=io)


def test_ImportLibrary():
    alg = ImportLibrary()
    io = {alg.P_LIBRARY: enmapboxtestdata.library,
          alg.P_OUTPUT_RASTER: join(outdir, 'ImportLibraryRaster.bsq')}
    runalg(alg=alg, io=io)

    alg = ImportLibraryClassificationAttribute()
    io = {alg.P_LIBRARY: enmapboxtestdata.library,
          alg.P_ATTRIBUTE: 'level_2',
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ImportLibraryClassification.bsq')}
    runalg(alg=alg, io=io)

    # alg = ImportLibraryRegressionAttribute()
    # io = {alg.P_LIBRARY: enmapboxtestdata.library,
    #      alg.P_ATTRIBUTES: 'Roof, Tree',
    #      alg.P_OUTPUT_REGRESSION: join(outdir, 'ImportLibraryRegression.bsq')}
    # runalg(alg=alg, io=io)

    # alg = ImportLibraryFractionAttribute()
    # io = {alg.P_LIBRARY: enmapboxtestdata.library,
    #      alg.P_ATTRIBUTES: 'Roof, Tree',
    #      alg.P_OUTPUT_FRACTION: join(outdir, 'ImportLibraryFraction.bsq')}
    # runalg(alg=alg, io=io)


def test_Mask():
    alg = MaskBuildFromRaster()
    io = {alg.P_RASTER: enmap,
          alg.P_TRUE: '[]',
          alg.P_FALSE: '[]',
          alg.P_OUTPUT_MASK: join(outdir, 'MaskBuildFromRaster.bsq')}
    runalg(alg=alg, io=io)


def test_OpenTestMaps():
    alg = OpenTestMaps_Toolbox()
    io = {}
    runalg(alg=alg, io=io)


def test_ExtractSamples():
    # alg = ExtractOrdinationFeilhauerEtAll2014()
    # io = {alg.P_RASTER: r'C:\Work\data\hannes_feilhauer\aisa.tif',
    #       alg.P_VECTOR: r'C:\Work\data\hannes_feilhauer\plotsClean.gpkg',
    #       alg.P_OUTPUT_RASTER: join(outdir, 'ExtractOrdinationFeilhauerEtAll2014Raster.bsq'),
    #       alg.P_OUTPUT_REGRESSION: join(outdir, 'ExtractOrdinationFeilhauerEtAll2014Regression.bsq'),
    #       alg.P_OUTPUT_VECTOR: join(outdir, 'ExtractOrdinationFeilhauerEtAll2014Vector.gpkg')}
    # runalg(alg=alg, io=io)

    alg = ExtractSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq')}
    runalg(alg=alg, io=io)

    assert exists(join(outdir, 'CreateTestdataClassification.bsq'))
    alg = ExtractClassificationSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_CLASSIFICATION: join(outdir, 'CreateTestdataClassification.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'ExtractSamplesClassification.bsq')}
    runalg(alg=alg, io=io)

    assert exists(join(outdir, 'CreateTestdataFraction.bsq'))
    alg = ExtractRegressionSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_REGRESSION: join(outdir, 'CreateTestdataFraction.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_REGRESSION: join(outdir, 'ExtractSamplesRegression.bsq')}
    runalg(alg=alg, io=io)

    alg = ExtractFractionSamples()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_FRACTION: join(outdir, 'CreateTestdataFraction.bsq'),
          alg.P_OUTPUT_RASTER: join(outdir, 'ExtractSamplesRaster.bsq'),
          alg.P_OUTPUT_FRACTION: join(outdir, 'ExtractSamplesFractions.bsq')}
    runalg(alg=alg, io=io)


def test_Fraction():
    alg = FractionFromVectorClassification()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_CLASSIFICATION_ATTRIBUTE: 'level_3_id',
          alg.P_MIN_OVERALL_COVERAGE: 0.,
          alg.P_MIN_DOMINANT_COVERAGE: 0.,
          alg.P_OVERSAMPLING: 10,
          alg.P_OUTPUT_FRACTION: join(outdir, 'FractionFromVectorClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = FractionFromClassification()
    io = {alg.P_CLASSIFICATION: enmapClassification,
          alg.P_OUTPUT_FRACTION: join(outdir, 'FractionFromClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = FractionAsClassColorRGB()
    io = {alg.P_FRACTION: enmapFraction,
          alg.P_OUTPUT_RASTER: join(outdir, 'FractionAsClassColorRGB.bsq')}
    runalg(alg=alg, io=io)


def test_FractionPerformance():
    alg = FractionPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapFraction,
          alg.P_REFERENCE: enmapClassification,
          alg.P_OUTPUT_REPORT: join(outdir, 'FractionPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_RasterBandSubsetting():
    filename = join(outdir, 'RasterBandSubsetting', 'tmp.bsq')
    print(filename)
    raster = RasterDataset.fromArray(array=np.zeros(shape=(5, 10, 10)), filename=filename)
    for i, band in enumerate(raster.bands()):
        band.setDescription(f'B{i + 1}')
    # set bad bands list (the bad band multiplier values of each band in an image, typically 0 for bad bands and 1 for good bands)
    raster.setMetadataItem(key='bbl', value=[0, 0, 1, 1, 1], domain='ENVI')
    raster.close()

    alg = RasterBandSubsetting()
    io = {alg.P_RASTER: filename,
          alg.P_STRING_LIST: '',
          alg.P_BBL: True,
          alg.P_BOOLEAN: False,
          alg.P_OUTPUT_RASTER: join(outdir, 'RasterBandSubsetting.bsq'),
          }
    result = runalg(alg=alg, io=io)

    outraster = Raster(filename=result[alg.P_OUTPUT_RASTER])
    assert outraster.dataset().zsize() == 3
    bandNames = ['B3', 'B4', 'B5']
    for bandName, band in zip(bandNames, outraster.dataset().bands()):
        assert bandName == band.description()

def test_RasterConvolve():
    assert exists(join(outdir, 'CreateTestdataFraction.bsq'))
    for alg in ALGORITHMS:
        if isinstance(alg, RasterConvolve):
            io = {alg.P_RASTER: join(outdir, 'CreateTestdataFraction.bsq'),  # enmap, EnMAP to slow
                  alg.P_CODE: alg.code(),
                  alg.P_OUTPUT_RASTER: join(outdir, 'RasterConvolve' + alg.name())}
            runalg(alg=alg, io=io)
            break

def test_Raster():
    test_RasterBandSubsetting()

    alg = RasterStatistics()
    io = {alg.P_RASTER: enmap,
          alg.P_BAND: 1}
    runalg(alg=alg, io=io)

    alg = RasterStatistics()
    io = {alg.P_RASTER: enmap,
          alg.P_BAND: 1}
    runalg(alg=alg, io=io)

    for alg in ALGORITHMS:
        if isinstance(alg, RasterApplySpatial):
            io = {alg.P_RASTER: enmap,
                  alg.P_CODE: alg.code(),
                  alg.P_OUTPUT_RASTER: join(outdir, 'RasterApplySpatial' + alg.name())}
            runalg(alg=alg, io=io)
            break

    test_RasterConvolve()

    alg = RasterUniqueValues()
    io = {alg.P_RASTER: enmapClassification,
          alg.P_BAND: 1}
    runalg(alg=alg, io=io)

    alg = RasterApplyMask()
    io = {alg.P_RASTER: enmap,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_OUTPUT_RASTER: join(outdir, 'RasterApplyMask.bsq')}
    runalg(alg=alg, io=io)

    alg = RasterFromVector()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: enmapboxtestdata.landcover_polygons,
          alg.P_INIT_VALUE: 0,
          alg.P_BURN_VALUE: 1,
          alg.P_BURN_ATTRIBUTE: 'level_2_id',
          alg.P_ALL_TOUCHED: True,
          alg.P_FILTER_SQL: '',
          alg.P_DATA_TYPE: 3,
          alg.P_NO_DATA_VALUE: 'None',
          alg.P_OUTPUT_RASTER: join(outdir, 'RasterFromVector.bsq')}
    runalg(alg=alg, io=io)


def test_Map():
    alg = MapViewMetadata()
    io = {alg.P_MAP: enmap}
    runalg(alg=alg, io=io)

    io = {alg.P_MAP: vector}
    runalg(alg=alg, io=io)


def test_Regression():
    alg = RegressionFromVectorRegression()
    io = {alg.P_GRID: enmap,
          alg.P_VECTOR: vector,
          alg.P_REGRESSION_ATTRIBUTE: 'level_2_id',
          alg.P_NO_DATA_VALUE: -1,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_OVERSAMPLING: 1,
          alg.P_OUTPUT_REGRESSION: join(outdir, 'RegressionFromVectorRegression.bsq')}
    runalg(alg=alg, io=io)


def test_RegressionSample():
    from enmapboxtestdata.artmo import directional_reflectance
    alg = RegressionSampleFromArtmo()
    io = {alg.P_FILE: directional_reflectance,
          alg.P_OUTPUT_RASTER: join(outdir, 'RegressionSampleFromArtmo.raster.bsq'),
          alg.P_OUTPUT_REGRESSION: join(outdir, 'RegressionSampleFromArtmo.regression.bsq')}
    runalg(alg=alg, io=io)


def test_RegressionPerformance():
    alg = RegressionPerformanceFromRaster()
    io = {alg.P_PREDICTION: enmapFraction,
          alg.P_REFERENCE: enmapFraction,
          alg.P_MASK: enmapMask,
          alg.P_INVERT_MASK: False,
          alg.P_OUTPUT_REPORT: join(outdir, 'RegressionPerformanceFromRaster.html')}
    runalg(alg=alg, io=io)


def test_Regressor():
    for algFit in ALGORITHMS:

        if not isinstance(algFit, RegressorFit):
            continue

        # if not algFit.displayName().endswith('RandomForestRegressor'):
        #        if not algFit.displayName().endswith('LinearRegression'):
        if not algFit.displayName().endswith('PLSRegression'):
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

        # cross-val perf
        algPCV = RegressorPerformanceCrossValidation()
        io = {algPCV.P_REGRESSOR: filenameEstimator,
              algPCV.P_NFOLD: 10,
              algPCV.P_OUTPUT_REPORT: join(outdir, 'RegressorPerformanceCrossValidation.html')}
        runalg(alg=algPCV, io=io)

        # training perf
        algPT = RegressorPerformanceTraining()
        io = {algPT.P_REGRESSOR: filenameEstimator,
              algPT.P_OUTPUT_REPORT: join(outdir, 'RegressorPerformanceTraining.html')}
        runalg(alg=algPT, io=io)


def test_Resampling():
    alg = SpatialResamplingRaster()
    io = {alg.P_GRID: enmap,
          alg.P_RASTER: enmap,
          alg.P_GDAL_RESAMPLING_ALG: 0,
          alg.P_OUTPUT_RASTER: join(outdir, 'SpatialResamplingRaster.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingMask()
    io = {alg.P_GRID: enmap,
          alg.P_MASK: enmapMask,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_OUTPUT_MASK: join(outdir, 'SpatialResamplingMask.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingClassification()
    io = {alg.P_GRID: enmap,
          alg.P_CLASSIFICATION: enmapClassification,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_CLASSIFICATION: join(outdir, 'SpatialResamplingClassification.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingRegression()
    io = {alg.P_GRID: enmap,
          alg.P_REGRESSION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_OUTPUT_REGRESSION: join(outdir, 'SpatialResamplingRegression.bsq')}
    runalg(alg=alg, io=io)

    alg = SpatialResamplingFraction()
    io = {alg.P_GRID: enmap,
          alg.P_FRACTION: enmapFraction,
          alg.P_MIN_OVERALL_COVERAGE: 0.5,
          alg.P_MIN_DOMINANT_COVERAGE: 0.5,
          alg.P_OUTPUT_FRACTION: join(outdir, 'SpatialResamplingFraction.bsq')}
    runalg(alg=alg, io=io)


def test_SensorDefinitionResampleRaster():
    alg = SensorDefinitionResampleRaster()
    io = {alg.P_RASTER: enmap,
          alg.P_OPTION1: 1,
          alg.P_OPTION2: None,
          alg.P_OPTION3: None,
          alg.P_ENUM: 0,
          alg.P_OUTPUT_RASTER: join(outdir, 'SensorDefinitionResampleRasterOption1.bsq')}
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
        if hasNoInverseTransform:
            continue

        filename = join(outdir, 'TransformerInverseTransform{}.bsq'.format(algInverse.displayName().split()[1]))
        io = {algInverse.P_RASTER: filenameTransformation,
              algInverse.P_MASK: enmapMask,
              algInverse.P_TRANSFORMER: filenameEstimator,
              algInverse.P_OUTPUT_RASTER: filename}
        runalg(alg=algInverse, io=io)


def test_VectorFromRandomPointsFromMask():
    alg = VectorFromRandomPointsFromMask()

    for n in [100, 0.1]:
        io = {alg.P_MASK: enmapMask,
              alg.P_INVERT_MASK: False,
              alg.P_NUMBER_OF_POINTS: n,
              alg.P_OUTPUT_VECTOR: join(outdir, 'VectorFromRandomPointsFromMask.gpkg')}
        runalg(alg=alg, io=io)


def test_VectorFromRandomPointsFromClassification():
    alg = VectorFromRandomPointsFromClassification()
    io = {alg.P_CLASSIFICATION: enmapClassification,
          alg.P_NUMBER_OF_POINTS_PER_CLASS: 0.1,
          alg.P_OUTPUT_VECTOR: join(outdir, 'VectorFromRandomPointsFromClassification.gpkg')}
    runalg(alg=alg, io=io)


def test_VectorUniqueValues():
    alg = VectorUniqueValues()
    io = {alg.P_VECTOR: enmapboxtestdata.landcover_polygons,
          alg.P_FIELD: 'level_2'}
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

    test_RasterConvolve()
    exit()

    test_Classification()
    test_ClassificationPerformance()
    test_Classifier()
    test_Clusterer()
    test_ClusteringPerformance()
    test_CreateTestdata()
    test_ExtractSamples()
    test_Fraction()
    test_FractionPerformance()
    test_Map()
    test_Mask()
    # test_OpenTestMaps() not possible to test here, because it needs QGIS iface
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

    generateRST()

# printMenu()
print('done!!!')
