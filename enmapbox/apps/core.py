# Import Processing libraries to add the algorithms to Processing toolbox
import enmapbox.processing
import enmapbox.processing.estimators
from processing.core.Processing import Processing
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *
from processing.core.outputs import *
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog
from processing.core.outputs import *
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.gui.AlgorithmDialog import AlgorithmDialog


class EnMAPBoxProvider(AlgorithmProvider):
    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.alglist = [ImageMLFit('imageML Fit', 'imageML', ''), ImageMLPredict(),
                        ImageMLOpenHyMapA()]

        for estimator in enmapbox.processing.estimators.all(enmapbox.processing.estimators.Classifiers):
            self.alglist.append(
                ImageMLFit(estimator.name() + ' Fit', 'imageML Classifier', 'eb.Classifiers.' + estimator.signature()))

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


class ToyAllParameters(GeoAlgorithm):
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
        self.addParameter(
            ParameterSelection(self.INPUT_SELECTION, 'ParameterSelection', options=enmapbox.processing.env.filelist))
        self.addParameter(
            ParameterString(self.INPUT_STRING, 'ParameterString', default=''.join(enmapbox.processing.env.filelist)))
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


class ImageMLOpenHyMapA(GeoAlgorithm):
    def defineCharacteristics(self):
        self.name = 'Open HyMap A'
        self.group = 'Management'

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('labels', 'Labels'))
        # self.addOutput(OutputHTML('html', 'HTML Report'))

    def processAlgorithm(self, progress):
        self.setOutputValue('image', r'C:\Work\data\Hymap_Berlin-A_Image')
        self.setOutputValue('mask', r'C:\Work\data\Hymap_Berlin-A_Mask')
        self.setOutputValue('labels', r'C:\Work\data\Hymap_Berlin-A_Classification-Training-Sample')


class ImageMLFit(GeoAlgorithm):
    INPUT_IMAGE = 'INPUT_IMAGE'
    INPUT_LABELS = 'INPUT_LABELS'
    INPUT_PARAMS = 'INPUT_PARAMS'
    INPUT_OPENHTML = 'INPUT_OPENHTML'
    OUTPUT_MODEL = 'OUTPUT_MODEL'
    OUTPUT_HTML = 'OUTPUT_HTML'

    def __init__(self, name, group, statement):

        self.name_ = name
        self.group_ = group
        self.statement = statement
        GeoAlgorithm.__init__(self)

    def defineCharacteristics(self):

        self.name = self.name_
        self.group = self.group_
        self.addParameter(ParameterRaster(self.INPUT_IMAGE, 'Image', optional=False))
        self.addParameter(ParameterRaster(self.INPUT_LABELS, 'Labels', optional=False))
        self.addParameter(ParameterString(self.INPUT_PARAMS, 'Parameters', self.statement, multiline=True))
        self.addOutput(OutputFile(self.OUTPUT_MODEL, 'Fitted Model'))
        self.addOutput(OutputHTML(self.OUTPUT_HTML, 'ImageML Fit Report'))
        self.addParameter(ParameterBoolean(self.INPUT_OPENHTML, 'Open Report in Web Browser?', True))

    def processAlgorithm(self, progress):

        image = enmapbox.processing.Image(self.getParameterValue(self.INPUT_IMAGE))
        labels = enmapbox.processing.Classification(self.getParameterValue(self.INPUT_LABELS))
        try:
            estimator = eval(self.getParameterValue(self.INPUT_PARAMS))
        except:
            raise GeoAlgorithmExecutionException('Parameters statement could not be evaluated!')

        assert isinstance(estimator, enmapbox.processing.Estimator), 'Model is not an estimator!'
        estimator.fit(image, labels, progress=progress)
        estimator.pickle(self.getOutputValue(self.OUTPUT_MODEL), progress=progress)
        report = estimator.report().saveHTML(self.getOutputValue(self.OUTPUT_HTML))
        if self.getParameterValue(self.INPUT_OPENHTML):
            report.open()


class ImageMLPredict(GeoAlgorithm):
    INPUT_IMAGE = 'INPUT_IMAGE'
    INPUT_MASK = 'INPUT_MASK'
    INPUT_MODEL = 'INPUT_MODEL'
    OUTPUT_PREDICTION = 'OUTPUT_PREDICTION'

    def defineCharacteristics(self):

        self.name = 'imageML Predict'
        self.group = 'imageML'

        self.addParameter(ParameterRaster(self.INPUT_IMAGE, 'Image', optional=False))
        self.addParameter(ParameterRaster(self.INPUT_MASK, 'Mask', optional=True))
        self.addParameter(ParameterFile(self.INPUT_MODEL, 'Model'))
        self.addOutput(OutputRaster(self.OUTPUT_PREDICTION, 'Prediction'))

    def processAlgorithm(self, progress):

        image = enmapbox.processing.Image(self.getParameterValue(self.INPUT_IMAGE))
        if self.getParameterValue(self.INPUT_MASK):
            mask = enmapbox.processing.Mask(self.getParameterValue(self.INPUT_MASK))
        else:
            mask = None

        estimator = enmapbox.processing.unpickle(str(self.getParameterValue(self.INPUT_MODEL)), progress=progress)
        assert isinstance(estimator, enmapbox.processing.Estimator), 'Model is not an estimator!'

        estimator.predict(image, mask, filename=self.getOutputValue(self.OUTPUT_PREDICTION), progress=progress)
