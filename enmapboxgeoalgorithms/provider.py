import sys
from qgis.core import *
from hubflow.core import *
import hubdc.progressbar
from enmapboxgeoalgorithms import ENMAPBOXGEOALGORITHMS_VERSION
# from enmapboxgeoalgorithms.algorithms import ALGORITHMS, TESTALGORITHMS
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm

TESTALGORITHMS = list()
ALGORITHMS = list()


class EnMAPProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        #for a in TESTALGORITHMS: self.addAlgorithm(a)
        for a in ALGORITHMS: self.addAlgorithm(a)

    def id(self):
        return 'EnMAPBoxTestProvider'

    def name(self):
        return 'EnMAP-Box Test Provider'

    def longName(self):
        version = ENMAPBOXGEOALGORITHMS_VERSION
        return 'EnMAP-Box TestProvider ({})'.format(version)

    def supportsNonFileBasedOutput(self):
        return False


class EnMAPAlgorithm(QgisAlgorithm):
    GROUP_ACCURACY_ASSESSMENT = 'Accuracy Assessment'
    GROUP_AUXILLIARY = 'Auxilliary'
    GROUP_CREATE_RASTER = 'Create Raster'
    GROUP_CREATE_SAMPLE = 'Create Sample'
    GROUP_CLASSIFICATION = 'Classification'
    GROUP_CLUSTERING = 'Clustering'
    GROUP_MASKING = 'Masking'
    GROUP_POSTPROCESSING = 'Post-Processing'
    GROUP_RANDOM = 'Random'
    GROUP_REGRESSION = 'Regression'
    GROUP_TEST = 'TEST'
    GROUP_TRANSFORMATION = 'Transformation'

    def initAlgorithm(self, configuration=None):
        self._configuration = configuration
        self.defineCharacteristics()

    def group(self):
        assert 0

    def displayName(self):
        assert 0

    def _generateId(self, name):
        id = name
        for c in ' !?-+/*()[]{}':
            id = id.replace(c, '')
        return id

    def groupId(self):
        groupId = self._generateId(self.group())
        return groupId

    def name(self):
        name = self._generateId(self.displayName())
        return name

    def validateInputCrs(self, parameters, context):
        return True  # we accept different crs per default

    def defineCharacteristics(self):
        assert 0, 'overload this methode!'

    def processAlgorithm(self, parameters, context, feedback):

        try:
            self._feedback = feedback
            self._progressBar = ProgressBar(feedback=feedback)
            self._context = context
            self._parameters = parameters
            result = self.processAlgorithm_()
            assert isinstance(result,
                              dict), 'return value error, expected a dict as return value, check {}.processAlgorithm_()'.format(
                self.__class__.__name__)
            return result
        except EnMAPAlgorithmParameterValueError as error:
            feedback.reportError(str(error))
            return {}
        except:

            import traceback
            traceback.print_exc()
            for line in traceback.format_exc().split('\n'):
                feedback.reportError(line)  # .replace('\n', '<br>')
            raise Exception('unexpected error')
            #return {}

    def addParameter_(self, parameterDefinition, help=None):
        self.addParameter(parameterDefinition=parameterDefinition)
        if help is None:
            help = 'undocumented parameter'
        parameterDefinition._helpString = help
        parameterDefinition.toolTip = lambda : 'Hello Tooltip'

    P_RASTER = 'raster'

    def addParameterRaster(self, name=P_RASTER, description='Raster', defaultValue=None, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterRasterLayer(name=name, description=description,
                                                             defaultValue=defaultValue, optional=optional),
                           help=help)

    def getParameterRaster(self, name=P_RASTER):
        assert name in self._parameters
        qgsRasterLayer = self.parameterAsRasterLayer(self._parameters, name, self._context)
        if qgsRasterLayer is None:
            return None
        elif isinstance(qgsRasterLayer, QgsRasterLayer):
            filename = qgsRasterLayer.source()
            return Raster(filename=filename)
        else:
            assert 0, repr(qgsRasterLayer)

    P_CLASSIFICATION = 'classification'

    def addParameterClassification(self, name=P_CLASSIFICATION, description='Classification', optional=False,
                                   help=None):
        self.addParameterRaster(name=name, description=description, optional=optional, help=help)

    def getParameterClassification(self, name=P_CLASSIFICATION, minOverallCoverage=None, minWinnerCoverage=None):
        return Classification(filename=self.getParameterRaster(name=name).filename,
                              minOverallCoverage=minOverallCoverage,
                              minWinnerCoverage=minWinnerCoverage)

    P_REGRESSION = 'regression'

    def addParameterRegression(self, name=P_REGRESSION, description='Regression', optional=False, help=None):
        self.addParameterRaster(name=name, description=description, optional=optional, help=help)

    def getParameterRegression(self, name=P_REGRESSION):
        return Regression(filename=self.getParameterRaster(name=name).filename)

    P_PROBABILITY = 'probability'

    def addParameterProbability(self, name=P_PROBABILITY, description='ClassProbability', optional=False, help=None):
        self.addParameterRaster(name=name, description=description, optional=optional, help=help)

    def getParameterProbability(self, name=P_PROBABILITY, minOverallCoverage=None, minWinnerCoverage=None):
        return Probability(filename=self.getParameterRaster(name=name).filename,
                           minOverallCoverage=minOverallCoverage,
                           minWinnerCoverage=minWinnerCoverage)

    P_MASK = 'mask'

    def addParameterMask(self, name=P_MASK, description='Mask', help=None):
        self.addParameterMap(name=name, description=description, optional=True, help=help)

    def getParameterMask(self, name=P_MASK):
        mask = self.getParameterMap(name=name)
        if isinstance(mask, Raster):
            mask = Mask(filename=mask.filename)
        return mask

    P_VECTOR = 'vector'

    def addParameterVector(self, name=P_VECTOR, description='Vector', defaultValue=None, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterVectorLayer(name=name, description=description,
                                                             defaultValue=defaultValue, optional=optional),
                           help=help)

    def getParameterVector(self, name=P_VECTOR, **kwargs):
        assert name in self._parameters
        qgsVectorLayer = self.parameterAsVectorLayer(self._parameters, name, self._context)

        if qgsVectorLayer is None:
            return None
        elif isinstance(qgsVectorLayer, QgsVectorLayer):
            filename = qgsVectorLayer.source()
            return Vector(filename=filename, **kwargs)
        else:
            assert 0, repr(qgsVectorLayer)

    P_MAP = 'map'

    def addParameterMap(self, name=P_MAP, description='Map', defaultValue=None, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterMapLayer(name=name, description=description,
                                                          defaultValue=defaultValue, optional=optional),
                           help=help)

    def getParameterMap(self, name=P_MAP):
        assert name in self._parameters, name
        qgsMapLayer = self.parameterAsLayer(self._parameters, name, self._context)
        if qgsMapLayer is None:
            return None
        elif isinstance(qgsMapLayer, QgsRasterLayer):
            filename = qgsMapLayer.source()
            return Raster(filename=filename)
        elif isinstance(qgsMapLayer, QgsVectorLayer):
            filename = qgsMapLayer.source()
            return Vector(filename=filename)
        else:
            assert 0, repr(qgsMapLayer)

    P_CLASSIDFIELD = 'classIdField'

    def addParameterVectorClassification(self, name=P_VECTOR, description='Vector', defaultValue=None, optional=False,
                                         minCoveragesDefaultValues=(None, None)):
        self.addParameterVector(name=name, description=description, defaultValue=defaultValue, optional=optional)
        self.addParameterField(name=self.P_CLASSIDFIELD, description='Class id attribute',
                               parentLayerParameterName=name,
                               type=QgsProcessingParameterField.Numeric)
        self.addParameterClassDefinition()
        self.addParameterMinCoverages(defaultValues=minCoveragesDefaultValues)
        self.addParameterOversampling()

    def getParameterVectorClassification(self):
        return VectorClassification(filename=self.getParameterVector().filename,
                                    idAttribute=self.getParameterField(self.P_CLASSIDFIELD),
                                    minOverallCoverage=self.getParameterMinOverallCoverage(),
                                    minWinnerCoverage=self.getParameterMinWinnerCoverage(),
                                    classDefinition=self.getParameterClassDefinition(),
                                    oversampling=self.getParameterOversampling())

    P_MINOVERALLCOVERAGE = 'minOverallCoverage'
    P_MINWINNERCOVERAGE = 'minWinnerCoverage'

    def addParameterMinCoverages(self, names=(P_MINOVERALLCOVERAGE, P_MINWINNERCOVERAGE),
                                 descriptions=('Minimal overall coverage', 'Minimal winner class coverage'),
                                 defaultValues=(None, None)):

        helps = [None, None]
        for name, description, defaultValue, help in zip(names, descriptions, defaultValues, helps):
            if defaultValue is None:
                defaultValue = 0.5
            self.addParameterFloat(name=name, description=description, minValue=0., maxValue=1.,
                                   defaultValue=defaultValue, help=help)

    def getParameterMinOverallCoverage(self, name=P_MINOVERALLCOVERAGE):
        return self.getParameterFloat(name=name)

    def getParameterMinWinnerCoverage(self, name=P_MINWINNERCOVERAGE):
        return self.getParameterFloat(name=name)

    P_OVERSAMPLING = 'oversampling'

    def addParameterOversampling(self, name=P_OVERSAMPLING, description='Oversampling factor'):
        self.addParameterInteger(name=name, description=description, minValue=1, maxValue=10, defaultValue=1, help=None)

    def getParameterOversampling(self, name=P_OVERSAMPLING):
        return self.getParameterInteger(name=name)

    P_FIELD = 'field'

    def addParameterField(self, name=P_FIELD, description='Field', defaultValue=None,
                          parentLayerParameterName=P_VECTOR, type=QgsProcessingParameterField.Any,
                          allowMultiple=False, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterField(name=name, description=description, defaultValue=defaultValue,
                                                       parentLayerParameterName=parentLayerParameterName,
                                                       type=type, allowMultiple=allowMultiple, optional=optional),
                           help=help)

    def getParameterField(self, name=P_FIELD):
        assert name in self._parameters
        return self._parameters[name]

    P_STRING = 'string'

    def addParameterString(self, name=P_STRING, description='String', defaultValue=None,
                           multiLine=False, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterString(name=name, description=description, defaultValue=defaultValue,
                                                        multiLine=multiLine, optional=optional), help=help)

    def getParameterString(self, name=P_STRING):
        assert name in self._parameters, name
        # string = self.parameterAsString(parameters=self._parameters, name=name, context=self._context) # this did not work
        string = str(self._parameters[name])
        return string

    P_INTEGER = 'integer'

    def addParameterInteger(self, name=P_INTEGER, description='Integer', defaultValue=0, optional=False,
                            minValue=None, maxValue=None, help=None):

        if minValue is None:
            minValue = -sys.maxsize
        if maxValue is None:
            maxValue = sys.maxsize

        self.addParameter_(QgsProcessingParameterNumber(name=name, description=description,
                                                        type=QgsProcessingParameterNumber.Integer,
                                                        defaultValue=defaultValue, optional=optional, minValue=minValue,
                                                        maxValue=maxValue), help=help)

    def getParameterInteger(self, name=P_INTEGER):
        assert name in self._parameters, name
        # number = self.parameterAsInt(parameters=self._parameters, name=name, context=self._context) # returned wrong numbers!?
        number = int(round(self._parameters[name], 0))
        return number

    P_FLOAT = 'float'

    def addParameterFloat(self, name=P_FLOAT, description='Float', defaultValue=0, optional=False,
                          minValue=None, maxValue=None, help=None):

        if minValue is None:
            minValue = -sys.maxsize
        if maxValue is None:
            maxValue = sys.maxsize

        self.addParameter_(QgsProcessingParameterNumber(name=name, description=description,
                                                        type=QgsProcessingParameterNumber.Double,
                                                        defaultValue=defaultValue, optional=optional, minValue=minValue,
                                                        maxValue=maxValue), help=help)

    def getParameterFloat(self, name=P_FLOAT):
        assert name in self._parameters, name
        # number = self.parameterAsDouble(parameters=self._parameters, name=name, context=self._context)
        number = float(self._parameters[name])
        return number

    P_BOOLEAN = 'boolean'

    def addParameterBoolean(self, name=P_BOOLEAN, description='Boolean', defaultValue=0, optional=False, help=None):

        self.addParameter_(QgsProcessingParameterBoolean(name=name, description=description, defaultValue=defaultValue,
                                                         optional=optional), help=help)

    def getParameterBoolean(self, name=P_BOOLEAN):
        assert name in self._parameters, name
        boolean = self._parameters[name]
        return boolean

    P_NO_DATA_VALUE = 'noDataValue'

    def addParameterNoDataValue(self, name=P_NO_DATA_VALUE, description='No Data Value', optional=False):
        self.addParameterString(name=name, description=description, optional=optional, help=None)

    def getParameterNoDataValue(self, name=P_NO_DATA_VALUE):
        string = self.getParameterString(name=name)
        if string in ['', 'None', None]:
            noDataValue = None
        else:
            noDataValue = float(string)
        return noDataValue

    P_LIST = 'list'

    def addParameterList(self, name=P_LIST, description='List', defaultValue=None, multiLine=False,
                         optional=False, help=None):
        if defaultValue is None:
            defaultValue = '[]'
        self.addParameterString(name=name, description=description, defaultValue=defaultValue, multiLine=multiLine,
                                optional=optional, help=help)

    def getParameterList(self, name=P_LIST, type=None):
        text = self.getParameterString(name=name)
        values = eval(text)
        assert isinstance(values, list)
        if type is not None:
            for v in values:
                assert isinstance(v, type)
        return values

    P_ENUM = 'enum'

    def addParameterEnum(self, name=P_ENUM, description='Enumerate', options=None, allowMultiple=False,
                         defaultValue=None, optional=False, help=None):

        self.addParameter_(QgsProcessingParameterEnum(name=name, description=description, options=options,
                                                      allowMultiple=allowMultiple, defaultValue=defaultValue,
                                                      optional=optional), help=help)

    def getParameterEnum(self, name=P_ENUM):
        assert name in self._parameters, name
        # selection = self.parameterAs???(parameters=self._parameters, name=name, context=self._context)
        selection = int(self._parameters[name])
        return selection

    P_DATA_TYPE = 'dataType'
    DATA_TYPES = ((numpy.int16, 'Integer 16 Bit'),
                  (numpy.int32, 'Integer 32 Bit'),
                  (numpy.int64, 'Integer 64 Bit'),
                  (numpy.uint8, 'Unsigned Integer 8 Bit'),
                  (numpy.uint16, 'Unsigned Integer 16 Bit'),
                  (numpy.uint32, 'Unsigned Integer 32 Bit'),
                  (numpy.uint64, 'Unsigned Integer 64 Bit'),
                  (numpy.float32, 'Single Precision Float 32 Bit'),
                  (numpy.float64, 'Double precision float 64 Bit'))
    DATA_TYPE_TYPES, DATA_TYPE_NAMES = zip(*DATA_TYPES)

    def addParameterDataType(self, name=P_DATA_TYPE, description='Data Type', defaultValue=7):
        self.addParameterEnum(name=name, description=description, options=self.DATA_TYPE_NAMES,
                              defaultValue=defaultValue, help=None)

    def getParameterDataType(self, name=P_DATA_TYPE):
        selection = self.getParameterEnum(name=name)
        return self.DATA_TYPE_TYPES[selection]

    P_FILE = 'file'

    def addParameterFile(self, name=P_FILE, description='File', extension=None, defaultValue=None, optional=False,
                         help=None):
        self.addParameter_(QgsProcessingParameterFile(name=name, description=description,
                                                      behavior=QgsProcessingParameterFile.File,
                                                      extension=extension, defaultValue=defaultValue,
                                                      optional=optional), help=help)

    def getParameterFile(self, name=P_FILE):
        assert name in self._parameters, name
        filename = self._parameters[name]
        return filename

    P_ENVI_SPECLIB = 'enviSpeclib'

    def addParameterEnviSpeclib(self, name=P_ENVI_SPECLIB, description='ENVI Spectral Library', optional=False,
                                help=None):
        self.addParameterFile(name=name, description=description, optional=optional,
                              help=help)  # extension='esl *.sli' two extensions seam not to work

    def getParameterEnviSpeclib(self, name=P_ENVI_SPECLIB):
        return self.getParameterOutputFile(name=name)

    P_UNSUPERVISED_SAMPLE = 'unsupervisedSample'

    def addParameterUnsupervisedSample(self, name=P_UNSUPERVISED_SAMPLE, description='Sample'):
        self.addParameterFlowObject(name=name, description=description)

    def getParameterUnsupervisedSample(self, name=P_UNSUPERVISED_SAMPLE):
        return self.getParameterFlowObject(name=name, cls=UnsupervisedSample)

    P_CLASSIFICATION_SAMPLE = 'classificationSample'

    def addParameterClassificationSample(self, name=P_CLASSIFICATION_SAMPLE, description='ClassificationSample'):
        self.addParameterFlowObject(name=name, description=description)

    def getParameterClassificationSample(self, name=P_CLASSIFICATION_SAMPLE):
        return self.getParameterFlowObject(name=name, cls=ClassificationSample)

    P_REGRESSION_SAMPLE = 'regressionSample'

    def addParameterRegressionSample(self, name=P_REGRESSION_SAMPLE, description='RegressionSample'):
        self.addParameterFlowObject(name=name, description=description)

    def getParameterRegressionSample(self, name=P_REGRESSION_SAMPLE):
        return self.getParameterFlowObject(name=name, cls=RegressionSample)

    P_CLASS_DEFINITION = 'classDefinition'

    def addParameterClassDefinition(self, name=P_CLASS_DEFINITION, description='Class Definition', defaultValue=None):

        help = '\n'.join(
            ["e.g. ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])",
             'For supported named colors see https://www.w3.org/TR/SVG/types.html#ColorKeywords'])

        self.addParameterString(name=name, description=description, defaultValue=defaultValue,
                                multiLine=True, optional=True, help=help)

    def getParameterClassDefinition(self, name=P_CLASS_DEFINITION):
        string = self.getParameterString(name=name)
        if string != '':
            classDefinition = eval(string)
        else:
            # get number of classes from vector or raster layer
            if self.P_VECTOR in self._parameters:
                assert self.P_CLASSIDFIELD in self._parameters
                vector = self.getParameterVector(name=self.P_VECTOR)
                classIdField = self.getParameterField(name=self.P_CLASSIDFIELD)
                classes = numpy.max(vector.uniqueValues(attribute=classIdField))
            elif self.P_RASTER in self._parameters:
                assert 0  # todo
            else:
                raise EnMAPAlgorithmParameterValueError('can not evaluate ClassDefinition')
            classDefinition = ClassDefinition(classes=classes)

        assert isinstance(classDefinition, ClassDefinition)
        return classDefinition


        self.addParameterInteger(self.P_N, 'Number of Points', minValue=0, defaultValue=0)
        n = self.getParameterInteger(self.P_N)


    P_NUMBER_OF_POINTS = 'numberOfPoints'

    def addParameterNumberOfPoints(self, name=P_NUMBER_OF_POINTS, description='Number of Points',
                                         defaultValue=100, optional=False):
        help = None
        self.addParameterString(name=name, description=description, defaultValue=str(defaultValue), optional=optional,
                                help=help)

    def getParameterNumberOfPoints(self, name=P_NUMBER_OF_POINTS):
        string = self.getParameterString(name)
        parameterDefinition = self.parameterDefinition(name)
        if string == '':
            n = None
        else:
            n = eval(string)
            if not isinstance(n, int) and n >= 0:
                raise EnMAPAlgorithmParameterValueError('Unexpected parameter value ({}): "{}"'.format(
                    parameterDefinition.name, string))
        return n


    P_NUMBER_OF_POINTS_PER_CLASS = 'numberOfPointsPerClass'

    def addParameterNumberOfPointsPerClass(self, name=P_NUMBER_OF_POINTS_PER_CLASS,
                                           description='Number of Points per Class',
                                           defaultValue=100, optional=False):
        help = None
        self.addParameterString(name=name, description=description, defaultValue=str(defaultValue), optional=optional,
                                help=help)

    def getParameterNumberOfPointsPerClass(self, name=P_NUMBER_OF_POINTS_PER_CLASS, classDefinition=None):
        assert isinstance(classDefinition, ClassDefinition)
        string = self.getParameterString(name)
        parameterDefinition = self.parameterDefinition(name)
        if string == '':
            n = None
        else:
            n = eval(string)
            if isinstance(n, int):
                n = [n] * classDefinition.classes
            if not isinstance(n, list) or len(n) != classDefinition.classes:
                raise EnMAPAlgorithmParameterValueError('Unexpected value (Number of Points per Class): "{}"'.format(
                    string))
        return n

    P_OUTPUT_RASTER = 'outRaster'

    def addParameterOutputRaster(self, name=P_OUTPUT_RASTER, description='Raster', help=None):
        parameter = QgsProcessingParameterRasterDestination(name=name, description=description)
#        parameter.defaultFileExtension = lambda : 'bsq'
        self.addParameter_(parameter, help=help)

    def getParameterOutputRaster(self, name=P_OUTPUT_RASTER):
        return self.getParameterOutputFile(name=name)

    P_OUTPUT_VECTOR = 'outVector'

    def addParameterOutputVector(self, name=P_OUTPUT_VECTOR, description='Vector', help=None):
        self.addParameter_(QgsProcessingParameterVectorDestination(name=name, description=description),
                           help=help)

    def getParameterOutputVector(self, name=P_OUTPUT_VECTOR):
        return self.getParameterOutputFile(name=name)


    P_OUTPUT_MASK = 'outMask'

    def addParameterOutputMask(self, name=P_OUTPUT_MASK, description='Mask', help=None):
        self.addParameterOutputRaster(name=name, description=description, help=help)

    def getParameterOutputMask(self, name=P_OUTPUT_MASK):
        return self.getParameterOutputFile(name=name)

    P_OUTPUT_CLASSIFICATION = 'outClassification'

    def addParameterOutputClassification(self, name=P_OUTPUT_CLASSIFICATION, description='Classification',
                                         help=None):
        self.addParameterOutputRaster(name=name, description=description, help=help)

    def getParameterOutputClassification(self, name=P_OUTPUT_CLASSIFICATION):
        return self.getParameterOutputFile(name=name)

    P_OUTPUT_PROBABILITY = 'outProbability'

    def addParameterOutputProbability(self, name=P_OUTPUT_PROBABILITY, description='ClassProbability',
                                      help=None):
        self.addParameterOutputRaster(name=name, description=description, help=help)

    def getParameterOutputProbability(self, name=P_OUTPUT_PROBABILITY):
        return self.getParameterOutputFile(name=name)

    P_OUTPUT_REPORT = 'outReport'

    def addParameterOutputReport(self, name=P_OUTPUT_REPORT, description='HTML Report', help=None):
        self.addParameter_(QgsProcessingParameterFileDestination(name=name, description=description,
                                                                 fileFilter='HTML files (*.html)'), help)
        self.addOutput(QgsProcessingOutputHtml(name=name, description=description))

    def getParameterOutputReport(self, name=P_OUTPUT_REPORT):
        self._progressBar.setText(str(self._parameters))
        assert name in self._parameters
        filename = self._parameters[name]
        return filename

    P_GRID = 'grid'

    def addParameterGrid(self, name=P_GRID, description='PixelGrid'):
        self.addParameterRaster(name=name, description=description)

    def getParameterGrid(self, name=P_GRID):
        return self.getParameterRaster(name=name).grid

    P_FLOW_OBJECT = 'flowObject'

    def addParameterFlowObject(self, name=P_FLOW_OBJECT, description='FlowObject File', defaultValue=None,
                               optional=False, help=None):
        self.addParameterFile(name=name, description=description, extension='pkl', defaultValue=defaultValue,
                              optional=optional, help=help)

    def getParameterFlowObject(self, name=P_FLOW_OBJECT, cls=FlowObject):
        filename = self.getParameterFile(name)
        try:
            flowObject = cls.unpickle(filename=filename)
        except FlowObjectTypeError as error:
            raise EnMAPAlgorithmParameterValueError(str(error))

        return flowObject

    P_ESTIMATOR = 'estimator'

    def addParameterEstimator(self, name=P_ESTIMATOR, description='Estimator'):
        self.addParameterFlowObject(name=name, description=description)

    def getParameterEstimator(self, name=P_ESTIMATOR, cls=Estimator):
        return self.getParameterFlowObject(name=name, cls=cls)

    P_CLASSIFIER = 'classifier'

    def addParameterClassifier(self, name=P_CLASSIFIER, description='Classifier'):
        self.addParameterEstimator(name=name, description=description)

    def getParameterClassifier(self, name=P_CLASSIFIER, cls=Classifier):
        return self.getParameterEstimator(name=name, cls=cls)

    P_REGRESSOR = 'regressor'

    def addParameterRegressor(self, name=P_REGRESSOR, description='Regressor'):
        self.addParameterEstimator(name=name, description=description)

    def getParameterRegressor(self, name=P_REGRESSOR, cls=Regressor):
        return self.getParameterEstimator(name=name, cls=cls)

    P_CLUSTERER = 'clusterer'

    def addParameterClusterer(self, name=P_CLUSTERER, description='Clusterer'):
        self.addParameterEstimator(name=name, description=description)

    def getParameterClusterer(self, name=P_CLUSTERER, cls=Clusterer):
        return self.getParameterEstimator(name=name, cls=cls)

    P_TRANSFORMER = 'transformer'

    def addParameterTransformer(self, name=P_TRANSFORMER, description='Transformer'):
        self.addParameterEstimator(name=name, description=description)

    def getParameterTransformer(self, name=P_TRANSFORMER, cls=Transformer):
        return self.getParameterEstimator(name=name, cls=cls)

    P_PROBABILITY_SAMPLE = 'probabilitySample'

    def addParameterProbabilitySample(self, name=P_PROBABILITY_SAMPLE, description='ProbabilitySample'):
        self.addParameterFlowObject(name=name, description=description)

    def getParameterProbabilitySample(self, name=P_PROBABILITY_SAMPLE):
        return self.getParameterFlowObject(name=name, cls=ProbabilitySample)

    P_OUTPUT_FILE = 'outFile'

    def addParameterOutputFile(self, name=P_OUTPUT_FILE, description='File', fileFilter=None,
                               defaultValue=None, optional=False, help=None):
        self.addParameter_(QgsProcessingParameterFileDestination(name=name, description=description,
                                                                 fileFilter=fileFilter, defaultValue=defaultValue,
                                                                 optional=optional), help=help)
        self.addOutput(QgsProcessingOutputFile(name=name, description=description))

    def getParameterOutputFile(self, name):
        assert name in self._parameters

        if isinstance(self._parameters[name], QgsProcessingOutputLayerDefinition):
            filename = str(self.parameterAsOutputLayer(self._parameters, name, self._context))
        elif isinstance(self._parameters[name], str):
            filename = self._parameters[name]
        else:
            assert 0, repr(self._parameters[name])
        assert isinstance(filename, str), repr(filename)
        return filename

    P_OUTPUT_FLOW_OBJECT = 'outFlowObject'

    def addParameterOutputFlowObject(self, name=P_OUTPUT_FLOW_OBJECT, description='FlowObject'):
        self.addParameterOutputFile(name=name, description=description, fileFilter='Pickle files (*.pkl)')

    def getParameterOutputFlowObject(self, name=P_OUTPUT_FLOW_OBJECT):
        filename = self.getParameterOutputFile(name=name)
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext != 'pkl':
            raise EnMAPAlgorithmParameterValueError(
                'Unexpected output pickle ({}) file extension: {}, use pkl instead.'.format(name, ext))
        return filename

    P_OUTPUT_ESTIMATOR = 'outEstimator'

    def addParameterOutputEstimator(self, name=P_OUTPUT_ESTIMATOR):
        self.addParameterOutputFlowObject(name=name, description='Estimator')

    def getParameterOutputEstimator(self, name=P_OUTPUT_ESTIMATOR):
        return self.getParameterOutputFlowObject(name=name)

    P_OUTPUT_CLASSIFICATION_SAMPLE = 'outClassificationSample'

    def addParameterOutputClassificationSample(self, name=P_OUTPUT_CLASSIFICATION_SAMPLE):
        self.addParameterOutputFlowObject(name=name, description='ClassificationSample')

    def getParameterOutputClassificationSample(self, name=P_OUTPUT_CLASSIFICATION_SAMPLE):
        return self.getParameterOutputFlowObject(name=name)

    P_OUTPUT_PROBABILITY_SAMPLE = 'outProbabilitySample'

    def addParameterOutputProbabilitySample(self, name=P_OUTPUT_PROBABILITY_SAMPLE):
        self.addParameterOutputFlowObject(name=name, description='ProbabilitySample')

    def getParameterOutputProbabilitySample(self, name=P_OUTPUT_PROBABILITY_SAMPLE):
        return self.getParameterOutputFlowObject(name=name)

    P_OUTPUT_REGRESSION_SAMPLE = 'outRegressionSample'

    def addParameterOutputRegressionSample(self, name=P_OUTPUT_REGRESSION_SAMPLE):
        self.addParameterOutputFlowObject(name=name, description='RegressionSample')

    def getParameterOutputRegressionSample(self, name=P_OUTPUT_REGRESSION_SAMPLE):
        return self.getParameterOutputFlowObject(name=name)

    P_OUTPUT_UNSUPERVISED_SAMPLE = 'outUnsupervisedSample'

    def addParameterOutputUnsupervisedSample(self, name=P_OUTPUT_UNSUPERVISED_SAMPLE, description='Sample'):
        self.addParameterOutputFlowObject(name=name, description=description)

    def getParameterOutputUnsupervisedSample(self, name=P_OUTPUT_UNSUPERVISED_SAMPLE):
        return self.getParameterOutputFlowObject(name=name)

    def hasHtmlOutputs(self, *args, **kwargs):
        return False

    def description(self):
        return 'undocumented algorithm'

    def shortHelpString(self):

        text = '<p>' + self.description() + '</p>'
        for pd in self.parameterDefinitions():
            assert isinstance(pd, QgsProcessingParameterDefinition)
            text += '<h3>' + pd.description() + '</h3>'
            text += '<p>' + pd._helpString.replace('\n', '<br>') + '</p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    def helpUrl(self, *args, **kwargs):
        return 'https://bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider/overview'

class ProgressBar(hubdc.progressbar.ProgressBar):
    def __init__(self, feedback):
        assert isinstance(feedback, QgsProcessingFeedback)
        self.feedback = feedback

    def setText(self, text):
        self.feedback.pushInfo(str(text))

    def setPercentage(self, percentage):
        if percentage == 100:
            return  # setting percentage to 100 would prevent further outputs in QGIS Dialog, at leaset under QGIS 2.x
        self.feedback.setProgress(percentage)


class EnMAPAlgorithmParameterValueError(Exception):
    pass
