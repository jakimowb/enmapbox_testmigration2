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
from enmapbox.processing.types import Image, Classification, Regression, Mask, NoMask, Estimator, Classifier, Regressor, Transformer, Clusterer, unpickle

class EnMAPBoxProvider(AlgorithmProvider):
    def __init__(self):

        AlgorithmProvider.__init__(self)
        self.alglist = [ImageMLPredict(),
                        ImageMLOpenHyMapA()]

        for estimator in Classifiers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Classifiers', 'Classifiers.' + estimator.signature(), estimator))
        for estimator in Regressors().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Regressors', 'Regressors.' + estimator.signature(), estimator))
        for estimator in Clusterers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Clusterers', 'Clusterers.' + estimator.signature(), estimator))
        for estimator in Transformers().yieldAll():
            self.alglist.append(ImageMLFit(estimator.name() + ' Fit', 'imageML Transformers', 'Transformers.' + estimator.signature(), estimator))



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


class EnmapBoxParameterSelectionFilename(ParameterSelection):

    def __init__(self, options, name='', description='', default=0, required=True):
        self.required = required
        if not required:
            description += ' [optional]'
        ParameterSelection.__init__(self, name=name, description=description, options=options, default=default)

    def getValue(self):
        if self.value==0:
            if self.required:
                raise GeoAlgorithmExecutionException(self.description+': select a file')
            else:
                return None
        return self.options[self.value]

class EnmapBoxParameterSelectionImage(EnmapBoxParameterSelectionFilename):

    enmapType = Image
    enmapOptions = Environment.rasterFilenames

    def __init__(self, name='', description='', default=0, required=True):
        EnmapBoxParameterSelectionFilename.__init__(self, options=self.enmapOptions, name=name, description=description, default=default, required=required)

    def getValue(self):

        filename = EnmapBoxParameterSelectionFilename.getValue(self)
        if filename is None:
            return None
        try:
            return self.enmapType(filename)
        except:
            traceback.print_exc()
            raise GeoAlgorithmExecutionException(self.description+': ' + filename + ' is not a correct ' + str(self.enmapType).split('.')[-1] + '!')


class EnmapBoxParameterSelectionClassification(EnmapBoxParameterSelectionImage):

    enmapType = Classification
    enmapOptions = Environment.rasterFilenames

class EnmapBoxParameterSelectionRegression(EnmapBoxParameterSelectionImage):

    enmapType = Regression
    enmapOptions = Environment.rasterFilenames

class EnmapBoxParameterSelectionMask(EnmapBoxParameterSelectionImage):

    enmapType = Mask
    enmapOptions = Environment.rasterFilenames

    def getValue(self):

        mask = EnmapBoxParameterSelectionImage.getValue(self)
        if mask is None:
            mask = NoMask()
        return mask

class EnmapBoxParameterSelectionModel(EnmapBoxParameterSelectionFilename):

    enmapOptions = Environment.modelFilenames

    def __init__(self, name='', description='', default=0, required=True):
        EnmapBoxParameterSelectionFilename.__init__(self, options=self.enmapOptions, name=name, description=description, default=default, required=required)


class EnmapBoxOutputFileModel(OutputFile):

    def __init__(self, name='', description='', ext=None):
        OutputFile.__init__(self, name=name, description=description, ext=ext)


class EnMAPBoxGeoAlgorithm(GeoAlgorithm):

    def getParameterValue(self, name):
        for param in self.parameters:
            if param.name == name:
                if isinstance(param, EnmapBoxParameterSelectionFilename):
                    return param.getValue()
                return param.value
        return None

    def getOutputValue(self, name):
        for out in self.outputs:
            if out.name == name:
                if isinstance(out, EnmapBoxOutputFileModel):
                     Environment.openModel(out.value)
                return out.value
        return None

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
        self.name = 'Show all Parameters'
        self.group = 'Testing'

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
        self.name = 'Open HyMap A'
        self.group = 'Management'

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('labels', 'Labels'))

    def processAlgorithm(self, progress):

        root = r'C:\Work\data'
        root = r'C:\Program Files\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image'

        image = os.path.join(root, 'Hymap_Berlin-A_Image')
        mask = os.path.join(root, 'Hymap_Berlin-A_Mask')
        labels = os.path.join(root, 'Hymap_Berlin-A_Classification-Training-Sample')

        self.setOutputValue('image', image)
        self.setOutputValue('mask', mask)
        self.setOutputValue('labels', labels)

        for filename in [image, mask, labels]:
            Environment.openRaster(filename)

class ImageMLFit(EnMAPBoxGeoAlgorithm):

    def __init__(self, name, group, statement, estimator):

        self.name_ = name
        self.group_ = group
        self.statement = statement
        self.estimator = estimator
        self.MODEL = self.estimator.name()
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):

        self.name = self.name_
        self.group = self.group_
        self.addParameter(EnmapBoxParameterSelectionImage('image', 'Image'))
        if isinstance(self.estimator, Classifier):
            self.addParameter(EnmapBoxParameterSelectionClassification('labels', 'Classification'))
        if isinstance(self.estimator, Regressor):
            self.addParameter(EnmapBoxParameterSelectionRegression('labels', 'Regression'))
        if isinstance(self.estimator, Transformer) or isinstance(self.estimator, Clusterer):
            self.addParameter(EnmapBoxParameterSelectionMask('labels', 'Mask', required=False))

        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(EnmapBoxOutputFileModel(self.MODEL, 'Fitted Model', ext='model'))

    def processAlgorithm(self, progress):

        image = self.getParameterValue('image')
        labels = self.getParameterValue('labels')
        try:
            estimator = eval(self.getParameterValue('parameters'))
        except:
            traceback.print_exc()
            raise GeoAlgorithmExecutionException('Statement could not be evaluated!')

        if not isinstance(estimator, Estimator):
            raise GeoAlgorithmExecutionException('Model is not a correct estimator!')

        estimator.fit(image, labels, progress=progress)
        estimator.pickle(self.getOutputValue(self.MODEL), progress=progress)
        estimator.info()


class ImageMLPredict(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'imageML Predict'
        self.group = 'imageML'

        self.addParameter(EnmapBoxParameterSelectionImage('image', 'Image'))
        self.addParameter(EnmapBoxParameterSelectionMask('mask', 'Mask', required=False))
        self.addParameter(EnmapBoxParameterSelectionModel('model', 'Model'))
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progress):

        image = self.getParameterValue('image')
        mask = self.getParameterValue('mask')

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimator.predict(image, mask, filename=self.getOutputValue('prediction'), progress=progress)
