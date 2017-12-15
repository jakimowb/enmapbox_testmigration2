import gdal, numpy
import hubdc.applier
import hubflow.types
import hubflow.signals

ApplierControls = hubdc.applier.ApplierControls

class Applier(hubdc.applier.Applier):

    def __init__(self, defaultGrid=None, **kwargs):
        hubdc.applier.Applier.__init__(self, controls=kwargs.get('controls', None))
        self.controls.setProgressBar(kwargs.get('progressBar', None))
        grid = kwargs.get('grid', defaultGrid)
        if isinstance(grid, hubflow.types.Image):
            grid = grid.grid
        #assert isinstance(grid, hubdc.applier.Grid)
        self.controls.setGrid(grid)
        self.kwargs = kwargs

    def apply(self, operator=None, description=None, *ufuncArgs, **ufuncKwargs):
        results = hubdc.applier.Applier.apply(self, operatorType=operator, description=description,
                                              overwrite=self.kwargs.get('overwrite', True), *ufuncArgs, **ufuncKwargs)
        for raster in self.outputRaster.flatRasters():
            hubflow.signals.sigFileCreated.emit(raster.filename())
        return results

#    def setInput(self, name, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour):
#        resampleAlg = resampleAlg
#        options = self.kwargs.get(name + 'Options', None)
#        self.inputRaster hubdc.applier.Applier.setInput(self, name=name, filename=filename, noData=noData, resampleAlg=resampleAlg, options=options)

    def setOutputRaster(self, name, filename):
        format = self.kwargs.get(name + 'Format', None)
        creationOptions = self.kwargs.get(name + 'Options', None)
        raster = hubdc.applier.ApplierOutputRaster(filename=filename, format=format, creationOptions=creationOptions)
        self.outputRaster.setRaster(key=name, value=raster)

    def setFlowImage(self, name, image):
        assert isinstance(image, hubflow.types.Image), image
        raster = hubdc.applier.ApplierInputRaster(filename=image.filename)
        self.inputRaster.setRaster(key=name, value=raster)

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename is None:
            pass
        elif isinstance(mask, (hubflow.types.Mask, hubflow.types.Image)):
            self.setFlowImage(name=name, image=mask)
        elif isinstance(mask, (hubflow.types.Vector, hubflow.types.VectorClassification)):
            self.setFlowVector(name=name, vector=mask)
        else:
            assert 0, mask

    def setFlowClassification(self, name, classification):
        if classification is None or classification.filename is None:
            pass
        elif isinstance(classification, hubflow.types.Classification):
            self.setFlowImage(name=name, image=classification)
        elif isinstance(classification, hubflow.types.VectorClassification):
            self.setFlowVector(name=name, vector=classification)
        else:
            assert 0, classification

    def setFlowRegression(self, name, regression):
        if regression is None or regression.filename is None:
            pass
        elif isinstance(regression, hubflow.types.Regression):
            self.setFlowImage(name=name, image=regression)
        else:
            assert 0, regression

    def setFlowProbability(self, name, probability):
        if probability is None or probability.filename is None:
            pass
        elif isinstance(probability, hubflow.types.Probability):
            self.setFlowImage(name=name, image=probability)
        elif isinstance(probability, (hubflow.types.Classification, hubflow.types.VectorClassification)):
            self.setFlowClassification(name=name, classification=probability)
        else:
            assert 0, probability

    def setFlowVector(self, name, vector):
        if isinstance(vector, (hubflow.types.Vector, hubflow.types.VectorClassification)):
            self.inputVector.setVector(key=name, value=hubdc.applier.ApplierInputVector(filename=vector.filename, layerNameOrIndex=vector.layer))
        else:
            assert 0, vector

class ApplierOperator(hubdc.applier.ApplierOperator):

    def getFlowImageArray(self, name, image, indicies=None, overlap=0):

        if isinstance(image, hubflow.types.Regression):
            array = self.getFlowRegressionArray(name=name, regression=image, overlap=overlap)
        elif isinstance(image, hubflow.types.Classification):
            array = self.getFlowClassificationArray(name=name, classification=image, overlap=overlap)
        elif isinstance(image, hubflow.types.Image):
            raster = self.inputRaster.raster(key=name)
            if indicies is None:
                array = raster.imageArray(overlap=overlap)
            else:
                array = raster.bandArray(indicies=indicies, overlap=overlap)
        else:
            assert 0, image
        return array

    def getFlowMaskArray(self, name, mask, aggregateFunction=numpy.all, overlap=0):
        if mask is None or mask.filename is None:
            array = self.getFull(value=True, bands=1, dtype=numpy.bool, overlap=overlap)
        elif isinstance(mask, hubflow.types.Mask):
            array = self.inputRaster.raster(key=name).imageArray(overlap=overlap, resampleAlg=gdal.GRA_Mode, noData="none")
            array = aggregateFunction(array != mask.noData, axis=0, keepdims=True)
        elif isinstance(mask, hubflow.types.Vector):
            array = self.inputVector.vector(key=name).imageArray(overlap=overlap, allTouched=mask.allTouched, filterSQL=mask.filterSQL, dtype=numpy.uint8) == 1
        elif isinstance(mask, hubflow.types.VectorClassification):
            array = self.inputVector.vector(key=name).imageArray(overlap=overlap, dtype=numpy.uint8) == 1
        else:
            raise Exception('wrong mask type')

        return array

    def getFlowClassificationArray(self, name, classification, oversampling=10, overlap=0):
        if classification is None or classification.filename is None:
            return numpy.array([])
        elif isinstance(classification, (hubflow.types.Classification, hubflow.types.VectorClassification)):
            fractionArray = self.getFlowProbabilityArray(name=name, probability=classification, oversampling=oversampling, overlap=overlap)
            invalid = numpy.all(fractionArray==-1, axis=0, keepdims=True)
            array = classification.dtype(numpy.argmax(fractionArray, axis=0)[None]+1)
            array[invalid] = 0
        else:
            assert 0, classification
        return array

    def getFlowRegressionArray(self, name, regression, overlap=0):
        if regression is None or regression.filename is None:
            array = numpy.array([])
        elif isinstance(regression, hubflow.types.Regression):
            array = self.inputRaster.raster(key=name).imageArray(overlap=overlap, resampleAlg=gdal.GRA_Average, noData=regression.noData)
            noDataFraction = self.inputRaster.raster(key=name).fractionArray(categories=[regression.noData], overlap=overlap, index=0)
            overallCoverageArray = 1. - noDataFraction
            invalid = overallCoverageArray <= regression.minOverallCoverage
            array[:, invalid[0]] = regression.noData
        else:
            assert 0, regression
        return array

    def getFlowProbabilityArray(self, name, probability, oversampling=10, overlap=0):
        if probability is None or probability.filename is None:
            array = numpy.array([])
        elif isinstance(probability, hubflow.types.Probability):
            array = self.inputRaster.raster(key=name).imageArray(overlap=overlap, resampleAlg=gdal.GRA_Average)
        elif isinstance(probability, hubflow.types.Classification):
            categories = range(1, probability.classDefinition.classes+1)
            array = self.inputRaster.raster(key=name).fractionArray(categories=categories, overlap=overlap)
            overallCoverageArray = numpy.sum(array, axis=0)
            winnerCoverageArray = numpy.max(array, axis=0)
            invalid = numpy.logical_or(overallCoverageArray <= probability.minOverallCoverage,
                                       winnerCoverageArray <= probability.minWinnerCoverage)
            array[:, invalid] = -1
        elif isinstance(probability, hubflow.types.VectorClassification):
            categories = probability.asVector().uniqueValues(attribute=probability.classAttribute)
            fractionArray = self.inputVector.vector(key=name).fractionArray(categories=categories, categoryAttribute=probability.classAttribute, oversampling=oversampling, overlap=overlap)
            overallCoverageArray = numpy.sum(fractionArray, axis=0)
            winnerCoverageArray = numpy.max(fractionArray, axis=0)
            valid = numpy.logical_and(overallCoverageArray > probability.minOverallCoverage,
                                      winnerCoverageArray > probability.minWinnerCoverage)

            array = self.getFull(value=-1, bands=probability.classDefinition.classes, dtype=numpy.float32, overlap=overlap)
            for category, categoryFractionArray in zip(categories, fractionArray):
                if probability.classAttributeType == 'id':  id = int(category)
                elif probability.classAttributeType == 'name': id = int(probability.classDefinition.getLabelByName(name=category))
                array[id-1][valid] = categoryFractionArray[valid]
        else:
            assert 0, probability
        return array

    def getFlowVectorArray(self, name, vector, overlap=0):
        assert isinstance(vector, hubflow.types.Vector)
        return self.inputVector.vector(key=name).imageArray(initValue=vector.initValue, burnValue=vector.burnValue,
                                                            burnAttribute=vector.burnAttribute, allTouched=vector.allTouched,
                                                            filterSQL=vector.filterSQL, overlap=overlap, dtype=vector.dtype)

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='classes', value=classDefinition.classes+1, domain='ENVI')
        raster.setMetadataItem(key='class names', value=['unclassified'] + classDefinition.names, domain='ENVI')
        lookup = [0, 0, 0] + list(numpy.array(classDefinition.lookup).flatten())
        raster.setMetadataItem(key='class lookup', value=lookup, domain='ENVI')

    def setFlowMetadataProbabilityDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        self.setFlowMetadataClassDefinition(name=name, classDefinition=classDefinition)
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='band names', value=classDefinition.names, domain='ENVI')
        raster.setMetadataItem(key='data ignore value', value=-1, domain='ENVI')
        raster.setNoDataValue(value=-1)

    def setFlowMetadataBandNames(self, name, bandNames):
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='band names', value=bandNames, domain='ENVI')
        for band, bandName in zip(raster.bands(), bandNames):
            band.setDescription(value=bandName)

    def getMaskFromBandArray(self, array, noData=None, noDataSource=None, index=None):
        if noData is None:
            assert noDataSource is not None
            assert index is not None
            noData = self.inputRaster.raster(key=noDataSource).noDataValues()[index]
        mask = array != noData
        return mask

    def getMaskFromImageArray(self, array, noData=None, noDataSource=None, aggregateFunction=numpy.all):
        if noData is None:
            assert noDataSource is not None
            noData = self.inputRaster.raster(key=noDataSource).noDataValue()
        mask = aggregateFunction(array != noData, axis=0, keepdims=True)
        return mask
