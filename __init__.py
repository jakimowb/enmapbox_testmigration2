import os
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *
from processing.core.outputs import *
from hubflow.types import *

def getPlugInVersion():
    with open(os.path.join(os.path.dirname(__file__), 'metadata.txt')) as f:
        for line in f:
            if line.startswith('version='):
                return line.split('=')[1].strip()

__version__ = getPlugInVersion()

def classFactory(iface):
    return Plugin(iface)


class Plugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.provider = Provider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)

ALGORITHMS = list()
class Provider(AlgorithmProvider):

    def getName(self):
        return 'EnMAP-Box TestProvider (v'+__version__+')'

    def getDescription(self):
        return 'EnMAP-Box TestProvider (v'+__version__+')'

    def _loadAlgorithms(self):
        self.algs.extend(ALGORITHMS)

class OpenTestdata(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Open Testdata'
        self.group = 'Open'

        self.addOutput(OutputRaster('enmap', 'EnMAP (30m; 244 bands)'))
        self.addOutput(OutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)'))
        self.addOutput(OutputVector('landcover', 'LandCover Layer'))
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm(self, progress):

        import enmaptestdata
        self.setOutputValue('enmap', enmaptestdata.enmap)
        self.setOutputValue('hymap', enmaptestdata.hymap)
        self.setOutputValue('landcover', enmaptestdata.landcover)
        self.setOutputValue('speclib', enmaptestdata.speclib)

    def help(self):
        return True, 'Open EnMAP-Box Testdata'
ALGORITHMS.append(OpenTestdata())

class UnsupervisedSampleFromENVISpectralLibrary(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Import ENVI Spectral Library'
        self.group = 'Import'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('sample', 'UnsupervisedSample', ext='pkl'))

    def processAlgorithm(self, progressBar):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
        sample.pickle(filename=self.getOutputValue('sample'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns an UnsupervisedSample imported from an ENVI Spectral Library file.'
ALGORITHMS.append(UnsupervisedSampleFromENVISpectralLibrary())

class UnsupervisedSampleClassifyByClassName(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classify Sample By Class Name'
        self.group = 'Sample'

        self.addParameter(ParameterFile('sample', 'Sample', optional=False))
        self.addParameter(ParameterString('prefix', 'ClassDefinition prefix', default=''))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('csample', 'ClassificationSample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        unsupervisedSample = UnsupervisedSample.unpickle(filename=self.getParameterValue('sample'))
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

        classificationSample.pickle(filename=self.getOutputValue('csample'))
        if self.getParameterValue('view'):
            classificationSample.browse()

    def help(self):
        return True, 'Returns a ClassificationSample. The input Sample is classified by using a ClassDefinition that must be provided inside the Sample metatdata'+\
                     '(i.e. <i>prefix</i> class names, <i>prefix</i> class lookup, <i>prefix</i> class names, <i>prefix</i> class spectra names).'
ALGORITHMS.append(UnsupervisedSampleClassifyByClassName())

#        classificationSample.scaleFeaturesInplace(factor=10000.)

class UnsupervisedSampleScaleFeatures(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Scale Sample Features'
        self.group = 'Sample'

        self.addParameter(ParameterFile('sample', 'Sample', optional=False))
        self.addParameter(ParameterNumber('factor', 'Scale factor', default=1.))
        self.addParameter(ParameterBoolean('view', 'View result', default=True))
        self.addOutput(OutputFile('outsample', 'Scaled Sample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        sample = UnsupervisedSample.unpickle(filename=self.getParameterValue('sample'))
        sample.scaleFeaturesInplace(factor=self.getParameterValue('factor'))
        sample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            sample.browse()

    def help(self):
        return True, 'Returns a Sample with scaled features.'
ALGORITHMS.append(UnsupervisedSampleScaleFeatures())

class ClassificationSampleSynthMix(GeoAlgorithm):
    options = ['proportional', 'equalized']
    def defineCharacteristics(self):
        self.name = 'Generate synthetically mixed ProbabilitySample'
        self.group = 'Sample'

        self.addParameter(ParameterFile('csample', 'ClassificationSample', optional=False))
        self.addParameter(ParameterNumber('n', 'n', default=1000))
        self.addParameter(ParameterNumber('complex2', 'Likelihood for mixing complexity 2', default=1.0))
        self.addParameter(ParameterNumber('complex3', 'Likelihood for mixing complexity 3', default=0.0))
        self.addParameter(ParameterSelection('option', 'Class likelihoods', options=self.options, default=0))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('outsample', 'ProbabilitySample', ext='pkl'))

    def processAlgorithm(self, progressBar):

        classificationSample = ClassificationSample.unpickle(filename=self.getParameterValue('csample'))
        mixingComplexities = {2:self.getParameterValue('complex2'), 3:self.getParameterValue('complex3')}
        probabilitySample = classificationSample.synthMix(mixingComplexities=mixingComplexities,
                                                          classLikelihoods=self.options[self.getParameterValue('option')],
                                                          n=self.getParameterValue('n'))
        probabilitySample.pickle(filename=self.getOutputValue('outsample'))
        if self.getParameterValue('view'):
            probabilitySample.browse()

    def help(self):
        return True, 'Returns a synthetically mixed ProbabilitySample.'
ALGORITHMS.append(ClassificationSampleSynthMix())

class EstimatorFit(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = TMP_NAME + ' Fit'
        self.group = TMP_GROUP

        if self.group == REGRESSORS_GROUP:
            self.addParameter(ParameterFile('sample', 'RegressionSample', optional=False))
        else:
            assert 0
        self.addParameter(ParameterString('parameters', 'Parameters', TMP_ESTIMATOR, multiline=True))
        self.addParameter(ParameterBoolean('view', 'View Result', default=True))
        self.addOutput(OutputFile('model', 'Fitted Model', ext='pkl'))

    def processAlgorithm(self, progressBar):
        if TMP_GROUP == REGRESSORS_GROUP:
            sample = RegressionSample.unpickle(filename=self.getParameterValue('sample'))
        sklEstimator = eval(self.getParameterValue('parameters'))
        estimator = Regressor(sklEstimator=sklEstimator)
        estimator.fit(sample=sample)
        estimator.pickle(filename=self.getOutputValue('model'))
        if self.getParameterValue('view'):
            estimator.browse()

    def help(self):
        if TMP_GROUP == REGRESSORS_GROUP:
            return True, 'Returns a Regressor fittet on a RegressionSample.'

class EstimatorPredict(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = TMP_GROUP[:-1] + ' Predict'
        self.group = 'Estimator'

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(ParameterVector('vmask', 'VectorMask', optional=True))
        if TMP_GROUP == REGRESSORS_GROUP:
            self.addParameter(ParameterFile('model', 'Regressor model', optional=False))
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progressBar):
        if TMP_GROUP == REGRESSORS_GROUP:
            estimator = Regressor.unpickle(filename=self.getParameterValue('model'))
        image = Image(filename=self.getParameterValue('image'))
        mask = Mask(filename=self.getParameterValue('mask'))
        vmask = VectorMask(filename=self.getParameterValue('vmask'), allTouched=True)
        estimator.predict(filename=self.getOutputValue('prediction'), image=image, mask=mask, vmask=vmask)

    def help(self):
        if TMP_GROUP == REGRESSORS_GROUP:
            return True, 'Returns a Regression.'


from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler, Normalizer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR, SVC, LinearSVR, LinearSVC, NuSVR, NuSVC

REGRESSORS_GROUP = 'Regressors'
REGRESSORS = dict()
REGRESSORS['RandomForestRegressor'] = \
'''RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=None,
                         max_features='auto', max_leaf_nodes=None,
                         min_impurity_split=1e-07, min_samples_leaf=1,
                         min_samples_split=2, min_weight_fraction_leaf=0.0,
                         n_estimators=10, n_jobs=1, oob_score=False, random_state=None,
                         verbose=0, warm_start=False)'''

TMP_GROUP = REGRESSORS_GROUP
for TMP_NAME, TMP_ESTIMATOR in REGRESSORS.items():
    ALGORITHMS.append(EstimatorFit())
ALGORITHMS.append(EstimatorPredict())

