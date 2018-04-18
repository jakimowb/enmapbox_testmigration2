
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


    def addParameterNoDataValue(self):
        self.addParameter(ParameterString('noDataValue', 'No Data Value', optional=True))

    def getParameterNoDataValue(self):
        noDataValue = self.getParameterValue(name='noDataValue')
        if noDataValue == '':
            noDataValue = None
        else:
            noDataValue = float(noDataValue)
        return noDataValue






    def addParameterRegression(self, name='regression', description='Regression'):
        self.addParameter(ParameterRaster(name=name, description=description))

    def getParameterRegression(self, name='regression'):
        return Regression(filename=self.getParameterValue(name=name))



    def addParameterMask(self, name='mask', description='Mask', optional=True):
        self.addParameter(ParameterRaster(name=name, description=description, optional=optional))

    def getParameterMask(self, name='mask'):
        filename = self.getParameterValue(name)
        if filename is not None:
            return Mask(filename=filename)






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


ALGORITHMS = list()














































