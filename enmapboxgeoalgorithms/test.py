from __future__ import absolute_import
import matplotlib
matplotlib.use('QT4Agg')
#from matplotlib import pyplot

# init QGIS
import processing.core.Processing
from processing.core.Processing import Processing
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
Processing.initialize()
from enmapboxgeoalgorithms.algorithms import EnMAPProvider
Processing.addProvider(EnMAPProvider())

# setup test environment
from os.path import join
from tempfile import gettempdir
import enmapboxtestdata
from enmapboxgeoalgorithms.algorithms import *
from hubdc.progressbar import CUIProgressBar
from processing.core.SilentProgress import SilentProgress as QGISSilentProgress

class ProgressBar(QGISSilentProgress):
    def __init__(self):
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

unsupervisedSampleFilename = join(outdir, 'unsupervisedSample.pkl')
classificationSampleFilename = join(outdir, 'classificationSample.pkl')
probabilitySampleFilename = join(outdir, 'probabilitySample.pkl')
regressionSampleFilename = join(outdir, 'regressionSample.pkl')
dummyPklFilename = join(outdir, 'dummy.pkl')

vectorFilename = enmapboxtestdata.landcover
imageFilename = enmapboxtestdata.enmap
maskFilename = join(outdir, 'mask.img')
classificationFilename = join(outdir, 'classification.img')
probabilityFilename = join(outdir, 'probability.img')
regressionFilename = probabilityFilename
dummyImageFilename = join(outdir, 'dummy.img')

reportFilename = join(outdir, 'report.html')


def runalg(alg, io):
    print('##############')
    print(alg.__class__.__name__)
    processing.runalg(alg, io, progress=[ProgressBar(), QGISSilentProgress()][0])
    print('')
    return

def classification_assessClassificationPerformance():
    io = {'prediction':classificationFilename, 'reference':classificationFilename, 'report':reportFilename}
    return runalg(ClassificationAssessClassificationPerformance(), io)


def classificationSample_fromENVISpectralLibrary():
    io = {'envi':enmapboxtestdata.speclib, 'prefix':'level 2', 'view':view, 'classificationSample':dummyPklFilename}
    return runalg(ClassificationSampleFromENVISpectralLibrary(), io)

def classificationSample_synthMix():
    io = {'classificationSample':classificationSampleFilename, 'n':100, 'complex2':1.0, 'complex3':0.0, 'option':0,
          'view':view, 'probabilitySample':probabilitySampleFilename}
    return runalg(ClassificationSampleSynthMix(), io)

def estimator_fit():
    for name, classifierFitGA in CLASSIFIERS_GA.items():
        assert isinstance(classifierFitGA, EnMAPGeoAlgorithm)
        io = {'sample':classificationSampleFilename,
              'parameters':classifierFitGA.getParameterFromName('parameters').default,
              'view':view, 'model':dummyPklFilename}
        return runalg(classifierFitGA, io)

def image_SampleByClassification():
    io = {'image':imageFilename, 'classification':classificationFilename, 'mask':maskFilename, 'view':view,
          'probabilitySample':dummyPklFilename}
    return runalg(ImageSampleByClassification(), io)

def probability_asClassColorRGB():
    io = {'probability':probabilityFilename, 'filterById':'', 'filterByName':'', 'image':dummyImageFilename}
    return runalg(ProbabilityAsClassColorRGB(), io)

def probabilitySample_classify():
    io = {'probabilitySample':probabilitySampleFilename, 'minOverallCoverage':1., 'minWinnerCoverage':0.5,
          'view':view, 'classificationSample':dummyPklFilename}
    return runalg(ProbabilitySampleClassify(), io)

def probabilitySample_subsetClassesByClassName():
    io = {'probabilitySample':probabilitySampleFilename, 'names':'Roof, Tree', 'view':view, 'probabilitySample2':dummyImageFilename}
    return runalg(ProbabilitySampleSubsetClassesByClassName(), io)

def regression_assessRegressionPerformance():
    io = {'prediction':regressionFilename, 'reference':regressionFilename, 'report':reportFilename}
    return runalg(RegressionAssessRegressionPerformance(), io)

def unsupervisedSample_fromENVISpectralLibrary():
    io = {'envi':enmapboxtestdata.speclib, 'view':view, 'unsupervisedSample':unsupervisedSampleFilename}
    return runalg(UnsupervisedSampleFromENVISpectralLibrary(), io)

def unsupervisedSample_scaleFeatures():
    io = {'unsupervisedSample':unsupervisedSampleFilename, 'factor':1., 'view':view, 'unsupervisedSample2':dummyPklFilename}
    return runalg(UnsupervisedSampleScaleFeatures(), io)

def vector_rasterize():

    io = {'image':enmapboxtestdata.enmap, 'vector':enmapboxtestdata.landcover, 'initValue':0, 'burnValue':1,
          'burnAttribute':enmapboxtestdata.landcoverAttributes.Level_2_ID, 'allTouched':True, 'dtype':3,
          'image2':dummyImageFilename}
    return runalg(VectorRasterize(), io)

def vectorClassification_rasterizeAsClassification():
    io = {'image':imageFilename, 'vector':vectorFilename, 'idAttribute':enmapboxtestdata.landcoverAttributes.Level_2_ID,
          'names':enmapboxtestdata.landcoverClassDefinition.level2.names,
          'lookup':enmapboxtestdata.landcoverClassDefinition.level2.lookup,
          'minOverallCoverage':1., 'minWinnerCoverage':0.5, 'oversampling':10,
          'classification':classificationFilename}
    return runalg(VectorClassificationRasterizeAsClassification(), io)

def vectorClassification_rasterizeAsProbability():
    io = {'image':imageFilename, 'vector':vectorFilename, 'idAttribute':enmapboxtestdata.landcoverAttributes.Level_2_ID,
	 'names': str(enmapboxtestdata.landcoverClassDefinition.level2.names), 'lookup': str(enmapboxtestdata.landcoverClassDefinition.level2.lookup),
     'minOverallCoverage':1, 'oversampling':10, 'probability':probabilityFilename}
    return runalg(VectorClassificationRasterizeAsProbability(), io)

def createAllTestInputs():
    classificationSample_fromENVISpectralLibrary()
    classificationSample_synthMix()
    vectorClassification_rasterizeAsClassification()
    vectorClassification_rasterizeAsProbability()

# todo test EstimatorFit, EstimatorPredict

def testAll():
    classification_assessClassificationPerformance()
    classificationSample_fromENVISpectralLibrary()
    classificationSample_synthMix()
    estimator_fit()
    image_SampleByClassification()
    probability_asClassColorRGB()
    probabilitySample_classify()
    probabilitySample_subsetClassesByClassName()
    regression_assessRegressionPerformance()
    unsupervisedSample_fromENVISpectralLibrary()
    unsupervisedSample_scaleFeatures()
    vector_rasterize()
    vectorClassification_rasterizeAsClassification()
    vectorClassification_rasterizeAsProbability()

def printAllAlgs():
    for key, algs in algList.algs.items():
        print(key)
        for name, alg in algs.items():
            if not isinstance(alg, VectorClassificationRasterizeAsProbability): continue
            print(name)
            processing.alghelp(name)

def printMenu():
    menu = dict()
    for key, algs in algList.algs.items():
        print(key)
        for name, alg in algs.items():
            if alg.group not in menu:
                menu[alg.group] = list()
            menu[alg.group].append(alg.name)
    for group in sorted(menu):
        print(group)
        for name in menu[group]:
            print('  '+name)

if __name__ == '__main__':
    print('output directory: ' + outdir)
    #printAllAlgs()
    #createAllTestInputs()
    testAll()
    #printMenu()
    #vector_rasterize()

