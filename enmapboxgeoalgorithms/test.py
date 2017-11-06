from __future__ import absolute_import
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
from tempfile import gettempdir
import enmapboxtestdata
from enmapboxgeoalgorithms.algorithms import *
from hubdc.progressbar import CUIProgressBar
from processing.core.SilentProgress import SilentProgress as QGISSilentProgress

class ProgressBar(QGISSilentProgress):
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
    def setLabelText(self,text):
        self.cuiProgressBar.setLabelText(text)
    def displayWarning(self,text):
        self.displayWarning(text)
    def displayError(self,text):
        self.cuiProgressBar.displayError(text)
    def displayInfo(self, text, type):
        self.cuiProgressBar.displayInfo(text, type)

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

#vectorFilename = enmapboxtestdata.landcover
#imageFilename = enmapboxtestdata.enmap
#maskFilename = join(outdir, 'mask.img')
#classificationFilename = join(outdir, 'classification.img')
#probabilityFilename = join(outdir, 'probability.img')
#regressionFilename = probabilityFilename
dummyImage = join(outdir, 'dummy.img')

def runalg(alg, io):
    print('\n##############')
    print(alg.__class__.__name__)
    processing.runalg(alg, io, progress=[None, ProgressBar(), QGISSilentProgress()][0])
    return

def test_Classification():

    filename = join(outdir, 'ClassificationFromVectorClassification.img')
    io = {'image':enmap, 'vector':vector, 'idAttribute':enmapboxtestdata.landcoverAttributes.Level_2_ID,
          'names':enmapboxtestdata.landcoverClassDefinition.level2.names,
          'lookup':enmapboxtestdata.landcoverClassDefinition.level2.lookup,
          'minOverallCoverage':1., 'minWinnerCoverage':0.5, 'oversampling':10,
          'classification':filename}
    runalg(ClassificationFromVectorClassification(), io)
    print(Classification(filename=filename))

def test_ClassificationPerformance():
    io = {'prediction':enmapClassification, 'reference':enmapClassification, 'report':join(outdir, 'ClassificationPerformanceFromClassification.html')}
    runalg(ClassificationPerformanceFromClassification(), io)

def test_ClassificationSample():
    sample = join(outdir, 'ClassificationSampleFromENVISpectralLibrary.pkl')
    io = {'envi':enmapboxtestdata.speclib, 'prefix':'level 2',
          'classificationSample':sample}
    runalg(ClassificationSampleFromENVISpectralLibrary(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleFromENVISpectralLibrary.pkl')
    io = {'probabilitySample':enmapProbabilitySample,
          'classificationSample':sample}
    runalg(ClassificationSampleFromProbabilitySample(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleSynthMix.pkl')
    io = {'classificationSample':enmapClassificationSample, 'n':100, 'complex2':1.0, 'complex3':0.0, 'option':0,
          'probabilitySample':sample}
    runalg(ClassificationSampleSynthMix(), io)
    print(ClassificationSample.unpickle(filename=sample))

    sample = join(outdir, 'ClassificationSampleFromClassification.pkl')
    io = {'image':enmap, 'classification':enmapClassification, 'mask':enmapMask,
          'classificationSample':sample}
    runalg(ClassificationSampleFromClassification(), io)
    print(ClassificationSample.unpickle(filename=sample))

def test_Classifier():
    for alg in CLASSIFIERS_GA.values()[1:]:
        model = join(outdir, 'Classifier{}.pkl'.format(alg.name.replace(' ','')))
        if alg.name in ['Fit RandomForestClassifier']:
            continue
        io = {'sample':enmapClassificationSample,
              'parameters':alg.getParameterValue('parameters'),
              'model':model}
        runalg(alg, io)
        print(model)
        print(Classifier.unpickle(filename=model))

def test_Regressor():
    for alg in REGRESSORS_GA.values():
        model = join(outdir, 'Regressor{}.pkl'.format(alg.name.replace(' ', '')))
        io = {'sample':enmapProbabilitySample,
              'parameters':alg.getParameterValue('parameters'),
              'model':model}
        runalg(alg, io)
        print(model)
        print(Regressor.unpickle(filename=model))

def test_Probability():
    filename = join(outdir, 'ProbabilityAsClassColorRGB.img')
    io = {'probability':enmapProbability, 'filterById':'', 'filterByName':'',
          'image':filename}
    runalg(ProbabilityAsClassColorRGB(), io)
    print(Image(filename=filename))

    filename = join(outdir, 'ProbabilityFromVectorClassification.img')
    io = {'image': enmap, 'vector': vector,
      'idAttribute': enmapboxtestdata.landcoverAttributes.Level_2_ID,
      'names': str(enmapboxtestdata.landcoverClassDefinition.level2.names),
      'lookup': str(enmapboxtestdata.landcoverClassDefinition.level2.lookup),
      'minOverallCoverage': 1, 'oversampling': 10, 'probability': filename}
    runalg(ProbabilityFromVectorClassification(), io)
    print(Probability(filename=filename))

def test_ProbabilitySample():

    print('!!! ProbabilitySampleSubsetClassesByName NOT WORKING !!!')
    # todo: not working
    #sample = join((outdir, 'ProbabilitySampleSubsetClassesByName.pkl'))
    #io = {'probabilitySample':enmapProbabilitySample, 'names':'Roof, Tree',
    #      'probabilitySample2':sample}
    #runalg(ProbabilitySampleSubsetClassesByName(), io)
    #print(ProbabilitySample.unpickle(filename=sample))

def test_RegressionPerformance():
    io = {'prediction':enmapProbability, 'reference':enmapProbability, 'report':join(outdir, 'RegressionPerformanceFromRegression.html')}
    runalg(RegressionPerformanceFromRegression(), io)

def test_UnsupervisedSample():
    sample = join(outdir, 'UnsupervisedSampleFromENVISpectralLibrary.pkl')
    io = {'envi':enmapboxtestdata.speclib, 'unsupervisedSample':sample}
    runalg(UnsupervisedSampleFromENVISpectralLibrary(), io)
    print(UnsupervisedSample.unpickle(filename=sample))

    sample = join(outdir, 'UnsupervisedSampleScaleFeatures.pkl')
    io = {'unsupervisedSample':enmapUnsupervisedSample, 'factor':1.,
          'unsupervisedSample2':sample}
    runalg(UnsupervisedSampleScaleFeatures(), io)
    print(UnsupervisedSample.unpickle(filename=sample))

def test_Image():

    image2 = join(outdir, 'ImageFromVector.img')
    io = {'image':enmapboxtestdata.enmap, 'vector':enmapboxtestdata.landcover, 'initValue':0, 'burnValue':1,
          'burnAttribute':enmapboxtestdata.landcoverAttributes.Level_2_ID, 'allTouched':True, 'dtype':3,
          'image2':image2}
    runalg(ImageFromVector(), io)
    print(Image(filename=image2))

def printAllAlgs():
    for key, algs in algList.algs.items():
        print(key)
        for name, alg in algs.items():
            #if not isinstance(alg, VectorClassificationRasterizeAsProbability): continue
            print(name)
            #processing.alghelp(name)

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

def run():
    pass
    #test_Classification()
    #test_ClassificationPerformance()
    #test_ClassificationSample()
    #test_Classifier()
    #test_Image()
    #test_Probability()
    #test_ProbabilitySample()
    #test_RegressionPerformance()
    #test_Regressor()
    #test_UnsupervisedSample()

if __name__ == '__main__':
    print('output directory: ' + outdir)
    run()
    #printAllAlgs()
    #printMenu()
