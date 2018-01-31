import gdal
import numpy as np
import hubdc.applier
import hubflow.types
import hubflow.signals

ApplierControls = hubdc.applier.ApplierControls

class Applier(hubdc.applier.Applier):

    def __init__(self, defaultGrid=None, **kwargs):
        hubdc.applier.Applier.__init__(self, controls=kwargs.get('controls', None))
        self.controls.setProgressBar(kwargs.get('progressBar', None))
        grid = kwargs.get('grid', defaultGrid)
        if isinstance(grid, hubflow.types.Raster):
            grid = grid.grid
        #assert isinstance(grid, hubdc.applier.Grid)
        self.controls.setGrid(grid)
        self.kwargs = kwargs

    def apply(self, operatorType=None, description=None, *ufuncArgs, **ufuncKwargs):
        results = hubdc.applier.Applier.apply(self, operatorType=operatorType, description=description,
                                              overwrite=self.kwargs.get('overwrite', True), *ufuncArgs, **ufuncKwargs)
        for raster in self.outputRaster.flatRasters():
            hubflow.signals.sigFileCreated.emit(raster.filename())
        return results

    def setOutputRaster(self, name, filename):
        driver = self.kwargs.get(name + 'Driver', None)
        creationOptions = self.kwargs.get(name + 'Options', None)
        raster = hubdc.applier.ApplierOutputRaster(filename=filename, driver=driver, creationOptions=creationOptions)
        self.outputRaster.setRaster(key=name, value=raster)

    def setFlowRaster(self, name, raster):
        assert isinstance(raster, hubflow.types.Raster)
        raster = hubdc.applier.ApplierInputRaster(filename=raster.filename)
        self.inputRaster.setRaster(key=name, value=raster)

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename is None:
            pass
        elif isinstance(mask, (hubflow.types.Mask, hubflow.types.Raster)):
            self.setFlowRaster(name=name, raster=mask)
        elif isinstance(mask, (hubflow.types.Vector, hubflow.types.VectorClassification)):
            self.setFlowVector(name=name, vector=mask)
        else:
            assert 0

    def setFlowClassification(self, name, classification):
        if classification is None or classification.filename is None:
            pass
        elif isinstance(classification, hubflow.types.Classification):
            self.setFlowRaster(name=name, raster=classification)
        elif isinstance(classification, hubflow.types.VectorClassification):
            self.setFlowVector(name=name, vector=classification)
        else:
            assert 0, classification

    def setFlowRegression(self, name, regression):
        if regression is None or regression.filename is None:
            pass
        elif isinstance(regression, hubflow.types.Regression):
            self.setFlowRaster(name=name, raster=regression)
        else:
            assert 0, regression

    def setFlowProbability(self, name, probability):
        if probability is None or probability.filename is None:
            pass
        elif isinstance(probability, hubflow.types.Probability):
            self.setFlowRaster(name=name, raster=probability)
        elif isinstance(probability, (hubflow.types.Classification, hubflow.types.VectorClassification)):
            self.setFlowClassification(name=name, classification=probability)
        else:
            assert 0, probability

    def setFlowVector(self, name, vector):
        if isinstance(vector, (hubflow.types.Vector, hubflow.types.VectorClassification)):
            self.inputVector.setVector(key=name, value=hubdc.applier.ApplierInputVector(filename=vector.filename, layerNameOrIndex=vector.layer))
        else:
            assert 0

    def setFlowInput(self, name, input):
        if isinstance(input, hubflow.types.Raster):
            self.setFlowRaster(name=name, raster=input)
        elif isinstance(input, hubflow.types.Vector):
            self.setFlowVector(name=name, vector=input)
        else:
            assert 0

class ApplierOperator(hubdc.applier.ApplierOperator):

    def flowRasterArray(self, name, raster, indicies=None, overlap=0):

        if isinstance(raster, hubflow.types.Regression):
            array = self.flowRegressionArray(name=name, regression=raster, overlap=overlap)
        elif isinstance(raster, hubflow.types.Classification):
            array = self.flowClassificationArray(name=name, classification=raster, overlap=overlap)
        elif isinstance(input, hubflow.types.Probability):
            array = self.flowProbabilityArray(name=name, probability=raster, overlap=overlap)
        elif isinstance(raster, hubflow.types.Mask):
            array = self.flowMaskArray(name=name, mask=raster, overlap=overlap)
        elif isinstance(raster, hubflow.types.Raster):
            raster = self.inputRaster.raster(key=name)
            if indicies is None:
                array = raster.array(overlap=overlap)
            else:
                array = raster.bandArray(indicies=indicies, overlap=overlap)
        else:
            assert 0
        return array

    def flowVectorArray(self, name, vector, overlap=0):
        if isinstance(input, hubflow.types.VectorClassification):
            array = self.flowClassificationArray(name=name, classification=vector, overlap=overlap)
        elif isinstance(vector, hubflow.types.Vector):
            array = self.inputVector.vector(key=name).array(initValue=vector.initValue, burnValue=vector.burnValue,
                                                            burnAttribute=vector.burnAttribute,
                                                            allTouched=vector.allTouched, filterSQL=vector.filterSQL,
                                                            overlap=overlap, dtype=vector.dtype)
        else:
            assert 0
        return array

    def flowMaskArray(self, name, mask, aggregateFunction=None, overlap=0):

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if mask is None or mask.filename is None:
            array = self.full(value=True, bands=1, dtype=np.bool, overlap=overlap)
        elif isinstance(mask, hubflow.types.Mask):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Mode, noData="none")
            array = aggregateFunction(array != mask.noData)
        elif isinstance(mask, hubflow.types.Vector):
            array = self.inputVector.vector(key=name).array(overlap=overlap, allTouched=mask.allTouched, filterSQL=mask.filterSQL, dtype=np.uint8) == 1
        elif isinstance(mask, hubflow.types.VectorClassification):
            array = self.inputVector.vector(key=name).array(overlap=overlap, dtype=np.uint8) == 1
        else:
            raise Exception('wrong mask type')

        return array

    def flowClassificationArray(self, name, classification, oversampling=1, overlap=0):
        if classification is None or classification.filename is None:
            return np.array([])
        elif isinstance(classification, (hubflow.types.Classification, hubflow.types.VectorClassification, hubflow.types.Probability)):
            fractionArray = self.flowProbabilityArray(name=name, probability=classification, oversampling=oversampling, overlap=overlap)
            invalid = np.all(fractionArray==-1, axis=0, keepdims=True)
            array = np.uint8(np.argmax(fractionArray, axis=0)[None]+1)
            array[invalid] = 0
        else:
            assert 0
        return array

    def flowRegressionArray(self, name, regression, overlap=0):
        if regression is None or regression.filename is None:
            array = np.array([])
        elif isinstance(regression, hubflow.types.Regression):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average, noData=regression.noData)
            noDataFraction = self.inputRaster.raster(key=name).fractionArray(categories=[regression.noData], overlap=overlap, index=0)
            overallCoverageArray = 1. - noDataFraction
            invalid = overallCoverageArray <= regression.minOverallCoverage
            array[:, invalid[0]] = regression.noData
        else:
            assert 0, regression
        return array

    def flowProbabilityArray(self, name, probability, oversampling=1, overlap=0):
        if probability is None or probability.filename is None:
            array = np.array([])
        elif isinstance(probability, hubflow.types.Probability):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average)
        elif isinstance(probability, hubflow.types.Classification):
            categories = range(1, probability.classDefinition.classes+1)
            array = self.inputRaster.raster(key=name).fractionArray(categories=categories, overlap=overlap)
            overallCoverageArray = np.sum(array, axis=0)
            winnerCoverageArray = np.max(array, axis=0)
            invalid = np.logical_or(overallCoverageArray <= probability.minOverallCoverage,
                                       winnerCoverageArray <= probability.minWinnerCoverage)
            array[:, invalid] = -1
        elif isinstance(probability, hubflow.types.VectorClassification):

            # initialize result array
            array = self.full(value=-1, bands=probability.classDefinition.classes, dtype=np.float32, overlap=overlap)

            # get all categories for the current block
            spatialFilter = self.subgrid().spatialExtent().geometry()
            categories = probability.uniqueValues(attribute=probability.classAttribute, spatialFilter=spatialFilter)

            if len(categories) > 0:
                fractionArray = self.inputVector.vector(key=name).fractionArray(categories=categories,
                                                                                categoryAttribute=probability.classAttribute,
                                                                                oversampling=oversampling, overlap=overlap)
                overallCoverageArray = np.sum(fractionArray, axis=0)
                winnerCoverageArray = np.max(fractionArray, axis=0)
                valid = np.logical_and(overallCoverageArray > probability.minOverallCoverage,
                                          winnerCoverageArray > probability.minWinnerCoverage)

                array = self.full(value=-1, bands=probability.classDefinition.classes, dtype=np.float32, overlap=overlap)
                for category, categoryFractionArray in zip(categories, fractionArray):
                    if probability.classAttributeType == 'id':
                        id = int(category)
                    elif probability.classAttributeType == 'name':
                        id = int(probability.classDefinition.getLabelByName(name=category))
                    else:
                        assert 0
                    array[id-1][valid] = categoryFractionArray[valid]
            else:
                # do nothing if there are no features for the current block
                pass
        else:
            assert 0
        return array

    def flowInputArray(self, name, input, overlap=0):
        if isinstance(input, hubflow.types.Vector):
            array = self.flowVectorArray(name=name, vector=input, overlap=overlap)
        elif isinstance(input, hubflow.types.Raster):
            array = self.flowRasterArray(name=name, raster=input, overlap=overlap)
        else:
            assert 0
        return array

    def flowInputZSize(self, name, input):
        if isinstance(input, hubflow.types.Vector):
            shape = 1
        elif isinstance(input, hubflow.types.Raster):
            shape = input.dataset().zsize()
        else:
            assert 0
        return shape

    def flowInputDType(self, name, input):
        if isinstance(input, hubflow.types.Vector):
            dtype = input.dtype
        elif isinstance(input, hubflow.types.Raster):
            dtype = input.dataset().dtype()
        else:
            assert 0
        return dtype

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='classes', value=classDefinition.classes+1, domain='ENVI')
        raster.setMetadataItem(key='class names', value=['unclassified'] + classDefinition.names, domain='ENVI')
        raster.setMetadataItem(key='file type', value='ENVI Classification', domain='ENVI')

        lookup = [0, 0, 0] + list(np.array(classDefinition.lookup).flatten())
        raster.setMetadataItem(key='class lookup', value=lookup, domain='ENVI')

    def setFlowMetadataProbabilityDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        self.setFlowMetadataClassDefinition(name=name, classDefinition=classDefinition)
        self.setFlowMetadataBandNames(name=name, bandNames=classDefinition.names)
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='data ignore value', value=-1, domain='ENVI')
        raster.setMetadataItem(key='file type', value='ENVI Standard', domain='ENVI')
        raster.setNoDataValue(value=-1)

    def setFlowMetadataBandNames(self, name, bandNames):
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='band names', value=bandNames, domain='ENVI')
        for band, bandName in zip(raster.bands(), bandNames):
            band.setDescription(value=bandName)

    def maskFromBandArray(self, array, noData=None, noDataSource=None, index=None):
        if noData is None:
            assert noDataSource is not None
            assert index is not None
            noData = self.inputRaster.raster(key=noDataSource).noDataValues()[index]
        mask = array != noData
        return mask

    def maskFromArray(self, array, noData=None, noDataSource=None, aggregateFunction=None):

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if noData is None:
            assert noDataSource is not None
            noData = self.inputRaster.raster(key=noDataSource).noDataValue(default=0)

        mask = aggregateFunction(array != noData)
        return mask
