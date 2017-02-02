# Import Processing libraries to add the algorithms to Processing toolbox
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.parameters import *
from processing.core.outputs import *
import PyQt4.QtCore

from os.path import join
import traceback

from enmapbox.processing.estimators import Classifiers, Regressors, Clusterers, Transformers
from enmapbox.processing.environment import Environment
from enmapbox.processing.types import Image, Classification, Probability, Regression, Mask, Vector, VectorClassification, Estimator, Classifier, Regressor, Transformer, Clusterer, unpickle

from hub.gdal.util import GDALWARP_OT_OPTIONS, GDALWARP_R_OPTIONS

GROUP_DATASET = 'Dataset'

GROUP_ESTIMATOR = 'Estimator'
GROUP_CLASSIFIER = 'Classifier'
GROUP_CLUSTERER = 'Clusterer'
GROUP_REGRESSOR = 'Regressor'
GROUP_TRANSFORMER = 'Transformer'

GROUP_IMAGE  = 'Image'
GROUP_CLASSIFICATION = 'Classification'
GROUP_PROBABILITY  = 'Probability'
GROUP_VECTORCLASSIFICATION = 'VectorClassification'
GROUP_SPECTRALLIBRARY = 'Spectral Library'

def GROUP_BY_TYPE(type):
    if type is Estimator: return GROUP_ESTIMATOR
    if type is Classifier: return GROUP_CLASSIFIER
    if type is Regressor: return GROUP_REGRESSOR
    if type is Transformer: return GROUP_TRANSFORMER
    if type is Clusterer: return GROUP_CLUSTERER
    raise Exception('Wrong type:'+str(type))

INSTANCE_OF = lambda group: ('<'+group+'>').lower()
CLASS_OF = lambda group: ('<'+group+'>').lower()

class EnMAPBoxProvider(AlgorithmProvider):
    _instance = None

    @staticmethod
    def instance():
        return EnMAPBoxProvider._instance

    def __del__(self):
        EnMAPBoxProvider._instance = None

    def __init__(self):

        AlgorithmProvider.__init__(self)
        if EnMAPBoxProvider.instance() is not None:
            print('Oh. It seems that the EnMAPBoxProvider was initialized twice.')
        EnMAPBoxProvider._instance = self

        self.alglist = list()

        Alglist = [EstimatorInfo, EstimatorPredict, EstimatorPredictProbability, EstimatorTransform, EstimatorTransformInverse,
                   ClassifierInfo, ClassifierPredict, ClassifierPredictProbability,
                   RegressorInfo, RegressorPredict, RegressorPredictProbability,
                   TransformerInfo, TransformerTransform, TransformerTransformInverse,
                   ClustererInfo, ClustererPredict, ClustererTransform,

                   ClassificationAssessClassificationPerformance, ClassificationAssessClassificationPerformanceAdjusted,

                   RegressionAssessRegressionPerformance,

                   ClassificationAssessClusteringPerformance,

                   ImageInfo, ImageStatistics, ImageResample, ImageFromENVISpectralLibrary,
                   DatasetHyMapA, DatasetHyMapB,

                   ProbabilityArgmaxProbabilityClassification, ProbabilityRgbClassColorComposite,

                   VectorClassificationCreateOccurrence
                   ]

        #Alglist.append(ToyAllParameters)

        for showInToolbox in [True, False]:
            showInModeler = not showInToolbox

            for Alg in Alglist:
                self.alglist.append(Alg(showInToolbox=showInToolbox, showInModeler=showInModeler))

            # insert generic Scikit-Learn estimators
            for estimator in Classifiers().yieldAll():
                self.alglist.append(EstimatorFit(estimator.name() + '().fit()', GROUP_CLASSIFIER, 'Classifiers.' + estimator.signature(), estimator, showInToolbox=showInToolbox, showInModeler=showInModeler))
            for estimator in Regressors().yieldAll():
                self.alglist.append(EstimatorFit(estimator.name() + '().fit()', GROUP_REGRESSOR, 'Regressors.' + estimator.signature(), estimator, showInToolbox=showInToolbox, showInModeler=showInModeler))
            for estimator in Clusterers().yieldAll():
                self.alglist.append(EstimatorFit(estimator.name() + '().fit()', GROUP_CLUSTERER, 'Clusterers.' + estimator.signature(), estimator, showInToolbox=showInToolbox, showInModeler=showInModeler))
            for estimator in Transformers().yieldAll():
                self.alglist.append(EstimatorFit(estimator.name() + '().fit()', GROUP_TRANSFORMER, 'Transformers.' + estimator.signature(), estimator, showInToolbox=showInToolbox, showInModeler=showInModeler))


    def example_HowToSignalThatANewFileWasCreated(self):

        newPath = r'C:/foo/bar.bsq'
        provider = EnMAPBoxProvider.instance()
        assert isinstance(provider, EnMAPBoxProvider) #for PyCharm intellisence only
        provider.sigFileCreated.emit(newPath)

    def example_HowToGetEnMAPBoxGUIRasterDataSources(self):
        import enmapbox.main
        emb = enmapbox.main.EnMAPBox.instance()
        print('Raster files registered in EnMAPBox GUI DataSourceManager')
        for uri in emb.getUriList(sourcetype = 'RASTER'):
            print(uri)

    def unload(self):
        AlgorithmProvider.unload(self)

    def getName(self):
        return 'enmapbox'

    def getDescription(self):
        return 'EnMAP-Box'

    def getIcon(self):
        from enmapbox.utils import IconProvider
        from PyQt4.Qt import QIcon
        return QIcon(IconProvider.EnMAP_Logo)

    def _loadAlgorithms(self):
        self.algs = self.alglist

    def getSupportedOutputRasterLayerExtensions(self):
        return ['img']


class EnMAPBoxGeoAlgorithm(GeoAlgorithm):

    def __init__(self, showInToolbox=False, showInModeler=False):

        assert showInModeler+showInToolbox == 1, self.__class__

        self._showInToolbox = showInToolbox
        self._showInModeler = showInModeler
        self.parametersEnmapBox = dict()
        GeoAlgorithm.__init__(self)
        self.showInToolbox = showInToolbox
        self.showInModeler = showInModeler
        # append group name to algo name to make it better searchable in the toolbox
        #self.setName(self.name + ' '*(1000-len(self.name)) + '['+self.group+']')


    def setName(self, name):
        if self._showInToolbox:
            self.name = name
        if self._showInModeler:
            self.name = name + ' (m)'


    def setGroup(self, group):
        if self._showInToolbox:
            self.group = group
        if self._showInModeler:
            self.group = group + ' (m)'

    def addParameterFile(self, name='', description='', default=0, optional=False):
        if self._showInToolbox:
            if optional: description += ' [optional]'
            options = Environment.modelBasenames
            param = ParameterSelection(name=name, description=description, options=options, default=default)

        elif self._showInModeler:
            param = ParameterFile(name=name, description=description, optional=optional)
        param.required = not optional
        self.addParameter(param)

    def getParameterFile(self, name):

        param = self.getParameterFromName(name)
        if self._showInToolbox:
            if param.value == 0:
                if param.required:
                    raise GeoAlgorithmExecutionException(param.description + ': select a file')
                else:
                    return None
            return Environment.modelFilenames[param.value]
        elif self._showInModeler:
            return param.value
        else:
            raise Exception('unexpected error')

    def getParameterType(self, name, type, *args, **kwargs):

        param = self.getParameterFromName(name)
        filename = param.value

        try:
            return type(filename, *args, **kwargs)
        except:
            if not param.optional:
                message = param.description + ': (' + str(filename) + ') is not a correct ' + str(type) + ' file!'
                if 0: #debug
                    message += '\nfilename: ' + filename
                    message += '\nargs: ' + str(args)
                    message += '\nkwargs: ' + str(kwargs)
                raise GeoAlgorithmExecutionException(message)
            else:
                return None

    def getParameterImage(self, name):
        image = self.getParameterType(name, type=Image)
        assert isinstance(image, Image)
        return image

    def getParameterClassification(self, name):
        return self.getParameterType(name, type=Classification)

    def getParameterRegression(self, name):
        return self.getParameterType(name, type=Regression)

    def getParameterMask(self, name):
        return self.getParameterType(name, type=Mask)

    def getParameterProbability(self, name):
        probability = self.getParameterType(name, type=Probability)
        assert isinstance(probability, Probability)
        return probability

    def getParameterVectorClassification(self, name, idField, nameField, colorField):
        return self.getParameterType(name, type=VectorClassification,
                                     idField=str(self.getParameterValue(idField)),
                                     nameField=str(self.getParameterValue(nameField)),
                                     colorField=str(self.getParameterValue(colorField)),
                                     parse=True)

    def getParameterSklearnModel(self, name, progress, type=Estimator):
        filename = self.getParameterFile(name)
        estimator = unpickle(filename, progress=progress)
        if not isinstance(estimator, type):
            param = self.getParameterFromName(name)
            if param.required:
                raise GeoAlgorithmExecutionException(param.description + ': is not a correct ' + str(type))

        return estimator

    def setOutputRaster(self, outputName, raster):
        filename = raster.filename
        self.setOutputValue(outputName=outputName, value=filename)
        #Environment.openRaster(filename)

    def setOutputEstimator(self, outputName, estimator, progress):
        filename = self.getOutputValue(outputName)
        estimator.pickle(filename, progress=progress)
        Environment.openModel(filename)
        self.setOutputValue(outputName, filename)

class ToyAllParameters(EnMAPBoxGeoAlgorithm):
    INPUT_IMAGE = 'INPUT_IMAGE'
    INPUT_LABELS = 'INPUT_LABELS'
    INPUT_ESTIMATOR = 'INPUT_ESTIMATOR'
    INPUT_BOOLEAN = 'INPUT_BOOLEAN'
    INPUT_CRS = 'INPUT_CRS'
    INPUT_DATAOBJECT = 'INPUT_DATAOBJECT'
    INPUT_EXTENT = 'INPUT_EXTENT'
    INPUT_FILE = 'INPUT_FILE'
    INPUT_FIXEDTABLE = 'INPUT_FIXEDTABLE'
    INPUT_GEOMETRYPREDICATE = 'INPUT_GEOMETRYPREDICATE'
    INPUT_MULTIPLEINPUT = 'INPUT_MULTIPLEINPUT'
    INPUT_NUMBER = 'INPUT_NUMBER'
    INPUT_RANGE = 'INPUT_RANGE'
    INPUT_RASTER = 'INPUT_RASTER'
    INPUT_SELECTION = 'INPUT_SELECTION'
    INPUT_STRING = 'INPUT_STRING'
    INPUT_TABLE = 'INPUT_TABLE'
    INPUT_TABLEFIELD = 'INPUT_TABLEFIELD'
    INPUT_VECTOR = 'INPUT_VECTOR'
    OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
    OUTPUT_EXTENT = 'OUTPUT_EXTENT'
    OUTPUT_FILE = 'OUTPUT_FILE'
    OUTPUT_HTML = 'OUTPUT_HTML'
    OUTPUT_NUMBER = 'OUTPUT_NUMBER'
    OUTPUT_RASTER = 'OUTPUT_RASTER'
    OUTPUT_STRING = 'OUTPUT_STRING'
    OUTPUT_TABLE = 'OUTPUT_TABLE'
    OUTPUT_VECTOR = 'OUTPUT_VECTOR'

    def defineCharacteristics(self):
        self.setName('Show all Parameters')
        self.setGroup('Testing')

        self.addParameter(ParameterBoolean(self.INPUT_BOOLEAN, 'ParameterBoolean'))
        self.addParameter(ParameterCrs(self.INPUT_CRS, 'ParameterCrs'))
        #self.addParameter(ParameterDataObject(self.INPUT_DATAOBJECT, 'ParameterDataObject'))
        self.addParameter(ParameterExtent(self.INPUT_EXTENT, 'ParameterExtent'))
        self.addParameter(ParameterFile(self.INPUT_FILE, 'ParameterFile'))
        self.addParameter(ParameterFixedTable(self.INPUT_FIXEDTABLE, 'ParameterFixedTable'))
        self.addParameter(ParameterGeometryPredicate(self.INPUT_GEOMETRYPREDICATE, 'ParameterGeometryPredicate'))
        self.addParameter(ParameterMultipleInput(self.INPUT_MULTIPLEINPUT, 'ParameterMultipleInput'))
        self.addParameter(ParameterNumber(self.INPUT_NUMBER, 'ParameterNumber'))
        self.addParameter(ParameterRange(self.INPUT_RANGE, 'ParameterRange'))
        self.addParameter(ParameterRaster(self.INPUT_RASTER, 'ParameterRaster'))
        self.addParameter(ParameterTable(self.INPUT_TABLE, 'ParameterTable'))
        self.addParameter(ParameterTableField(self.INPUT_TABLEFIELD, 'ParameterTableField'))
        self.addParameter(ParameterVector(self.INPUT_VECTOR, 'ParameterVector'))
        self.addOutput(OutputDirectory(self.OUTPUT_DIRECTORY, 'OutputDirectory'))
        self.addOutput(OutputString(self.OUTPUT_STRING, 'OutputString'))
        self.addOutput(OutputFile(self.OUTPUT_FILE, 'OutputFile'))
        self.addOutput(OutputRaster(self.OUTPUT_RASTER, 'OutputRaster'))
        self.addOutput(OutputExtent(self.OUTPUT_EXTENT, 'OutputExtent'))
        self.addOutput(OutputHTML(self.OUTPUT_HTML, 'OutputHTML'))
        self.addOutput(OutputNumber(self.OUTPUT_NUMBER, 'OutputNumber'))
        self.addOutput(OutputTable(self.OUTPUT_TABLE, 'OutputTable'))
        self.addOutput(OutputVector(self.OUTPUT_VECTOR, 'OutputVector'))

    def processAlgorithm(self, progress):
        assert isinstance(progress, AlgorithmDialog)
        progress.setInfo('setInfo from AlgorithmDialog')
        progress.setConsoleInfo('setConsoleInfo from AlgorithmDialog')
        progress.setDebugInfo('setDebugInfo from AlgorithmDialog')
        progress.setText('setText from AlgorithmDialog')
        progress.setPercentage(42)

        filename = self.getParameterValue(self.OUTPUT_MODEL)
        #qgis.core.QgsMessageLog.logMessage('Hello', 'EnMAP-Box')
        raise Exception('Filename: ' + str(self.getParameterValue(self.OUTPUT_MODEL)))

        raise GeoAlgorithmExecutionException('Hello World')
        # qgis.core.QgsMessageLog.logMessage('hello', 'world')
        # image = eb.Image(self.getParameterValue(self.INPUT_IMAGE))
        # labels = eb.Classification(self.getParameterValue(self.INPUT_LABELS))
        # classifier = eb.classifier.SVCTuned().fit(image, labels)

        classifier = processing.classifier.SVCTuned()
        classifier.pickle(filename)

class DatasetHyMapA(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open HyMap A')
        self.setGroup(GROUP_DATASET)

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))
        self.addOutput(OutputRaster('predicted', 'Predicted'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        self.setOutputRaster('image', Image(join(root, 'Hymap_Berlin-A_Image')))
        self.setOutputRaster('mask', Mask(join(root, 'Hymap_Berlin-A_Mask')))
        self.setOutputRaster('train', Classification(join(root, 'Hymap_Berlin-A_Classification-Training-Sample')))
        self.setOutputRaster('test', Classification(join(root, 'Hymap_Berlin-A_Classification-Validation-Sample')))
        self.setOutputRaster('predicted', Classification(join(root, 'Hymap_Berlin-A_Classification-Estimation')))

class DatasetHyMapB(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open HyMap B')
        self.setGroup(GROUP_DATASET)

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        self.setOutputRaster('image', Image(join(root, 'Hymap_Berlin-B_Image')))
        self.setOutputRaster('mask', Mask(join(root, 'Hymap_Berlin-B_Mask')))
        self.setOutputRaster('train',Regression(join(root, 'Hymap_Berlin-B_Regression-Training-Sample')))
        self.setOutputRaster('test', Regression(join(root, 'Hymap_Berlin-B_Regression-Validation-Sample')))

class EstimatorFit(EnMAPBoxGeoAlgorithm):

    def __init__(self, name, group, statement, estimator, showInToolbox, showInModeler):

        self.name_ = name
        self.group_ = group
        self.statement = statement
        self.estimator = estimator
        self.MODEL = self.estimator.name()
        EnMAPBoxGeoAlgorithm.__init__(self, showInToolbox=showInToolbox, showInModeler=showInModeler)

    def getParameterSklearnEstimator(self, name, type=Estimator):
        statement = self.getParameterValue(name)
        try:
            estimator = eval(statement)
        except:
            traceback.print_exc()
            param = self.getParameterFromName(name)
            raise GeoAlgorithmExecutionException(param.description + ': statement could not be evaluated!')

        if not isinstance(estimator, type):
            param = self.getParameterFromName(name)
            if param.required:
                raise GeoAlgorithmExecutionException(param.description + ': is not a correct ' + str(type))

        return estimator

    def getParameterSklearnClassifier(self, name):
        return self.getParameterSklearnEstimator(name, type=Classifier)

    def getParameterSklearnRegressor(self, name):
        return self.getParameterSklearnEstimator(name, type=Regressor)

    def getParameterSklearnClusterer(self, name):
        return self.getParameterSklearnEstimator(name, type=Clusterer)

    def getParameterSklearnTransformer(self, name):
        return self.getParameterSklearnEstimator(name, type=Transformer)

    def defineCharacteristics(self):

        self.setName(self.name_)
        self.setGroup(self.group_)
        self.addParameter(ParameterRaster('image', 'Image'))
        if isinstance(self.estimator, Classifier):
            self.addParameter(ParameterRaster('labels', 'Classification'))
        elif isinstance(self.estimator, Regressor):
            self.addParameter(ParameterRaster('labels', 'Regression'))
        elif isinstance(self.estimator, Clusterer):
            self.addParameter(ParameterRaster('labels', 'Mask', optional=True))
        elif isinstance(self.estimator, Transformer):
            self.addParameter(ParameterRaster('labels', 'Mask', optional=True))
        else:
            raise Exception('unknown estimator type')

        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(OutputFile(self.MODEL, 'Fitted Model', ext='iml'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')

        if isinstance(self.estimator, Classifier):
            labels = self.getParameterClassification('labels')
            estimator = self.getParameterSklearnClassifier('parameters')
        elif isinstance(self.estimator, Regressor):
            labels = self.getParameterRegression('labels')
            estimator = self.getParameterSklearnRegressor('parameters')
        elif isinstance(self.estimator, Clusterer):
            labels = self.getParameterMask('labels')
            estimator = self.getParameterSklearnClusterer('parameters')
        elif isinstance(self.estimator, Transformer):
            labels = self.getParameterMask('labels')
            estimator = self.getParameterSklearnTransformer('parameters')
        else:
            raise Exception('unknown estimator type')

        estimator.fit(image, labels, progress=progress)
        if self.showInToolbox:
            estimator.info()

        self.setOutputEstimator(self.MODEL, estimator=estimator, progress=progress)

class EstimatorPredict(EnMAPBoxGeoAlgorithm):

    ESTIMATOR = Estimator

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_BY_TYPE(self.ESTIMATOR))+'.predict()')
        self.setGroup(GROUP_BY_TYPE(self.ESTIMATOR))

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', progress=progress, type=self.estimator)
        estimation = estimator.predict(image, mask, filename=self.getOutputValue('prediction'), progress=progress)
        self.setOutputRaster('prediction', estimation)

class EstimatorInfo(EnMAPBoxGeoAlgorithm):

    ESTIMATOR = Estimator

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_BY_TYPE(self.ESTIMATOR))+'.info()')
        self.setGroup(GROUP_BY_TYPE(self.ESTIMATOR))

        self.addParameterFile('model', 'Model')

    def processAlgorithm(self, progress):

        estimator = self.getParameterSklearnModel('model', progress=progress)
        estimator.info()

class EstimatorTransform(EnMAPBoxGeoAlgorithm):

    ESTIMATOR = Estimator

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_BY_TYPE(self.ESTIMATOR))+'.transform()')
        self.setGroup(GROUP_BY_TYPE(self.ESTIMATOR))

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('transformation', 'Transformation'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', progress=progress, type=Transformer)
        estimator.transform(image, mask, filename=self.getOutputValue('transformation'), progress=progress)

class EstimatorTransformInverse(EnMAPBoxGeoAlgorithm):

    ESTIMATOR = Estimator

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_BY_TYPE(self.ESTIMATOR))+'.inverseTransformation()')
        self.setGroup(GROUP_BY_TYPE(self.ESTIMATOR))

        self.addParameter(ParameterRaster('transformation', 'Transformation'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('inverseTransformation', 'InverseTransformation'))

    def processAlgorithm(self, progress):

        transformation = self.getParameterImage('transformation')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', progress=progress, type=Transformer)
        estimator.transformInverse(transformation, mask, filename=self.getOutputValue('inverseTransformation'), progress=progress)

class EstimatorPredictProbability(EnMAPBoxGeoAlgorithm):

    ESTIMATOR = Estimator

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_BY_TYPE(self.ESTIMATOR))+'.predictProbability()')
        self.setGroup(GROUP_BY_TYPE(self.ESTIMATOR))

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('probability', 'Probability'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', type=Classifier, progress=progress)
        estimator.predictProbability(image, mask, filename=self.getOutputValue('probability'), progress=progress)

class ClassifierInfo(EstimatorInfo):
    ESTIMATOR = Classifier

class ClassifierPredict(EstimatorPredict):
    ESTIMATOR = Classifier

class ClassifierPredictProbability(EstimatorPredictProbability):
    ESTIMATOR = Classifier

class RegressorInfo(EstimatorInfo):
    ESTIMATOR = Regressor

class RegressorPredict(EstimatorPredict):
    ESTIMATOR = Regressor

class RegressorPredictProbability(EstimatorPredictProbability):
    ESTIMATOR = Regressor

class TransformerInfo(EstimatorInfo):
    ESTIMATOR = Transformer

class TransformerTransform(EstimatorTransform):
    ESTIMATOR = Transformer

class TransformerTransformInverse(EstimatorTransformInverse):
    ESTIMATOR = Transformer

class ClustererInfo(EstimatorInfo):
    ESTIMATOR = Clusterer

class ClustererPredict(EstimatorPredict):
    ESTIMATOR = Clusterer

class ClustererTransform(EstimatorTransform):
    ESTIMATOR = Clusterer

class ClassificationAssessClassificationPerformance(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_CLASSIFICATION)+'.assessClassificationPerformance()')
        self.setGroup(GROUP_CLASSIFICATION)
        self.addParameter(ParameterRaster('predicted', 'Predicted Classification'))
        self.addParameter(ParameterRaster('observed', 'Observed Classification'))


    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        predicted.assessClassificationPerformance(observed).info()

class ClassificationAssessClassificationPerformanceAdjusted(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_CLASSIFICATION)+'.assessClassificationPerformance() (adjusted)')
        self.setGroup(GROUP_CLASSIFICATION)

        self.addParameter(ParameterRaster('predicted', 'Predicted Classification'))
        self.addParameter(ParameterRaster('observed', 'Observed Classification'))
        self.addParameter(ParameterRaster('stratification', 'Stratification'))

    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        stratification = self.getParameterClassification('stratification')

        predicted.assessClassificationPerformance(observed, stratification).info()

class ClassificationAssessClusteringPerformance(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_CLASSIFICATION)+'.assessClusteringPerformance()')
        self.setGroup(GROUP_CLASSIFICATION)
        self.addParameter(ParameterRaster('observed', 'Observed Clustering'))
        self.addParameter(ParameterRaster('predicted', 'Predicted Clustering'))

    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        predicted.assessClusteringPerformance(observed).info()

class ClassificationStatistics(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_CLASSIFICATION) + '.statistics()')
        self.setGroup(GROUP_CLASSIFICATION)

        self.addParameter(ParameterRaster('image', 'Image'))

    def processAlgorithm(self, progress):

        try:
            image = self.getParameterClassification('image')
        except:
            image = self.getParameterImage('image')

        image.statistics().info()

class RegressionAssessRegressionPerformance(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_REGRESSOR)+'.assessRegressionPerformance()')
        self.setGroup(GROUP_REGRESSOR)
        self.addParameter(ParameterRaster('observed', 'Observed Regression'))
        self.addParameter(ParameterRaster('predicted', 'Predicted Regression'))

    def processAlgorithm(self, progress):

        observed = self.getParameterRegression('observed')
        predicted = self.getParameterRegression('predicted')
        predicted.assessRegressionPerformance(observed).info()


class ProbabilityArgmaxProbabilityClassification(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_PROBABILITY)+'.argmaxProbabilityClassification()')
        self.setGroup(GROUP_PROBABILITY)

        self.addParameter(ParameterRaster('probability', 'Probability'))
        self.addParameter(ParameterNumber('minWinProb', 'Minimal Winner Probability', minValue=0., maxValue=1., default=0.))
        self.addParameter(ParameterNumber('minCumProb', 'Minimal Cumulativ Probability', minValue=0., maxValue=1., default=0.999))
        self.addOutput(OutputRaster('classification', 'Classification'))

    def processAlgorithm(self, progress):

        propability = self.getParameterProbability('probability')
        minWinProb = self.getParameterValue('minWinProb')
        minCumProb = self.getParameterValue('minCumProb')

        propability.argmaxProbabilityClassification(filename=self.getOutputValue('classification'), minWinProb=minWinProb, minCumProb=minCumProb, progress=progress)

class ProbabilityRgbClassColorComposite(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_PROBABILITY)+'.rgbClassColorComposite()')
        self.setGroup(GROUP_PROBABILITY)

        self.addParameter(ParameterRaster('probability', 'Probability'))
        self.addOutput(OutputRaster('rgb', 'RGB Class Color Composite'))

    def processAlgorithm(self, progress):

        propability = self.getParameterProbability('probability')
        propability.rgbClassColorComposite(filename=self.getOutputValue('rgb'), progress=progress)

class VectorClassificationCreateOccurrence(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_VECTORCLASSIFICATION)+'.occurrenceImage()')
        self.setGroup(GROUP_VECTORCLASSIFICATION)

        self.addParameter(ParameterVector('vector', 'Vector Classification', shapetype=ParameterVector.VECTOR_TYPE_POLYGON))
        self.addParameter(ParameterTableField('idField', self.tr('Class ID Field'), parent='vector'))
        self.addParameter(ParameterTableField('nameField', self.tr('Class Name Field'), parent='vector'))
        self.addParameter(ParameterTableField('colorField', self.tr('Class Color Field'), parent='vector'))
        self.addParameter(ParameterRaster('reference', 'Image (defining the Reference Pixel Grid)'))
        self.addParameter(ParameterNumber('oversamplingRate', 'Oversampling Rate', minValue=1, default=10))
        self.addOutput(OutputRaster('occurrence', 'Occurrence Image'))

    def processAlgorithm(self, progress):

        vector = self.getParameterVectorClassification('vector', 'idField', 'nameField', 'colorField')
        reference = self.getParameterImage('reference')

        # create class occurence image at finer resolution
        occurrence = vector.occurrenceImage(filename=self.getOutputValue('occurrence'),
                                            pixelGrid=reference.pixelGrid,
                                            oversamplingRate=self.getParameterValue('oversamplingRate'))

class ImageInfo(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_IMAGE)+'.info()')
        self.setGroup(GROUP_IMAGE)

        self.addParameter(ParameterRaster('image', 'Image'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        image.info()

class ImageStatistics(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_IMAGE)+'.statistics()')
        self.setGroup(GROUP_IMAGE)

        self.addParameter(ParameterRaster('image', 'Image'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        image.statistics().info()

class ImageResample(EnMAPBoxGeoAlgorithm):

    R = GDALWARP_R_OPTIONS

    def defineCharacteristics(self):

        self.setName(INSTANCE_OF(GROUP_IMAGE) + '.resample()')
        self.setGroup(GROUP_IMAGE)

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('pixelGridImage', 'Pixel Grid from Image'))
        self.addParameter(ParameterSelection('r', 'Resampling Methode', options=self.R, default=0))
        self.addParameter(ParameterBoolean('saveAsVRT', 'save as VRT'))
        self.addOutput(OutputRaster('resampled', 'Output Image'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        pixelGridImage = self.getParameterImage('pixelGridImage')
        resampledFilename = self.getOutputValue('resampled')
        r = self.R[self.getParameterValue('r')]

        if self.getParameterValue('saveAsVRT'):
            of = 'VRT'
        else:
            of = 'GTiff'

        resampled = image.resample(filename=resampledFilename, pixelGrid=pixelGridImage.pixelGrid, r=r, of=of)

class ImageFromENVISpectralLibrary(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName(CLASS_OF(GROUP_IMAGE)+'.fromENVISpectralLibrary()')
        self.setGroup(GROUP_IMAGE)

        self.addParameter(ParameterFile('speclib', 'ENVI Spectral Library', optional=False))
        self.addOutput(OutputRaster('importedSpeclib', 'Pseudo Image'))

    def processAlgorithm(self, progress):

        infilename = self.getParameterValue('speclib')
        outfilename = self.getOutputValue('importedSpeclib')
        Image.fromENVISpectralLibrary(infilename=infilename, outfilename=outfilename)

if __name__ == '__main__':
    pass