from osgeo import gdal
import numpy as np
import hubdc.applier
import hubflow.core
import hubflow.signals

ApplierControls = hubdc.applier.ApplierControls


class Applier(hubdc.applier.Applier):
    def __init__(self, defaultGrid=None, **kwargs):
        hubdc.applier.Applier.__init__(self, controls=kwargs.get('controls', None))
        self.controls.setProgressBar(kwargs.get('progressBar', None))
        grid = kwargs.get('grid', defaultGrid)
        if isinstance(grid, hubflow.core.Raster):
            grid = grid.grid
        # assert isinstance(grid, hubdc.applier.Grid)
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
        if isinstance(raster, hubflow.core.Raster):
            self.inputRaster.setRaster(key=name,
                                       value=hubdc.applier.ApplierInputRaster(filename=raster.filename))
        elif isinstance(raster, hubflow.core.RasterStack):
            rasterStack = raster
            group = hubdc.applier.ApplierInputRasterGroup()
            self.inputRaster.setGroup(key=name, value=group)
            for i, raster in enumerate(rasterStack.rasters()):
                group.setRaster(key=str(i), value=hubdc.applier.ApplierInputRaster(filename=raster.filename))
        else:
            assert 0

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename is None:
            pass
        elif isinstance(mask, (hubflow.core.Mask, hubflow.core.Raster)):
            self.setFlowRaster(name=name, raster=mask)
        elif isinstance(mask, (hubflow.core.Vector, hubflow.core.VectorClassification)):
            self.setFlowVector(name=name, vector=mask)
        else:
            assert 0

    def setFlowMasks(self, masks):
        name = 'mask'
        if masks is None:
            return
        if isinstance(masks, hubflow.core.FlowObject):
            masks = [masks]

        for i, mask in enumerate(masks):
            self.setFlowMask(name+str(i), mask=mask)

    def setFlowClassification(self, name, classification):
        if classification is None or classification.filename is None:
            pass
        elif isinstance(classification, (hubflow.core.Classification, hubflow.core.Probability)):
            self.setFlowRaster(name=name, raster=classification)
        elif isinstance(classification, hubflow.core.VectorClassification):
            self.setFlowVector(name=name, vector=classification)
        else:
            assert 0, classification

    def setFlowRegression(self, name, regression):
        if regression is None or regression.filename is None:
            pass
        elif isinstance(regression, hubflow.core.Regression):
            self.setFlowRaster(name=name, raster=regression)
        else:
            assert 0, regression

    def setFlowProbability(self, name, probability):
        if probability is None or probability.filename is None:
            pass
        elif isinstance(probability, hubflow.core.Probability):
            self.setFlowRaster(name=name, raster=probability)
        elif isinstance(probability, (hubflow.core.Classification, hubflow.core.VectorClassification)):
            self.setFlowClassification(name=name, classification=probability)
        else:
            assert 0, probability

    def setFlowVector(self, name, vector):
        if isinstance(vector, (hubflow.core.Vector, hubflow.core.VectorClassification)):
            self.inputVector.setVector(key=name, value=hubdc.applier.ApplierInputVector(filename=vector.filename,
                                                                                        layerNameOrIndex=vector.layer))
        else:
            assert 0

    def setFlowInput(self, name, input):
        if isinstance(input, hubflow.core.Raster):
            self.setFlowRaster(name=name, raster=input)
        elif isinstance(input, hubflow.core.Vector):
            self.setFlowVector(name=name, vector=input)
        else:
            assert 0


class ApplierOperator(hubdc.applier.ApplierOperator):
    def flowRasterArray(self, name, raster, indicies=None, overlap=0):

        if isinstance(raster, hubflow.core.Regression):
            array = self.flowRegressionArray(name=name, regression=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Classification):
            array = self.flowClassificationArray(name=name, classification=raster, overlap=overlap)
        elif isinstance(input, hubflow.core.Probability):
            array = self.flowProbabilityArray(name=name, probability=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Mask):
            array = self.flowMaskArray(name=name, mask=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Raster):
            raster = self.inputRaster.raster(key=name)
            if indicies is None:
                array = raster.array(overlap=overlap)
            else:
                array = raster.bandArray(indicies=indicies, overlap=overlap)
        elif isinstance(raster, hubflow.core.RasterStack):
            rasterStack = raster
            assert indicies is None # todo
            array = list()
            for i, raster in enumerate(rasterStack.rasters()):
                raster = self.inputRaster.raster(key=name+'/'+str(i))
                array.append(raster.array(overlap=overlap))
            array = np.concatenate(array, axis=0)
        else:
            assert 0
        return array

    def flowVectorArray(self, name, vector, overlap=0):
        if isinstance(input, hubflow.core.VectorClassification):
            array = self.flowClassificationArray(name=name, classification=vector, overlap=overlap)
        elif isinstance(vector, hubflow.core.Vector):
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
        elif isinstance(mask, hubflow.core.Mask):
            #array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Mode, noDataValue="none")
            #array = aggregateFunction(array != mask.noDataValue)

            # get mask for each band
            maskArrays = list()
            if mask.index is None:
                indices = range(mask.dataset().zsize())
            else:
                indices = [mask.index]

            for index in indices:
                fractionArray = 1.- self.inputRaster.raster(key=name).fractionArray(categories=[mask.noDataValue],
                                                                                    overlap=overlap,
                                                                                    index=index)
                maskArray = fractionArray > mask.minOverallCoverage
                maskArrays.append(maskArray[0])

            # aggregate to single band mask
            array = aggregateFunction(maskArrays)

        elif isinstance(mask, hubflow.core.Vector):
            array = self.inputVector.vector(key=name).array(overlap=overlap, allTouched=mask.allTouched,
                                                            filterSQL=mask.filterSQL, dtype=np.uint8) == 1
        elif isinstance(mask, hubflow.core.VectorClassification):
            array = self.inputVector.vector(key=name).array(overlap=overlap, dtype=np.uint8) == 1
        else:
            assert 0, repr()

        return array

    def flowMasksArray(self, masks, aggregateFunction=None, overlap=0):
        name = 'mask'
        array = self.full(value=True, bands=1, dtype=np.bool, overlap=overlap)
        if masks is None:
            return array

        if isinstance(masks, hubflow.core.FlowObject):
            masks = [masks]

        for i, mask in enumerate(masks):
            array *= self.flowMaskArray(name=name+str(i), mask=mask, aggregateFunction=aggregateFunction,
                                        overlap=overlap)
        return array

    def flowClassificationArray(self, name, classification, overlap=0):
        if classification is None or classification.filename is None:
            return np.array([])
        elif isinstance(classification,
                        (hubflow.core.Classification, hubflow.core.VectorClassification, hubflow.core.Probability)):
            fractionArray = self.flowProbabilityArray(name=name, probability=classification, overlap=overlap)
            invalid = np.all(fractionArray == -1, axis=0, keepdims=True)
            array = np.uint8(np.argmax(fractionArray, axis=0)[None] + 1)
            array[invalid] = 0
        else:
            assert 0
        return array

    def flowRegressionArray(self, name, regression, overlap=0):
        if regression is None or regression.filename is None:
            array = np.array([])
        elif isinstance(regression, hubflow.core.Regression):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average,
                                                            noDataValue=regression.noDataValue)
            noDataFraction = self.inputRaster.raster(key=name).fractionArray(categories=[regression.noDataValue],
                                                                             overlap=overlap, index=0)
            overallCoverageArray = 1. - noDataFraction
            invalid = overallCoverageArray <= regression.minOverallCoverage
            array[:, invalid[0]] = regression.noDataValue
        else:
            assert 0, regression
        return array

    def flowProbabilityArray(self, name, probability, overlap=0):
        if probability is None or probability.filename is None:
            array = np.array([])
        elif isinstance(probability, hubflow.core.Probability):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=probability.minOverallCoverage,
                                                 minWinnerCoverage=probability.minWinnerCoverage,
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(probability, hubflow.core.Classification):
            categories = range(1, probability.classDefinition.classes + 1)
            array = self.inputRaster.raster(key=name).fractionArray(categories=categories, overlap=overlap)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=probability.minOverallCoverage,
                                                 minWinnerCoverage=probability.minWinnerCoverage,
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(probability, hubflow.core.VectorClassification):

            # initialize result array
            array = self.full(value=-1, bands=probability.classDefinition.classes, dtype=np.float32, overlap=overlap)

            # get all categories for the current block
            spatialFilter = self.subgrid().spatialExtent().geometry()
            categories = probability.uniqueValues(attribute=probability.classAttribute,
                                                             spatialFilter=spatialFilter)

            if len(categories) > 0:
                fractionArray = self.inputVector.vector(key=name).fractionArray(categories=categories,
                                                                                categoryAttribute=probability.classAttribute,
                                                                                oversampling=probability.oversampling,
                                                                                overlap=overlap)
                valid = self.maskFromFractionArray(fractionArray=fractionArray,
                                                   minOverallCoverage=probability.minOverallCoverage,
                                                   minWinnerCoverage=probability.minWinnerCoverage)

                array = self.full(value=-1, bands=probability.classDefinition.classes, dtype=np.float32,
                                  overlap=overlap)
                for category, categoryFractionArray in zip(categories, fractionArray):
                    if probability.classAttributeType == 'id':
                        id = int(category)
                    elif probability.classAttributeType == 'name':
                        id = int(probability.classDefinition.getLabelByName(name=category))
                    else:
                        assert 0
                    array[id - 1][valid] = categoryFractionArray[valid]
            else:
                # do nothing if there are no features for the current block
                pass
        else:
            assert 0
        return array

    def flowInputArray(self, name, input, overlap=0):
        if isinstance(input, hubflow.core.Vector):
            array = self.flowVectorArray(name=name, vector=input, overlap=overlap)
        elif isinstance(input, hubflow.core.Raster):
            array = self.flowRasterArray(name=name, raster=input, overlap=overlap)
        else:
            assert 0
        return array

    def flowInputZSize(self, name, input):
        if isinstance(input, hubflow.core.Vector):
            shape = 1
        elif isinstance(input, hubflow.core.Raster):
            shape = input.dataset().zsize()
        else:
            assert 0
        return shape

    def flowInputDType(self, name, input):
        if isinstance(input, hubflow.core.Vector):
            dtype = input.dtype
        elif isinstance(input, hubflow.core.Raster):
            dtype = input.dataset().dtype()
        else:
            assert 0
        return dtype

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.core.ClassDefinition)
        raster = self.outputRaster.raster(key=name)

        names = ['unclassified'] + classDefinition.names
        lookup = [0, 0, 0] + list(np.array([(c.red(), c.green(), c.blue()) for c in classDefinition.colors]).flatten())

        # setup in ENVI domain
        raster.setMetadataItem(key='classes', value=classDefinition.classes + 1, domain='ENVI')
        raster.setMetadataItem(key='class names', value=names, domain='ENVI')
        raster.setMetadataItem(key='file type', value='ENVI Classification', domain='ENVI')
        raster.setMetadataItem(key='class lookup', value=lookup, domain='ENVI')

        # setuo in GDAL data model
        colors = np.array(lookup).reshape(-1, 3)
        colors = [tuple(color) for color in colors]
        band = raster.band(0)
        band.setCategoryNames(names=names)
        band.setCategoryColors(colors=colors)

    def setFlowMetadataProbabilityDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.core.ClassDefinition)
        raster = self.outputRaster.raster(key=name)

        lookup = list(np.array([(c.red(), c.green(), c.blue()) for c in classDefinition.colors]).flatten())
        self.setFlowMetadataBandNames(name=name, bandNames=classDefinition.names)
        raster.setMetadataItem(key='band lookup', value=lookup, domain='ENVI')
        self.setFlowMetadataNoDataValue(name=name, noDataValue=-1)

    def setFlowMetadataRegressionDefinition(self, name, noDataValue, outputNames):
        self.setFlowMetadataNoDataValue(name=name, noDataValue=noDataValue)
        self.setFlowMetadataBandNames(name=name, bandNames=outputNames)

    def setFlowMetadataBandNames(self, name, bandNames):
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='band names', value=bandNames, domain='ENVI')
        for band, bandName in zip(raster.bands(), bandNames):
            band.setDescription(value=bandName)

    def setFlowMetadataNoDataValue(self, name, noDataValue):
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='data ignore value', value=noDataValue, domain='ENVI')
        raster.setNoDataValue(value=noDataValue)

    def maskFromBandArray(self, array, noDataValue=None, noDataValueSource=None, index=None):
        assert array.ndim == 3
        assert len(array) == 1
        if noDataValue is None:
            assert noDataValueSource is not None
            assert index is not None
            noDataValue = self.inputRaster.raster(key=noDataValueSource).noDataValues()[index]

        if noDataValue is not None:
            mask = array != noDataValue
        else:
            mask = np.full_like(array, fill_value=np.True_, dtype=np.bool)
        return mask

    def maskFromArray(self, array, noDataValue=None, defaultNoDataValue=None, noDataValueSource=None, aggregateFunction=None):

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if noDataValue is None:
            assert noDataValueSource is not None
            try: # in case of a normal raster
                raster = self.inputRaster.raster(key=noDataValueSource)
                noDataValue = raster.noDataValue(default=0)
            except: # in case of a raster stack
                group = self.inputRaster.group(key=noDataValueSource)
                keys = sorted([int(key) for key in group.rasterKeys()])
                noDataValue = list()
                for key in keys:
                    raster = group.raster(key=str(key))
                    noDataValue = noDataValue + raster.noDataValues(default=defaultNoDataValue)


        mask = np.full_like(array, fill_value=np.True_, dtype=np.bool)
        if not isinstance(noDataValue, (list, tuple)):
            noDataValue = [noDataValue] * len(array)

        for i, band in enumerate(array):
            if noDataValue is not None:
                mask[i] = band != noDataValue

        mask = aggregateFunction(mask)
        return mask

    def maskFromFractionArray(self, fractionArray, minOverallCoverage, minWinnerCoverage, invert=False):
        overallCoverageArray = np.sum(fractionArray, axis=0)
        winnerCoverageArray = np.max(fractionArray, axis=0)
        maskArray = np.logical_and(overallCoverageArray > minOverallCoverage,
                                   winnerCoverageArray > minWinnerCoverage)
        if invert:
            return np.logical_not(maskArray)
        else:
            return maskArray
