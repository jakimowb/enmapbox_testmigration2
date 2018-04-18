#from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
import numpy
import traceback
from collections import OrderedDict
from processing.core.GeoAlgorithm import GeoAlgorithm, GeoAlgorithmExecutionException
from processing.core.parameters import *
from processing.core.outputs import *
import processing.core.parameters
import processing.core.outputs
from hubflow.core import *
import hubdc.progressbar
from enmapboxgeoalgorithms.estimators import *
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.SilentProgress import SilentProgress


class ProgressBar(hubdc.progressbar.ProgressBar):
    '''Wrapper for processing.gui.AlgorithmDialog.AlgorithmDialog to modify some behaviour when updating the progress bar.'''

    def __init__(self, progress):
        assert isinstance(progress, (AlgorithmDialog, SilentProgress))
        self.progress = progress

    def setText(self, text):
        self.progress.setInfo(msg=str(text))

    def setPercentage(self, percentage):
        if percentage == 100:
            return  # setting percentage to 100 would prevent further outputs in QGIS Dialog :-(
        self.progress.setPercentage(percentage)


class OutputRaster(processing.core.outputs.OutputRaster):

    def getFileFilter(self, alg):
        fileFilter = 'ENVI files (*.bsq *.bil *.bip);;GeoTiff files (*.tif);;Erdas Imagine files (*.img);;Files (*.*)'
        #fileFilter = 'ENVI BSQ files (*.bsq);;ENVI BIL files (*.bil);;ENVI BIP files (*.bip);;GeoTiff files (*.tif);;Erdas Imagine files (*.img);;Files (*.*)'
        return fileFilter

    def getDefaultFileExtension(self, alg):
        return 'bsq'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

class OutputVector(processing.core.outputs.OutputVector):

    def getFileFilter(self, alg):
        fileFilter = 'GeoPackage (*.gpkg);;ESRI Shapefile (*.shp);;Files (*.*)'
        return fileFilter

    def getDefaultFileExtension(self, alg):
        return 'gpkg'

class EnMAPGeoAlgorithmConsistencyError(Exception):
    pass


class EnMAPGeoAlgorithm(GeoAlgorithm):

#    def __init__(self):
#        GeoAlgorithm.__init__(self)
#        self.doc = 'undocumented algorithm'

    @staticmethod
    def tempfilename(basename):
        import tempfile
        subdir = ''.join(np.random.randint(0,9, 20).astype(np.str))
        return os.path.join(tempfile.gettempdir(), subdir, basename)

    def addParameter(self, param, help=None):
        GeoAlgorithm.addParameter(self, param=param)
        if help is None:
            help = 'undocumented input parameter'
        param.help = help

    def addOutput(self, output, help=None):
        GeoAlgorithm.addOutput(self, output=output)
        if help is None:
            help = 'undocumented output parameter'
        output.help = help

    def addOutputRaster(self, name, description, help=None):
        if help is None:
            help = 'output raster'
        self.addOutput(OutputRaster(name=name, description=description), help=help)

    def getOutputRaster(self, name):
        filename = self.getOutputValue(name=name)
        try:
            driver = RasterDriver.fromFilename(filename=filename)
        except AssertionError as error:
            ext = os.path.splitext(filename)[1][1:].lower()
            raise EnMAPGeoAlgorithmConsistencyError('Unexpected output raster ({}) file extension: {}, use bsq (ENVI BSQ), bil (ENVI BIL), bip (ENVI BIP), tif (GTiff) or img (Erdas Imagine) instead'.format(name, ext))
        return filename

    def addOutputVector(self, name, description):
        self.addOutput(OutputVector(name=name, description=description))

    def getOutputVector(self, name):
        filename = self.getOutputValue(name=name)
        try:
            driver = VectorDriver.fromFilename(filename=filename)
        except AssertionError as error:
            ext = os.path.splitext(filename)[1][1:].lower()
            raise EnMAPGeoAlgorithmConsistencyError('Unexpected output vector ({}) file extension: {}, use shp (ESRI Shapefile) or gpkg (GeoPackage) instead.'.format(name, ext))
        return filename

    def addOutputReport(self, name='report', description='HTML Report', help=None):
        self.addOutput(OutputFile(name=name, description=description, ext='html'), help=help)

    def getOutputReport(self, name='report'):
        filename = self.getOutputValue(name=name)
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext != 'html':
            raise EnMAPGeoAlgorithmConsistencyError('Unexpected output report ({}) file extension: {}, use html instead.'.format(name, ext))
        return filename

    def addOutputPickle(self, name, description):
        self.addOutput(OutputFile(name=name, description=description, ext='pkl'))

    def getOutputPickle(self, name):
        filename = self.getOutputValue(name=name)
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext != 'pkl':
            raise EnMAPGeoAlgorithmConsistencyError('Unexpected output pickle ({}) file extension: {}, use pkl instead.'.format(name, ext))
        return filename

    def addOutputPickleClassificationSample(self):
        self.addOutputPickle(name='classificationSample', description='ClassificationSample')

    def getOutputPickleClassificationSample(self):
        return self.getOutputPickle(name='classificationSample')

    def addOutputPickleProbabilitySample(self):
        self.addOutputPickle(name='probabilitySample', description='ProbabilitySample')

    def getOutputPickleProbabilitySample(self):
        return self.getOutputPickle(name='probabilitySample')

    def addOutputPickleRegressionSample(self):
        self.addOutputPickle(name='regressionSample', description='RegressionSample')

    def getOutputPickleRegressionSample(self):
        return self.getOutputPickle(name='regressionSample')

    def addOutputPickleUnsupervisedSample(self, name='sample', description='UnsupervisedSample'):
        self.addOutputPickle(name=name, description=description)

    def getOutputPickleUnsupervisedSample(self, name='sample'):
        return self.getOutputPickle(name=name)

    def addParameterNumberOfPointsPerClass(self, default=100, optional=False):
        self.addParameter(ParameterString('n', 'Number of Points per Class', default=str(default), optional=optional))

    def getParameterNumberOfPointsPerClass(self, classDefinition):
        assert isinstance(classDefinition, ClassDefinition)
        n = self.getParameterValue('n')
        if n == '':
            n = None
        else:
            n = eval(self.getParameterValue('n'))
            if isinstance(n, int):
                n = [n] * classDefinition.classes
            if not isinstance(n, list):
                raise EnMAPGeoAlgorithmConsistencyError('Unexpected value (Number of Points per Class): "{}"'.format(
                    self.getParameterValue('n')))
        return n

    def getParameterRandomPointsPerClass(self, classification, masks, grid, progressBar):
        n = self.getParameterNumberOfPointsPerClass(classDefinition=classification.classDefinition)
        if n is not None:
            classificationMasked = Classification.fromClassification(filename=self.tempfilename('classification.bsq'),
                                                                     classification=classification,
                                                                     grid=grid,
                                                                     oversampling=self.getParameterOversampling(),
                                                                     masks=masks, progressBar=progressBar)

            points = Vector.fromRandomPointsFromClassification(filename=self.tempfilename('points.gpkg'),
                                                               classification=classificationMasked, n=n,
                                                               progressBar=progressBar)
        else:
            points = None
        return points

    def addParameterClassDefinition(self, name='classDefinition', description='Class Definition'):

        help = '\n'.join(
                ["e.g. ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])",
                'For supported named colors see https://www.w3.org/TR/SVG/types.html#ColorKeywords'])

        self.addParameter(ParameterString(name=name, description=description, multiline=True, optional=True),
                          help=help)

    def getParameterClassDefinition(self, name='classDefinition', vector='vector', idAttribute='idAttribute'):
        text = self.getParameterValue(name)

        if text is not None and text != '':
            classDefinition = eval(text)
        else:
            classes = numpy.max(Vector(filename=self.getParameterValue(vector)).uniqueValues(
                attribute=self.getParameterValue(idAttribute)))
            classDefinition = ClassDefinition(classes=classes)

        assert isinstance(classDefinition, ClassDefinition)
        return classDefinition

    def addParameterMinCoverages(self, names=('minOverallCoverage','minWinnerCoverage'),
                                 descriptions=('Minimal overall coverage', 'Minimal winner class coverage'),
                                 defaults=(None, None)):

        helps = [None, None]
        for name, description, default, help in zip(names, descriptions, defaults, helps):
            if default is None:
                default = 0.5
            self.addParameter(ParameterNumber(name=name, description=description,
                                              minValue=0., maxValue=1., default=default),
                              help)

    def getParameterMinOverallCoverage(self, name='minOverallCoverage'):
        return float(self.getParameterValue(name=name))

    def getParameterMinWinnerCoverage(self, name='minWinnerCoverage'):
        return float(self.getParameterValue(name=name))

    def addParameterOversampling(self, name='oversampling', description='Oversampling factor'):
        self.addParameter(ParameterNumber(name=name, description=description, minValue=1, maxValue=10, default=1))

    def getParameterOversampling(self, name='oversampling'):
        return int(self.getParameterValue(name=name))

    def addParameterClassification(self, name='classification', description='Classification'):
        self.addParameter(ParameterRaster(name=name, description=description))

    def getParameterClassification(self, name='classification', minOverallCoverage=None, minWinnerCoverage=None):
        return Classification(filename=self.getParameterValue(name=name),
                              minOverallCoverage=minOverallCoverage,
                              minWinnerCoverage=minWinnerCoverage)

    def addParameterRegression(self, name='regression', description='Regression'):
        self.addParameter(ParameterRaster(name=name, description=description))

    def getParameterRegression(self, name='regression'):
        return Regression(filename=self.getParameterValue(name=name))

    def addParameterProbability(self, name='probability', description='ClassProbability'):
        self.addParameter(ParameterRaster(name=name, description=description))

    def getParameterProbability(self, name='probability', minOverallCoverage=None, minWinnerCoverage=None):
        return Probability(filename=self.getParameterValue(name=name),
                           minOverallCoverage=minOverallCoverage,
                           minWinnerCoverage=minWinnerCoverage)

    def addParameterRaster(self, name='raster', description='Raster', optional=False, help=None):
        if help is None:
            help = 'input raster'
        self.addParameter(ParameterRaster(name=name, description=description, optional=optional), help=help)

    def getParameterRaster(self, name='raster'):
        return Raster(filename=self.getParameterValue(name=name))

    def addParameterGrid(self):
        self.addParameterRaster(name='grid', description='PixelGrid')

    def getParameterGrid(self):
        return self.getParameterRaster(name='grid').grid

    def addParameterMask(self, name='mask', description='Mask', optional=True):
        self.addParameter(ParameterRaster(name=name, description=description, optional=optional))

    def getParameterMask(self, name='mask'):
        filename = self.getParameterValue(name)
        if filename is not None:
            return Mask(filename=filename)

    def addParameterMultiMask(self):
        self.addParameterRaster('mask', 'Mask (Raster)', optional=True)
        self.addParameter(ParameterVector('mask2', 'Mask (Vector)', optional=True))

    def getParameterMultiMask(self):
        return [self.getParameterRaster('mask'), self.getParameterVector('mask2')]

    def addParameterVector(self, name='vector', description='Vector', optional=False):
        self.addParameter(ParameterVector(name=name, description=description, optional=optional))

    def getParameterVector(self, name='vector', **kwargs):
        filename = self.getParameterValue(name)
        if filename is not None:
            return Vector(filename=filename, **kwargs)

    def addParameterVectorClassification(self, minCoveragesDefaults=(None, None)):
        self.addParameterVector()
        self.addParameter(ParameterTableField('idAttribute', 'Class id attribute',
                                              datatype=ParameterTableField.DATA_TYPE_NUMBER, parent='vector'))
        self.addParameterClassDefinition()
        self.addParameterMinCoverages(defaults=minCoveragesDefaults)

    def getParameterVectorClassification(self):
        return VectorClassification(filename=self.getParameterVector().filename,
                                    idAttribute=self.getParameterValue('idAttribute'),
                                    minOverallCoverage=self.getParameterMinOverallCoverage(),
                                    minWinnerCoverage=self.getParameterMinWinnerCoverage(),
                                    classDefinition=self.getParameterClassDefinition())

    def addParameterPickle(self, name, description, optional=False):
        self.addParameter(ParameterFile(name=name, description=description, optional=optional, ext='pkl'))

    def getParameterPickle(self, name, cls=FlowObject):
        filename = self.getParameterValue(name)
        if filename is not None:
            return cls.unpickle(filename=filename)

    def addParameterUnsupervisedSample(self, name='sample', description='Sample'):
        self.addParameterPickle(name=name, description=description)

    def getParameterUnsupervisedSample(self, name='sample'):
        return self.getParameterPickle(name=name, cls=UnsupervisedSample)

    def addParameterClassificationSample(self, name='classificationSample', description='ClassificationSample'):
        self.addParameter(ParameterFile(name=name, description=description))

    def getParameterClassificationSample(self, name='classificationSample'):
        return self.getParameterPickle(name=name, cls=ClassificationSample)

    def addParameterRegressionSample(self, name='regressionSample', description='RegressionSample'):
        self.addParameter(ParameterFile(name=name, description=description))

    def getParameterRegressionSample(self, name='regressionSample'):
        return self.getParameterPickle(name=name, cls=RegressionSample)

    def addParameterProbabilitySample(self, name='probabilitySample', description='ProbabilitySample'):
        self.addParameter(ParameterFile(name=name, description=description))

    def getParameterProbabilitySample(self, name='probabilitySample'):
        return self.getParameterPickle(name=name, cls=ProbabilitySample)

    def processAlgorithm(self, progress):
        try:
            progressBar = ProgressBar(progress=progress)
            self.processAlgorithm_(progressBar=progressBar)
        except EnMAPGeoAlgorithmConsistencyError as error:
            raise GeoAlgorithmExecutionException(str(error))
        except:
            traceback.print_exc()
            progress.setConsoleInfo(str(traceback.format_exc()).replace('\n', '<br>'))
            raise GeoAlgorithmExecutionException('catched unhandled error')

    def processAlgorithm_(self, progressBar):
        assert isinstance(progressBar, ProgressBar)
        assert 0 # overload this method

    def checkOutputFileExtensions(self):
        pass # disables standard behaviour

    def help(self):

        text = '<h2>'+self.name+'</h2>'
        text += '<p>' + getattr(self, 'doc', '') + '</p>'
        for param in self.parameters:
            text += '<h3>' + param.description + '</h3>'
            text += '<p>' + param.help.replace('\n', '<br>') + '</p>'
        for output in self.outputs:
            text += '<h3>' + output.description + '</h3>'
            text += '<p>' + output.help + '</p>'
        #text += '<p><a href="http://www.google.com" target="_blank">here</a></p>'

        return True, text

DTYPE = OrderedDict()
DTYPE['int16'] = numpy.int16, 'Integer 16 Bit'
DTYPE['int32'] = numpy.int32, 'Integer 32 Bit'
DTYPE['int64'] = numpy.int64, 'Integer 64 Bit'
DTYPE['uint8'] = numpy.uint8, 'Unsigned Integer 8 Bit'
DTYPE['uint16'] = numpy.uint16, 'Unsigned Integer 16 Bit'
DTYPE['uint32'] = numpy.uint32, 'Unsigned Integer 32 Bit'
DTYPE['uint64'] = numpy.uint64, 'Unsigned Integer 64 Bit'
DTYPE['float32'] = numpy.float32, 'Single Precision Float 32 Bit'
DTYPE['float64'] = numpy.float64, 'Double precision float 64 Bit'

ALGORITHMS = list()


class ClassificationPerformanceFromRaster(EnMAPGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Classification Performance'
        self.group = 'Accuracy Assessment'
        self.addParameterClassification('prediction', 'Prediction')
        self.addParameterClassification('reference', 'Reference')
        self.addOutputReport()

    def processAlgorithm_(self, progressBar):
        prediction = self.getParameterClassification('prediction')
        reference = self.getParameterClassification('reference')
        performance = ClassificationPerformance.fromRaster(prediction=prediction, reference=reference,
                                                           progressBar=progressBar)
        performance.report().saveHTML(filename=self.getOutputReport(), open=True)


ALGORITHMS.append(ClassificationPerformanceFromRaster())

class ClusteringPerformanceFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Clustering Performance'
        self.group = 'Accuracy Assessment'

        self.addParameterClassification('prediction', 'Prediction')
        self.addParameterClassification('reference', 'Reference')
        self.addOutputReport()

    def processAlgorithm_(self, progressBar):
        prediction = self.getParameterClassification('prediction')
        reference = self.getParameterClassification('reference')
        performance = ClusteringPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=progressBar)
        performance.report().saveHTML(filename=self.getOutputReport(), open=True)


ALGORITHMS.append(ClusteringPerformanceFromRaster())


class ClassificationSampleFromENVISpectralLibrary(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassificationSample from ENVI Spectral Library'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addParameter(ParameterString('prefix', 'ClassDefinition prefix', default=''))
        self.addOutputPickleClassificationSample()

    def processAlgorithm_(self, progressBar):
        unsupervisedSample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
        prefix = self.getParameterValue('prefix')
        if not prefix.endswith(' '):
            prefix = prefix + ' '
        for key in ['class names', 'class lookup', 'class spectra names']:
            key = prefix + key
            if not key in unsupervisedSample.metadata:
                raise EnMAPGeoAlgorithmConsistencyError('missing metatdata: ' + key)

        classDefinition = ClassDefinition(names=unsupervisedSample.metadata[prefix + 'class names'][1:],
                                          colors=numpy.array(unsupervisedSample.metadata[prefix + 'class lookup'][3:]))
        classificationSample = unsupervisedSample.classifyByName(
            names=unsupervisedSample.metadata[prefix + 'class spectra names'],
            classDefinition=classDefinition)

        classificationSample.pickle(filename=self.getOutputPickle('classificationSample'), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleFromENVISpectralLibrary())


class ClassificationSampleSynthMix(EnMAPGeoAlgorithm):
    options = ['proportional', 'equalized']

    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from synthetically mixed ClassificationSample'
        self.group = 'Create Sample'

        self.addParameterClassificationSample()
        self.addParameter(ParameterNumber('n', 'n', default=1000))
        self.addParameter(ParameterNumber('complex2', 'Likelihood for mixing complexity 2', default=1.0))
        self.addParameter(ParameterNumber('complex3', 'Likelihood for mixing complexity 3', default=0.0))
        self.addParameter(ParameterSelection('option', 'Class likelihoods', options=self.options, default=0))
        self.addOutput(OutputFile('probabilitySample', 'ClassProbabilitySample', ext='pkl'))

    def processAlgorithm_(self, progressBar):
        classificationSample = self.getParameterClassificationSample()
        mixingComplexities = {2: self.getParameterValue('complex2'), 3: self.getParameterValue('complex3')}
        probabilitySample = classificationSample.synthMix(mixingComplexities=mixingComplexities,
                                                          classLikelihoods=self.options[
                                                              self.getParameterValue('option')],
                                                          n=self.getParameterValue('n'))
        probabilitySample.pickle(filename=self.getOutputPickle('probabilitySample'), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleSynthMix())


class EstimatorFit(EnMAPGeoAlgorithm):
    def __init__(self, name, group, code):
        self._name = 'Fit ' + name
        self._group = group
        self.code = code
        EnMAPGeoAlgorithm.__init__(self)

    def defineCharacteristics(self):
        self.name = self._name
        self.group = self._group

        if self.group == REGRESSORS_GROUP:
            self.addParameterRegressionSample()
        elif self.group == CLASSIFIERS_GROUP:
            self.addParameterClassificationSample()
        elif self.group == CLUSTERERS_GROUP:
            self.addParameterUnsupervisedSample()
        elif self.group == TRANSFORMERS_GROUP:
            self.addParameterUnsupervisedSample()
        else:
            assert 0
        self.addParameter(ParameterString('parameters', 'Parameters', self.code, multiline=True))
        self.addOutputPickle('model', 'Fitted Model')

    def processAlgorithm_(self, progressBar):
        if self.group == REGRESSORS_GROUP:
            sample = self.getParameterRegressionSample()
            exec self.getParameterValue('parameters')
            sklEstimator = eval('estimator')
            estimator = Regressor(sklEstimator=sklEstimator)
        elif self.group == CLASSIFIERS_GROUP:
            sample = self.getParameterClassificationSample()
            exec self.getParameterValue('parameters')
            sklEstimator = eval('estimator')
            estimator = Classifier(sklEstimator=sklEstimator)
        elif self.group == CLUSTERERS_GROUP:
            sample = self.getParameterUnsupervisedSample()
            exec self.getParameterValue('parameters')
            sklEstimator = eval('estimator')
            estimator = Clusterer(sklEstimator=sklEstimator)
        elif self.group == TRANSFORMERS_GROUP:
            sample = self.getParameterUnsupervisedSample()
            exec self.getParameterValue('parameters')
            sklEstimator = eval('estimator')
            estimator = Transformer(sklEstimator=sklEstimator)
        else:
            assert 0
        estimator.fit(sample=sample)
        estimator.pickle(filename=self.getOutputPickle('model'), progressBar=progressBar)

CLASSIFIERS = parseClassifiers()
REGRESSORS = parseRegressors()
CLUSTERERS = parseClusterers()
TRANSFORMERS = parseTransformers()

CLASSIFIERS_GA = dict()
REGRESSORS_GA = dict()
CLUSTERERS_GA = dict()
TRANSFORMERS_GA = dict()

CLASSIFIERS_GROUP = 'Classification'
REGRESSORS_GROUP = 'Regression'
CLUSTERERS_GROUP = 'Clustering'
TRANSFORMERS_GROUP = 'Transformation'

for group, estimators in [(CLASSIFIERS_GROUP, CLASSIFIERS), (REGRESSORS_GROUP, REGRESSORS),
                          (CLUSTERERS_GROUP, CLUSTERERS), (TRANSFORMERS_GROUP, TRANSFORMERS)]:
    for name, code in estimators.items():
        ALGORITHMS.append(EstimatorFit(name=name, group=group, code=code))
        if group == CLASSIFIERS_GROUP:
            CLASSIFIERS_GA[name] = ALGORITHMS[-1]
        elif group == REGRESSORS_GROUP:
            REGRESSORS_GA[name] = ALGORITHMS[-1]
        elif group == CLUSTERERS_GROUP:
            CLUSTERERS_GA[name] = ALGORITHMS[-1]
        elif group == TRANSFORMERS_GROUP:
            TRANSFORMERS_GA[name] = ALGORITHMS[-1]
        else:
            assert 0


class EstimatorPredict(EnMAPGeoAlgorithm):
    def __init__(self, group):
        self._name = 'Predict ' + group
        self._group = group
        EnMAPGeoAlgorithm.__init__(self)

    def defineCharacteristics(self):
        self.name = self._name
        self.group = self._group
        self.addParameterRaster()
        self.addParameterMultiMask()

        if self.group == REGRESSORS_GROUP:
            description = 'Regressor'
        elif self.group == CLASSIFIERS_GROUP:
            description = 'Classifier'
        elif self.group == CLUSTERERS_GROUP:
            description = 'Clusterer'
        else:
            assert 0
        self.addParameterPickle('model', description=description)
        self.addOutputRaster('prediction', 'Prediction')


    def processAlgorithm_(self, progressBar):
        if self.group == REGRESSORS_GROUP:
            estimator = self.getParameterPickle('model', cls=Regressor)
        elif self.group == CLASSIFIERS_GROUP:
            estimator = Classifier.unpickle(filename=self.getParameterValue('model'))
        elif self.group == CLUSTERERS_GROUP:
            estimator = Clusterer.unpickle(filename=self.getParameterValue('model'))
        else:
            assert 0
        raster = self.getParameterRaster()
        mask, mask2 = self.getParameterMultiMask()
        estimator.predict(filename=self.getOutputRaster('prediction'), raster=raster, mask=mask, mask2=mask2,
                          progressBar=progressBar)


ALGORITHMS.append(EstimatorPredict(group=CLASSIFIERS_GROUP))
ALGORITHMS.append(EstimatorPredict(group=REGRESSORS_GROUP))
ALGORITHMS.append(EstimatorPredict(group=CLUSTERERS_GROUP))


class EstimatorPredictProbability(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Predict ClassProbability'
        self.group = 'Classification'
        self.addParameterRaster()
        self.addParameterMultiMask()
        self.addParameterPickle('model', 'Classifier')
        self.addOutputRaster('prediction', 'Prediction')

    def processAlgorithm_(self, progressBar):
        estimator = self.getParameterPickle('model', cls=Classifier)
        raster = self.getParameterRaster()
        mask, mask2 = self.getParameterMultiMask()
        estimator.predictProbability(filename=self.getOutputRaster('prediction'), raster=raster, mask=mask, mask2=mask2,
                                     progressBar=progressBar)


ALGORITHMS.append(EstimatorPredictProbability())


class EstimatorTransform(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Transform Raster'
        self.group = 'Transformation'
        self.addParameterRaster()
        self.addParameterMultiMask()
        self.addParameterPickle('model', 'Transformer')
        self.addOutputRaster('transformation', 'Transformation')

    def processAlgorithm_(self, progressBar):
        estimator = self.getParameterPickle('model', cls=Transformer)
        raster = self.getParameterRaster()
        mask, mask2 = self.getParameterMultiMask()
        estimator.transform(filename=self.getOutputRaster('transformation'), raster=raster, mask=mask, mask2=mask2,
                            progressBar=progressBar)


ALGORITHMS.append(EstimatorTransform())


class EstimatorInverseTransform(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'InverseTransform Transformation'
        self.group = 'Transformation'
        self.addParameterRaster('transformation', 'Transformation')
        self.addParameterMultiMask()
        self.addParameterPickle('model', 'Transformer')
        self.addOutputRaster('inverseTransformation', 'Inverse Transformation')

    def processAlgorithm_(self, progressBar):
        estimator = self.getParameterPickle('model', cls=Transformer)
        transformation = self.getParameterRaster('transformation')
        mask, mask2 = self.getParameterMultiMask()
        estimator.inverseTransform(filename=self.getOutputRaster('inverseTransformation'), raster=transformation,
                                   mask=mask, mask2=mask2, progressBar=progressBar)


ALGORITHMS.append(EstimatorInverseTransform())


class ClassificationSampleFromRasterAndClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassificationSample from Raster and Classification'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterMultiMask()
        self.addParameterMinCoverages()
        self.addOutputPickleClassificationSample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        classification = self.getParameterClassification(minOverallCoverage=self.getParameterMinWinnerCoverage(),
                                                         minWinnerCoverage=self.getParameterMinWinnerCoverage())
        mask, mask2 = self.getParameterMultiMask()
        classificationSample = ClassificationSample.fromRasterAndClassification(raster, classification=classification,
                                                                                grid=raster, mask=mask, mask2=mask2,
                                                                                progressBar=progressBar)
        classificationSample.pickle(filename=self.getOutputPickleClassificationSample(), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleFromRasterAndClassification())


class ClassificationSampleFromRasterAndVectorClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassificationSample from Raster and Vector'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterVectorClassification()
        self.addParameterOversampling()
        self.addParameterMultiMask()
        self.addParameterNumberOfPointsPerClass(optional=True)
        self.addOutputPickleClassificationSample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        vectorClassification = self.getParameterVectorClassification()
        masks = self.getParameterMultiMask()
        weiter
        masks.append(self.getParameterRandomPointsPerClass())
        n = self.getParameterNumberOfPointsPerClass(classDefinition=vectorClassification.classDefinition)
        if n is not None:
            classification = Classification.fromVectorClassification(filename=self.tempfilename('classification.bsq'),
                                                                     vectorClassification=vectorClassification,
                                                                     grid=raster,
                                                                     oversampling=self.getParameterOversampling(),
                                                                     masks=masks, progressBar=progressBar)

            masks.append(Vector.fromRandomPointsFromClassification(filename=self.tempfilename('points.gpkg'),
                                                                   classification=classification, n=n,
                                                                   progressBar=progressBar))
        else:
            classification = vectorClassification

        classificationSample = ClassificationSample.fromRasterAndClassification(raster=raster,
                                                                                classification=classification,
                                                                                grid=raster, masks=masks,
                                                                                progressBar=progressBar)
        classificationSample.pickle(filename=self.getOutputPickleClassificationSample(), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleFromRasterAndVectorClassification())


class ClassificationSampleFromRasterAndProbability(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassificationSample from Raster and Probability'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterProbability()
        self.addParameterMultiMask()
        self.addParameterMinCoverages()
        self.addOutputPickleClassificationSample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        probability = self.getParameterProbability()
        mask, mask2 = self.getParameterMultiMask()
        minOverallCoverage = self.getParameterMinOverallCoverage()
        minWinnerCoverage = self.getParameterMinWinnerCoverage()

        classificationSample = ClassificationSample.fromRasterAndProbability(raster=raster, probability=probability,
                                                                             grid=raster, mask=mask, mask2=mask2,
                                                                             minOverallCoverage=minOverallCoverage,
                                                                             minWinnerCoverage=minWinnerCoverage,
                                                                             progressBar=progressBar)
        classificationSample.pickle(filename=self.getOutputPickleClassificationSample(), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleFromRasterAndProbability())


class ProbabilityPerformanceFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbability Performance'
        self.group = 'Accuracy Assessment'

        self.addParameterRaster('prediction', 'Prediction (Probabiliy)')
        self.addParameterRaster('reference', 'Reference (Classification)')
        self.addOutputReport()

    def processAlgorithm_(self, progressBar):
        prediction = self.getParameterProbability('prediction')
        reference = self.getParameterClassification('reference')
        performance = ProbabilityPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=progressBar)
        performance.report().saveHTML(filename=self.getOutputReport(), open=True)


ALGORITHMS.append(ProbabilityPerformanceFromRaster())


class ProbabilitySampleFromRasterAndProbability(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from Raster and ClassProbability'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterProbability()
        self.addParameterMultiMask()
        self.addOutputPickleProbabilitySample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        probability = self.getParameterProbability()
        mask, mask2 = self.getParameterMultiMask()
        probabilitySample = ProbabilitySample.fromRasterAndProbability(raster=raster, probability=probability,
                                                                       grid=raster, mask=mask, mask2=mask2,
                                                                       progressBar=progressBar)
        probabilitySample.pickle(filename=self.getOutputPickleProbabilitySample(), progressBar=progressBar)



ALGORITHMS.append(ProbabilitySampleFromRasterAndProbability())


class ProbabilitySampleFromRasterAndClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from Raster and Classification'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterClassification()
        self.addParameterMultiMask()
        self.addOutputPickleProbabilitySample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        classification = self.getParameterClassification()
        mask, mask2 = self.getParameterMultiMask()
        probabilitySample = ProbabilitySample.fromRasterAndClassification(raster=raster, classification=classification,
                                                                          grid=raster, mask=mask, mask2=mask2,
                                                                          progressBar=progressBar)
        probabilitySample.pickle(filename=self.getOutputPickleProbabilitySample(), progressBar=progressBar)


ALGORITHMS.append(ProbabilitySampleFromRasterAndClassification())


class ProbabilitySampleFromRasterAndVector(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from Raster and Vector'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterVectorClassification(minCoveragesDefaults=(0., 0.))
        self.addParameterOversampling()
        self.addParameterMultiMask()
        self.addOutputPickleProbabilitySample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        classification = self.getParameterClassification()
        mask, mask2 = self.getParameterMultiMask()
        probabilitySample = ProbabilitySample.fromRasterAndClassification(raster=raster, classification=classification,
                                                                          grid=raster, mask=mask, mask2=mask2,
                                                                          oversampling=self.getParameterOversampling(),
                                                                          progressBar=progressBar)
        probabilitySample.pickle(filename=self.getOutputPickleProbabilitySample(), progressBar=progressBar)


ALGORITHMS.append(ProbabilitySampleFromRasterAndVector())


class RegressionSampleFromRasterAndRegression(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'RegressionSample from Raster and Regression'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterRegression()
        self.addParameterMultiMask()
        self.addOutputPickleRegressionSample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        regression = self.getParameterRegression()
        mask, mask2 = self.getParameterMultiMask()
        regressionSample = RegressionSample.fromRasterAndRegression(raster=raster, regression=regression,
                                                                    grid=raster, mask=mask, mask2=mask2,
                                                                    progressBar=progressBar)
        regressionSample.pickle(filename=self.getOutputPickleRegressionSample(), progressBar=progressBar)


ALGORITHMS.append(RegressionSampleFromRasterAndRegression())


class UnsupervisedSampleFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'UnsupervisedSample from Raster'
        self.group = 'Create Sample'
        self.addParameterRaster()
        self.addParameterMultiMask()
        self.addOutputPickleUnsupervisedSample()

    def processAlgorithm_(self, progressBar):
        raster = self.getParameterRaster()
        mask, mask2 = self.getParameterMultiMask()
        unsupervisedSample = UnsupervisedSample.fromRasterAndMask(raster=raster, grid=raster, mask=mask, mask2=mask2,
                                                                  progressBar=progressBar)
        unsupervisedSample.pickle(filename=self.getOutputPickleUnsupervisedSample(), progressBar=progressBar)


ALGORITHMS.append(UnsupervisedSampleFromRaster())


class OpenTestdata(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Open Testdata (small dataset)'
        self.group = 'Auxilliary'
        self.doc = 'Open EnMAP-Box Testdata'
        self.addOutputRaster('enmap', 'EnMAP (30m; 177 bands)')
        self.addOutputRaster('hymap', 'HyMap (3.6m; Blue, Green, Red, NIR bands)')
        self.addOutputVector('landcover', 'LandCover Layer')
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm_(self, progressBar):
        import enmapboxtestdata
        self.setOutputValue('enmap', enmapboxtestdata.enmap)
        self.setOutputValue('hymap', enmapboxtestdata.hymap)
        self.setOutputValue('landcover', enmapboxtestdata.landcover)
        self.setOutputValue('speclib', enmapboxtestdata.speclib)

ALGORITHMS.append(OpenTestdata())


class OpenTestdataFull(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Open Testdata (full dataset)'
        self.group = 'Auxilliary'
        self.doc = 'Open EnMAP-Box Testdata'
        self.addOutputRaster('enmap', 'EnMAP (30m; 177 bands)')
        self.addOutputVector('landcover', 'LandCover Layer')
        self.addOutput(OutputFile('speclib', 'ENVI Spectral Library'))

    def processAlgorithm_(self, progressBar):
        import enmapboxtestdata_full
        self.setOutputValue('enmap', enmapboxtestdata_full.enmap)
        self.setOutputValue('landcover', enmapboxtestdata_full.landcover)
        self.setOutputValue('speclib', enmapboxtestdata_full.speclib)


ALGORITHMS.append(OpenTestdataFull())


class CreateAdditionalTestdata(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Create additional Testdata'
        self.group = 'Auxilliary'

        self.addOutputRaster('classification', 'LandCover L2 Classification')
        self.addOutputRaster('probability', 'LandCover L2 ClassProbability')
        self.addOutputPickleUnsupervisedSample()
        self.addOutputPickleClassificationSample()
        self.addOutputPickleProbabilitySample()
        self.addOutputPickleRegressionSample()

    def processAlgorithm_(self, progressBar):
        import enmapboxtestdata
        enmap = Raster(filename=enmapboxtestdata.enmap)
        classDefinitionL2 = ClassDefinition(names=enmapboxtestdata.landcoverClassDefinition.level2.names,
                                            colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup)
        vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
                                                    nameAttribute=enmapboxtestdata.landcoverAttributes.Level_2,
                                                    classDefinition=classDefinitionL2,
                                                    minWinnerCoverage=0.5)
        probability = Probability.fromVectorClassification(filename=self.getOutputRaster('probability'),
                                                           vectorClassification=vectorClassification,
                                                           grid=enmap, oversampling=5)
        classification = Classification.fromProbability(filename=self.getOutputRaster('classification'),
                                                        probability=probability)

        psample = ProbabilitySample.fromRasterAndProbability(raster=enmap, probability=probability, grid=enmap)
        csample = ClassificationSample.fromProbabilitySample(sample=psample)
        rsample = RegressionSample.fromProbabilitySample(sample=psample)
        usample = UnsupervisedSample.fromSample(sample=psample)

        usample.pickle(filename=self.getOutputPickleUnsupervisedSample(), progressBar=progressBar)
        csample.pickle(filename=self.getOutputPickleClassificationSample(), progressBar=progressBar)
        psample.pickle(filename=self.getOutputPickleProbabilitySample(), progressBar=progressBar)
        rsample.pickle(filename=self.getOutputPickleRegressionSample(), progressBar=progressBar)


ALGORITHMS.append(CreateAdditionalTestdata())


class ProbabilityAsClassColorRGB(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbability as RGB Raster'
        self.group = 'Post-Processing'

        self.addParameterProbability()
        self.addOutputRaster('raster', 'RGB Raster')

    def processAlgorithm_(self, progressBar):
        probability = self.getParameterProbability()
        probability.asClassColorRGBRaster(filename=self.getOutputRaster('raster'), progressBar=progressBar)


ALGORITHMS.append(ProbabilityAsClassColorRGB())


class ClassificationSampleFromProbabilitySample(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassificationSample from ClassProbabilitySample'
        self.group = 'Create Sample'

        self.addParameterProbabilitySample()
        self.addParameterMinCoverages()
        self.addOutputPickleClassificationSample()

    def processAlgorithm_(self, progressBar):
        probabilitySample = self.getParameterProbabilitySample()
        classificationSample = ClassificationSample.fromProbabilitySample(sample=probabilitySample,
                                                            minOverallCoverage=self.getParameterMinOverallCoverage(),
                                                            minWinnerCoverage=self.getParameterMinWinnerCoverage())
        classificationSample.pickle(filename=self.getOutputPickleClassificationSample(), progressBar=progressBar)


ALGORITHMS.append(ClassificationSampleFromProbabilitySample())


class ProbabilitySampleFromClassificationSample(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbabilitySample from ClassificationSample'
        self.group = 'Create Sample'

        self.addParameterClassificationSample()
        self.addOutputPickleProbabilitySample()

    def processAlgorithm_(self, progressBar):
        classificationSample = self.getParameterClassificationSample()
        probabilitySample = ProbabilitySample.fromClassificationSample(sample=classificationSample)
        probabilitySample.pickle(filename=self.getOutputPickleProbabilitySample(), progressBar=progressBar)


ALGORITHMS.append(ProbabilitySampleFromClassificationSample())


class RegressionPerformanceFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Regression Performance'
        self.group = 'Accuracy Assessment'

        self.addParameterRegression('prediction', 'Prediction')
        self.addParameterRegression('reference', 'Reference')
        self.addOutputReport()

    def processAlgorithm_(self, progressBar):
        prediction = self.getParameterRegression('prediction')
        reference = self.getParameterRegression('reference')
        performance = RegressionPerformance.fromRaster(prediction=prediction, reference=reference,
                                                       progressBar=progressBar)
        performance.report().saveHTML(filename=self.getOutputReport(), open=True)


ALGORITHMS.append(RegressionPerformanceFromRaster())


class UnsupervisedSampleFromENVISpectralLibrary(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'UnsupervisedSample from ENVI Spectral Library'
        self.group = 'Create Sample'

        self.addParameter(ParameterFile('envi', 'ENVI Spectral Library', optional=False))
        self.addOutputPickleUnsupervisedSample()

    def processAlgorithm_(self, progressBar):
        sample = UnsupervisedSample.fromENVISpectralLibrary(filename=self.getParameterValue('envi'))
        sample.pickle(filename=self.getOutputPickleUnsupervisedSample(), progressBar=progressBar)

ALGORITHMS.append(UnsupervisedSampleFromENVISpectralLibrary())


class UnsupervisedSampleScaleFeatures(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Scale Sample Features'
        self.group = 'Auxilliary'

        self.addParameterUnsupervisedSample(description='Sample')
        self.addParameter(ParameterNumber('factor', 'Scale factor', default=1.))
        self.addOutputPickleUnsupervisedSample('unsupervisedSample2', 'Scaled Sample')

    def processAlgorithm_(self, progressBar):
        sample = self.getParameterUnsupervisedSample()
        sample.scaleFeaturesInplace(factor=self.getParameterValue('factor'))
        sample.pickle(filename=self.getOutputPickleUnsupervisedSample('unsupervisedSample2'), progressBar=progressBar)


ALGORITHMS.append(UnsupervisedSampleScaleFeatures())


class RasterFromVector(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Raster from Vector'
        self.group = 'Create Raster'

        self.addParameterGrid()
        self.addParameterVector()
        self.addParameter(ParameterNumber('initValue', 'Init Value', default=0))
        self.addParameter(ParameterNumber('burnValue', 'Burn Value', default=1))
        self.addParameter(ParameterTableField('burnAttribute', 'Burn Attribute',
                                              datatype=ParameterTableField.DATA_TYPE_NUMBER,
                                              parent='vector', optional=True))
        self.addParameter(ParameterBoolean('allTouched', 'All touched', default=False))
        self.addParameter(ParameterString('filterSQL', 'Filter SQL', default='', optional=True))
        self.addParameter(ParameterSelection('dtype', 'Data Type', options=DTYPE.keys(),
                                             default=DTYPE.keys().index('uint8')))
        self.addParameterNoDataValue()
        self.addOutputRaster('raster', 'Raster')

    def processAlgorithm_(self, progressBar):
        grid = self.getParameterGrid()
        vector = self.getParameterVector('vector',
                                         initValue=self.getParameterValue('initValue'),
                                         burnValue=self.getParameterValue('burnValue'),
                                         burnAttribute=self.getParameterValue('burnAttribute'),
                                         allTouched=self.getParameterValue('allTouched'),
                                         filterSQL=self.getParameterValue('filterSQL') if self.getParameterValue(
                                                                             'filterSQL') != '' else None,
                                        dtype=DTYPE.values()[self.getParameterValue('dtype')][0])

        Raster.fromVector(filename=self.getOutputRaster('raster'), vector=vector, grid=grid,
                          noDataValue=self.getParameterNoDataValue(),
                          progressBar=progressBar)


ALGORITHMS.append(RasterFromVector())


class RasterApplyMask(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Apply Mask to Raster'
        self.group = 'Masking'

        self.addParameterRaster()
        self.addParameterMultiMask()
        self.addOutputRaster('maskedRaster', 'Masked Raster')

    def processAlgorithm_(self, progressBar):
        raster = Raster(filename=self.getParameterValue('raster'))
        mask = Mask(filename=self.getParameterValue('mask'))
        raster.applyMask(filename=self.getOutputRaster('maskedRaster'), mask=mask, progressBar=progressBar)


ALGORITHMS.append(RasterApplyMask())


class TEST(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'TEST'
        self.group = 'TEST'

        self.addOutputRaster('raster', 'Output Raster')
        self.addOutputVector('vector', 'Output Vector')
        self.addOutputPickle('pickle', 'Output Pickle')
        self.addOutputReport()

    def processAlgorithm_(self, progressBar):
        self.getOutputRaster('raster')
        self.getOutputVector('vector')
        self.getOutputPickle('pickle')
        self.getOutputReport()


#ALGORITHMS.append(TEST())


class ClassificationFromVectorClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Classification from Vector'
        self.group = 'Create Raster'

        self.addParameterGrid()
        self.addParameterVectorClassification()
        self.addParameterOversampling()
        self.addOutputRaster('classification', 'Classification')

    def processAlgorithm_(self, progressBar):

        vectorClassification = self.getParameterVectorClassification()
        Classification.fromVectorClassification(filename=self.getOutputRaster('classification'),
                                                vectorClassification=vectorClassification,
                                                grid=self.getParameterGrid(),
                                                oversampling=self.getParameterOversampling(),
                                                progressBar=progressBar)


ALGORITHMS.append(ClassificationFromVectorClassification())


class ClassificationFromProbability(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Classification from Probability'
        self.group = 'Create Raster'

        self.addParameter(ParameterRaster('probability', 'Probability'))
        self.addParameterMinCoverages()
        self.addOutputRaster('classification', 'Classification')

    def processAlgorithm_(self, progressBar):
        probability = Probability(filename=self.getParameterValue('probability'),
                                  minOverallCoverage=self.getParameterMinOverallCoverage(),
                                  minWinnerCoverage=self.getParameterMinWinnerCoverage())
        Classification.fromProbability(filename=self.getOutputValue('classification'),
                                       probability=probability, progressBar=progressBar)


ALGORITHMS.append(ClassificationFromProbability())


class ProbabilityFromVectorClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbability from Vector'
        self.group = 'Create Raster'

        self.addParameterGrid()
        self.addParameterVectorClassification(minCoveragesDefaults=(0., 0.))
        self.addParameterOversampling()
        self.addOutputRaster('probability', 'ClassProbability')

    def processAlgorithm_(self, progressBar):

        vectorClassification = self.getParameterVectorClassification()
        Probability.fromVectorClassification(filename=self.getOutputRaster('probability'),
                                             vectorClassification=vectorClassification,
                                             grid=self.getParameterGrid(),
                                             oversampling=self.getParameterOversampling(),
                                             progressBar=progressBar)

ALGORITHMS.append(ProbabilityFromVectorClassification())


class ProbabilityFromClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassProbability from Classification'
        self.group = 'Create Raster'

        self.addParameterClassification()
        self.addOutputRaster('probability', 'ClassProbability')

    def processAlgorithm_(self, progressBar):
        classification = self.getParameterClassification()
        Probability.fromClassification(filename=self.getOutputRaster('probability'), classification=classification,
                                       progressBar=progressBar)

ALGORITHMS.append(ProbabilityFromClassification())


class MaskBuildFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Build Mask from Raster'
        self.group = 'Masking'
        self.doc = 'Create a binary mask from given forground/background values and ranges.'
        self.addParameterRaster('raster', 'Raster')
        self.addParameter(ParameterString('trueValues', 'Foreground values', default='[]'),
                          help='List of values that are mapped to True, e.g. [1, 2, 5].')
        self.addParameter(ParameterString('trueRanges', 'Foreground ranges', default='[]'),
                          help='List of [min, max] ranges, e.g. [[1, 3], [5, 7]]. Values inside those ranges are mapped to True.')
        self.addParameter(ParameterString('falseValues', 'Background values', default='[]'),
                          help='List of values that are mapped to False, e.g. [1, 2, 5].')
        self.addParameter(ParameterString('falseRanges', 'Background ranges', default='[]'),
                          help='List of [min, max] ranges, e.g. [[-999, 0], [10, 255]]. Values inside those ranges are mapped to False.')
        self.addOutputRaster('mask', 'Mask')

    def processAlgorithm_(self, progressBar):
        raster = Raster(filename=self.getParameterValue('raster'))

        # expected format for values '[0, 2, 3, 9]'
        trueValues = eval(self.getParameterValue('trueValues'))
        falseValues = eval(self.getParameterValue('falseValues'))
        # expected format for ranges '[[1, 3], [5, 9]]'
        trueRanges = eval(self.getParameterValue('trueRanges'))
        falseRanges = eval(self.getParameterValue('falseRanges'))
        mask = Mask.fromRaster(filename=self.getOutputValue('mask'), raster=raster,
                               trueValues=trueValues, trueRanges=trueRanges,
                               falseValues=falseValues, falseRanges=falseRanges)



ALGORITHMS.append(MaskBuildFromRaster())


class VectorFromRandomPointsFromMask(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Random Points from Mask'
        self.group = 'Random'

        self.addParameterMask()
        self.addParameter(ParameterNumber('n', 'Number of Points', minValue=0, default=0))
        self.addOutputVector('vector', 'Random Points')

    def processAlgorithm_(self, progressBar):
        mask = Mask(filename=self.getParameterValue('mask'))
        n = self.getParameterValue('n')
        Vector.fromRandomPointsFromMask(filename=self.getOutputVector('vector'), mask=mask, n=n)


ALGORITHMS.append(VectorFromRandomPointsFromMask())


class VectorFromRandomPointsFromClassification(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Random Points from Classification'
        self.group = 'Random'

        self.addParameterClassification()
        self.addParameterNumberOfPointsPerClass()
        self.addOutputVector('vector', 'Random Points')

    def processAlgorithm_(self, progressBar):
        classification = self.getParameterClassification()
        n = self.getParameterNumberOfPointsPerClass(classDefinition=classification.classDefinition)
        Vector.fromRandomPointsFromClassification(filename=self.getOutputVector('vector'),
                                                  classification=classification, n=n)


ALGORITHMS.append(VectorFromRandomPointsFromClassification())


class VectorUniqueValues(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Unique Values from Vector Attribute '
        self.group = 'Auxilliary'

        self.addParameter(ParameterVector('vector', 'Vector'))
        self.addParameter(ParameterTableField('attribute', 'Attribute', parent='vector'))

    def processAlgorithm_(self, progressBar):
        vector = Vector(filename=self.getParameterValue('vector'))
        values = vector.uniqueValues(attribute=self.getParameterValue('attribute'))
        progressBar.setText('Unique value: {}'.format(repr(values)))


ALGORITHMS.append(VectorUniqueValues())


class ClassDefinitionFromRaster(EnMAPGeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'ClassDefinition from Raster'
        self.group = 'Auxilliary'

        self.addParameter(ParameterRaster('raster', 'Raster'))
        #self.addOutput(OutputString('string', 'String'))

    def processAlgorithm_(self, progressBar):

        raster = Raster(filename=self.getParameterValue('raster'))
        try:
            classDefinition = ClassDefinition.fromENVIClassification(raster)
        except:
            try:
                classDefinition = ClassDefinition.fromGDALMeta(raster)
            except:
                raise EnMAPGeoAlgorithmConsistencyError('insufficient metadata to derive ClassDefinition')

        progressBar.setText('Class definition: {}'.format(repr(classDefinition)))

ALGORITHMS.append(ClassDefinitionFromRaster())


def generateRST():
    global ALGORITHMS

    groups = dict()

    for alg in ALGORITHMS:
        if alg.group not in groups:
            groups[alg.group] = dict()
        groups[alg.group][alg.name] = alg

    text =  '=============\n'
    text += 'GeoAlgotithms\n'
    text += '=============\n\n'

    for gkey in sorted(groups.keys()):

        text += gkey + '\n'
        text += '=' * len(gkey) + '\n\n'

        for akey in groups[gkey]:
            alg = groups[gkey][akey]
            assert isinstance(alg, EnMAPGeoAlgorithm)

            text += alg.name + '\n'
            text += '-' * len(alg.name) + '\n\n'

            text += alg.doc + '\n\n'

            for param in alg.parameters + alg.outputs:
                text += param.description + '\n'
                text += '~' * len(param.description) + '\n\n'

                text += param.help + '\n\n'

    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'doc', 'source', 'ga.rst')
    with open(filename, mode='w') as f:
        f.write(text)
    print('created GeoAlgoritms RST file: ', filename)