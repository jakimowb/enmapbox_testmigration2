from __future__ import absolute_import

# change working directory to prevent creation of "processing" directory, which corrupts the imports
import os, tempfile
outdir = os.path.join(tempfile.gettempdir(), 'eb_test')
if not os.path.exists(outdir):
    os.mkdir(outdir)
os.chdir(outdir)

import qgis.PyQt
import time

tic = time.time


def toc(t0):
    print('{} sec'.format(int(tic() - t0)))


import matplotlib
matplotlib.use('QT4Agg')
import hubflow.test


# init QGIS
import processing.core.Processing
from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.alglist import algList
from qgis.core import QgsApplication


# - temporarily overwrite Processing.addProvider() to prevent loading external providers
class Processing_(Processing):
    @staticmethod
    def addProvider(provider, updateList=True): return


processing.core.Processing.Processing = Processing_

QgsApplication.setGraphicsSystem('raster')
qgsApp = QgsApplication([], True)
qgsApp.initQgis()

# load Enmap-Box TestProvider
from enmapboxgeoalgorithms.algorithms import ALGORITHMS


class EnMAPProvider(AlgorithmProvider):
    def getName(self):
        return 'EBTest'

    def getDescription(self):
        return 'EnMAP-Box TestProvider'

    def _loadAlgorithms(self):
        self.algs.extend(ALGORITHMS)


Processing.initialize()
Processing.addProvider(EnMAPProvider())

# setup test environment
from os.path import join, exists
import os
from tempfile import gettempdir
import enmapboxtestdata
from enmapboxgeoalgorithms.algorithms import *
from hubdc.progressbar import CUIProgressBar
from processing.core.SilentProgress import SilentProgress as QGISSilentProgress


'''class ProgressBar(QGISSilentProgress):
    def __init__(self):
        QGISSilentProgress.__init__(self)
        self.cuiProgressBar = CUIProgressBar()

    def error(self, msg):
        self.cuiProgressBar.displayError(msg)

    def setText(self, text):
        self.cuiProgressBar.setLabelText(text)

    def setPercentage(self, i):
        self.cuiProgressBar.setProgress(i)

    def setInfo(self, msg):
        self.cuiProgressBar.displayInfo(msg)

    def setCommand(self, msg):
        self.cuiProgressBar.setLabelText(msg)

    def setDebugInfo(self, msg):
        self.cuiProgressBar.displayInfo(msg, type='DEBUG ')

    def setConsoleInfo(self, msg):
        self.cuiProgressBar.displayInfo(msg, type='CONSOLE ')

    def close(self):
        pass

    def setTotalSteps(self, steps):
        self.cuiProgressBar.setTotalSteps(steps)

    def setProgress(self, progress):
        self.cuiProgressBar.setProgress(progress)

    def setLabelText(self, text):
        self.cuiProgressBar.setLabelText(text)

    def displayWarning(self, text):
        self.displayWarning(text)

    def displayError(self, text):
        self.cuiProgressBar.displayError(text)

    def displayInfo(self, text, type):
        self.cuiProgressBar.displayInfo(text, type)'''


outdir = join(gettempdir(), 'eb_test')
view = False

enmap = hubflow.test.enmap.filename
enmapClassification = hubflow.test.enmapClassification.filename
enmapProbability = hubflow.test.enmapProbability.filename
enmapMask = hubflow.test.enmapMask.filename
vector = hubflow.test.vector.filename

enmapUnsupervisedSample = join(outdir, 'enmapUnsupervisedSample.pkl')
hubflow.test.enmapUnsupervisedSample.pickle(filename=enmapUnsupervisedSample)

enmapClassificationSample = join(outdir, 'enmapClassificationSample.pkl')
hubflow.test.enmapClassificationSample.pickle(filename=enmapClassificationSample)

enmapRegressionSample = join(outdir, 'enmapRegressionSample.pkl')
hubflow.test.enmapProbabilitySample.pickle(filename=enmapRegressionSample)

enmapProbabilitySample = join(outdir, 'enmapProbabilitySample.pkl')
hubflow.test.enmapProbabilitySample.pickle(filename=enmapProbabilitySample)

dummyPickle = join(outdir, 'dummy.pkl')

# vectorFilename = enmapboxtestdata.landcover
# imageFilename = enmapboxtestdata.enmap
# maskFilename = join(outdir, 'mask.img')
# classificationFilename = join(outdir, 'classification.img')
# probabilityFilename = join(outdir, 'probability.img')
# regressionFilename = probabilityFilename
dummyImage = join(outdir, 'dummy.img')


def runalg(alg, io, info=None):
    print('\n##############')
    print(alg.__class__.__name__)
    if info is not None:
        print(info)
    processing.runalg(alg, io, progress=None) #[None, ProgressBar(), QGISSilentProgress()][0])


def test_Classification():
    filename = join(outdir, 'ClassificationFromVectorClassification.img')
    io = {'raster': enmap, 'vector': vector, 'idAttribute': enmapboxtestdata.landcoverAttributes.Level_2_ID,
          'names': enmapboxtestdata.landcoverClassDefinition.level2.names,
          'lookup': enmapboxtestdata.landcoverClassDefinition.level2.lookup,
          'minOverallCoverage': 1., 'minWinnerCoverage': 0.5, 'oversampling': 10,
          'classification': filename}
    runalg(ClassificationFromVectorClassification(), io)
    print(Classification(filename=filename))


def test_ClassificationPerformance():
    io = {'prediction': enmapClassification, 'reference': enmapClassification,
          'report': join(outdir, 'ClassificationPerformanceFromClassification.html')}
    runalg(ClassificationPerformanceFromRaster(), io)


def test_ClassificationSample():
    sample = join(outdir, 'ClassificationSampleFromProbability.pkl')
    io = {'raster': enmap, 'probability': enmapProbability, 'mask': enmapMask,
          'classificationSample': sample}
    runalg(ClassificationSampleFromProbability(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleFromENVISpectralLibrary.pkl')
    io = {'envi': enmapboxtestdata.speclib, 'prefix': 'level 2',
          'classificationSample': sample}
    runalg(ClassificationSampleFromENVISpectralLibrary(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleFromProbabilitySample.pkl')
    io = {'probabilitySample': enmapProbabilitySample,
          'classificationSample': sample,
          'minOverallCoverage': 0.0,
          'minWinnerCoverage': 0.0}
    runalg(ClassificationSampleFromProbabilitySample(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleSynthMix.pkl')
    io = {'classificationSample': enmapClassificationSample, 'n': 100, 'complex2': 1.0, 'complex3': 0.0, 'option': 0,
          'probabilitySample': sample}
    runalg(ClassificationSampleSynthMix(), io)
    print(ProbabilitySample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleFromClassification.pkl')
    io = {'raster': enmap, 'classification': enmapClassification, 'mask': enmapMask,
          'classificationSample': sample}
    runalg(ClassificationSampleFromRasterAndClassification(), io)
    print(ClassificationSample.unpickle(filename=sample))


def test_Classifier():
    for alg in CLASSIFIERS_GA.values():

        if not alg.name.endswith('RandomForestClassifier'): continue

        # fit
        model = join(outdir, 'Classifier{}.pkl'.format(alg.name.replace(' ', '')))
        io = {'sample': enmapClassificationSample,
              'parameters': alg.getParameterValue('parameters'),
              'model': model}
        runalg(alg, io, info=alg.name)
        print(model)
        print(Classifier.unpickle(filename=model))

        # predict
        prediction = join(outdir, 'ClassifierPredict{}.img'.format(alg.name.split()[1]))
        io = {'raster': enmap, 'mask': enmapMask, 'model': model,
              'prediction': prediction}
        runalg(EstimatorPredict(group=CLASSIFIERS_GROUP), io)
        print(Classification(filename=prediction))

        # predict probability
        if not alg.name.endswith('RandomForestClassifier'): continue
        probability = join(outdir, 'ClassifierPredictProbability{}.img'.format(alg.name.split()[1]))
        io = {'raster': enmap, 'mask': enmapMask, 'model': model,
              'prediction': probability}
        runalg(EstimatorPredictProbability(), io)
        print(Probability(filename=probability))


def test_Clusterer():
    for alg in CLUSTERERS_GA.values():

        if not alg.name.endswith('KMeans'): continue

        t0 = tic()
        model = join(outdir, 'Clusterer{}.pkl'.format(alg.name.replace(' ', '')))
        io = {'sample': enmapProbabilitySample,
              'parameters': alg.getParameterValue('parameters'),
              'model': model}
        runalg(alg, io, info=alg.name)
        print(Clusterer.unpickle(filename=model))
        toc(t0)

        # predict
        prediction = join(outdir, 'ClustererPredict{}.img'.format(alg.name.split()[1]))
        io = {'raster': enmap, 'mask': enmapMask, 'model': model,
              'prediction': prediction}
        runalg(EstimatorPredict(group=CLUSTERERS_GROUP), io)
        print(Classification(filename=prediction))


def test_ClusteringPerformance():
    io = {'prediction': enmapClassification, 'reference': enmapClassification,
          'report': join(outdir, 'ClusteringPerformanceFromRaster.html')}
    runalg(ClusteringPerformanceFromRaster(), io)


def test_MaskFromRaster():
    io = {'raster': enmap, 'mask': join(outdir, 'MaskFromRaster.img')}
    runalg(MaskBuildFromRaster(), io)


def test_Probability():
    filename = join(outdir, 'ProbabilityAsClassColorRGB.img')
    io = {'probability': enmapProbability, 'filterById': '[]', 'filterByName': '[]',
          'raster': filename}
    runalg(ProbabilityAsClassColorRGB(), io)
    print(Raster(filename=filename))

    filename = join(outdir, 'ProbabilityFromVectorClassification.img')
    io = {'raster': enmap, 'vector': vector,
          'idAttribute': enmapboxtestdata.landcoverAttributes.Level_2_ID,
          'names': str(enmapboxtestdata.landcoverClassDefinition.level2.names),
          'lookup': str(enmapboxtestdata.landcoverClassDefinition.level2.lookup),
          'minOverallCoverage': 0.5, 'oversampling': 10, 'probability': filename}
    runalg(ProbabilityFromVectorClassification(), io)
    print(Probability(filename=filename))


def test_ProbabilityPerformance():
    io = {'prediction': enmapProbability, 'reference': enmapClassification,
          'report': join(outdir, 'ProbabilityPerformanceFromRaster.html')}
    runalg(ProbabilityPerformanceFromRaster(), io)


def test_ProbabilitySample():
    sample = join(outdir, 'ProbabilitySampleFromClassification.pkl')
    io = {'raster': enmap, 'classification': enmapClassification, 'mask': enmapMask,
          'probabilitySample': sample}
    runalg(ProbabilitySampleFromClassification(), io)
    print(ProbabilitySample.unpickle(filename=sample))

    sample = join(outdir, 'ProbabilitySampleFromProbability.pkl')
    io = {'raster': enmap, 'probability': enmapProbability, 'mask': enmapMask,
          'probabilitySample': sample}
    runalg(ProbabilitySampleFromProbability(), io)
    print(ProbabilitySample.unpickle(filename=sample))


def test_Raster():
    maskedRaster = join(outdir, 'RasterApplyMask.img')
    io = {'raster': enmap, 'mask': enmapMask, 'fillValue': 0, 'maskedRaster': maskedRaster}
    runalg(RasterApplyMask(), io)
    print(Raster(filename=maskedRaster))

    raster2 = join(outdir, 'RasterFromVector.img')
    io = {'raster': enmap, 'vector': enmapboxtestdata.landcover, 'initValue': 0, 'burnValue': 1,
          'burnAttribute': enmapboxtestdata.landcoverAttributes.Level_2_ID, 'allTouched': True, 'dtype': 3,
          'raster2': raster2}
    runalg(RasterFromVector(), io)
    print(Raster(filename=raster2))


def test_RegressionPerformance():
    io = {'prediction': enmapProbability, 'reference': enmapProbability,
          'report': join(outdir, 'RegressionPerformanceFromRegression.html')}
    runalg(RegressionPerformanceFromRaster(), io)


def test_RegressionSample():
    sample = join(outdir, 'RegressionSampleFromRegression.pkl')
    io = {'raster': enmap, 'regression': enmapProbability,# 'mask': enmapMask,
          'regressionSample': sample}
    runalg(RegressionSampleFromRegression(), io)
    print(RegressionSample.unpickle(filename=sample))


def test_Regressor():
    for alg in REGRESSORS_GA.values():

        if not alg.name.endswith('RandomForestRegressor'): continue

        t0 = tic()
        model = join(outdir, 'Regressor{}.pkl'.format(alg.name.replace(' ', '')))
        io = {'sample': enmapProbabilitySample,
              'parameters': alg.getParameterValue('parameters'),
              'model': model}
        runalg(alg, io, info=alg.name)
        print(model)
        print(Regressor.unpickle(filename=model))
        toc(t0)

        # predict
        prediction = join(outdir, 'RegressorPredict{}.img'.format(alg.name.split()[1]))
        io = {'raster': enmap, 'mask': enmapMask, 'model': model,
              'prediction': prediction}
        runalg(EstimatorPredict(group=REGRESSORS_GROUP), io)
        print(Regression(filename=prediction))


def test_Testdata():
    io = {'enmap': '', 'hymap': '', 'landcover': '', 'speclib': ''}
    runalg(OpenTestdata(), io)

    io = {'enmap': '', 'landcover': '', 'speclib': ''}
    runalg(OpenTestdataFull(), io)

    io = {'classification': join(outdir, 'CreateAdditionalTestdataClassification.img'),
          'probability': join(outdir, 'CreateAdditionalTestdataProbability.img'),
          'unsupervisedSample': join(outdir, 'CreateAdditionalTestdataUnsupervisedSample.img'),
          'classificationSample': join(outdir, 'CreateAdditionalTestdataClassificationSample.img'),
          'probabilitySample': join(outdir, 'CreateAdditionalTestdataProbabilitySample.img'),
          'regressionSample': join(outdir, 'CreateAdditionalTestdataRegressionSample.img')}
    runalg(CreateAdditionalTestdata(), io)


def test_Transformers():
    for alg in TRANSFORMERS_GA.values():

        if not alg.name.endswith(' PCA'): continue

        model = join(outdir, 'Transformers{}.pkl'.format(alg.name.replace(' ', '')))
        io = {'sample': enmapProbabilitySample,
              'parameters': alg.getParameterValue('parameters'),
              'model': model}
        runalg(alg, io, info=alg.name)
        print(model)
        print(Transformer.unpickle(filename=model))

        # transform
        transformation = join(outdir, 'TransformerTransform{}.img'.format(alg.name.split()[1]))
        io = {'raster': enmap, 'mask': enmapMask, 'model': model,
              'transformation': transformation}
        runalg(EstimatorTransform(), io)
        print(Raster(filename=transformation))

        hasNoInverseTransform = False
        for name in ['SparsePCA', 'Imputer', 'FactorAnalysis', 'Normalizer', 'FeatureAgglomeration']:
            if alg.name.endswith(name):
                hasNoInverseTransform = True

        if hasNoInverseTransform: continue

        # inverse transform
        inverseTransformation = join(outdir, 'TransformerInverseTransform{}.img'.format(alg.name.split()[1]))
        io = {'transformation': transformation, 'mask': enmapMask, 'model': model,
              'inverseTransformation': inverseTransformation}
        runalg(EstimatorInverseTransform(), io)
        print(Raster(filename=inverseTransformation))


def test_UnsupervisedSample():
    sample = join(outdir, 'UnsupervisedSampleFromENVISpectralLibrary.pkl')
    io = {'envi': enmapboxtestdata.speclib, 'unsupervisedSample': sample}
    runalg(UnsupervisedSampleFromENVISpectralLibrary(), io)
    print(UnsupervisedSample.unpickle(filename=sample))

    sample = join(outdir, 'UnsupervisedSampleScaleFeatures.pkl')
    io = {'unsupervisedSample': enmapUnsupervisedSample, 'factor': 1.,
          'unsupervisedSample2': sample}
    runalg(UnsupervisedSampleScaleFeatures(), io)
    print(UnsupervisedSample.unpickle(filename=sample))


def test_VectorFromRandomPointsFromMask():
    vector = join(outdir, 'VectorFromRandomPointsFromMask.gpkg')
    io = {'mask': enmapMask, 'n': 100,
          'vector': vector}
    runalg(VectorFromRandomPointsFromMask(), io)
    print(Vector(filename=vector))


def test_defaultOutputFilenames():
    maskedRaster = join(outdir, 'RasterApplyMask.bsq')
    io = {'maskedRaster': maskedRaster}
    runalg(TEST(), io)


def test_generateRST():
    # generate GeoAlgorithms RST files
    generateRST()

def test_outdir():
    print(outdir)


def printAllAlgs():
    for key, algs in algList.algs.items():
        print(key)
        for name, alg in algs.items():
            # if not isinstance(alg, VectorClassificationRasterizeAsProbability): continue
            print(name)
            # processing.alghelp(name)


def printMenu():
    menu = dict()
    for key, algs in algList.algs.items():
        print(key)
        for name, alg in algs.items():
            if alg.group not in menu:
                menu[alg.group] = list()
            menu[alg.group].append((alg.name, alg.__class__.__name__))
    for group in sorted(menu):
        print(group)
        for name, className in sorted(menu[group]):
            print('  {} ({})'.format(name, className))
