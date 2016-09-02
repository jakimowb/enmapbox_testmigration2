# Import Processing libraries to add the algorithms to Processing toolbox
from processing.core.Processing import Processing
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.parameters import *
from processing.core.outputs import *

import traceback

from enmapbox.processing.estimators import Classifiers, Regressors, Clusterers, Transformers
from enmapbox.processing.environment import Environment
from enmapbox.processing.types import Image, Classification, Probability, Regression, Mask, Estimator, Classifier, Regressor, Transformer, Clusterer, unpickle

class EnMAPBoxProvider(AlgorithmProvider):
    def __init__(self):

        AlgorithmProvider.__init__(self)
        self.alglist = list()
        self.alglist.append(OpenEnmapBoxRaster(showInModeler=True))
        Alglist = [ImageMLOpenHyMapA, ImageMLPredict, ImageMLPredictProbability,
                   ImageMLTransform, ImageMLTransformInverse, ImageMLArgmaxProbability]

        for Alg in Alglist:
            self.alglist.append(Alg(showInToolbox=True))
            self.alglist.append(Alg(showInModeler=True))

        # insert generic Scikit-Learn estimators
        for estimator in Classifiers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Classifiers', 'Classifiers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Classifiers', 'Classifiers.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Regressors().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Regressors', 'Regressors.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Regressors', 'Regressors.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Clusterers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Clusterers', 'Clusterers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Clusterers', 'Clusterers.' + estimator.signature(), estimator, showInModeler=True))
        for estimator in Transformers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Transformers', 'Transformers.' + estimator.signature(), estimator, showInToolbox=True))
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Transformers', 'Transformers.' + estimator.signature(), estimator, showInModeler=True))



                #             self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Regressors', statement))

            #        for name, statement in eb.clusterer.AllSignatures():
            #            self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Clusterer', statement))

            #        for name, statement in eb.transformer.AllSignatures():
            #            self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Transformer', statement))

            #        for alg in self.alglist:
            #            alg.provider = self

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

class EnmapBoxParameter(): pass

class EnmapBoxParameterModel(EnmapBoxParameter):

    def __init__(self, name='', description='', default=0, optional=False):
        self.name = name
        self.required = not optional
        self.paramModeler = ParameterFile(name=name, description=description, optional=optional)
        if optional: description += ' [optional]'
        self.paramToolbox = ParameterSelection(name=name, description=description, options=Environment.modelFilenames, default=default)

    def getValue(self, geoAlgorithm):

        param = geoAlgorithm.getParameterFromName(self.name)
        if geoAlgorithm._showInToolbox:

            if param.value == 0:
                if self.required:
                    raise GeoAlgorithmExecutionException(param.description + ': select a file')
                else:
                    return None
            return param.options[param.value]

        if geoAlgorithm._showInModeler:
            geoAlgorithm.getParameterValue(param)


class EnmapBoxParameterRaster(EnmapBoxParameter):

    def __init__(self, name='', description='', default=0, optional=False):
        self.name = name
        self.required = not optional
        self.paramModeler = ParameterRaster(name=name, description=description, optional=optional)
        if optional: description += ' [optional]'
        self.paramToolbox = ParameterSelection(name=name, description=description, options=Environment.rasterFilenames, default=default)

    def getValue(self, geoAlgorithm):
        param = geoAlgorithm.getParameterFromName(self.name)
        if geoAlgorithm._showInToolbox:
            if param.value == 0:
                if self.required:
                    raise GeoAlgorithmExecutionException(param.description + ': select a file')
                else:
                    return None
            return param.options[param.value]

        if geoAlgorithm._showInModeler:
            return geoAlgorithm.getParameterValue(param)

class EnmapBoxParameterRaster2(EnmapBoxParameterRaster):
    def __init__(self, *args, **kwargs):
        EnmapBoxParameterRaster.__init__(self, *args, **kwargs)
        self.paramModeler = self.paramToolbox

class EnmapBoxOutputFile(OutputFile):

    def __init__(self, name='', description='', ext=None):
        OutputFile.__init__(self, name=name, description=description, ext=ext)

class EnmapBoxOutputRaster(OutputRaster):

    def __init__(self, name='', description=''):
        OutputRaster.__init__(self, name=name, description=description)

class EnMAPBoxGeoAlgorithm(GeoAlgorithm):

    def __init__(self, showInToolbox=False, showInModeler=False):

        assert showInModeler+showInToolbox == 1, self.__class__

        self._showInToolbox = showInToolbox
        self._showInModeler = showInModeler
        self.parametersEnmapBox = dict()
        GeoAlgorithm.__init__(self)
        self.showInToolbox = showInToolbox
        self.showInModeler = showInModeler

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

    def addParameter(self, param):
        if isinstance(param, EnmapBoxParameter):
            if self._showInToolbox:
                GeoAlgorithm.addParameter(self, param.paramToolbox)
            if self._showInModeler:
                GeoAlgorithm.addParameter(self, param.paramModeler)
            self.parametersEnmapBox[param.name] = param
        else:
            GeoAlgorithm.addParameter(self, param)

    def getParameterValue(self, name):
        if name in self.parametersEnmapBox:
            return self.parametersEnmapBox[name].getValue(geoAlgorithm=self)
        else:
            return GeoAlgorithm.getParameterValue(self, name)

    def getParameterRaster(self, name, type=Image):
        filename = self.getParameterValue(name)
        try:
            return type(filename)
        except:
            if self.parametersEnmapBox[name].required:
                param = self.getParameterFromName(name)
                traceback.print_exc()
                raise GeoAlgorithmExecutionException(param.description + ': (' + str(filename) + ') is not a correct ' + str(type) + ' file!')
            else:
                return None

    def getParameterSklearnStatement(self, name, type=Estimator):
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

    def setOutputRaster(self, outputName, raster):
        filename = raster.filename
        self.setOutputValue(outputName=outputName, value=filename)
        Environment.openRaster(filename)


    def setOutputEstimator(self, outputName, estimator, progress):
        filename = self.getOutputValue(outputName)
        estimator.pickle(filename, progress=progress)
        Environment.openModel(filename)


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

class OpenEnmapBoxRaster(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open Image')
        self.setGroup('Management')

        self.addParameter(EnmapBoxParameterRaster2('inimage', 'Image'))
        self.addOutput(EnmapBoxOutputRaster('outimage', 'Output Image'))

    def processAlgorithm(self, progress):

        image = self.getParameterRaster('inimage')
        self.setOutputRaster('outimage', image)


class ImageMLOpenHyMapA(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.setName('Open HyMap A')
        self.setGroup('Management')

        self.addOutput(EnmapBoxOutputRaster('image', 'Image'))
        self.addOutput(EnmapBoxOutputRaster('mask', 'Mask'))
        self.addOutput(EnmapBoxOutputRaster('labels', 'Labels'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        self.setOutputRaster('image', Image(os.path.join(root, 'Hymap_Berlin-A_Image')))
        self.setOutputRaster('mask', Mask(os.path.join(root, 'Hymap_Berlin-A_Mask')))
        self.setOutputRaster('labels', Classification(os.path.join(root, 'Hymap_Berlin-A_Classification-Training-Sample')))



class ImageMLFit(EnMAPBoxGeoAlgorithm):

    def __init__(self, name, group, statement, estimator, showInToolbox=False, showInModeler=False):

        self.name_ = name
        self.group_ = group
        self.statement = statement
        self.estimator = estimator
        self.MODEL = self.estimator.name()
        EnMAPBoxGeoAlgorithm.__init__(self, showInToolbox=showInToolbox, showInModeler=showInModeler)

    def defineCharacteristics(self):

        self.setName(self.name_)
        self.setGroup(self.group_)
        self.addParameter(EnmapBoxParameterRaster('image', 'Image'))
        if isinstance(self.estimator, Classifier):
            self.addParameter(EnmapBoxParameterRaster('labels', 'Classification'))
        if isinstance(self.estimator, Regressor):
            self.addParameter(EnmapBoxParameterRaster('labels', 'Regression'))
        if isinstance(self.estimator, Transformer) or isinstance(self.estimator, Clusterer):
            self.addParameter(EnmapBoxParameterRaster('labels', 'Mask', optional=True))

        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(EnmapBoxOutputFile(self.MODEL, 'Fitted Model', ext='iml'))

    def processAlgorithm(self, progress):

        image = self.getParameterRaster('image')
        labels = self.getParameterRaster('labels', Classification)
        estimator = self.getParameterSklearnStatement('parameters', self.estimator.__class__)

        estimator.fit(image, labels, progress=progress)
        estimator.info()

        self.setOutputEstimator(self.MODEL, estimator=estimator, progress=progress)


class ImageMLPredict(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Predict')
        self.setGroup('imageML')

        self.addParameter(EnmapBoxParameterRaster('image', 'Image'))
        self.addParameter(EnmapBoxParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(EnmapBoxParameterModel('model', 'Model'))
        self.addOutput(EnmapBoxOutputRaster('prediction', 'Prediction'))


    def processAlgorithm(self, progress):

        image = self.getParameterRaster('image')
        mask = self.getParameterRaster('mask', Mask)

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimation = estimator.predict(image, mask, filename=self.getOutputValue('prediction'), progress=progress)

        self.setOutputRaster('prediction', estimation)

class ImageMLTransform(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Transform')
        self.setGroup('imageML')

        self.addParameter(EnmapBoxParameterRaster('image', 'Image'))
        self.addParameter(EnmapBoxParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(EnmapBoxParameterRaster('model', 'Model'))
        self.addOutput(EnmapBoxOutputRaster('transformation', 'Transformation'))

    def processAlgorithm(self, progress):

        image = self.getParameterValue('image')
        mask = self.getParameterValue('mask')

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimator.transform(image, mask, filename=self.getOutputValue('transformation'), progress=progress)

class ImageMLTransformInverse(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Transform Inverse')
        self.setGroup('imageML')

        #self.addParameter(EnmapBoxParameterSelectionImage('transformation', 'Transformation'))
        #self.addParameter(EnmapBoxParameterSelectionMask('mask', 'Mask', optional=True))
        #self.addParameter(EnmapBoxParameterSelectionModel('model', 'Model'))
        #self.addOutput(EnmapBoxOutputRaster('inverseTransformation', 'Inversion'))

    def processAlgorithm(self, progress):

        transformation = self.getParameterValue('transformation')
        mask = self.getParameterValue('mask')

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimator.transformInverse(transformation, mask, filename=self.getOutputValue('inverseTransformation'), progress=progress)


class ImageMLPredictProbability(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Predict Probability')
        self.setGroup('imageML')

        self.addParameter(EnmapBoxParameterRaster('image', 'Image'))
        self.addParameter(EnmapBoxParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(EnmapBoxParameterModel('model', 'Model'))
        self.addOutput(EnmapBoxOutputRaster('probability', 'Probability'))

    def processAlgorithm(self, progress):

        image = self.getParameterValue('image')
        mask = self.getParameterValue('mask')

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not a estimator!'

        estimator.predictProbability(image, mask, filename=self.getOutputValue('probability'), progress=progress)


class ImageMLArgmaxProbability(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.setName('Argmax Probability Classification')
        self.setGroup('imageML')

        self.addParameter(EnmapBoxParameterRaster('probability', 'Probability'))
        self.addOutput(EnmapBoxOutputRaster('classification', 'Classification'))

    def processAlgorithm(self, progress):

        propability = self.getParameterValue('probability')
        propability.argmax(filename=self.getOutputValue('classification'), progress=progress)
