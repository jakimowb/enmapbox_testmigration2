# Import Processing libraries to add the algorithms to Processing toolbox
from processing.core.Processing import Processing
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.parameters import *
from processing.core.outputs import *

import traceback

from enmapbox.processing.estimators import Classifiers
from enmapbox.processing.environment import Environment
from enmapbox.processing.types import Image, Classification, Mask, Estimator, unpickle

class EnMAPBoxProvider(AlgorithmProvider):
    def __init__(self):

        AlgorithmProvider.__init__(self)
        self.alglist = [ImageMLFit('imageML Fit', 'imageML', ''), ImageMLPredict(),
                        ImageMLOpenHyMapA()]

        for estimator in Classifiers().yieldAll():
            self.alglist.append(
                ImageMLFit(estimator.name() + ' Fit', 'imageML Classifier', 'Classifiers.' + estimator.signature()))

            #        for name, statement in eb.regressor.AllSignatures():
            #            self.alglist.append(ImageMLFit(name + ' Fit', 'imageML Regressors', statement))

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


class EnmapBoxParameterSelection(ParameterSelection):

    def __init__(self, options, name='', description='', default=-1):
        ParameterSelection.__init__(self, name=name, description=description, options=options, default=default)


class EnmapBoxParameterSelectionImage(EnmapBoxParameterSelection):

    def __init__(self, name='', description='', default=-1, optional=False):
        options = Environment.rasterFilenames
        EnmapBoxParameterSelection.__init__(self, options=options, name=name, description=description, default=default)


class EnmapBoxParameterSelectionModel(EnmapBoxParameterSelection):

    def __init__(self, name='', description='', default=-1, optional=False):
        options = Environment.modelFilenames
        EnmapBoxParameterSelection.__init__(self, options=options, name=name, description=description, default=default)


class EnmapBoxOutputFileModel(OutputFile):

    def __init__(self, name='', description='', ext=None):
        OutputFile.__init__(self, name=name, description=description, ext=ext)


class EnMAPBoxGeoAlgorithm(GeoAlgorithm):

    def getParameterValue(self, name):
        for param in self.parameters:
            if param.name == name:
                if isinstance(param, EnmapBoxParameterSelection):
                    return param.options[param.value]
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
        image = os.path.join(root, 'Hymap_Berlin-A_Image')
        mask = os.path.join(root, 'Hymap_Berlin-A_Mask')
        labels = os.path.join(root, 'Hymap_Berlin-A_Classification-Training-Sample')

        self.setOutputValue('image', image)
        self.setOutputValue('mask', mask)
        self.setOutputValue('labels', labels)

        for filename in [image, mask, labels]:
            Environment.openRaster(filename)

class ImageMLFit(EnMAPBoxGeoAlgorithm):

    def __init__(self, name, group, statement):

        self.name_ = name
        self.group_ = group
        self.statement = statement
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):

        self.name = self.name_
        self.group = self.group_
        self.addParameter(EnmapBoxParameterSelectionImage('image', 'Image'))
        self.addParameter(EnmapBoxParameterSelectionImage('labels', 'Labels'))

        self.addParameter(ParameterString('parameters', 'Parameters', self.statement, multiline=True))
        self.addOutput(EnmapBoxOutputFileModel('model', 'Fitted Model'))

    def processAlgorithm(self, progress):
        image = Image(self.getParameterValue('image'))

        try:
            filename = self.getParameterValue('labels')
            labels = Classification(filename)
        except:
            traceback.print_exc()
            raise GeoAlgorithmExecutionException(r'Labels (' + filename + ') is not a correct classification image!')

        try:
            estimator = eval(self.getParameterValue('parameters'))
        except:
            traceback.print_exc()
            raise GeoAlgorithmExecutionException('Statement could not be evaluated!')

        assert isinstance(estimator, Estimator), 'Model is not an estimator!'
        estimator.fit(image, labels, progress=progress)
        estimator.pickle(self.getOutputValue('model'), progress=progress)
        estimator.info()


class ImageMLPredict(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):

        self.name = 'imageML Predict'
        self.group = 'imageML'

        self.addParameter(EnmapBoxParameterSelectionImage('image', 'Image', optional=True))
        self.addParameter(ParameterRaster('mask', 'Mask', optional=True))
        self.addParameter(EnmapBoxParameterSelectionModel('model', 'Model'))
        self.addOutput(OutputRaster('prediction', 'Prediction'))

    def processAlgorithm(self, progress):

        image = Image(self.getParameterValue('image'))
        if self.getParameterValue('mask'):
            mask = Mask(self.getParameterValue('mask'))
        else:
            mask = None

        estimator = unpickle(str(self.getParameterValue('model')), progress=progress)
        assert isinstance(estimator, Estimator), 'Model is not an estimator!'

        estimator.predict(image, mask, filename=self.getOutputValue('prediction'), progress=progress)
