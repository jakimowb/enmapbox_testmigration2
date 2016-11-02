# Import Processing libraries to add the algorithms to Processing toolbox

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.parameters import *
from processing.core.outputs import *
import PyQt4.QtCore
import traceback

from enmapbox.processing.estimators import Classifiers, Regressors, Clusterers, Transformers
from enmapbox.processing.environment import Environment
from enmapbox.processing.types import Image, Classification, Probability, Regression, Mask, Estimator, Classifier, Regressor, Transformer, Clusterer, unpickle

add = lambda main, sub: ' -> '.join([main, sub])
group_file  = '1. File'
group_tools = '2. Tools'
group_apps  = '3. Applications'
group_apps_ml = add(group_apps, 'Machine Learning')


class EnMAPBoxProvider(AlgorithmProvider):
    _instance = None

    @staticmethod
    def instance():
        return EnMAPBoxProvider._instance

    def __init__(self):

        AlgorithmProvider.__init__(self)
        if EnMAPBoxProvider.instance() is not None:
            print('Oh. It seems that the EnMAPBoxProvider was initialized twice.')
        EnMAPBoxProvider._instance = self

        self.alglist = list()

        Alglist = [AccuracyAssessmentClassififcation, AccuracyAssessmentClassififcationAdjusted, AccuracyAssessmentRegression, AccuracyAssessmentClustering,
                   ImageViewMetadata, ImageViewStatistics,
                   ImportENVISpectralLibrary,
                   ImageMLOpenHyMapA, ImageMLOpenHyMapB, ImageMLPredict, ImageMLPredictProbability, ImageMLViewModel,
                   ImageMLTransform, ImageMLTransformInverse, ImageMLArgmaxProbability]

        for Alg in Alglist:
            self.alglist.append(Alg(showInToolbox=True))
            self.alglist.append(Alg(showInModeler=True))

        # insert generic Scikit-Learn estimators
        for estimator in Classifiers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Classification'), 'Classifiers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Classification'), 'Classifiers.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Regressors().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Regression'), 'Regressors.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Regression'), 'Regressors.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Clusterers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Clustering'), 'Clusterers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Clustering'), 'Clusterers.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Transformers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Transformation'), 'Transformers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', add(group_apps_ml, 'Transformation'), 'Transformers.' + estimator.signature(), estimator, showInModeler=True))



                #             self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Regressors', statement))

            #        for name, statement in eb.clusterer.AllSignatures():
            #            self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Clusterer', statement))

            #        for name, statement in eb.transformer.AllSignatures():
            #            self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Transformer', statement))

            #        for alg in self.alglist:
            #            alg.provider = self



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

#    def getIcon(self):
#        return QIcon(":/plugins/EnMAP-Box/icon.svg")

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

    def getParameterRaster(self, name, type):

        param = self.getParameterFromName(name)
        assert isinstance(param, ParameterRaster)
        filename = param.value

        try:
            return type(filename)
        except:
            if not param.optional:
                traceback.print_exc()
                raise GeoAlgorithmExecutionException(param.description + ': (' + str(filename) + ') is not a correct ' + str(type) + ' file!')
            else:
                return None

    def getParameterImage(self, name):
        return self.getParameterRaster(name, type=Image)

    def getParameterClassification(self, name):
        return self.getParameterRaster(name, type=Classification)

    def getParameterRegression(self, name):
        return self.getParameterRaster(name, type=Regression)

    def getParameterMask(self, name):
        return self.getParameterRaster(name, type=Mask)

    def getParameterProbability(self, name):
        return self.getParameterRaster(name, type=Probability)


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
        # self.addParameter(ParameterDataObject(self.INPUT_DATAOBJECT, 'ParameterDataObject'))
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

class ImageMLOpenHyMapA(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open HyMap A')
        self.setGroup(group_file)

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))
        self.addOutput(OutputRaster('predicted', 'Predicted'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        self.setOutputRaster('image', Image(os.path.join(root, 'Hymap_Berlin-A_Image')))
        self.setOutputRaster('mask', Mask(os.path.join(root, 'Hymap_Berlin-A_Mask')))
        self.setOutputRaster('train', Classification(os.path.join(root, 'Hymap_Berlin-A_Classification-Training-Sample')))
        self.setOutputRaster('test', Classification(os.path.join(root, 'Hymap_Berlin-A_Classification-Validation-Sample')))
        self.setOutputRaster('predicted', Classification(os.path.join(root, 'Hymap_Berlin-A_Classification-Estimation')))


class ImageMLOpenHyMapB(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open HyMap B')
        self.setGroup(group_file)

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        self.setOutputRaster('image', Image(os.path.join(root, 'Hymap_Berlin-B_Image')))
        self.setOutputRaster('mask', Mask(os.path.join(root, 'Hymap_Berlin-B_Mask')))
        self.setOutputRaster('train',Regression(os.path.join(root, 'Hymap_Berlin-B_Regression-Training-Sample')))
        self.setOutputRaster('test', Regression(os.path.join(root, 'Hymap_Berlin-B_Regression-Validation-Sample')))


class ImageMLFit(EnMAPBoxGeoAlgorithm):

    def __init__(self, name, group, statement, estimator, showInToolbox=False, showInModeler=False):

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

class ImageViewMetadata(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Image Metadata')
        self.setGroup(group_tools)
        self.addParameter(ParameterRaster('image', 'Image'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        image.info()

class ImageViewStatistics(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Image Statistics')
        self.setGroup(group_tools)
        self.addParameter(ParameterRaster('image', 'Image'))

    def processAlgorithm(self, progress):

        try:
            image = self.getParameterClassification('image')
        except:
            image = self.getParameterImage('image')

        image.statistics().info()

class AccuracyAssessmentClassififcation(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Classification')
        self.setGroup('3. Applications -> Accuracy Assessment')
        self.addParameter(ParameterRaster('predicted', 'Predicted Classification'))
        self.addParameter(ParameterRaster('observed', 'Observed Classification'))


    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        predicted.assessClassificationPerformance(observed).info()

class AccuracyAssessmentClassififcationAdjusted(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Classification (adjusted)')
        self.setGroup('3. Applications -> Accuracy Assessment')

        self.addParameter(ParameterRaster('predicted', 'Predicted Classification'))
        self.addParameter(ParameterRaster('observed', 'Observed Classification'))
        self.addParameter(ParameterRaster('stratification', 'Stratification'))

    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        stratification = self.getParameterClassification('stratification')

        predicted.assessClassificationPerformance(observed, stratification).info()


class AccuracyAssessmentRegression(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Regression')
        self.setGroup('3. Applications -> Accuracy Assessment')
        self.addParameter(ParameterRaster('observed', 'Observed Regression'))
        self.addParameter(ParameterRaster('predicted', 'Predicted Regression'))

    def processAlgorithm(self, progress):

        observed = self.getParameterRegression('observed')
        predicted = self.getParameterRegression('predicted')
        predicted.assessRegressionPerformance(observed).info()

class AccuracyAssessmentClustering(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Clustering')
        self.setGroup('3. Applications -> Accuracy Assessment')
        self.addParameter(ParameterRaster('observed', 'Observed Clustering'))
        self.addParameter(ParameterRaster('predicted', 'Predicted Clustering'))

    def processAlgorithm(self, progress):

        observed = self.getParameterClassification('observed')
        predicted = self.getParameterClassification('predicted')
        predicted.assessClusteringPerformance(observed).info()

class ImportENVISpectralLibrary(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Import ENVI Spectral Library')
        self.setGroup(group_file)

        self.addParameter(ParameterFile('speclib', 'ENVI Spectral Library', optional=False))
        self.addOutput(OutputRaster('importedSpeclib', 'Pseudo Image'))


    def processAlgorithm(self, progress):

        infilename = self.getParameterValue('speclib')
        outfilename = self.getOutputValue('importedSpeclib')
        Image.importENVISpectralLibrary(infilename=infilename, outfilename=outfilename)


class ImageMLPredict(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Predict')
        self.setGroup(group_apps_ml)

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('prediction', 'Prediction'))


    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        modelfilename = self.getParameterFile('model')
        estimator = unpickle(modelfilename, progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimation = estimator.predict(image, mask, filename=self.getOutputValue('prediction'), progress=progress)

        self.setOutputRaster('prediction', estimation)

class ImageMLViewModel(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('View Model')
        self.setGroup(group_apps_ml)

        self.addParameterFile('model', 'Model')

    def processAlgorithm(self, progress):

        estimator = self.getParameterSklearnModel('model', progress=progress)
        estimation = estimator.info()


class ImageMLTransform(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Transform')
        self.setGroup(group_apps_ml)

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('transformation', 'Transformation'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', progress=progress, type=Transformer)
        estimator.transform(image, mask, filename=self.getOutputValue('transformation'), progress=progress)

class ImageMLTransformInverse(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Transform Inverse')
        self.setGroup(group_apps_ml)

        self.addParameter(ParameterRaster('transformation', 'Transformation'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('inverseTransformation', 'Inversion'))

    def processAlgorithm(self, progress):

        transformation = self.getParameterImage('transformation')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', progress=progress, type=Transformer)
        estimator.transformInverse(transformation, mask, filename=self.getOutputValue('inverseTransformation'), progress=progress)


class ImageMLPredictProbability(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Predict Probability')
        self.setGroup(group_apps_ml)

        self.addParameter(ParameterRaster('image', 'Image'))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameterFile('model', 'Model')
        self.addOutput(OutputRaster('probability', 'Probability'))

    def processAlgorithm(self, progress):

        image = self.getParameterImage('image')
        mask = self.getParameterMask('mask')
        estimator = self.getParameterSklearnModel('model', type=Classifier, progress=progress)
        estimator.predictProbability(image, mask, filename=self.getOutputValue('probability'), progress=progress)


class ImageMLArgmaxProbability(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Argmax Probability Classification')
        self.setGroup(group_apps_ml)

        self.addParameter(ParameterRaster('probability', 'Probability'))
        self.addOutput(OutputRaster('classification', 'Classification'))

    def processAlgorithm(self, progress):

        propability = self.getParameterProbability('probability')
        propability.argmax(filename=self.getOutputValue('classification'), progress=progress)

if __name__ == '__main__':
    print group_apps_ml