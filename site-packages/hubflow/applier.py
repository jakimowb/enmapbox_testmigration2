from osgeo import gdal
import numpy as np
import hubdc.applier
import hubflow.core
import hubflow.signals

ApplierControls = hubdc.applier.ApplierControls


class Applier(hubdc.applier.Applier):
    def __init__(self, defaultGrid=None, **kwargs):
        controls = kwargs.get('controls', None)
        hubdc.applier.Applier.__init__(self, controls=controls)

        grid = kwargs.get('grid', defaultGrid)
        if isinstance(grid, hubflow.core.Raster):
            grid = grid.grid()
        progressBar = kwargs.get('progressBar', None)

        self.controls.setProgressBar(progressBar)
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
                                       value=hubdc.applier.ApplierInputRaster(filename=raster.filename()))
        elif isinstance(raster, hubflow.core.RasterStack):
            rasterStack = raster
            group = hubdc.applier.ApplierInputRasterGroup()
            self.inputRaster.setGroup(key=name, value=group)
            for i, raster in enumerate(rasterStack.rasters()):
                group.setRaster(key=str(i), value=hubdc.applier.ApplierInputRaster(filename=raster.filename()))
        else:
            assert 0

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename() is None:
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
        if classification is None or classification.filename() is None:
            pass
        elif isinstance(classification, (hubflow.core.Classification, hubflow.core.Fraction)):
            self.setFlowRaster(name=name, raster=classification)
        elif isinstance(classification, hubflow.core.VectorClassification):
            self.setFlowVector(name=name, vector=classification)
        else:
            assert 0, classification

    def setFlowRegression(self, name, regression):
        if regression is None or regression.filename() is None:
            pass
        elif isinstance(regression, hubflow.core.Regression):
            self.setFlowRaster(name=name, raster=regression)
        else:
            assert 0, regression

    def setFlowFraction(self, name, fraction):
        if fraction is None or fraction.filename() is None:
            pass
        elif isinstance(fraction, hubflow.core.Fraction):
            self.setFlowRaster(name=name, raster=fraction)
        elif isinstance(fraction, (hubflow.core.Classification, hubflow.core.VectorClassification)):
            self.setFlowClassification(name=name, classification=fraction)
        else:
            assert 0, fraction

    def setFlowVector(self, name, vector):
        if isinstance(vector, (hubflow.core.Vector, hubflow.core.VectorClassification)):
            self.inputVector.setVector(key=name, value=hubdc.applier.ApplierInputVector(filename=vector.filename(),
                                                                                        layerNameOrIndex=vector.layer()))
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
    def flowRasterArray(self, name, raster, indices=None, overlap=0):

        if isinstance(raster, hubflow.core.Regression):
            array = self.flowRegressionArray(name=name, regression=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Classification):
            array = self.flowClassificationArray(name=name, classification=raster, overlap=overlap)
        elif isinstance(input, hubflow.core.Fraction):
            array = self.flowFractionArray(name=name, fraction=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Mask):
            array = self.flowMaskArray(name=name, mask=raster, overlap=overlap)
        elif isinstance(raster, hubflow.core.Raster):
            raster = self.inputRaster.raster(key=name)
            if indices is None:
                array = raster.array(overlap=overlap)
            else:
                array = raster.bandArray(indicies=indices, overlap=overlap)
        elif isinstance(raster, hubflow.core.RasterStack):
            rasterStack = raster
            assert indices is None # todo
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
            array = self.inputVector.vector(key=name).array(initValue=vector.initValue(), burnValue=vector.burnValue(),
                                                            burnAttribute=vector.burnAttribute(),
                                                            allTouched=vector.allTouched(), filterSQL=vector.filterSQL(),
                                                            overlap=overlap, dtype=vector.dtype())
        else:
            assert 0
        return array

    def flowMaskArray(self, name, mask, aggregateFunction=None, overlap=0):

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if mask is None or mask.filename() is None:
            array = self.full(value=True, bands=1, dtype=np.bool, overlap=overlap)
        elif isinstance(mask, hubflow.core.Mask):

            # get mask for each band
            maskArrays = list()
            if mask.index is None:
                indices = range(mask.dataset().zsize())
            else:
                indices = [mask.index]

            for index in indices:
                fractionArray = 1.- self.inputRaster.raster(key=name).fractionArray(categories=mask.noDataValues(),
                                                                                    overlap=overlap,
                                                                                    index=index)
                maskArray = fractionArray > min(0.9999, mask.minOverallCoverage())
                maskArrays.append(maskArray[0])

            # aggregate to single band mask
            array = aggregateFunction(maskArrays)

        elif isinstance(mask, (hubflow.core.Classification, hubflow.core.VectorClassification, hubflow.core.Fraction)):
            array = self.flowClassificationArray(name=name, classification=mask, overlap=overlap) != 0

        elif isinstance(mask, hubflow.core.Vector):
            array = self.inputVector.vector(key=name).array(overlap=overlap, allTouched=mask.allTouched(),
                                                            filterSQL=mask.filterSQL(), dtype=np.uint8) == 1
        else:
            assert 0, repr(mask)

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
        if classification is None or classification.filename() is None:
            return np.array([])
        elif isinstance(classification,
                        (hubflow.core.Classification, hubflow.core.VectorClassification, hubflow.core.Fraction)):
            fractionArray = self.flowFractionArray(name=name, fraction=classification, overlap=overlap)
            invalid = np.all(fractionArray == -1, axis=0, keepdims=True)
            array = np.uint8(np.argmax(fractionArray, axis=0)[None] + 1)
            array[invalid] = 0
        else:
            assert 0
        return array

    def flowRegressionArray(self, name, regression, overlap=0):
        if regression is None or regression.filename() is None:
            array = np.array([])
        elif isinstance(regression, hubflow.core.Regression):
            raster = self.inputRaster.raster(key=name)
            array = raster.array(overlap=overlap, resampleAlg=gdal.GRA_Average,
                                                            noDataValue=regression.noDataValues())

            invalid = self.full(value=np.False_, dtype=np.bool)
            for i, noDataValue in enumerate(regression.noDataValues()):
                overallCoverageArray = 1. - raster.fractionArray(categories=[noDataValue], overlap=overlap, index=0)
                invalid += overallCoverageArray <= min(0.9999, regression.minOverallCoverage())

            for i, noDataValue in enumerate(regression.noDataValues()):
                array[i, invalid[0]] = noDataValue
        else:
            assert 0, regression
        return array

    def flowFractionArray(self, name, fraction, overlap=0):
        if fraction is None or fraction.filename() is None:
            array = np.array([])
        elif isinstance(fraction, hubflow.core.Fraction):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=fraction.minOverallCoverage(),
                                                 minDominantCoverage=fraction.minDominantCoverage(),
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(fraction, hubflow.core.Classification):
            categories = range(1, fraction.classDefinition().classes() + 1)
            array = self.inputRaster.raster(key=name).fractionArray(categories=categories, overlap=overlap)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=fraction.minOverallCoverage(),
                                                 minDominantCoverage=fraction.minDominantCoverage(),
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(fraction, hubflow.core.VectorClassification):

            # get all categories for the current block
            spatialFilter = self.subgrid().spatialExtent().geometry()
            categories = fraction.uniqueValues(attribute=fraction.classAttribute(),
                                                             spatialFilter=spatialFilter)

            if len(categories) > 0:
                array = self.full(value=0, bands=fraction.classDefinition().classes(), dtype=np.float32,
                                  overlap=overlap)

                fractionArray = self.inputVector.vector(key=name).fractionArray(categories=categories,
                                                                                categoryAttribute=fraction.classAttribute(),
                                                                                oversampling=fraction.oversampling(),
                                                                                overlap=overlap)

                invalid = self.maskFromFractionArray(fractionArray=fractionArray,
                                                     minOverallCoverage=fraction.minOverallCoverage(),
                                                     minDominantCoverage=fraction.minDominantCoverage(),
                                                     invert=True)

                for category, categoryFractionArray in zip(categories, fractionArray):
                    id = int(category)
                    array[id - 1] = categoryFractionArray

                array[:, invalid] = -1

            else:
                array = self.full(value=-1, bands=fraction.classDefinition().classes(), dtype=np.float32,
                                  overlap=overlap)

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
            dtype = input.dtype()
        elif isinstance(input, hubflow.core.Raster):
            dtype = input.dataset().dtype()
        else:
            assert 0
        return dtype

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        hubflow.core.MetadataEditor.setClassDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                       classDefinition=classDefinition)

    def setFlowMetadataFractionDefinition(self, name, classDefinition):
        return hubflow.core.MetadataEditor.setFractionDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                                 classDefinition=classDefinition)

    def setFlowMetadataRegressionDefinition(self, name, noDataValues, outputNames):
        return hubflow.core.MetadataEditor.setRegressionDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                                   noDataValues=noDataValues, outputNames=outputNames)

    def setFlowMetadataBandNames(self, name, bandNames):
        return hubflow.core.MetadataEditor.setBandNames(rasterDataset=self.outputRaster.raster(key=name),
                                                        bandNames=bandNames)

    def setFlowMetadataNoDataValues(self, name, noDataValues):
        self.outputRaster.raster(key=name).setNoDataValues(values=noDataValues)

    def setFlowMetadataSensorDefinition(self, name, sensor):
        assert isinstance(sensor, hubflow.core.SensorDefinition)
        raster = self.outputRaster.raster(key=name)
        raster.setMetadataItem(key='wavelength', value=sensor.wavebandCenters(), domain='ENVI')
        fwhms = sensor.wavebandFwhms()
        if not all([fwhm is None for fwhm in fwhms]):
            raster.setMetadataItem(key='fwhm', value=fwhms, domain='ENVI')
        raster.setMetadataItem(key='wavelength units', value='nanometers', domain='ENVI')

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

    def maskFromArray(self, array, noDataValues=None, defaultNoDataValue=None, noDataValueSource=None, aggregateFunction=None):

        assert array.ndim == 3

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if noDataValues is None:
            assert noDataValueSource is not None
            try: # in case of a normal raster
                raster = self.inputRaster.raster(key=noDataValueSource)
                noDataValues = raster.noDataValues(default=0)
            except: # in case of a raster stack
                group = self.inputRaster.group(key=noDataValueSource)
                keys = sorted([int(key) for key in group.rasterKeys()])
                noDataValues = list()
                for key in keys:
                    raster = group.raster(key=str(key))
                    noDataValues = noDataValues + raster.noDataValues(default=defaultNoDataValue)

        assert len(array) == len(noDataValues)

        mask = np.full_like(array, fill_value=np.True_, dtype=np.bool)

        for i, band in enumerate(array):
            if noDataValues[i] is not None:
                mask[i] = band != noDataValues[i]

        mask = aggregateFunction(mask)
        return mask

    def maskFromFractionArray(self, fractionArray, minOverallCoverage, minDominantCoverage, invert=False):
        overallCoverageArray = np.sum(fractionArray, axis=0)
        winnerCoverageArray = np.max(fractionArray, axis=0)
        maskArray = np.logical_and(overallCoverageArray > min(0.9999, minOverallCoverage),
                                   winnerCoverageArray > min(0.9999, minDominantCoverage))
        if invert:
            return np.logical_not(maskArray)
        else:
            return maskArray
