import random, pickle
from collections import OrderedDict, namedtuple
from osgeo import gdal
import numpy as np
from PyQt5.QtGui import QColor
from hubdc.progressbar import ProgressBar, SilentProgressBar, CUIProgressBar
from hubdc.core import *
import hubdc.applier
from hubdc.applier import ApplierOutputRaster, ApplierControls, ApplierDefaults
from hubflow.report import *
from hubflow.errors import *
import hubflow.signals

class Applier(hubdc.applier.Applier):
    def __init__(self, defaultGrid=None, **kwargs):
        controls = kwargs.get('controls', None)
        hubdc.applier.Applier.__init__(self, controls=controls)

        grid = kwargs.get('grid', defaultGrid)
        if isinstance(grid, Raster):
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
        if isinstance(raster, Raster):
            self.inputRaster.setRaster(key=name,
                                       value=hubdc.applier.ApplierInputRaster(filename=raster.filename()))
        elif isinstance(raster, RasterStack):
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
        elif isinstance(mask, (Mask, Raster)):
            self.setFlowRaster(name=name, raster=mask)
        elif isinstance(mask, (Vector, VectorClassification)):
            self.setFlowVector(name=name, vector=mask)
        else:
            assert 0

    def setFlowMasks(self, masks):
        name = 'mask'
        if masks is None:
            return
        if isinstance(masks, FlowObject):
            masks = [masks]

        for i, mask in enumerate(masks):
            self.setFlowMask(name + str(i), mask=mask)

    def setFlowClassification(self, name, classification):
        if classification is None or classification.filename() is None:
            pass
        elif isinstance(classification, (Classification, Fraction)):
            self.setFlowRaster(name=name, raster=classification)
        elif isinstance(classification, VectorClassification):
            self.setFlowVector(name=name, vector=classification)
        else:
            assert 0, classification

    def setFlowRegression(self, name, regression):
        if regression is None or regression.filename() is None:
            pass
        elif isinstance(regression, Regression):
            self.setFlowRaster(name=name, raster=regression)
        else:
            assert 0, regression

    def setFlowFraction(self, name, fraction):
        if fraction is None or fraction.filename() is None:
            pass
        elif isinstance(fraction, Fraction):
            self.setFlowRaster(name=name, raster=fraction)
        elif isinstance(fraction, (Classification, VectorClassification)):
            self.setFlowClassification(name=name, classification=fraction)
        else:
            assert 0, fraction

    def setFlowVector(self, name, vector):
        if isinstance(vector, (Vector, VectorClassification)):
            self.inputVector.setVector(key=name, value=hubdc.applier.ApplierInputVector(filename=vector.filename(),
                                                                                        layerNameOrIndex=vector.layer()))
        else:
            assert 0

    def setFlowInput(self, name, input):
        if isinstance(input, Raster):
            self.setFlowRaster(name=name, raster=input)
        elif isinstance(input, Vector):
            self.setFlowVector(name=name, vector=input)
        else:
            assert 0


class ApplierOperator(hubdc.applier.ApplierOperator):
    def flowRasterArray(self, name, raster, indices=None, overlap=0):

        if isinstance(raster, Regression):
            array = self.flowRegressionArray(name=name, regression=raster, overlap=overlap)
        elif isinstance(raster, Classification):
            array = self.flowClassificationArray(name=name, classification=raster, overlap=overlap)
        elif isinstance(input, Fraction):
            array = self.flowFractionArray(name=name, fraction=raster, overlap=overlap)
        elif isinstance(raster, Mask):
            array = self.flowMaskArray(name=name, mask=raster, overlap=overlap)
        elif isinstance(raster, Raster):
            raster = self.inputRaster.raster(key=name)
            if indices is None:
                array = raster.array(overlap=overlap)
            else:
                array = raster.bandArray(indices=indices, overlap=overlap)
        elif isinstance(raster, RasterStack):
            rasterStack = raster
            assert indices is None  # todo
            array = list()
            for i, raster in enumerate(rasterStack.rasters()):
                raster = self.inputRaster.raster(key=name + '/' + str(i))
                array.append(raster.array(overlap=overlap))
            array = np.concatenate(array, axis=0)
        else:
            assert 0
        return array

    def flowVectorArray(self, name, vector, overlap=0):
        if isinstance(input, VectorClassification):
            array = self.flowClassificationArray(name=name, classification=vector, overlap=overlap)
        elif isinstance(vector, Vector):
            array = self.inputVector.vector(key=name).array(initValue=vector.initValue(), burnValue=vector.burnValue(),
                                                            burnAttribute=vector.burnAttribute(),
                                                            allTouched=vector.allTouched(),
                                                            filterSQL=vector.filterSQL(),
                                                            overlap=overlap, dtype=vector.dtype())
        else:
            assert 0
        return array

    def flowMaskArray(self, name, mask, aggregateFunction=None, overlap=0):

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if mask is None or mask.filename() is None:
            array = self.full(value=True, bands=1, dtype=np.bool, overlap=overlap)
        elif isinstance(mask, Mask):

            # get mask for each band
            maskArrays = list()
            if mask.indices() is None:
                indices = range(mask.dataset().zsize())
            else:
                indices = mask.indices()

            for index in indices:
                fractionArray = 1. - self.inputRaster.raster(key=name).fractionArray(categories=mask.noDataValues(),
                                                                                     overlap=overlap,
                                                                                     index=index)

                maskArray = fractionArray > min(0.9999, mask.minOverallCoverage())
                if mask.invert():
                    np.logical_not(maskArray, out=maskArray)

                maskArrays.append(maskArray[0])

            # aggregate to single band mask
            array = aggregateFunction(maskArrays)

        elif isinstance(mask, (Classification, VectorClassification, Fraction)):
            array = self.flowClassificationArray(name=name, classification=mask, overlap=overlap) != 0

        elif isinstance(mask, Vector):
            array = self.inputVector.vector(key=name).array(overlap=overlap, allTouched=mask.allTouched(),
                                                            filterSQL=mask.filterSQL(), dtype=np.uint8) != 0
            if isinstance(mask, VectorMask) and mask.invert():
                np.logical_not(array, out=array)

        else:
            assert 0, repr(mask)

        return array

    def flowMasksArray(self, masks, aggregateFunction=None, overlap=0):
        name = 'mask'
        array = self.full(value=True, bands=1, dtype=np.bool, overlap=overlap)
        if masks is None:
            return array

        if isinstance(masks, FlowObject):
            masks = [masks]

        for i, mask in enumerate(masks):
            array *= self.flowMaskArray(name=name + str(i), mask=mask, aggregateFunction=aggregateFunction,
                                        overlap=overlap)
        return array

    def flowClassificationArray(self, name, classification, overlap=0):
        if classification is None or classification.filename() is None:
            return np.array([])
        elif isinstance(classification,
                        (Classification, VectorClassification, Fraction)):
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
        elif isinstance(regression, Regression):
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
        elif isinstance(fraction, Fraction):
            array = self.inputRaster.raster(key=name).array(overlap=overlap, resampleAlg=gdal.GRA_Average)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=fraction.minOverallCoverage(),
                                                 minDominantCoverage=fraction.minDominantCoverage(),
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(fraction, Classification):
            categories = range(1, fraction.classDefinition().classes() + 1)
            array = self.inputRaster.raster(key=name).fractionArray(categories=categories, overlap=overlap)
            invalid = self.maskFromFractionArray(fractionArray=array,
                                                 minOverallCoverage=fraction.minOverallCoverage(),
                                                 minDominantCoverage=fraction.minDominantCoverage(),
                                                 invert=True)
            array[:, invalid] = -1
        elif isinstance(fraction, VectorClassification):

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
        if isinstance(input, Vector):
            array = self.flowVectorArray(name=name, vector=input, overlap=overlap)
        elif isinstance(input, Raster):
            array = self.flowRasterArray(name=name, raster=input, overlap=overlap)
        else:
            assert 0
        return array

    def flowInputZSize(self, name, input):
        if isinstance(input, Vector):
            shape = 1
        elif isinstance(input, Raster):
            shape = input.dataset().zsize()
        else:
            assert 0
        return shape

    def flowInputDType(self, name, input):
        if isinstance(input, Vector):
            dtype = input.dtype()
        elif isinstance(input, Raster):
            dtype = input.dataset().dtype()
        else:
            assert 0
        return dtype

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        MetadataEditor.setClassDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                       classDefinition=classDefinition)

    def setFlowMetadataFractionDefinition(self, name, classDefinition):
        return MetadataEditor.setFractionDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                                 classDefinition=classDefinition)

    def setFlowMetadataRegressionDefinition(self, name, noDataValues, outputNames):
        return MetadataEditor.setRegressionDefinition(rasterDataset=self.outputRaster.raster(key=name),
                                                                   noDataValues=noDataValues, outputNames=outputNames)

    def setFlowMetadataBandNames(self, name, bandNames):
        return MetadataEditor.setBandNames(rasterDataset=self.outputRaster.raster(key=name),
                                                        bandNames=bandNames)

    def setFlowMetadataNoDataValues(self, name, noDataValues):
        self.outputRaster.raster(key=name).setNoDataValues(values=noDataValues)

    def setFlowMetadataSensorDefinition(self, name, sensor):
        assert isinstance(sensor, SensorDefinition)
        raster = self.outputRaster.raster(key=name)
        centers = [wd.center() for wd in sensor.wavebandDefinitions()]
        raster.setMetadataItem(key='wavelength', value=centers, domain='ENVI')
        fwhms = [wd.fwhm() for wd in sensor.wavebandDefinitions()]
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

    def maskFromArray(self, array, noDataValues=None, defaultNoDataValue=None, noDataValueSource=None,
                      aggregateFunction=None):

        assert array.ndim == 3

        if aggregateFunction is None:
            aggregateFunction = lambda a: np.all(a, axis=0, keepdims=True)

        if noDataValues is None:
            assert noDataValueSource is not None
            try:  # in case of a normal raster
                raster = self.inputRaster.raster(key=noDataValueSource)
                noDataValues = raster.noDataValues(default=0)
            except:  # in case of a raster stack
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


class FlowObject(object):
    '''Base class for all workflow type.'''

    def __repr__(self):
        kwargs = list()
        for key, value in self.__getstate__().items():
            if isinstance(value, str):
                valueRepr = value
            elif isinstance(value,np.ndarray):
                valueRepr = 'array[{}]'.format(', '.join([str(n) for n in value.shape]))
            else:
                valueRepr = repr(value)
            kwarg =  '{}={}'.format(key, valueRepr)
            kwargs.append(kwarg)

        return '{}({})'.format(type(self).__name__, ', '.join(kwargs))

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.__init__(**state)

    def pickle(self, filename, progressBar=None):
        '''
        Pickles itself into the given file.

        :param filename: path to the output file
        :type filename: str
        :param progressBar: reports pickling action
        :type progressBar: hubdc.progressbar.ProgressBar
        :rtype: FlowObject
        '''
        self._initPickle()
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)
        hubflow.signals.sigFileCreated.emit(filename)

        if progressBar is not None:
            assert isinstance(progressBar, ProgressBar)
            progressBar.setText('{}.pickle(filename={})'.format(self.__class__.__name__, filename))
            progressBar.setText(repr(self))

        return self

    @classmethod
    def unpickle(cls, filename, raiseError=True):
        '''
        Unpickle FlowObject from the given file.

        :param filename: path to input file.
        :type filename: str
        :param raiseError: If set to ``True`` and unpickling is not successful, an exception is raised.
                           If set to ``False``, ``None`` is returned.
        :type raiseError: bool
        :rtype: Union[FlowObject, None]
        :raises: Union[hubflow.errors.FlowObjectTypeError, hubflow.errors.FlowObjectPickleFileError]
        '''

        try:
            with open(filename, 'rb') as f:
                obj = pickle.load(file=f)
        except:
            if raiseError:
                raise FlowObjectPickleFileError('not a valid pickle file: ' + str(filename))
            else:
                return None

        if not isinstance(obj, cls):
            if raiseError:
                raise FlowObjectTypeError('wrong type ({t1}), expected type: {t2}'.format(t1=obj.__class__.__name__,
                                                                                          t2=cls.__name__))
            else:
                return None
        return obj

    def _initPickle(self):
        pass


class MapCollection(FlowObject):
    '''Class for managing a collection of :class:`~Map` 's.'''

    def __init__(self, maps):
        '''Create an instance by a given list of maps.'''
        self._maps = maps

    def __getstate__(self):
        return OrderedDict([('maps', self.maps())])

    def _initPickle(self):
        for map in self.maps():
            map._initPickle()

    def maps(self):
        '''Return the list of maps'''
        return self._maps

    def extractAsArray(self, masks, grid=None, onTheFlyResampling=False, **kwargs):
        '''
        Returns a list of arrays, one for each map in the collection.
        Each array holds the extracted profiles for all pixels, where all maps inside ``masks`` evaluate to ``True``.

        :param masks: List of maps that are evaluated as masks.
        :type masks: List[Map]
        :param grid: If set to ``None``, all pixel grids in the collection and in ``masks`` must match.
                     If set to a valid Grid and ``onTheFlyResampling=True``, all maps and masks are resampled.
        :type grid: hubdc.core.Grid
        :param onTheFlyResampling: If set to ``True``, all maps and masks are resampled into the given ``grid``.
        :type onTheFlyResampling: bool
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :return: list of 2d arrays of size (bands, profiles)
        :rtype: List[numpy.ndarray]


        :example:

        >>> raster = Raster.fromArray(array=[[[1, 2], [3, 4]],[[1, 2], [3, 4]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[1, 2],
                [3, 4]],
        <BLANKLINE>
               [[1, 2],
                [3, 4]]])
        >>> mask = Mask.fromArray(array=[[[1, 0], [0, 1]]], filename='/vsimem/mask.bsq')
        >>> mask.array()
        array([[[1, 0],
                [0, 1]]], dtype=uint8)
        >>> mapCollection = MapCollection(maps=[raster])
        >>> mapCollection.extractAsArray(masks=[mask])
        [array([[1, 4],
               [1, 4]])]
        '''

        if grid is None:
            grid = self.maps()[0].grid()
        assert isinstance(grid, Grid)
        equalGrids = True
        for map in self.maps() + masks:
            if isinstance(map, Raster):
                equalGrids &= map.grid().equal(other=grid, tol=1e-8)

        if equalGrids:

            def getRasterDataset(map):
                if isinstance(map, Raster):
                    rasterDataset = map.dataset()
                elif isinstance(map, Vector):
                    gdalType = gdal_array.NumericTypeCodeToGDALTypeCode(map.dtype())
                    rasterDataset = map.dataset().rasterize(grid=grid,
                                                            gdalType=gdalType,
                                                            initValue=map.initValue(),
                                                            burnValue=map.burnValue(),
                                                            burnAttribute=map.burnAttribute(),
                                                            allTouched=map.allTouched(),
                                                            filterSQL=map.filterSQL(),
                                                            noDataValue=map.noDataValue())
                elif map is None:
                    rasterDataset = None
                else:
                    assert 0, repr(map)
                return rasterDataset

            # calculate overall mask
            marray = np.full(shape=grid.shape(), fill_value=np.True_)
            for map in masks:
                rasterDataset = getRasterDataset(map=map)
                if rasterDataset is None:
                    continue
                for band in rasterDataset.bands():
                    marray *= band.readAsArray() != band.noDataValue(default=0)

            nothingToExtract = not marray.any()

            # extract values for all masked pixels
            arrays = list()
            for map in self.maps():
                zsize = map.dataset().zsize()
                if nothingToExtract:
                    zsize = map.dataset().zsize()
                    profiles = np.empty(shape=(zsize, 0), dtype=np.uint8)
                else:
                    array = getRasterDataset(map=map).readAsArray()
                    profiles = array[:, marray]

                arrays.append(profiles)

        else:
            assert onTheFlyResampling is True
            arrays = extractPixels(inputs=self.maps(), masks=masks, grid=grid, **kwargs)
        return arrays

    def extractAsRaster(self, filenames, masks, grid=None, onTheFlyResampling=False, **kwargs):
        '''
        Returns the result of :meth:`~MapCollection.extractAsArray` as a list of
        :class:`Map` objects.

        :param filenames: list of output paths, one for each map inside the collection
        :type filenames: List[str]
        :rtype: List[Map]


        All other parameters are passed to :meth:`~MapCollection.extractAsArray`.

        :example:

        Same example as in :meth:`~MapCollection.extractAsArray`.

        >>> raster = Raster.fromArray(array=[[[1, 2], [3, 4]],[[1, 2], [3, 4]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[1, 2],
                [3, 4]],
        <BLANKLINE>
               [[1, 2],
                [3, 4]]])
        >>> mask = Mask.fromArray(array=[[[1, 0], [0, 1]]], filename='/vsimem/mask.bsq')
        >>> mask.array()
        array([[[1, 0],
                [0, 1]]], dtype=uint8)
        >>> mapCollection = MapCollection(maps=[raster])
        >>> extractedRaster = mapCollection.extractAsRaster(filenames=['/vsimem/rasterExtracted.bsq'], masks=[mask])
        >>> extractedRaster[0].array()
        array([[[1],
                [4]],
        <BLANKLINE>
               [[1],
                [4]]])

        '''
        assert isinstance(filenames, list)
        assert len(filenames) == len(self.maps())
        arrays = self.extractAsArray(grid=grid, masks=masks, onTheFlyResampling=onTheFlyResampling, **kwargs)
        rasters = list()

        for filename, array, map in zip(filenames, arrays, self.maps()):
            # from single line 3d array ...
            array = np.atleast_3d(array)

            # ... to multiple line 3d array (to avoid very long lines)
            from math import ceil
            bands = array.shape[0]
            lines = min(3600, array.shape[1])
            samples = ceil(array.shape[1] / float(lines))
            array2 = np.full(shape=(bands, lines*samples, 1), fill_value=map.noDataValue(default=np.nan),
                             dtype=map.dtype())
            array2[:, :array.shape[1]] = array[:]
            array2 = np.reshape(array2, (bands, lines, samples))

            rasterDataset = createRasterDatasetFromArray(array=array2,
                                                         filename=filename,
                                                         driver=RasterDriver.fromFilename(filename=filename))

            if isinstance(map, (Classification, VectorClassification)):
                MetadataEditor.setClassDefinition(rasterDataset=rasterDataset,
                                                  classDefinition=map.classDefinition())
            elif isinstance(map, Fraction):
                MetadataEditor.setFractionDefinition(rasterDataset=rasterDataset,
                                                     classDefinition=map.classDefinition())
            elif isinstance(map, Regression):
                MetadataEditor.setRegressionDefinition(rasterDataset=rasterDataset,
                                                       noDataValues=map.noDataValues(),
                                                       outputNames=map.outputNames())
            elif isinstance(map, Vector):
                pass
            elif isinstance(map, Raster):
                bandCharacteristics = MetadataEditor.bandCharacteristics(rasterDataset=rasterDataset)
                MetadataEditor.setBandCharacteristics(rasterDataset=rasterDataset, **bandCharacteristics)
            else:
                assert 0, repr(map)

            rasterDataset.flushCache()
            if isinstance(map, Raster):
                raster = type(map).fromRasterDataset(rasterDataset=rasterDataset)
            else:
                raster = Raster.fromRasterDataset(rasterDataset=rasterDataset)
            rasters.append(raster)
        return rasters


class Map(FlowObject):
    '''
    Base class for all spatial workflow types.
    For example :class:`~Raster` and :class:`~Vector`.'''


class Raster(Map):
    '''Class for managing raster maps like :class:`~Mask`, :class:`~Classification`,
    :class:`~Regression` and :class:`~Fraction`.'''

    def __init__(self, filename):
        '''Create instance from the raster located at the given ``filename``.'''
        self._filename = filename
        self._rasterDataset = None

    def __getstate__(self):
        return OrderedDict([('filename', self.filename())])

    def _initPickle(self):
        self._rasterDataset = None
        return self

    def filename(self):
        '''Return the filename.'''
        return self._filename

    def dataset(self):
        '''Return the :class:`hubdc.core.RasterDataset` object.'''
        if self._rasterDataset is None:
            self._rasterDataset = openRasterDataset(self.filename())
        assert isinstance(self._rasterDataset, RasterDataset)
        return self._rasterDataset

    def noDataValue(self, default=None):
        '''Forwards :meth:`hubdc.core.RasterDataset.noDataValue` result.'''
        return self.dataset().noDataValue(default=default)

    def dtype(self):
        '''Forwards :meth:`hubdc.core.RasterDataset.dtype` result.'''
        return self.dataset().dtype()

    def grid(self):
        '''Forwards :meth:`hubdc.core.RasterDataset.grid` result.'''
        return self.dataset().grid()

    def shape(self):
        '''Forwards :meth:`hubdc.core.RasterDataset.shape` result.'''
        return self.dataset().shape()

    def readAsArray(self, grid=None, resampleAlg=gdal.GRA_NearestNeighbour):
        '''Forwards :meth:`hubdc.core.RasterDataset.readAsArray` result.'''
        return self.dataset().readAsArray(grid=grid, resampleAlg=resampleAlg)

    def array(self, grid=None, resampleAlg=gdal.GRA_NearestNeighbour, **kwargs):
        '''
        Returns raster data as array. Performes on-the-fly resampling if ``grid`` is given.

        :param grid:
        :type grid: :class:`~hubdc.core.Grid`
        :param resampleAlg: GDAL resampling algorithm, e.g. ``gdal.GRA_NearestNeighbour``
        :param kwargs: passed to :meth:`~Raster.resample`
        :type kwargs:
        :return:
        :rtype: numpy.ndarray

        :example:

        >>> raster = Raster.fromArray(array=[[[1, 2, 3]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[1, 2, 3]]])
        '''
        if grid is None:
            grid = self.grid()
        raster = self.resample(filename='/vsimem/raster.array.{}.bsq'.format(self.filename()),
                               grid=grid, resampleAlg=resampleAlg, progressBar=SilentProgressBar(), **kwargs)
        array = raster.dataset().readAsArray()
        gdal.Unlink(raster.filename())
        return array

    @classmethod
    def fromRasterDataset(cls, rasterDataset, **kwargs):
        '''
        Create instance from given ``rasterDataset``.

        :param rasterDataset: existing hubdc.core.RasterDataset
        :type rasterDataset: hubdc.core.RasterDataset
        :param kwargs: passed to class constructor
        :rtype: Raster

        :example:

        >>> rasterDataset = RasterDataset.fromArray(array=[[[1,2,3]]], filename='/vsimem/raster.bsq', driver=ENVIBSQDriver())
        >>> rasterDataset # doctest: +ELLIPSIS
        RasterDataset(gdalDataset=<osgeo.gdal.Dataset; proxy of <Swig Object of type 'GDALDatasetShadow *' at 0x...> >)
        >>> Raster.fromRasterDataset(rasterDataset=rasterDataset)
        Raster(filename=/vsimem/raster.bsq)
        '''

        assert isinstance(rasterDataset, RasterDataset)
        raster = cls(rasterDataset.filename(), **kwargs)
        raster._rasterDataset = rasterDataset
        return raster

    @classmethod
    def fromVector(cls, filename, vector, grid, noDataValue=None, **kwargs):
        '''
        Create instance from given ``vector`` by rasterizing it into the given ``grid``.

        :param filename: output path
        :type filename: str
        :param vector: input vector
        :type vector: Vector
        :param grid: output pixel grid
        :type grid: hubdc.core.Grid
        :param noDataValue: output no data value
        :type noDataValue: float
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: hubflow.core.Raster

        :example:

        >>> import tempfile
        >>> vector = Vector.fromPoints(points=[(-1, -1), (1, 1)], filename=join(tempfile.gettempdir(), 'vector.shp'), projection=Projection.WGS84())
        >>> grid = Grid(extent=Extent(xmin=-1.5, xmax=1.5, ymin=-1.5, ymax=1.5), resolution=1, projection=Projection.WGS84())
        >>> raster = Raster.fromVector(filename='/vsimem/raster.bsq', vector=vector, grid=grid)
        >>> print(raster.array())
        [[[ 0.  0.  1.]
          [ 0.  0.  0.]
          [ 1.  0.  0.]]]

        '''
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowVector('vector', vector=vector)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_RasterFromVector, vector=vector, noDataValue=noDataValue)
        return Raster(filename=filename)

    @staticmethod
    def fromENVISpectralLibrary(filename, library):
        '''
        Create instance from given ``library``.

        :param filename: output path
        :type filename: str
        :param library:
        :type library: ENVISpectralLibrary`
        :rtype: Raster

        :example:

        >>> import enmapboxtestdata
        >>> speclib = ENVISpectralLibrary(filename=enmapboxtestdata.speclib)
        >>> raster = Raster.fromENVISpectralLibrary(filename='/vsimem/raster.bsq', library=speclib)
        >>> raster.shape()
        (177, 75, 1)

        '''
        assert isinstance(library, ENVISpectralLibrary)
        rasterDataset = library.raster().dataset().translate(filename=filename,
                                                             driver=RasterDriver.fromFilename(filename=filename))
        rasterDataset.copyMetadata(other=library.raster().dataset())
        return Raster.fromRasterDataset(rasterDataset=rasterDataset)

    @classmethod
    def fromArray(cls, array, filename, grid=None, noDataValues=None, **kwargs):
        '''
        Create instance from given ``array``.

        :param array:
        :type array: Union[numpy.ndarray, list]
        :param filename: output path
        :type filename: str
        :param grid: output grid
        :type grid: hubdc.core.Grid
        :param noDataValues: list of band no data values
        :type noDataValues: List[float]
        :rtype: Raster

        :example:

        >>> raster = Raster.fromArray(array=np.zeros(shape=[177, 100, 100]), filename='/vsimem/raster.bsq')
        >>> raster.shape()
        (177, 100, 100)
        >>> raster.grid() # default grid uses WGS84 projection and millisecond (1/3600 degree) resolution
        Grid(extent=Extent(xmin=0.0, xmax=0.027777777777777776, ymin=0.0, ymax=0.027777777777777776), resolution=Resolution(x=0.0002777777777777778, y=0.0002777777777777778), projection=Projection(wkt=GEOGCS["WGS84", DATUM["WGS_1984", SPHEROID["WGS84",6378137,298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich",0, AUTHORITY["EPSG","8901"]], UNIT["degree",0.0174532925199433, AUTHORITY["EPSG","9122"]], AUTHORITY["EPSG","4326"]])

        '''

        if isinstance(array, list):
            array = np.array(array)
        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        rasterDataset = createRasterDatasetFromArray(array=array,
                                                     grid=grid,
                                                     filename=filename,
                                                     driver=RasterDriver.fromFilename(filename=filename))
        rasterDataset.setNoDataValues(values=noDataValues)
        return cls.fromRasterDataset(rasterDataset=rasterDataset, **kwargs)


    def uniqueValues(self, index):
        '''
        Return unique values for band at given ``index``.

        :example:

        >>> raster = Raster.fromArray(array=[[[1, 1, 1, 5, 2]]], filename='/vsimem/raster.bsq')
        >>> raster.uniqueValues(index=0)
        array([1, 2, 5])

        '''

        values = np.unique(self.dataset().band(index=index).readAsArray())
        return values

    def convolve(self, filename, kernel, **kwargs):
        '''
        Perform convolution of itself with the given ``kernel`` and return the result raster,
        where an 1D kernel is applied along the z dimension,
        an 2D kernel is applied spatially (i.e. y/x dimensions),
        and an 3D kernel is applied directly to the 3D z-y-x data cube.

        :param filename: output path
        :type filename: str
        :param kernel:
        :type kernel: astropy.convolution.kernels.Kernel
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: Raster

        :example:

        >>> array = np.zeros(shape=[1, 5, 5])
        >>> array[0, 2, 2] = 1
        >>> raster = Raster.fromArray(array=array, filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[ 0.,  0.,  0.,  0.,  0.],
                [ 0.,  0.,  0.,  0.,  0.],
                [ 0.,  0.,  1.,  0.,  0.],
                [ 0.,  0.,  0.,  0.,  0.],
                [ 0.,  0.,  0.,  0.,  0.]]])

        >>> from astropy.convolution.kernels import Kernel2D
        >>> kernel = Kernel2D(array=np.ones(shape=[3, 3]))
        >>> kernel.array
        array([[ 1.,  1.,  1.],
               [ 1.,  1.,  1.],
               [ 1.,  1.,  1.]])
        >>> result = raster.convolve(filename='/vsimem/result.bsq', kernel=kernel)
        >>> result.array()
        array([[[ 0.,  0.,  0.,  0.,  0.],
                [ 0.,  1.,  1.,  1.,  0.],
                [ 0.,  1.,  1.,  1.,  0.],
                [ 0.,  1.,  1.,  1.,  0.],
                [ 0.,  0.,  0.,  0.,  0.]]], dtype=float32)
        '''
        from astropy.convolution import Kernel
        assert isinstance(kernel, Kernel)
        assert kernel.dimension <= 3
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterConvolve, raster=self, kernel=kernel)
        return Raster(filename=filename)

    def applySpatial(self, filename, function, **kwargs):
        '''
        Apply given ``function`` to each band of itself and return the result raster.

        :param filename:
        :type filename: str
        :param function: user defined function that takes one argument ``array``
        :type function: function
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: Raster

        :example:

        >>> raster = Raster.fromArray(array=[[[1, 2, 3]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[1, 2, 3]]])
        >>> def square(array): return array**2
        >>> result = raster.applySpatial(filename='/vsimem/result.bsq', function=square)
        >>> result.array()
        array([[[1, 4, 9]]])

        '''
        applier = Applier(defaultGrid=self, **kwargs)
        applier.controls.setBlockFullSize()
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterApplySpatial, raster=self, function=function)
        return Raster(filename=filename)

    def resample(self, filename, grid, resampleAlg=gdal.GRA_NearestNeighbour, **kwargs):
        '''
        Return itself resampled into the given ``grid``.

        :param filename: output path
        :type filename: str
        :param grid:
        :type grid: hubdc.core.Grid
        :param resampleAlg: GDAL resampling algorithm
        :type resampleAlg: int
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: Raster

        :example:

        >>> raster = Raster.fromArray(array=[[[1, 2, 3]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[1, 2, 3]]])
        >>> grid = Grid(extent=raster.grid().spatialExtent(),
        ...             resolution=raster.grid().resolution() / (2, 1))
        >>> result = raster.resample(filename='/vsimem/result.bsq', grid=grid)
        >>> result.array()
        array([[[1, 1, 2, 2, 3, 3]]])
        '''

        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster('inraster', raster=self)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_RasterResample, raster=self, resampleAlg=resampleAlg)
        return Raster(filename=filename)

    def asMask(self, noDataValues=None, minOverallCoverage=0.5, indices=None, invert=False):
        '''
        Return itself as a :class:`~hubflow.core.Mask`.
        
        :param noDataValues: list of band-wise no data values
        :type noDataValues: List[Union[None, float]]
        :param minOverallCoverage: threshold that defines, in case of on-the-fly average-resampling, which pixel will be evaluated as True
        :type minOverallCoverage: float
        :param indices: if set, a band subset mask for the given ``indices`` is created
        :type indices: int
        :param invert: whether to invert the mask
        :type invert: int
        :rtype: Mask

        :example:

        >>> raster = Raster.fromArray(array=[[[-1, 0, 5, 3, 0]]], filename='/vsimem/raster.bsq',
        ...                           noDataValues=[-1])
        >>> raster.array()
        array([[[-1,  0,  5,  3,  0]]])
        >>> raster.asMask().array()
        array([[[0, 1, 1, 1, 1]]], dtype=uint8)
        '''

        return Mask(filename=self.filename(), noDataValues=noDataValues, minOverallCoverage=minOverallCoverage,
                    indices=indices, invert=invert)

    def statistics(self, bandIndices=None, mask=None,
                   calcPercentiles=False, calcHistogram=False, calcMean=False, calcStd=False,
                   percentiles=list(), histogramRanges=None, histogramBins=None,
                   **kwargs):
        '''
        Return a list of BandStatistic named tuples:

        ============   ====================================================================
        key            value/description
        ============   ====================================================================
        index          band index
        nvalid         number of valid pixel (not equal to noDataValue and not masked)
        ninvalid       number of invalid pixel (equal to noDataValue or masked)
        min            smallest value
        max            largest value
        percentiles+   list of (rank, value) tuples for given percentiles
        std+           standard deviation
        mean+          mean
        histo+         Histogram(hist, bin_edges) tuple with histogram counts and bin edges
        ============   ====================================================================

        +set corresponding calcPercentiles/Histogram/Mean/Std keyword to True


        :param bandIndices: calculate statistics only for given ``bandIndices``
        :type bandIndices: Union[None, None, None]
        :param mask:
        :type mask: Union[None, None, None]
        :param calcPercentiles: if set True, band percentiles are calculated; see ``percentiles`` keyword
        :type calcPercentiles: bool
        :param calcHistogram: if set True, band histograms are calculated; see ``histogramRanges`` and ``histogramBins`` keywords
        :type calcHistogram: bool
        :param calcMean: if set True, band mean values are calculated
        :type calcMean: bool
        :param calcStd: if set True, band standard deviations are calculated
        :type calcStd: bool
        :param percentiles: values between 0 (i.e. min value) and 100 (i.e. max value), 50 is the median
        :type percentiles: List[float]
        :param histogramRanges: list of ranges, one for each band; ranges are passed to ``numpy.histogram``; None ranges are set to (min, max)
        :type histogramRanges: List[numpy.histogram ranges]
        :param histogramBins: list of bins, one for each band; bins are passed to ``numpy.histogram``; None bins are set to 256
        :type histogramBins: List[numpy.histogram bins]
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: List[BandStatistics(index, nvalid, ninvalid, min, max, percentiles, std, mean, histo)]

        :Example:

        >>> # create raster with no data values
        >>> raster = Raster.fromArray(array=[[[1, np.nan, 3], [0, 2, np.inf], [1, 0, 3]]], filename='/vsimem/raster.bsq', noDataValues=[0])
        >>> # calculate basic statistics
        >>> statistics = raster.statistics()
        >>> print(statistics[0])
        BandStatistics(index=0, nvalid=5, ninvalid=4, min=1.0, max=3.0, percentiles=None, std=None, mean=None, histo=None)
        >>> # calculate histograms
        >>> statistics = raster.statistics(calcHistogram=True, histogramRanges=[(1, 4)], histogramBins=[3])
        >>> print(statistics[0].histo)
        Histogram(hist=array([2, 1, 2], dtype=int64), bin_edges=array([ 1.,  2.,  3.,  4.]))
        >>> # calculate percentiles (min, median, max)
        >>> statistics = raster.statistics(calcPercentiles=True, percentiles=[0, 50, 100])
        >>> print(statistics[0].percentiles)
        [Percentile(rank=0, value=1.0), Percentile(rank=50, value=2.0), Percentile(rank=100, value=3.0)]
        '''

        applier = Applier(defaultGrid=self, **kwargs)
        applier.controls.setBlockFullSize()
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        return applier.apply(operatorType=_RasterStatistics, raster=self, bandIndices=bandIndices, mask=mask,
                             calcPercentiles=calcPercentiles, calcMean=calcMean, calcStd=calcStd,
                             calcHistogram=calcHistogram, percentiles=percentiles, histogramRanges=histogramRanges, histogramBins=histogramBins)

    def scatterMatrix(self, raster2, bandIndex1, bandIndex2, range1, range2, bins=256, mask=None, stratification=None,
                      **kwargs):
        '''
        Return scatter matrix between itself's band given by ``bandIndex1`` and ``raster2``'s band given by ``bandIndex2``
        stored as a named tuple ``ScatterMatrix(H, xedges, yedges)``. Where ``H`` is the 2d count matrix for the
        binning given by ``xedges`` and ``yedges`` lists. If a ``stratication`` is defined, ``H`` will be a list of
        2d count matrices, one for each strata.

        :param raster2:
        :type raster2: Raster
        :param bandIndex1: first band index
        :type bandIndex1: int
        :param bandIndex2: second band index
        :type bandIndex2: int
        :param range1: first band range as (min, max) tuple
        :type range1: Tuple[float, float]
        :param range2: second band range as (min, max) tuple
        :type range2: Tuple[float, float]
        :param bins: passed to ``np.histogram2d``
        :param mask: map that is evaluated as a mask
        :type mask: Map
        :param stratification: classification that stratifies the calculation into different classes
        :type stratification: Classification
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: ScatterMatrix(H, xedges, yedges)

        :Example:

        >>> # create two single band raster
        >>> raster1 = Raster.fromArray(array=[[[1, 2, 3]]], filename='/vsimem/raster1.bsq')
        >>> raster2 = Raster.fromArray(array=[[[10, 20, 30]]], filename='/vsimem/raster2.bsq')
        >>> # calculate scatter matrix between both raster bands
        >>> scatterMatrix = raster1.scatterMatrix(raster2=raster2, bandIndex1=0, bandIndex2=0, range1=[1, 4], range2=[10, 40], bins=3)
        >>> scatterMatrix.H
        array([[1, 0, 0],
               [0, 1, 0],
               [0, 0, 1]], dtype=uint64)
        >>> scatterMatrix.xedges
        array([ 1.,  2.,  3.,  4.])
        >>> scatterMatrix.yedges
        array([ 10.,  20.,  30.,  40.])
        '''

        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster1', raster=self)
        applier.setFlowRaster('raster2', raster=raster2)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowClassification('stratification', classification=stratification)

        _, xedges, yedges = np.histogram2d(x=[0], y=[0], bins=bins, range=[range1, range2])
        bins = [xedges, yedges]
        results = applier.apply(operatorType=_RasterScatterMatrix, raster1=self, raster2=raster2,
                                bandIndex1=bandIndex1, bandIndex2=bandIndex2, bins=bins, mask=mask,
                                stratification=stratification)
        H = np.sum(np.stack(results), axis=0, dtype=np.uint64)
        ScatterMatrix = namedtuple('ScatterMatrix', ['H', 'xedges', 'yedges'])

        return ScatterMatrix(H, xedges, yedges)

    def applyMask(self, filename, mask, **kwargs):
        '''
        Applies a ``mask`` to itself.

        :param filename: output path
        :type filename: str
        :param mask: a map that is evaluated as a mask
        :type mask: Map
        :param kwargs: passed to :class:`hubflow.core.Applier`
        :rtype: Raster

        :example:

        >>> raster = Raster.fromArray(array=[[[1, 2, 3]]], filename='/vsimem/raster.bsq', noDataValues=[-1])
        >>> mask = Mask.fromArray(array=[[[0, 0, 1]]], filename='/vsimem/mask.bsq')
        >>> result = raster.applyMask(filename='/vsimem/result.bsq', mask=mask)
        >>> result.array()
        array([[[-1, -1,  3]]])

        '''
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('raster', raster=self)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('maskedRaster', filename=filename)
        applier.apply(operatorType=_RasterApplyMask, raster=self, mask=mask)
        return type(self)(filename=filename)

    def metadataWavelength(self):
        '''
        Return list of band center wavelengths in nanometers.

        :example:

        >>> import enmapboxtestdata
        >>> Raster(filename=enmapboxtestdata.enmap).metadataWavelength() # doctest: +ELLIPSIS
        [460.0, 465.0, 470.0, ..., 2393.0, 2401.0, 2409.0]
        '''

        wavelength = self.dataset().metadataItem(key='wavelength', domain='ENVI', dtype=float, required=True)
        unit = self.dataset().metadataItem(key='wavelength units', domain='ENVI', required=True)
        assert unit.lower() in ['nanometers', 'micrometers']
        wavelength = [float(v) for v in wavelength]
        if unit.lower() == 'micrometers':
            wavelength = [v * 1000 for v in wavelength]
        return wavelength

    def metadataFWHM(self, required=False):
        '''
        Return list of band full width at half maximums in nanometers. If not defined, list entries are ``None``.

        :example:

        >>> import enmapboxtestdata
        >>> Raster(filename=enmapboxtestdata.enmap).metadataFWHM() # doctest: +ELLIPSIS
        [5.8, 5.8, 5.8, ..., 9.1, 9.1, 9.1]
        '''

        fwhm = self.dataset().metadataItem(key='fwhm', domain='ENVI', dtype=float, required=required)
        if fwhm is None:
            fwhm = [None] * self.dataset().zsize()
        else:
            unit = self.dataset().metadataItem(key='wavelength units', domain='ENVI', required=True)
            assert unit.lower() in ['nanometers', 'micrometers']
            fwhm = [float(v) for v in fwhm]
            if unit.lower() == 'micrometers':
                fwhm = [v * 1000 for v in fwhm]

        return fwhm

    def sensorDefinition(self):
        '''
        Return :class:`~hubflow.core.SenserDefinition` created from center wavelength and FWHM.

        :example:

        >>> SensorDefinition.predefinedSensorNames()
        ['modis', 'moms', 'mss', 'npp_viirs', 'pleiades1a', 'pleiades1b', 'quickbird', 'rapideye', 'rasat', 'seawifs', 'sentinel2', 'spot', 'spot6', 'tm', 'worldview1', 'worldview2', 'worldview3']
        >>> SensorDefinition.fromPredefined('sentinel2') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SensorDefinition(wavebandDefinitions=[WavebandDefinition(center=443.0, fwhm=None, responses=[...], name=Sentinel-2 - Band B1), ...,
                                              WavebandDefinition(center=2196.5, fwhm=None, responses=[...], name=Sentinel-2 - Band B12)])
        '''
        return SensorDefinition._fromFWHM(centers=self.metadataWavelength(), fwhms=self.metadataFWHM())

    def plotZProfile(self, *args, **kwargs):
        '''Forwards :meth:`hubdc.core.RasterDataset.plotZProfile`'''
        return self.dataset().plotZProfile(*args, **kwargs)

    def plotSinglebandGrey(self, *args, **kwargs):
        '''Forwards :meth:`hubdc.core.RasterDataset.plotSinglebandGrey`'''
        return self.dataset().plotSinglebandGrey(*args, **kwargs)

    def plotCategoryBand(self, *args, **kwargs):
        '''Forwards :meth:`hubdc.core.RasterDataset.plotCategoryBand`'''
        return self.dataset().plotCategoryBand(*args, **kwargs)


class _RasterResample(ApplierOperator):
    def ufunc(self, raster, resampleAlg):
        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')

        array = inraster.array(resampleAlg=resampleAlg)
        metadataDict = inraster.metadataDict()
        noDataValues = inraster.noDataValues()

        outraster.setArray(array=array)
        outraster.setMetadataDict(metadataDict=metadataDict)
        outraster.setNoDataValues(values=noDataValues)


class _RasterConvolve(ApplierOperator):
    def ufunc(self, raster, kernel):
        from astropy.convolution import convolve, CustomKernel

        if kernel.dimension == 3:
            pass
        elif kernel.dimension == 2:
            kernel = CustomKernel(array=kernel.array[None])
        elif kernel.dimension == 1:
            kernel = CustomKernel(array=kernel.array.reshape(-1, 1, 1))

        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')
        zsize, ysize, xsize = kernel.shape
        overlap = int((max(ysize, xsize)+1)/2.)
        array = np.float32(inraster.array(overlap=overlap))
        noDataValues = self.inputRaster.raster(key='inraster').noDataValues()
        for band, noDataValue in zip(array, noDataValues):
            if noDataValue is not None:
                band[band==noDataValue] = np.nan
        outarray = convolve(array=array, kernel=kernel,
                            fill_value=np.nan, nan_treatment='fill',
                            normalize_kernel=False)
        outraster.setArray(array=outarray, overlap=overlap)
        #outraster.setMetadataDict(metadataDict=inraster.metadataDict())
        outraster.setNoDataValue(value=np.nan)


class _RasterApplySpatial(ApplierOperator):
    def ufunc(self, raster, function):

        inraster = self.inputRaster.raster(key='inraster')
        outraster = self.outputRaster.raster(key='outraster')
        outraster.setZsize(zsize=inraster.dataset().zsize())
        for index in range(inraster.dataset().zsize()):
            array = inraster.bandArray(indices=[index])[0]
            outarray = function(array)
            outraster.band(index=index).setArray(array=outarray)


class _RasterStatistics(ApplierOperator):
    def ufunc(self, raster, bandIndices, mask, calcPercentiles, calcHistogram, calcMean, calcStd,
              percentiles, histogramRanges, histogramBins):

        maskValid = self.flowMaskArray('mask', mask=mask)

        if bandIndices is None:
            bandIndices = range(self.inputRaster.raster('raster').dataset().zsize())

        result = list()

        BandStatistics = namedtuple('BandStatistics', ['index', 'nvalid', 'ninvalid', 'min', 'max', 'percentiles',
                                                       'std', 'mean', 'histo'])
        Histogram = namedtuple('Histogram', ['hist', 'bin_edges'])
        Percentile = namedtuple('Percentile', ['rank', 'value'])

        for i, index in enumerate(bandIndices):
            self.progressBar.setPercentage((float(i) + 1) / len(bandIndices) * 100)
            band = self.flowRasterArray('raster', raster=raster, indices=[index]).astype(dtype=np.float64)
            finiteValid = np.isfinite(band)
            valid = self.maskFromBandArray(array=band, noDataValueSource='raster', index=index)
            valid *= maskValid
            valid *= finiteValid
            values = band[valid]  # may still contain NaN
            bandResult = dict()
            bandResult['index'] = index
            bandResult['nvalid'] = np.sum(valid)
            bandResult['ninvalid'] = np.product(band.shape) - bandResult['nvalid']
            bandResult['min'] = np.min(values)
            bandResult['max'] = np.max(values)

            if calcPercentiles:
                qs = percentiles
                ps = np.percentile(values, q=percentiles)
                bandResult['percentiles'] = [Percentile(rank=rank, value=value) for rank, value in zip(qs, ps)]
            else:
                bandResult['percentiles'] = None

            if calcStd:
                bandResult['std'] = np.nanstd(values)
            else:
                bandResult['std'] = None

            if calcMean:
                bandResult['mean'] = np.nanmean(values)
            else:
                bandResult['mean'] = None

            if calcHistogram:
                if histogramRanges is None:
                    range_ = [bandResult['min'], bandResult['max']]
                else:
                    assert len(histogramRanges) == len(bandIndices)
                    range_ = histogramRanges[index]
                if histogramBins is None:
                    bins = 256
                else:
                    assert len(histogramBins) == len(bandIndices)
                    bins = histogramBins[index]

                hist, bin_edges = np.histogram(values, bins=bins, range=range_)
                bandResult['histo'] = Histogram(hist=hist, bin_edges=bin_edges)
            else:
                bandResult['histo'] = None

            result.append(BandStatistics(**bandResult))
        return result

    @staticmethod
    def aggregate(blockResults, grid, *args, **kwargs):
        return blockResults[0]

class _RasterFromVector(ApplierOperator):
    def ufunc(self, vector, noDataValue):
        array = self.flowVectorArray('vector', vector=vector)
        self.outputRaster.raster(key='raster').setArray(array=array)
        self.setFlowMetadataNoDataValues('raster', noDataValues=[noDataValue])


class _RasterScatterMatrix(ApplierOperator):
    def ufunc(self, raster1, raster2, bandIndex1, bandIndex2, bins, mask, stratification):

        band1 = self.flowRasterArray('raster1', raster=raster1, indices=[bandIndex1])
        band2 = self.flowRasterArray('raster2', raster=raster2, indices=[bandIndex2])
        strata = self.flowClassificationArray('stratification', classification=stratification)

        valid = self.maskFromBandArray(array=band1, noDataValueSource='raster1', index=bandIndex1)
        valid *= self.maskFromBandArray(array=band2, noDataValueSource='raster2', index=bandIndex2)
        valid *= self.flowMaskArray('mask', mask=mask)

        x = band1[valid]
        y = band2[valid]

        if strata.size == 0:
            H = np.histogram2d(x=x, y=y, bins=bins)[0]
        else:
            s = strata[valid]
            HList = list()
            for i in range(1, stratification.classDefinition().classes() + 1):
                v = s == i
                Hi = np.histogram2d(x=x[v], y=y[v], bins=bins)[0]
                HList.append(np.array(Hi))
            H = np.stack(HList)

        return H


class _RasterApplyMask(ApplierOperator):
    def ufunc(self, raster, mask):
        noDataValue = self.inputRaster.raster(key='raster').noDataValue(default=0)
        array = self.flowRasterArray('raster', raster=raster)
        marray = self.flowMaskArray('mask', mask=mask)
        tobefilled = np.logical_not(marray[0])
        array[:, tobefilled] = noDataValue
        inraster = self.inputRaster.raster(key='raster')
        outraster = self.outputRaster.raster(key='maskedRaster')
        outraster.setArray(array=array)
        outraster.setMetadataDict(metadataDict=inraster.metadataDict())
        outraster.setNoDataValue(value=noDataValue)
        outraster.setCategoryColors(colors=inraster.categoryColors())
        outraster.setCategoryNames(names=inraster.categoryNames())


class WavebandDefinition(FlowObject):
    '''Class for managing waveband definitions.'''


    def __init__(self, center, fwhm=None, responses=None, name=None):
        '''
        Create an instance.

        :param center: center wavelength location
        :type center: float
        :param fwhm: full width at half maximum
        :type fwhm: float
        :param responses: list of response function (wavelength, value) tuples
        :type responses: List[(float, float)]
        :param name: waveband name
        :type name: str
        '''

        if responses is not None:
            responses = [(float(x), float(y)) for x, y in responses]

        self._center = float(center)
        if fwhm is not None:
            fwhm = float(fwhm)
        self._fwhm = fwhm
        self._responses = responses
        self._name = name

    def __getstate__(self):
        return OrderedDict([('center', self.center()),
                            ('fwhm', self.fwhm()),
                            ('responses', self.responses()),
                            ('name', self.name())])

    @staticmethod
    def fromFWHM(center, fwhm, sigmaLimits=3):
        '''
        Create an instance from given ``center`` and ``fwhm``.
        The waveband response function is modeled inside the range: ``center`` +/- sigma * ``sigmaLimits``,
        where sigma is given by ``fwhm / 2.3548``.

        :example:

        >>> WavebandDefinition.fromFWHM(center=500, fwhm=10) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        WavebandDefinition(center=500.0, fwhm=10.0, responses=[(487.0, 0.009227241211564235), (488.0, 0.01845426465118729), (489.0, 0.03491721729455092), (490.0, 0.06250295020961404), (491.0, 0.10584721091054979), (492.0, 0.1695806637893581), (493.0, 0.2570344015689991), (494.0, 0.3685735673688072), (495.0, 0.5000059003147861), (496.0, 0.6417177952459099), (497.0, 0.7791678897157294), (498.0, 0.8950267608170881), (499.0, 0.9726554065273144), (500.0, 1.0), (501.0, 0.9726554065273144), (502.0, 0.8950267608170881), (503.0, 0.7791678897157294), (504.0, 0.6417177952459099), (505.0, 0.5000059003147861), (506.0, 0.3685735673688072), (507.0, 0.2570344015689991), (508.0, 0.1695806637893581), (509.0, 0.10584721091054979), (510.0, 0.06250295020961404), (511.0, 0.03491721729455092)], name=None)
        '''
        center = float(center)
        if fwhm is not None:
            fwhm = float(fwhm)
            sigma = fwhm / 2.3548
            wl = np.array(range(int(center - sigmaLimits * sigma), int(center + sigmaLimits * sigma)))
            responses = list(zip(wl, np.exp(-(wl - center) ** 2 / (2 * sigma ** 2))))
        else:
            responses = None
        return WavebandDefinition(center=center, fwhm=fwhm, responses=responses)

    def center(self):
        '''
        Return center wavelength location.

        >>> WavebandDefinition(center=560).center()
        560.0
        '''
        return self._center

    def fwhm(self):
        '''
        Return full width at half maximum.
        
        >>> WavebandDefinition(center=560, fwhm=10).fwhm()
        10.0
        '''
        return self._fwhm

    def responses(self):
        '''
        Return response function as list of (wavelength, response) tuples.

        :example:

        >>> sentinelBlue = SensorDefinition.fromPredefined(name='sentinel2').wavebandDefinition(index=1)
        >>> sentinelBlue.responses()
        [(454.0, 0.02028969), (455.0, 0.06381729), (456.0, 0.14181057), (457.0, 0.27989078), (458.0, 0.53566604), (459.0, 0.75764752), (460.0, 0.81162521), (461.0, 0.81796823), (462.0, 0.82713398), (463.0, 0.8391982), (464.0, 0.85271397), (465.0, 0.85564352), (466.0, 0.85505457), (467.0, 0.86079216), (468.0, 0.86901422), (469.0, 0.8732093), (470.0, 0.8746579), (471.0, 0.87890232), (472.0, 0.88401742), (473.0, 0.88568426), (474.0, 0.8864462), (475.0, 0.89132953), (476.0, 0.89810187), (477.0, 0.89921862), (478.0, 0.89728783), (479.0, 0.899455), (480.0, 0.90808729), (481.0, 0.91663575), (482.0, 0.92044598), (483.0, 0.92225061), (484.0, 0.9262647), (485.0, 0.93060572), (486.0, 0.93187505), (487.0, 0.93234856), (488.0, 0.93660786), (489.0, 0.94359652), (490.0, 0.94689153), (491.0, 0.94277939), (492.0, 0.93912406), (493.0, 0.9435992), (494.0, 0.95384075), (495.0, 0.96115588), (496.0, 0.96098811), (497.0, 0.96023166), (498.0, 0.96653039), (499.0, 0.97646982), (500.0, 0.98081022), (501.0, 0.97624561), (502.0, 0.97399225), (503.0, 0.97796507), (504.0, 0.98398942), (505.0, 0.98579982), (506.0, 0.98173313), (507.0, 0.97932703), (508.0, 0.98329935), (509.0, 0.98777523), (510.0, 0.98546073), (511.0, 0.97952735), (512.0, 0.97936162), (513.0, 0.98807291), (514.0, 0.99619133), (515.0, 0.99330779), (516.0, 0.98572054), (517.0, 0.9860457), (518.0, 0.99517659), (519.0, 1.0), (520.0, 0.99782113), (521.0, 0.93955431), (522.0, 0.70830999), (523.0, 0.42396802), (524.0, 0.24124566), (525.0, 0.13881543), (526.0, 0.07368388), (527.0, 0.03404689), (528.0, 0.01505348)]
        '''
        return self._responses

    def name(self):
        '''
        Return waveband name.

        :example:

        >>> for wavebandDefinition in SensorDefinition.fromPredefined(name='sentinel2').wavebandDefinitions():
        ...     print(wavebandDefinition.name())
        Sentinel-2 - Band B1
        Sentinel-2 - Band B2
        Sentinel-2 - Band B3
        Sentinel-2 - Band B4
        Sentinel-2 - Band B5
        Sentinel-2 - Band B6
        Sentinel-2 - Band B7
        Sentinel-2 - Band B8
        Sentinel-2 - Band B8A
        Sentinel-2 - Band B9
        Sentinel-2 - Band B10
        Sentinel-2 - Band B11
        Sentinel-2 - Band B12
        '''
        return self._name

    def resamplingWeights(self, sensor):
        '''
        Return resampling weights for the center wavelength of the given :class:`~hubflow.core.SensorDefinition`.

        :example:

        Calculate weights for resampling EnMAP sensor into Sentinel-2 band 3.

        >>> import enmapboxtestdata
        >>> enmapSensor = Raster(filename=enmapboxtestdata.enmap).sensorDefinition()
        >>> enmapSensor # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SensorDefinition(wavebandDefinitions=[WavebandDefinition(center=460.0, fwhm=5.8, responses=[(452.0, 0.0051192261189367235), ..., (466.0, 0.051454981460462346)], name=None),
                                              ...,
                                              WavebandDefinition(center=2409.0, fwhm=9.1, responses=[(2397.0, 0.008056878623001433), ..., (2419.0, 0.035151930528992195)], name=None)])
        >>> sentinel2Band4 = SensorDefinition.fromPredefined(name='sentinel2').wavebandDefinition(index=2)
        >>> sentinel2Band4 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        WavebandDefinition(center=560.0, fwhm=None, responses=[(538.0, 0.01591234), ..., (582.0, 0.01477064)], name=Sentinel-2 - Band B3)
        >>> weights = sentinel2Band4.resamplingWeights(sensor=enmapSensor)
        >>> centers = [wd.center() for wd in enmapSensor.wavebandDefinitions()]
        >>> list(zip(centers, weights)) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [(460.0, 0.0), ..., (533.0, 0.0), (538.0, 0.01591234), (543.0, 0.6156192), (549.0, 0.99344666), (554.0, 0.98899243), (559.0, 0.99746124), (565.0, 0.98366361), (570.0, 0.99787368), (575.0, 0.95940618), (581.0, 0.03900649), (587.0, 0.0), ..., (2409.0, 0.0)]
        '''

        assert isinstance(sensor, SensorDefinition)
        weights = list()
        x = np.array([x for x, y in self.responses()])
        for wd in sensor.wavebandDefinitions():
            if wd.center() > x[-1] or wd.center() < x[0]:
                weight = 0.
            else:
                weight = self.responses()[np.abs(np.subtract(x, wd.center())).argmin()][1]
            weights.append(weight)
        return weights

    def plot(self, plotWidget=None, yscale=1., **kwargs):
        '''
        Return response function plot.

        :param plotWidget: if None, a new plot widget is created, otherwise, the given ``plotWidget`` is used
        :type plotWidget: pyqtgraph.graphicsWindows.PlotWindow
        :param yscale: scale factor for y values
        :type yscale: float
        :param kwargs: passed to ``pyqtgraph.graphicsWindows.PlotWindow.plot``
        :rtype: pyqtgraph.graphicsWindows.PlotWindow

        :example:

        >>> plotWidget = SensorDefinition.fromPredefined(name='sentinel2').wavebandDefinition(index=2).plot()

        .. image:: plots/wavebandDefinition_plot.png
        '''
        import pyqtgraph as pg
        if plotWidget is None:
            plotWidget = pg.plot(title='Response Curve')
        x, y = zip(*self.responses())
        plotWidget.plot(x=np.array(x), y=np.array(y) * yscale, **kwargs)
        return plotWidget


class SensorDefinition(FlowObject):
    '''Class for managing sensor definitions.'''

    RESAMPLE_RESPONSE = 'response'
    RESAMPLE_LINEAR = 'linear'
    RESAMPLE_OPTIONS = [RESAMPLE_LINEAR, RESAMPLE_RESPONSE]

    def __init__(self, wavebandDefinitions):
        '''Create an instance by given list of ::class:`~WavebandDefinition`'s.'''
        self._wavebandDefinitions = wavebandDefinitions

    def __getstate__(self):
        return OrderedDict([('wavebandDefinitions', list(self.wavebandDefinitions()))])

    @staticmethod
    def fromPredefined(name):
        '''
        Create an instance for a predefined sensor (e.g. ``name='sentinel2'``).
        See :meth:`~SensorDefinition.predefinedSensorNames` for a full list of predifined sensors.
        Sensor response filter functions (.sli files) are stored here `hubflow/sensors`.

        :example:

        >>> SensorDefinition.fromPredefined(name='sentinel2') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SensorDefinition(wavebandDefinitions=[WavebandDefinition(center=443.0, fwhm=None, responses=[...], name=Sentinel-2 - Band B1),
                                              ...,
                                              WavebandDefinition(center=2196.5, fwhm=None, responses=[...], name=Sentinel-2 - Band B12)])
        '''

        import hubflow.sensors
        assert isinstance(name, str)
        filename = join(hubflow.sensors.__path__[0], name + '.sli')
        assert exists(filename)
        library = ENVISpectralLibrary(filename=filename)
        return SensorDefinition.fromENVISpectralLibrary(library=library, isResponseFunction=True)

    @staticmethod
    def predefinedSensorNames():
        '''
        Return list of predefined sensor names.

        :example:

        >>> SensorDefinition.predefinedSensorNames()
        ['modis', 'moms', 'mss', 'npp_viirs', 'pleiades1a', 'pleiades1b', 'quickbird', 'rapideye', 'rasat', 'seawifs', 'sentinel2', 'spot', 'spot6', 'tm', 'worldview1', 'worldview2', 'worldview3']
        '''
        import hubflow.sensors
        names = [basename(f)[:-4] for f in os.listdir(hubflow.sensors.__path__[0]) if f.endswith('.sli')]
        return names

    @classmethod
    def fromENVISpectralLibrary(cls, library, isResponseFunction):
        '''
        Create instance from :class:`ENVISpectralLibrary`.

        :param library:
        :type library: ENVISpectralLibrary
        :param isResponseFunction: If True, ``library`` is interpreted as sensor response function.
                                   If False, center wavelength and FWHM information is used.
        :type isResponseFunction: bool
        :rtype: SensorDefinition

        :example:

        Case 1 - Library contains spectra with wavelength and FWHM information (i.e. set ``isResponseFunction=False``)

        >>> import enmapboxtestdata
        >>> library = ENVISpectralLibrary(filename=enmapboxtestdata.speclib)
        >>> SensorDefinition.fromENVISpectralLibrary(library=library, isResponseFunction=False) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SensorDefinition(wavebandDefinitions=[WavebandDefinition(center=460.0, fwhm=5.8, responses=[...], name=None),
                                              ...,
                                              WavebandDefinition(center=2409.0, fwhm=9.1, responses=[...], name=None)])

        Case 2 - Library contains response function (i.e. set ``isResponseFunction=True``)

        >>> import hubflow.sensors, os.path
        >>> library = ENVISpectralLibrary(filename = os.path.join(hubflow.sensors.__path__[0], 'sentinel2.sli'))
        >>> SensorDefinition.fromENVISpectralLibrary(library=library, isResponseFunction=True) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SensorDefinition(wavebandDefinitions=[WavebandDefinition(center=443.0, fwhm=None, responses=[...], name=Sentinel-2 - Band B1),
                                              ...,
                                              WavebandDefinition(center=2196.5, fwhm=None, responses=[...], name=Sentinel-2 - Band B12)])
        '''
        assert isinstance(library, ENVISpectralLibrary)

        names = library.raster().dataset().metadataItem(key='spectra names', domain='ENVI')
        wavelengths = np.float32(library.raster().metadataWavelength())

        if isResponseFunction:
            responsess = [list(zip(wavelengths, y)) for y in library.raster().dataset().readAsArray().T[0]]
            sensor = cls._fromResponseFunctions(centers=None, names=names, responsess=responsess)
        else:
            fwhm = library.raster().metadataFWHM(required=True)
            sensor = cls._fromFWHM(centers=wavelengths, fwhms=fwhm)

        return sensor

    @staticmethod
    def _fromResponseFunctions(centers, names, responsess):
        '''
        Create instance from given lists of response function given by ``responsess``.

        :param centers: list of center wavelengths
        :type centers: List[float]
        :param names: list of waveband names
        :type names: List[str]
        :param responsess: list of response functions
        :type responsess: List[List[(float, float)]]
        :rtype: SensorDefinition

        '''
        if names is None:
            names = [None] * len(responsess)
        if centers is None:
            centers = [None] * len(responsess)

        assert len(centers) == len(names)
        assert isinstance(responsess, list)

        wavebandDefinitions = list()
        for responses, name, center in zip(responsess, names, centers):
            x, y = list(zip(*responses))
            valid = np.array(y) > 0.01
            if center is None:
                center = np.array(x)[valid][[0, -1]].mean()
            responsesValid = list(np.array(responses)[valid])
            wavebandDefinitions.append(WavebandDefinition(center=center,
                                                          fwhm=None,
                                                          responses=responsesValid,
                                                          name=name))

        return SensorDefinition(wavebandDefinitions=wavebandDefinitions)

    @staticmethod
    def _fromFWHM(centers, fwhms):
        '''
        Create instance from lists of center wavelengths and FWHMs.

        :param centers: list of center wavelengths
        :type centers: List[float]
        :param fwhms: list if FWHMs
        :type fwhms: List[float]
        :rtype: SensorDefinition
        '''

        assert len(centers) == len(fwhms)
        wavebandDefinitions = [WavebandDefinition.fromFWHM(center=center, fwhm=fwhm)
                               for center, fwhm in zip(centers, fwhms)]
        return SensorDefinition(wavebandDefinitions=wavebandDefinitions)

    @staticmethod
    def fromRaster(raster):
        '''Forwards :meth:`Raster.sensorDefinition`.'''
        assert isinstance(raster, Raster)
        return raster.sensorDefinition()

    def wavebandDefinition(self, index):
        '''Return :class:`WavebandDefinition` for band given by ``index``.'''
        wavebandDefinition = self._wavebandDefinitions[index]
        assert isinstance(wavebandDefinition, WavebandDefinition)
        return wavebandDefinition

    def wavebandDefinitions(self):
        '''Return iterator over all :class:`WavebandDefinition`'s.'''
        for index in range(self.wavebandCount()):
            yield self.wavebandDefinition(index=index)

    def wavebandCount(self):
        '''Return number of wavebands.'''
        return len(self._wavebandDefinitions)

    def plot(self, plotWidget=None, yscale=1., **kwargs):
        '''
        Return sensor definition plot.

        :param plotWidget: if None, a new plot widget is created, otherwise, the given ``plotWidget`` is used
        :type plotWidget: pyqtgraph.graphicsWindows.PlotWindow
        :param yscale: scale factor for y values
        :type yscale: float
        :param kwargs: passed to ``pyqtgraph.graphicsWindows.PlotWindow.plot``
        :rtype: pyqtgraph.graphicsWindows.PlotWindow

        :example:

        >>> plotWidget = SensorDefinition.fromPredefined(name='sentinel2').plot()

        .. image:: plots/sensorDefinition_plot.png

        '''

        import pyqtgraph as pg
        if plotWidget is None:
            plotWidget = pg.plot()

        for wavebandDefinition in self.wavebandDefinitions():
            wavebandDefinition.plot(plotWidget=plotWidget, yscale=yscale, **kwargs)

        return plotWidget

    def resampleRaster(self, filename, raster, minResponse=None, resampleAlg=RESAMPLE_LINEAR, **kwargs):
        '''
        Resample the given spectral ``raster``.

        :param filename: output path
        :type filename: str
        :param raster: spectral raster
        :type raster: hubflow.core.Raster
        :param minResponse: limits the wavelength region of the response filter function to wavelength with responses higher than ``minResponse``;
                            higher values speed up computation; 0.5 corresponds to the full width at half maximum region;
                            values greater 0.5 may lead to very inaccurate results
        :type minResponse: float
        :param resampleAlg: available resampling algorithms are linear interpolation between neighbouring wavelength
                            and response function filtering
        :type resampleAlg: enum(SensorDefinition.RESAMPLE_LINEAR, SensorDefinition.RESAMPLE_RESPONSE)
        :param kwargs: passed to hubflow.core.Applier
        :rtype: Union[hubflow.core.Raster, None]

        :example:

        >>> import enmapboxtestdata
        >>> sentinel2Sensor = SensorDefinition.fromPredefined(name='sentinel2')
        >>> enmapRaster = Raster(filename=enmapboxtestdata.enmap)
        >>> resampled = sentinel2Sensor.resampleRaster(filename='/vsimem/resampledLinear.bsq', raster=enmapRaster)
        >>> pixel = Pixel(x=0, y=0)
        >>> plotWidget = enmapRaster.plotZProfile(pixel=pixel, spectral=True, xscale=1000) # draw original enmap profile
        >>> plotWidget = resampled.plotZProfile(pixel=pixel, spectral=True, plotWidget=plotWidget) # draw resampled profile on top

        .. image:: plots/sensorDefinition_resampleRaster.png
        '''
        assert isinstance(raster, Raster)
        if resampleAlg is None:
            resampleAlg = self.RESAMPLE_LINEAR
        assert resampleAlg in self.RESAMPLE_OPTIONS
        sourceSensor = raster.sensorDefinition()
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('outraster', filename=filename)
        applier.apply(operatorType=_SensorDefinitionResampleRaster, raster=raster,
                      targetSensor=self, sourceSensor=sourceSensor, minResponse=minResponse, resampleAlg=resampleAlg)
        return Raster(filename=filename)

    def resampleProfiles(self, array, wavelength, wavelengthUnits, minResponse=None, resampleAlg=None, **kwargs):
        '''
        Resample a list of profiles given as a 2d ``array`` of size (profiles, bands).

        Implementation: the ``array``, together with the ``wavelength`` and ``wavelengthUnits`` metadata,
        is turned into a spectral raster, which is resampled using :class:~hubflow.core.SensorDefinition.resampleRaster``.

        :param array: list of profiles or 2d array of size (profiles, bands)
        :type array: Union[list, numpy.ndarray]
        :param wavelength: list of center wavelength of size (bands, )
        :type wavelength: List[float]
        :param wavelengthUnits: wavelength unit 'nanometers' | 'micrometers'
        :type wavelengthUnits: str
        :param minResponse: passed to :meth:`~hubflow.core.SensorDefinition.resampleRaster`
        :param resampleAlg: passed to :meth:`~hubflow.core.SensorDefinition.resampleRaster`
        :param kwargs: passed to :class:`~hubflow.core.SensorDefinition.resampleRaster`
        :rtype: numpy.ndarray

        :example:

        >>> import pyqtgraph as pg
        >>> import enmapboxtestdata
        >>> sentinel2Sensor = SensorDefinition.fromPredefined(name='sentinel2')
        >>> enmapRaster = Raster(filename=enmapboxtestdata.enmap)
        >>> enmapArray = enmapRaster.array().reshape((enmapRaster.shape()[0], -1)).T
        >>> resampled = sentinel2Sensor.resampleProfiles(array=enmapArray, wavelength=enmapRaster.metadataWavelength(), wavelengthUnits='nanometers')
        >>> index = 0 # select single profile
        >>> plotWidget = pg.plot(x=enmapRaster.metadataWavelength(), y=enmapArray[index]) # draw original enmap profile
        >>> plotWidget = plotWidget.plot(x=[wd.center() for wd in sentinel2Sensor.wavebandDefinitions()], y=resampled[index]) # draw resampled profile on top

        .. image:: plots/sensorDefinition_resampleProfiles.png
        '''
        array = np.array(array)
        assert array.ndim == 2
        samples, bands = array.shape
        assert len(wavelength) == bands

        rasterDataset = createRasterDatasetFromArray(array=np.atleast_3d(array.T),
                                                     filename='/vsimem/SensorDefinitionResampleInProfiles.bsq',
                                                     driver=ENVIBSQDriver())
        MetadataEditor.setBandCharacteristics(rasterDataset=rasterDataset,
                                              wavelength=wavelength,
                                              wavelengthUnits=wavelengthUnits)
        rasterDataset.flushCache()
        raster = Raster.fromRasterDataset(rasterDataset=rasterDataset)
        outraster = self.resampleRaster(filename='/vsimem/SensorDefinitionResampleOutProfiles.bsq',
                                        raster=raster, minResponse=minResponse, resampleAlg=resampleAlg, **kwargs)
        outarray = outraster.dataset().readAsArray().T[0]
        return outarray

class _SensorDefinitionResampleRaster(ApplierOperator):
    def ufunc(self, raster, targetSensor, sourceSensor, minResponse, resampleAlg):
        assert isinstance(targetSensor, SensorDefinition)
        assert isinstance(sourceSensor, SensorDefinition)
        self.targetSensor = targetSensor
        self.sourceSensor = sourceSensor
        self.raster = raster

        if minResponse is None:
            minResponse = 0.001
        self.minResponse = minResponse

        self.marray = self.flowMaskArray(name='raster', mask=raster.asMask(indices=[0]))

        # resample
        if resampleAlg == SensorDefinition.RESAMPLE_LINEAR:
            outarray = self.resampleWithLinearInterpolation()
        elif resampleAlg == SensorDefinition.RESAMPLE_RESPONSE:
            outarray = self.resampleWithResponseFunction()

        # mask
        if raster.dataset().noDataValue() is not None:
            outarray[:, np.logical_not(self.marray[0])] = raster.dataset().noDataValue()

        # write and set metadata
        outraster = self.outputRaster.raster(key='outraster')
        outraster.setArray(array=outarray)
        self.setFlowMetadataSensorDefinition(name='outraster', sensor=targetSensor)
        outraster.setNoDataValue(value=raster.dataset().noDataValue())

    def resampleWithResponseFunction(self):
        outarray = self.full(value=0, bands=self.targetSensor.wavebandCount(), dtype=np.float32)
        for outindex, wavebandDefinition in enumerate(self.targetSensor.wavebandDefinitions()):
            assert isinstance(wavebandDefinition, WavebandDefinition)
            weights = wavebandDefinition.resamplingWeights(sensor=self.sourceSensor)
            weightsSum = 0.

            for inindex, weight in enumerate(weights):
                if weight > self.minResponse:
                    weightsSum += weight
                    invalues = self.flowRasterArray(name='raster',
                                                   raster=self.raster,
                                                   indices=[inindex])[self.marray]
                    outarray[outindex][self.marray[0]] += weight * invalues
            if weightsSum == 0:  # if no source bands are inside the responsive region of the target band
                import warnings
                warnings.warn(Warning(
                    'target waveband ({}, from {} nm to {} nm) is outside the responsive region'.format(
                        wavebandDefinition.name(), wavebandDefinition.wavelengths()[0],
                        wavebandDefinition.wavelengths()[-1])))
                outarray[outindex] = np.nan
            else:
                outarray[outindex][self.marray[0]] /= weightsSum

        return outarray


    def resampleWithLinearInterpolation(self):
        outarray = self.full(value=0, bands=self.targetSensor.wavebandCount(), dtype=np.float32)
        incenters = [wd.center() for wd in self.sourceSensor.wavebandDefinitions()]
        outcenters = [wd.center() for wd in self.targetSensor.wavebandDefinitions()]

        for outindex, outcenter in enumerate(outcenters):
            if outcenter <= incenters[0]:
                indexA = indexB = 0
                wA = wB = 0.5
            elif outcenter >= incenters[-1]:
                indexA = indexB = len(incenters)-1
                wA = wB = 0.5
            else:
                for inindex, incenter in enumerate(incenters):
                    if incenter > outcenter:
                        indexA = inindex - 1
                        indexB = inindex
                        distanceA = np.abs(incenters[indexA]-outcenter)
                        distanceB = np.abs(incenters[indexB]-outcenter)
                        wA = 1. - distanceA / (distanceA + distanceB)
                        wB = 1. - wA
                        break

            inarrayA, inarrayB = self.flowRasterArray(name='raster', raster=self.raster, indices=[indexA, indexB])
            outarray[outindex][self.marray[0]] = inarrayA[self.marray[0]] * wA + inarrayB[self.marray[0]] * wB
        return outarray


class ENVISpectralLibrary(FlowObject):
    '''Class for managing ENVI Spectral Library files.'''

    def __init__(self, filename):
        '''Create an instance for given ``filename``.'''
        self._filename = filename

    def __getstate__(self):
        return OrderedDict([('filename', self.filename())])

    def filename(self):
        '''Return the filename.'''
        return self._filename

    def raster(self, transpose=True):
        '''
        Return a :class:`~hubflow.core.Raster` pointing to the library's binary file.

        If ``transpose=False`` the binary raster is a single band, where profiles are arranged along the y axis and wavebands along the x axis.
        If ``transpose=True`` profiles are still arranged along the y axis, but wavebands are transpose into the z axis,
        which matches the natural order of spectral raster files, and enables the direct application of various
        raster processing algorithms to library profiles.

        :param transpose: whether or not to transpose the profiles from [1, profiles, bands] to [bands, profiles, 1] order.
        :type transpose: bool
        :rtype: hubflow.core.Raster

        :example:

        >>> import enmapboxtestdata
        >>> # as single column multiband raster
        >>> ENVISpectralLibrary(filename=enmapboxtestdata.speclib).raster().shape()
        (177, 75, 1)
        >>> # as single band raster (original ENVI format)
        >>> ENVISpectralLibrary(filename=enmapboxtestdata.speclib).raster(transpose=False).shape()
        (1, 75, 177)
        '''

        filename = r'/vsimem/{filename}{transpose}.vrt'.format(filename=self.filename(),
                                                               transpose='.transposed' if transpose else '')
        try:
            raster = Raster(filename=filename)
            raster.dataset()  # try opening
        except (RuntimeError, errors.InvalidGDALDatasetError):
            metadata = ENVI.readHeader(filenameHeader=ENVI.findHeader(filenameBinary=self.filename()))
            gdalType = ENVI.gdalType(enviType=int(metadata['data type']))
            bytes = ENVI.typeSize(enviType=int(metadata['data type']))
            byteOrder = ['LSB', 'MSB'][int(metadata['byte order'])]

            profiles = int(metadata['lines'])
            bands = int(metadata['samples'])
            options = 'subclass=VRTRawRasterBand\n' \
                      'SourceFilename={SourceFilename}\n' \
                      'ByteOrder={ByteOrder}\n'

            if transpose:
                rasterDataset = RasterDriver(name='VRT').create(grid=PseudoGrid(size=Size(x=1, y=profiles)),
                                                                bands=0, gdalType=gdalType, filename=filename)

                options += 'ImageOffset={ImageOffset}\n' \
                           'PixelOffset={PixelOffset}\n' \
                           'LineOffset={LineOffset}'

                for band in range(bands):
                    rasterDataset.gdalDataset().AddBand(datatype=gdalType,
                                                        options=options.format(SourceFilename=self.filename(),
                                                                               ByteOrder=byteOrder,
                                                                               ImageOffset=band * bytes,
                                                                               PixelOffset=bands * bytes,
                                                                               LineOffset=bands * bytes).split('\n'))

            else:
                rasterDataset = RasterDriver(name='VRT').create(grid=PseudoGrid(size=Size(x=bands, y=profiles)),
                                                                bands=0, gdalType=gdalType, filename=filename)

                rasterDataset.gdalDataset().AddBand(datatype=gdalType,
                                                    options=options.format(SourceFilename=self.filename(),
                                                                           ByteOrder=byteOrder).split('\n'))

            for key in ['file compression', 'band names']:
                metadata.pop(key=key, default=None)

            rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')

            # check for attribute table in csv file
            filenameCSV = ENVI.findHeader(filenameBinary=self.filename(), ext='.csv')
            if filenameCSV is not None:
                array = np.genfromtxt(filenameCSV, delimiter=',', dtype=np.str)
                keys = list(array[0])
                values = array[1:].T
                for i, (key, value) in enumerate(zip(keys, values)):
                    if i == 0:
                        key = 'spectra names'
                    value = [str(v) for v in value]
                    rasterDataset.setMetadataItem(key=key, value=value, domain='CSV')

                # check for classification attribute definition files

                for key in keys:
                    key2 = key.replace(' ', '_')
                    filenameClassDefinition = filenameCSV.replace('.csv', '.{}.classdef.csv'.format(key2))
                    if exists(filenameClassDefinition):
                        array = np.genfromtxt(filenameClassDefinition, delimiter=';', dtype=np.str)
                        names = list(array[1:, 0])
                        colors = list(np.array([s[s.find('(')+1: s.find(')')].split(',') for s in array[1:, 1]]).flatten())
                        rasterDataset.setMetadataItem(key='{} class names'.format(key), value=names, domain='CSV')
                        rasterDataset.setMetadataItem(key='{} class lookup'.format(key), value=colors, domain='CSV')

            rasterDataset.flushCache()
            rasterDataset.close()
            raster = Raster(filename=filename)

        return raster

    @staticmethod
    def fromRaster(filename, raster):
        '''
        Create instance from given ``raster``.

        :param filename: output path
        :type filename:
        :param raster: input raster
        :type raster: hubflow.core.Raster
        :return:
        :rtype: hubflow.core.ENVISpectralLibrary

        :example:

        >>> import enmapboxtestdata, tempfile, os
        >>> raster = ENVISpectralLibrary(filename=enmapboxtestdata.speclib).raster()
        >>> library = ENVISpectralLibrary.fromRaster(filename='/vsimem/speclib.sli', raster=raster)
        >>> library
        ENVISpectralLibrary(filename=/vsimem/speclib.sli)
        '''
        assert isinstance(raster, Raster)
        bands = raster.dataset().zsize()
        array = raster.dataset().readAsArray().reshape(bands, -1).T[None]
        rasterDataset = createRasterDatasetFromArray(array=array, grid=PseudoGrid.fromArray(array=array),
                                                     filename=filename, driver=ENVIBSQDriver())
        metadata = raster.dataset().metadataDomain(domain='ENVI')
        for key in ['file compression']:
            metadata.pop(key, None)
        rasterDataset.setMetadataDomain(metadataDomain=metadata, domain='ENVI')
        rasterDataset.band(0).setDescription('Spectral Library')
        rasterDataset.flushCache()
        rasterDataset.close()

        # fix header

        # - delete PAM header
        try:
            remove(filename + '.aux.xml')
        except:
            pass

        # - rewrite ENVI header
        try:
            filenameHeader = ENVI.findHeader(filenameBinary=filename)
            metadata = ENVI.readHeader(filenameHeader=filenameHeader)
            metadata['file type'] = 'ENVI Spectral Library'
            for key in ['file compression', 'coordinate system string', 'map info', 'projection_info', 'x start',
                        'y start']:
                metadata.pop(key, None)
            ENVI.writeHeader(filenameHeader=filenameHeader, metadata=metadata)
        except:
            pass
        return ENVISpectralLibrary(filename=filename)


class RasterStack(FlowObject):
    '''
    Class for managing virtual raster stacks that can be used inside an :class:`~hubflow.core.Applier`.

    :example:

    Stack two rasters virtually and read on-the-fly stacked data inside Applier.

    >>> raster = RasterStack(rasters=[Raster.fromArray(array=[[[1, 1], [1, 1]]], filename='/vsimem/raster1.bsq'),
    ...                               Raster.fromArray(array=[[[2, 2], [2, 2]]], filename='/vsimem/raster2.bsq')])
    >>>
    >>> applier = Applier(progressBar=SilentProgressBar())
    >>> applier.setFlowRaster(name='stack', raster=raster)
    >>>
    >>> class MyOperator(ApplierOperator):
    ...     def ufunc(self, raster):
    ...         array = self.flowRasterArray(name='stack', raster=raster)
    ...         return array
    >>>
    >>> applier.apply(operatorType=MyOperator, raster=raster) # doctest: +NORMALIZE_WHITESPACE
    [array([[[1, 1],
             [1, 1]],
    <BLANKLINE>
            [[2, 2],
             [2, 2]]])]
    '''

    def __init__(self, rasters):
        self._rasters = rasters

    def __getstate__(self):
        return OrderedDict([('rasters', list(self.rasters()))])

    def raster(self, index):
        '''Return raster at given ``index``'''
        assert isinstance(self._rasters[index], Raster)
        return self._rasters[index]

    def rasters(self):
        '''Return iterator over all raster.'''
        for i in range(len(self._rasters)):
            yield self.raster(i)


class Mask(Raster):
    def __init__(self, filename, noDataValues=None, minOverallCoverage=0.5, indices=None, invert=False):
        '''
        Class for managing raster mask maps.

        :param filename: input path
        :type filename: str
        :param noDataValues: if not None, it overwrites the band no data values given by the raster.
        :type noDataValues: List[floats] or None
        :param minOverallCoverage: in case of resampling, values between 0 (False) and 1 (True) can ocure,
                                   minOverallCoverage is the threshold at which those "soft" mask values are categoriest into True and False
        :type minOverallCoverage: float
        :param indices: if not None, only the bands corresponding to the given indices are used as mask
        :type indices: List[int]
        :param invert: whether to invert the mask
        :type invert: bool

        :examples:

        If a raster is interpreted as a mask, all pixel that contain a no data value in at leased one band are interpreted as False.

        >>> raster = Raster.fromArray(array=[[[-99, 0], [1, 2]], [[-99, 0], [1, 0]]], noDataValues=[-99, -99], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[-99,   0],
                [  1,   2]],
        <BLANKLINE>
               [[-99,   0],
                [  1,   0]]])

        >>> Mask(filename=raster.filename()).array()
        array([[[0, 1],
                [1, 1]]], dtype=uint8)

        Masks can be inverted.
        >>> Mask(filename=raster.filename(), invert=True).array()
        array([[[1, 0],
                [0, 0]]], dtype=uint8)

        If no data values are not defined, it defaults to zero in all bands.

        >>> rasterWithoutNoData = Raster.fromArray(array=[[[-99, 0], [1, 2]], [[-99, 0], [1, 0]]], filename='/vsimem/rasterWithoutNoData.bsq')
        >>> Mask(filename=rasterWithoutNoData.filename()).array()
        array([[[1, 0],
                [1, 0]]], dtype=uint8)

        Missing no data values can be passed to the mask constructor.

        >>> Mask(filename=rasterWithoutNoData.filename(), noDataValues=[-99, -99]).array()
        array([[[0, 1],
                [1, 1]]], dtype=uint8)

        Pick a single band as mask from a multiband raster.

        >>> Mask(filename=rasterWithoutNoData.filename(), indices=[0]).array()
        array([[[1, 0],
                [1, 1]]], dtype=uint8)
        >>> Mask(filename=rasterWithoutNoData.filename(), indices=[1]).array()
        array([[[1, 0],
                [1, 0]]], dtype=uint8)

        '''
        Raster.__init__(self, filename)
        if noDataValues is None:
            noDataValues = self.dataset().noDataValues(default=0)
        self._noDataValues = noDataValues
        self._minOverallCoverage = float(minOverallCoverage)
        self._indices = indices
        self._invert = invert

    def noDataValues(self):
        '''Return band no data values.'''
        assert isinstance(self._noDataValues, list)
        return self._noDataValues

    def minOverallCoverage(self):
        '''Return minimal overall coverage threshold.'''
        return self._minOverallCoverage

    def indices(self):
        '''Return band subset indices.'''
        return self._indices

    def invert(self):
        '''Whether to invert the mask.'''
        return self._invert

    @staticmethod
    def fromVector(filename, vector, grid, **kwargs):
        '''Create a mask from a vector.

        :param filename: output path
        :type filename:
        :param vector: input vector
        :type vector: hubflow.core.Vector
        :param grid:
        :type grid: hubdc.core.Grid
        :param kwargs:
        :type kwargs:
        :return:
        :rtype: hubflow.core.Mask

        :example:

        >>> import enmapboxtestdata
        >>> vector = Vector(filename=enmapboxtestdata.landcover, initValue=0)
        >>> grid = Raster(filename=enmapboxtestdata.enmap).grid()
        >>> mask = Mask.fromVector(filename='/vsimem/mask.bsq', vector=vector, grid=grid)
        >>> plotWidget = mask.plotSinglebandGrey()

        .. image:: plots/mask_fromVector.png
        '''
        return Raster.fromVector(filename=filename, vector=vector, grid=grid, **kwargs).asMask()

    @staticmethod
    def fromRaster(filename, raster, initValue=False, true=(), false=(),
                   invert=False, aggregateFunction=None, **kwargs):
        '''
        Returns a mask created from a raster map, where given lists of ``true`` and ``false`` values and value ranges
        are used to define True and False regions.

        :param filename: output path
        :type filename:
        :param raster: input raster
        :type raster: hubflow.core.Raster
        :param initValue: initial fill value, default is False
        :type initValue: bool
        :param true: list of forground numbers and ranges
        :type true: List[number or range]
        :param false: list of forground numbers and ranges
        :type false: List[number or range]
        :param invert: whether to invert the mask
        :type invert: bool
        :param aggregateFunction: aggregation function (e.g. numpy.all or numpy.any) to reduce multiband rasters to a single band mask;
                                  the default is to not reduce and returning a multiband mask
        :type aggregateFunction: func
        :param kwargs: passed to hubflow.core.Applier
        :type kwargs:
        :return: hubflow.core.Mask
        :rtype:

        :example:

        >>> raster = Raster.fromArray(array=[[[-99, 1, 2, 3, 4, 5]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[-99,   1,   2,   3,   4,   5]]])
        >>> # values 1, 2, 3 are True
        >>> Mask.fromRaster(raster=raster, true=[1, 2, 3], filename='/vsimem/mask.bsq').array()
        array([[[0, 1, 1, 1, 0, 0]]], dtype=uint8)
        >>> # value range 1 to 4 is True
        >>> Mask.fromRaster(raster=raster, true=[range(1, 4)], filename='/vsimem/mask.bsq').array()
        array([[[0, 1, 1, 1, 1, 0]]], dtype=uint8)
        >>> # all values are True, but -99
        >>> Mask.fromRaster(raster=raster, initValue=True, false=[-99], filename='/vsimem/mask.bsq').array()
        array([[[0, 1, 1, 1, 1, 1]]], dtype=uint8)

        Different aggregations over multiple bands

        >>> raster = Raster.fromArray(array=[[[0, 0, 1, 1]], [[0, 1, 0, 1]]], filename='/vsimem/raster.bsq')
        >>> raster.array()
        array([[[0, 0, 1, 1]],
        <BLANKLINE>
               [[0, 1, 0, 1]]])
        >>> # no aggregation
        >>> Mask.fromRaster(raster=raster, true=[1], filename='/vsimem/mask.bsq').readAsArray()
        array([[[0, 0, 1, 1]],
        <BLANKLINE>
               [[0, 1, 0, 1]]], dtype=uint8)
        >>> # True if all pixel profile values are True
        >>> def aggregate(array): return np.all(array, axis=0)
        >>> Mask.fromRaster(raster=raster, true=[1], aggregateFunction=aggregate, filename='/vsimem/mask.bsq').readAsArray()
        array([[[0, 0, 0, 1]]], dtype=uint8)

        >>> # True if any pixel profile values are True
        >>> def aggregate(array): return np.any(array, axis=0)
        >>> Mask.fromRaster(raster=raster, true=[1], aggregateFunction=aggregate, filename='/vsimem/mask.bsq').readAsArray()
        array([[[0, 1, 1, 1]]], dtype=uint8)

        '''
        assert isinstance(raster, Raster)
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('mask', filename=filename)
        applier.apply(operatorType=_MaskFromRaster, raster=raster, initValue=initValue,
                      true=true, false=false, invert=invert,
                      aggregateFunction=aggregateFunction)
        return Mask(filename=filename)

    def resample(self, filename, grid, **kwargs):
        '''
        Returns a resampled mask of itself into the given ``grid``.

        :param filename: output path
        :type filename: str
        :param grid: output grid
        :type grid: hubdc.core.Grid
        :param kwargs: passed to hubflow.core.Applier
        :type kwargs:
        :return:
        :rtype: hubflow.core.Mask

        :example:

        >>> mask = Mask.fromArray(array=[[[0, 1]]], filename='/vsimem/mask.bsq')
        >>> grid = Grid(extent=mask.grid().spatialExtent(), resolution=mask.grid().resolution().zoom(factor=(2, 1)))
        >>> mask.resample(grid=grid, filename='/vsimem/resampled.bsq').array()
        array([[[0, 0, 1, 1]]], dtype=uint8)
        '''
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowMask('inmask', mask=self)
        applier.setOutputRaster('outmask', filename=filename)
        applier.apply(operatorType=_MaskResample, mask=self)
        return Mask(filename=filename, minOverallCoverage=self.minOverallCoverage())


class _MaskResample(ApplierOperator):
    def ufunc(self, mask):
        array = self.flowMaskArray('inmask', mask=mask)
        self.outputRaster.raster(key='outmask').setArray(array=array)


class _MaskFromRaster(ApplierOperator):
    def ufunc(self, raster, initValue, true, false, invert,
              aggregateFunction=None):
        array = self.flowRasterArray('raster', raster=raster)
        marray = np.full_like(array, fill_value=initValue, dtype=np.bool)

        for value in true:
            if isinstance(value, (int, float)):
                marray[array == value] = True
            elif isinstance(value, range):
                assert value.step == 1
                marray[(array >= value.start) * (array <= value.stop)] = True

        for value in false:
            if isinstance(value, (int, float)):
                marray[array == value] = False
            elif isinstance(value, range):
                assert value.step == 1
                marray[(array >= value.start) * (array <= value.stop)] = False

        if invert:
            marray = np.logical_not(marray)

        if aggregateFunction is not None:
            marray = aggregateFunction(marray)
            assert (marray.ndim == 3 and len(marray) == 1) or marray.ndim == 2

        self.outputRaster.raster(key='mask').setArray(array=marray)


class Vector(Map):
    '''Class for managing vector maps. See also :class:`~VectorMask`, :class:`~VectorClassification`'''

    def __init__(self, filename, layer=0, initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                 filterSQL=None, dtype=np.float32, noDataValue=None):

        '''
        Create an instance from the vector located at ``filename``.

        :param filename: input path
        :type filename: str
        :param layer: layer index or name
        :type layer: int or str
        :param initValue: rasterization option - values to pre-initialize the output band
        :type initValue: number
        :param burnValue: rasterization option - fixed value to burn into output band for all objects; excusive with burnAttribute.
        :type burnValue: number
        :param burnAttribute: rasterization option - identifies an attribute field on the features to be used for a burn-in value; exclusive with burnValue
        :type burnAttribute: str
        :param allTouched: rasterization option - whether to enable the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :type allTouched: bool
        :param filterSQL: rasterization option - SQL filter statement to apply to the source dataset
        :type filterSQL: str
        :param dtype: rasterization option - output numpy data type
        :type dtype: type
        :param noDataValue: rasterization option - no data value
        :type noDataValue: None or float
        '''
        self._filename = filename
        self._layer = layer
        self._initValue = initValue
        self._burnValue = burnValue
        self._burnAttribute = burnAttribute
        self._allTouched = allTouched
        self._filterSQL = filterSQL
        self._dtype = dtype
        self._noDataValue = noDataValue
        self._vectorDataset = None

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('layer', self.layer()),
                            ('initValue', self.initValue()),
                            ('burnValue', self.burnValue()),
                            ('burnAttribute', self.burnAttribute()),
                            ('allTouched', self.allTouched()),
                            ('filterSQL', self.filterSQL()),
                            ('dtype', self.dtype()),
                            ('noDataValue', self.noDataValue())])

    def filename(self):
        '''Return filename.'''
        return self._filename

    def layer(self):
        '''Return layer name or index'''
        return self._layer

    def initValue(self):
        '''Return rasterization initialization value.'''
        return self._initValue

    def burnValue(self):
        '''Return rasterization burn value.'''
        return self._burnValue

    def burnAttribute(self):
        '''Return rasterization burn attribute.'''
        return self._burnAttribute

    def allTouched(self):
        '''Return rasterization all touched option.'''
        return self._allTouched

    def filterSQL(self):
        '''Return rasterization SQL filter statement.'''
        return self._filterSQL

    def dtype(self):
        '''Return rasterization data type.'''
        return self._dtype

    def noDataValue(self, default=None):
        '''Return rasterization no data value.'''
        if self._noDataValue is None:
            return default
        return self._noDataValue

    def dataset(self):
        '''Return hubdc.core.VectorDataset object.'''
        if self._vectorDataset is None:
            self._vectorDataset = openVectorDataset(self.filename(), layerNameOrIndex=self.layer())
        assert isinstance(self._vectorDataset, VectorDataset)
        return self._vectorDataset

    #def _initPickle(self):
    #    self._vectorDataset = None

    @classmethod
    def fromVectorDataset(cls, vectorDataset, **kwargs):
        '''
        Create instance from hubdc.core.VectorDataset.

        :param vectorDataset:
        :type vectorDataset: hubdc.core.VectorDataset
        :param kwargs: passed to cls.__init__ constructor
        :type kwargs:
        :return:
        :rtype: hubflow.core.Vector

        :example:

        >>> import enmapboxtestdata
        >>> vectorDataset = Vector(filename=enmapboxtestdata.landcover).dataset()
        >>> Vector.fromVectorDataset(vectorDataset=vectorDataset) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Vector(filename=...LandCov_BerlinUrbanGradient.shp, layer=0, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, dtype=<class 'numpy.float32'>, noDataValue=None)
        '''
        assert isinstance(vectorDataset, VectorDataset)
        vector = cls(vectorDataset.filename(), **kwargs)
        vector._vectorDataset = vectorDataset
        return vector

    @classmethod
    def fromPoints(cls, filename, points, projection):
        '''
        Create instance from given points.

        :param filename: output path
        :type filename: str
        :param points: list of points
        :type points: List[Tuple[int, int]]
        :param projection:
        :type projection: hubdc.core.Projection
        :return:
        :rtype: hubflow.core.Vector

        :example:

        >>> vector = Vector.fromPoints(points=[(-1, -1), (1, 1)], filename=join(tempfile.gettempdir(), 'vector.shp'), projection=Projection.WGS84())
        >>> grid = Grid(extent=Extent(xmin=-1.5, xmax=1.5, ymin=-1.5, ymax=1.5), resolution=1, projection=Projection.WGS84())
        >>> raster = Raster.fromVector(filename='/vsimem/raster.bsq', vector=vector, grid=grid)
        >>> raster.array()
        array([[[ 0.,  0.,  1.],
                [ 0.,  0.,  0.],
                [ 1.,  0.,  0.]]], dtype=float32)
        '''
        vectorDataset = VectorDataset.fromPoints(points=points, filename=filename, projection=projection)
        return Vector.fromVectorDataset(vectorDataset=vectorDataset)

    @classmethod
    def fromRandomPointsFromMask(cls, filename, mask, n, **kwargs):
        '''
        Draw random locations from raster mask and return as point vector.

        :param filename: output path
        :type filename: str
        :param mask: input mask
        :type mask: hubflow.core.Mask
        :param n: number of points
        :type n: int
        :param kwargs: passed to hubflow.core.Applier
        :type kwargs:
        :return:
        :rtype: hubflow.core.Vector

        :example:

        Create a mask, ...

        >>> import enmapboxtestdata
        >>> grid = Raster(filename=enmapboxtestdata.enmap).grid()
        >>> mask = Mask.fromVector(filename='/vsimem/mask.bsq',
        ...                        vector=Vector(filename=enmapboxtestdata.landcover), grid=grid)
        >>> mask.plotSinglebandGrey()

        .. image:: plots/mask_fromVector.png

        ... draw 10 random locations, ...

        >>> points = Vector.fromRandomPointsFromMask(mask=mask, n=10, filename=join(tempfile.gettempdir(), 'vector.shp'))

        ... and rasterize the result into the grid of the mask.

        >>> Mask.fromVector(filename='/vsimem/mask.bsq', vector=points, grid=grid).plotSinglebandGrey()

        .. image:: plots/vector_fromRandomPointsFromMask.png

        '''
        applier = Applier(**kwargs)
        applier.setFlowMask('mask', mask=mask)
        applier.apply(operatorType=_VectorFromRandomPointsFromMask, mask=mask, n=n, filename=filename)
        return Vector(filename=filename)

    @classmethod
    def fromRandomPointsFromClassification(cls, filename, classification, n, **kwargs):
        '''
        Draw stratified random locations from raster classification and return as point vector.

        :param filename: output path
        :type filename: str
        :param classification: input classification used as stratification
        :type classification:
        :param n: list of number of points, one for each class
        :type n: List[int]
        :param kwargs: passed to hubflow.core.Applier
        :type kwargs:
        :return:
        :rtype: hubflow.core.Vector

        :example:

        Create classification from landcover polygons, ...

        >>> import enmapboxtestdata
        >>> grid = Raster(filename=enmapboxtestdata.enmap).grid()
        >>> vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
        ...                                             classAttribute=enmapboxtestdata.landcoverAttributes.Level_2_ID,
        ...                                             classDefinition=ClassDefinition(colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup),
        ...                                             oversampling=5)
        >>> classification = Classification.fromClassification(filename='/vsimem/classification.bsq', classification=vectorClassification, grid=grid)
        >>> classification.plotCategoryBand()

        .. image:: plots/classification_fromClassification.png

        ... draw 10 random locations from each class, ...

        >>> points = Vector.fromRandomPointsFromClassification(classification=classification, n=[10]*6, filename=join(tempfile.gettempdir(), 'vector.shp'))

        ... apply those points as mask to the original classification

        >>> labels = classification.applyMask(filename='/vsimem/labels.bsq', mask=points)
        >>> labels.plotCategoryBand()

        .. image:: plots/classification_applyMask.png

        '''
        applier = Applier(**kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.apply(operatorType=_VectorFromRandomPointsFromClassification, classification=classification, n=n,
                      filename=filename)
        return Vector(filename=filename)

    def uniqueValues(self, attribute, spatialFilter=None):
        '''
        Returns unique values for given attribute.

        :param attribute:
        :type attribute: str
        :param spatialFilter: optional spatial filter
        :type spatialFilter: hubdc.core.SpatialGeometry
        :return:
        :rtype: List

        :example:

        >>> import enmapboxtestdata
        >>> vector = Vector(filename=enmapboxtestdata.landcover)
        >>> vector.uniqueValues(attribute=enmapboxtestdata.landcoverAttributes.Level_2)
        ['Low vegetation', 'Other', 'Pavement', 'Roof', 'Soil', 'Tree']

        >>> spatialFilter = SpatialExtent(xmin=384000, xmax=384800,
        ...                               ymin=5818000, ymax=5819000,
        ...                               projection=vector.projection()).geometry()
        >>> spatialFilter # doctest: +ELLIPSIS
        SpatialGeometry(wkt='POLYGON ((384000 5819000 0,384800 5819000 0,384800 5818000 0,384000 5818000 0,384000 5819000 0))', projection=Projection(wkt=PROJCS["WGS_1984_UTM_Zone_33N", ..., AUTHORITY["EPSG","32633"]]))
        >>> vector.uniqueValues(attribute=enmapboxtestdata.landcoverAttributes.Level_2,
        ...                     spatialFilter=spatialFilter)
        ['Low vegetation', 'Pavement', 'Roof', 'Tree']
        '''
        vector = openVectorDataset(filename=self.filename(), layerNameOrIndex=self.layer())
        layer = vector.ogrLayer()
        layer.SetAttributeFilter(self.filterSQL())
        values = OrderedDict()
        if spatialFilter is not None:
            assert isinstance(spatialFilter, SpatialGeometry)
            spatialFilterReprojected = spatialFilter.reproject(targetProjection=vector.projection())
            layer.SetSpatialFilter(spatialFilterReprojected.ogrGeometry())
        for feature in layer:
            values[feature.GetField(attribute)] = None
        return list(values.keys())

    def spatialExtent(self):
        '''
        Returns the spatial extent.

        :return:
        :rtype: hubdc.core.SpatialExtent

        :example:

        >>> import enmapboxtestdata
        >>> Vector(filename=enmapboxtestdata.landcover).spatialExtent() # doctest: +ELLIPSIS
        SpatialExtent(xmin=383918.24389999924, xmax=384883.2196000004, ymin=5815685.854300001, ymax=5818407.0616999995, projection=Projection(wkt=PROJCS["WGS_1984_UTM_Zone_33N", GEOGCS["GCS_WGS_1984", DATUM["WGS_1984", SPHEROID["WGS_84",6378137,298.257223563]], PRIMEM["Greenwich",0], UNIT["Degree",0.017453292519943295], AUTHORITY["EPSG","4326"]], ..., AUTHORITY["EPSG","32633"]]))
        '''
        return self.dataset().spatialExtent()

    def projection(self):
        '''
        Returns the projection.

        :return:
        :rtype: hubdc.core.Projection

        :example:

        >>> import enmapboxtestdata
        >>> Vector(filename=enmapboxtestdata.landcover).projection() # doctest: +ELLIPSIS
        Projection(wkt=PROJCS["WGS_1984_UTM_Zone_33N", GEOGCS["GCS_WGS_1984", DATUM["WGS_1984", SPHEROID["WGS_84",6378137,298.257223563]], PRIMEM["Greenwich",0], UNIT["Degree",0.017453292519943295], AUTHORITY["EPSG","4326"]], PROJECTION["Transverse_Mercator"], PARAMETER["latitude_of_origin",0], PARAMETER["central_meridian",15], PARAMETER["scale_factor",0.9996], PARAMETER["false_easting",500000], PARAMETER["false_northing",0], UNIT["Meter",1], AUTHORITY["EPSG","32633"]])
        '''
        return self.dataset().projection()

    def grid(self, resolution):
        '''
        Returns the grid for the given ``resolution``.

        :param resolution:
        :type resolution: hubdc.core.Resolution
        :return:
        :rtype: hubdc.core.Grid

        :example:

        >>> import enmapboxtestdata
        >>> Vector(filename=enmapboxtestdata.landcover).grid(resolution=30) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Grid(extent=Extent(xmin=383918.24389999924, xmax=384878.24389999924,
                           ymin=5815685.854300001, ymax=5818415.854300001),
             resolution=Resolution(x=30.0, y=30.0),
             projection=Projection(wkt=PROJCS["WGS_1984_UTM_Zone_33N", GEOGCS["GCS_WGS_1984", DATUM["WGS_1984", SPHEROID["WGS_84",6378137,298.257223563]], PRIMEM["Greenwich",0], UNIT["Degree",0.017453292519943295], AUTHORITY["EPSG","4326"]], ..., AUTHORITY["EPSG","32633"]])
        '''
        return Grid(extent=self.spatialExtent(), resolution=resolution)


class _VectorFromRandomPointsFromMask(ApplierOperator):
    def ufunc(self, mask, n, filename):
        array = self.flowMaskArray('mask', mask=mask)
        xmap = self.subgrid().xMapCoordinatesArray()[array[0]]
        ymap = self.subgrid().yMapCoordinatesArray()[array[0]]
        return xmap, ymap

    @staticmethod
    def aggregate(blockResults, grid, mask, n, filename):
        assert isinstance(grid, Grid)
        xmap = np.concatenate([result[0] for result in blockResults])
        ymap = np.concatenate([result[1] for result in blockResults])
        indicis = np.arange(0, len(xmap), 1)
        indicis = np.random.choice(indicis, size=n, replace=False)
        xmap, ymap = xmap[indicis], ymap[indicis]

        # Create the output vector
        driver = VectorDriver.fromFilename(filename=filename)
        driver.prepareCreation(filename)
        ds = driver.ogrDriver().CreateDataSource(filename)
        srs = grid.projection().osrSpatialReference()
        layer = ds.CreateLayer('random_points', srs, ogr.wkbPoint)

        for x, y in zip(xmap, ymap):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(x, y)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            layer.CreateFeature(feature)

        layer = None
        ds = None


class _VectorFromRandomPointsFromClassification(ApplierOperator):
    def ufunc(self, classification, n, filename):
        array = self.flowClassificationArray('classification', classification=classification)
        valid = array != 0
        xmap = self.subgrid().xMapCoordinatesArray()[valid[0]]
        ymap = self.subgrid().yMapCoordinatesArray()[valid[0]]
        id = array[valid]
        return xmap, ymap, id

    @staticmethod
    def aggregate(blockResults, grid, classification, n, filename):
        assert isinstance(grid, Grid)
        assert len(n) == classification.classDefinition().classes(), 'n must be a list with length of number of classes'
        xmap = np.concatenate([result[0] for result in blockResults])
        ymap = np.concatenate([result[1] for result in blockResults])
        id = np.concatenate([result[2] for result in blockResults])
        indicis = np.arange(0, len(xmap), 1)

        indicisList = list()
        for i, ni in enumerate(n):
            indicisi = indicis[id == i + 1]
            ni = min(ni, len(indicisi))
            indicisi = np.random.choice(indicisi, size=ni, replace=False)
            indicisList.append(indicisi)

        indicis = np.concatenate(indicisList)
        xmap, ymap = xmap[indicis], ymap[indicis]

        # Create the output vector
        driver = VectorDriver.fromFilename(filename=filename)
        driver.prepareCreation(filename)

        ds = driver.ogrDriver().CreateDataSource(filename)
        srs = grid.projection().osrSpatialReference()
        layer = ds.CreateLayer('random_points', srs, ogr.wkbPoint)

        for x, y in zip(xmap, ymap):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(x, y)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(point)
            layer.CreateFeature(feature)

        layer = None
        ds = None


class VectorMask(Vector):
    '''Class for managing vector masks.'''

    def __init__(self, filename, invert=False, **kwargs):
        '''
        Create new instace.

        :param filename: input path
        :type filename: str
        :param invert: whether to invert the mask
        :type invert: bool
        :param kwargs: passed to Vector
        :type kwargs: Dict
        '''
        Vector.__init__(self, filename=filename, **kwargs)
        self._kwargs = kwargs
        self._invert = invert

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('invert', self.invert())]
                           + list(self.kwargs().items()))

    def invert(self):
        'Returns whether to invert the mask.'
        return self._invert

    def kwargs(self):
        'Returns additional keyword arguments.'
        return self._kwargs

class VectorClassification(Vector):
    '''Class for manaing vector classifications.'''

    def __init__(self, filename, classAttribute, classDefinition=None, layer=0, minOverallCoverage=0.5,
                 minDominantCoverage=0.5, dtype=np.uint8, oversampling=1):
        '''
        Creates a new instance.

        :param filename: input path
        :type filename: str
        :param classDefinition: if not provided, the namber of classes is assumed to be the largest value in the class attribute
                                with generic class names and random class colors
        :type classDefinition: hubflow.core.ClassDefinition
        :param classAttribute: numeric attribute with class ids from 1 to number of classes
        :type classAttribute: str
        :param layer: input layer name or index
        :type layer: int or str
        :param minOverallCoverage: in case of resampling, pixels that are not fully covered can ocure,
                                   minOverallCoverage is the threshold under which those pixels are rejected (i.e. set to unclassified)
        :type minOverallCoverage: float
        :param minDominantCoverage: in case of resampling, pixels that are not fully covered by a single class can ocure,
                                   minDominantCoverage is the threshold under which "not pure enought" pixels are rejected (i.e. set to unclassified)
        :type minDominantCoverage: float
        :param dtype: numpy datatype
        :type dtype: type
        :param oversampling: factor by which the target resolution is oversampled before aggregated back
        :type oversampling: int

        :example:

        >>> import enmapboxtestdata
        >>> classDefinition = ClassDefinition(names=['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other'],
        ...                                   colors=[(230, 0, 0),   (156, 156, 156),   (152, 230, 0),   (38, 115, 0),   (168, 112, 0), (245, 245, 122)])
        >>> vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover, classAttribute='Level_2_ID', classDefinition=classDefinition)
        >>> vectorClassification # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        VectorClassification(filename=...LandCov_BerlinUrbanGradient.shp, classDefinition=ClassDefinition(classes=6, names=['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other'], colors=['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#f5f57a']), classAttribute=Level_2_ID, minOverallCoverage=0.5, minDominantCoverage=0.5, oversampling=1)

        '''

        Vector.__init__(self, filename=filename, layer=layer, burnAttribute=classAttribute, dtype=dtype)

        if classDefinition is None:
            classDefinition = ClassDefinition(classes=max(self.uniqueValues(attribute=classAttribute)))

        assert isinstance(classDefinition, ClassDefinition)
        self._classDefinition = classDefinition
        self._minOverallCoverage = float(minOverallCoverage)
        self._minDominantCoverage = float(minDominantCoverage)
        self._oversampling = oversampling

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('classDefinition', self.classDefinition()),
                            ('classAttribute', self.classAttribute()),
                            ('minOverallCoverage', self.minOverallCoverage()),
                            ('minDominantCoverage', self.minDominantCoverage()),
                            ('oversampling', self.oversampling())])

    def classDefinition(self):
        '''Returns the class definition.'''
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def classAttribute(self):
        '''Returns the class attribute.'''
        return self.burnAttribute()

    def minOverallCoverage(self):
        '''Returns the minimal overall coverage threshold.'''
        return self._minOverallCoverage

    def minDominantCoverage(self):
        '''Returns the minimal dominant class coverage threshold.'''
        return self._minDominantCoverage

    def oversampling(self):
        '''Returns the oversampling factor.'''
        return self._oversampling

class ClassDefinition(FlowObject):
    '''Class for managing class definitions.'''

    def __init__(self, classes=None, names=None, colors=None):
        '''
        Create new instance.

        :param classes: number of classes; if not provided, it is derived from length of names or colors
        :type classes: int
        :param names: class names; if not provided, generic names are used
        :type names: List[str]
        :param colors: class colors as (r, g, b) tripel or '#000000' strings; if not provided, random colors are used;
        :type colors: List
        '''

        if classes is not None:
            pass
        elif names is not None:
            classes = len(names)
        elif colors is not None:
            classes = len(colors)
        else:
            assert 0

        if names is None:
            names = ['class {}'.format(i + 1) for i in range(classes)]
        if colors is None:  # create random colors
            colors = [random.randint(1, 255) for i in range(classes * 3)]
        if len(colors) == classes * 3:  # format as tripels
            colors = [colors[i * 3: i * 3 + 3] for i in range(classes)]

        assert len(names) == classes
        assert len(colors) == classes

        self._classes = int(classes)
        self._names = [str(name) for name in names]
        self._colors = [QColor(*c) if isinstance(c, (list, tuple)) else QColor(c) for c in colors]

    def __getstate__(self):
        return OrderedDict([('classes', self.classes()),
                            ('names', self.names()),
                            ('colors', [str(c.name()) for c in self.colors()])])

    def classes(self):
        return self._classes

    def names(self):
        assert isinstance(self._names, list)
        return self._names

    def colors(self):
        assert isinstance(self._colors, list)
        return self._colors

    def labels(self):
        return list(range(1, self.classes()+1))

    @staticmethod
    def fromRaster(raster):
        try:
            classDefinition = ClassDefinition.fromENVIClassification(raster=raster)
        except:
            try:
                classDefinition = ClassDefinition.fromGDALMeta(raster=raster)
            except:
                statistics = Raster(filename=raster.filename()).statistics()
                classDefinition = ClassDefinition(classes=int(statistics[0].max))
        return classDefinition

    @staticmethod
    def fromENVIClassification(raster):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        classes = ds.metadataItem(key='classes', domain='ENVI', dtype=int, required=True)
        names = ds.metadataItem(key='class names', domain='ENVI', required=True)
        lookup = ds.metadataItem(key='class lookup', domain='ENVI', dtype=int, required=True)
        return ClassDefinition(classes=classes - 1, names=names[1:], colors=lookup[3:])

    @staticmethod
    def fromENVIFraction(raster):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        names = ds.metadataItem(key='band names', domain='ENVI')
        lookup = ds.metadataItem(key='band lookup', domain='ENVI', dtype=int)
        return ClassDefinition(names=names, colors=lookup)

    @staticmethod
    def fromGDALMeta(raster, index=0, skipZeroClass=True):
        assert isinstance(raster, Raster)
        ds = raster.dataset()
        names = ds.gdalDataset().GetRasterBand(index + 1).GetCategoryNames()
        classes = len(names)
        colors = [ds.gdalDataset().GetRasterBand(index + 1).GetColorTable().GetColorEntry(i)[:3] for i in
                  range(classes)]
        if skipZeroClass:
            classes = classes - 1
            names = names[1:]
            colors = colors[1:]
        return ClassDefinition(classes=classes, names=names, colors=colors)

    def dtype(self):
        for dtype in [np.uint8, np.uint16, np.uint32, np.uint64]:
            if self.classes() == dtype(self.classes()):
                return dtype

    def equal(self, other, compareColors=True):
        assert isinstance(other, ClassDefinition)
        equal = self.classes() == other.classes()
        equal &= all([a == b for a, b in zip(self.names(), other.names())])
        if compareColors:
            for color1, color2 in zip(self.colors(), other.colors()):
                equal &= color1.red() == color2.red()
                equal &= color1.green() == color2.green()
                equal &= color1.blue() == color2.blue()

        return equal

    def color(self, label):
        return self.colors()[label - 1]

    def colorByName(self, name):
        return self.color(label=self.names().index((name)) + 1)

    def name(self, label):
        return self.names()[label - 1]

    def labelByName(self, name):
        return self.names().index(name) + 1

    def colorsFlatRGB(self):
        values = list()
        for color in self.colors():
            values.append(color.red())
            values.append(color.green())
            values.append(color.blue())
        return values


class Classification(Raster):
    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minDominantCoverage=0.5):
        Raster.__init__(self, filename)
        self._classDefinition = classDefinition
        self._minOverallCoverage = minOverallCoverage
        self._minDominantCoverage = minDominantCoverage

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('classDefinition', self.classDefinition()),
                            ('minOverallCoverage', self.minOverallCoverage()),
                            ('minDominantCoverage', self.minDominantCoverage())])

    def classDefinition(self):
        if self._classDefinition is None:
            self._classDefinition = ClassDefinition.fromRaster(raster=self)

        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def minOverallCoverage(self):
        assert isinstance(self._minOverallCoverage, float)
        return self._minOverallCoverage

    def minDominantCoverage(self):
        assert isinstance(self._minDominantCoverage, float)
        return self._minDominantCoverage

    def noDataValues(self):
        return [0]

    def dtype(self):
        return self.classDefinition().dtype()

    def asMask(self, minOverallCoverage=0.5):
        return Raster.asMask(self, minOverallCoverage=minOverallCoverage)

    @classmethod
    def fromArray(cls, array, filename, classDefinition=None, grid=None, noDataValues=None):
        raster = Raster.fromArray(array=array, filename=filename, grid=grid, noDataValues=noDataValues)
        MetadataEditor.setClassDefinition(rasterDataset=raster.dataset(), classDefinition=classDefinition)
        raster.dataset().close()
        return Classification(filename=filename)

    @classmethod
    def fromClassification(cls, filename, classification, grid=None, masks=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.setOutputRaster('classification', filename=filename)
        applier.setFlowMasks(masks=masks)
        applier.apply(operatorType=_ClassificationFromClassification, classification=classification, masks=masks)
        return Classification(filename=filename)

    @classmethod
    def fromFraction(cls, filename, fraction, grid=None, masks=None, **kwargs):
        return cls.fromClassification(filename=filename, classification=fraction, grid=grid, masks=masks, **kwargs)

    @classmethod
    def fromRasterAndFunction(cls, filename, raster, ufunc, classDefinition, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setOutputRaster('classification', filename=filename)
        applier.apply(operatorType=_ClassificationFromRasterAndFunction, raster=raster, ufunc=ufunc,
                      classDefinition=classDefinition)
        return Classification(filename=filename)

    @staticmethod
    def fromENVISpectralLibrary(filename, library, attribute):
        assert isinstance(library, ENVISpectralLibrary)

        names = library.raster().dataset().metadataItem(key='{} class names'.format(attribute),
                                              domain='CSV', required=True)[1:]
        classes = len(names)
        lookup = library.raster().dataset().metadataItem(key='{} class lookup'.format(attribute),
                                               domain='CSV', dtype=int, required=True)[3:]

        lookup = [int(v) for v in lookup]
        classDefinition = ClassDefinition(classes=classes, names=names, colors=lookup)
        labels = np.array(library.raster().dataset().metadataItem(key=attribute,
                                                        domain='CSV', required=True))

        # convert names to ids

        array = np.zeros(shape=len(labels))
        for i, name in enumerate(names):
            array[labels == name] = str(i + 1)

        # sort profiles

        ordered = OrderedDict()
        spectraNames = library.raster().dataset().metadataItem(key='spectra names', domain='CSV', required=True)
        for name in library.raster().dataset().metadataItem(key='spectra names', domain='ENVI', required=True):
            ordered[name] = array[spectraNames.index(name)]

        # write to dataset
        bands, lines, samples = library.raster().dataset().shape()
        array = np.reshape(list(ordered.values()), newshape=(1, lines, samples)).astype(dtype=classDefinition.dtype())

        rasterDataset = createRasterDatasetFromArray(array=array, filename=filename,
                                                     driver=RasterDriver.fromFilename(filename=filename))
        MetadataEditor.setClassDefinition(rasterDataset=rasterDataset, classDefinition=classDefinition)
        rasterDataset.setNoDataValues(values=[0])
        rasterDataset.flushCache().close()
        return Classification(filename=filename)

    def reclassify(self, filename, classDefinition, mapping, **kwargs):
        assert isinstance(classDefinition, ClassDefinition)
        assert isinstance(mapping, dict)
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowClassification('inclassification', classification=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operatorType=_ClassificationReclassify, classification=self, classDefinition=classDefinition,
                      mapping=mapping)
        return Classification(filename=filename)

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('inclassification', classification=self)
        applier.setOutputRaster('outclassification', filename=filename)
        applier.apply(operatorType=_ClassificationResample, classification=self)
        return Classification(filename=filename)

    def statistics(self, mask=None, **kwargs):

        applier = Applier(defaultGrid=self, **kwargs)
        applier.controls.setBlockSize(50)
        applier.setFlowClassification('classification', classification=self)
        applier.setFlowMask('mask', mask=mask)
        return applier.apply(operatorType=_ClassificationStatistics, classification=self, mask=mask)

class _ClassificationStatistics(ApplierOperator):
    def ufunc(self, classification, mask):

        array = self.flowClassificationArray('classification', classification=classification)
        array[np.logical_not(self.flowMaskArray('mask', mask=mask))] = 0
        hist, bin_edges = np.histogram(array,
                                       bins=classification.classDefinition().classes(),
                                       range=[1, classification.classDefinition().classes()+1,])
        return hist

    @staticmethod
    def aggregate(blockResults, grid, *args, **kwargs):
        return np.sum(blockResults, axis=0)

class _ClassificationReclassify(ApplierOperator):
    def ufunc(self, classification, classDefinition, mapping):
        inclassification = self.flowClassificationArray('inclassification', classification=classification)
        outclassification = self.full(value=0, bands=1, dtype=np.uint8)
        for inclass, outclass in mapping.items():
            if inclass in classification.classDefinition().names():
                inclass = classification.classDefinition().names().index(inclass) + 1
            if outclass in classDefinition.names():
                outclass = classDefinition.names().index(outclass) + 1
            outclassification[inclassification == inclass] = outclass
        self.outputRaster.raster(key='outclassification').setArray(array=outclassification)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classDefinition)


class _ClassificationResample(ApplierOperator):
    def ufunc(self, classification):
        array = self.flowClassificationArray('inclassification', classification=classification)
        self.outputRaster.raster(key='outclassification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='outclassification', classDefinition=classification.classDefinition())


class _ClassificationFromClassification(ApplierOperator):
    def ufunc(self, classification, masks):
        array = self.flowClassificationArray('classification', classification=classification)
        marray = self.flowMasksArray(masks=masks)
        array[marray == 0] = 0
        self.outputRaster.raster(key='classification').setArray(array=array)
        self.setFlowMetadataClassDefinition(name='classification', classDefinition=classification.classDefinition())


class _ClassificationFromRasterAndFunction(ApplierOperator):
    def ufunc(self, raster, ufunc, classDefinition):
        array = self.flowRasterArray('raster', raster=raster)
        metadataDict = self.inputRaster.raster(key='raster').metadataDict()
        classificationArray = ufunc(array, metadataDict)
        self.outputRaster.raster(key='classification').setArray(array=classificationArray)
        self.setFlowMetadataClassDefinition(name='classification', classDefinition=classDefinition)


class Regression(Raster):
    def __init__(self, filename, noDataValues=None, outputNames=None, minOverallCoverage=0.5):
        Raster.__init__(self, filename)
        self._noDataValues = noDataValues
        self._outputNames = outputNames
        self._minOverallCoverage = float(minOverallCoverage)

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('noDataValues', self.noDataValues()),
                            ('outputNames', self.outputNames()),
                            ('minOverallCoverage', self.minOverallCoverage())])

    def noDataValues(self):
        if self._noDataValues is None:
            self._noDataValues = self.dataset().noDataValues(required=True)
        assert isinstance(self._noDataValues, list)
        return self._noDataValues

    def outputNames(self):
        if self._outputNames is None:
            self._outputNames = [band.description() for band in self.dataset().bands()]
        assert isinstance(self._outputNames, list)
        return self._outputNames

    def minOverallCoverage(self):
        assert isinstance(self._minOverallCoverage, float)
        return self._minOverallCoverage

    @staticmethod
    def fromRasterMetadata(filename, raster, outputNames, noDataValues=None):
        assert isinstance(raster, Raster)
        assert isinstance(outputNames, list)

        metadata = raster.dataset().metadataDomain(domain='ENVI')

        if noDataValues is None:
            noDataValues = [float(metadata['{} no data value'.format(outName)]) for outName in outputNames]
        assert isinstance(noDataValues, list)

        array = np.atleast_3d([np.array(metadata[outName], dtype=np.float32) for outName in outputNames])

        rasterDataset = createRasterDatasetFromArray(array=array,
                                                     filename=filename,
                                                     driver=RasterDriver.fromFilename(filename=filename))

        MetadataEditor.setRegressionDefinition(rasterDataset=rasterDataset, noDataValues=noDataValues,
                                               outputNames=outputNames)
        rasterDataset.flushCache().close()
        return Regression(filename=filename)

    def toRasterMetadata(self, raster):
        assert isinstance(raster, Raster)

        labels = self.dataset().readAsArray()
        outputNames = self.outputNames()
        noDataValues = self.noDataValues()
        for i, (outname, values, noDataValue) in enumerate(zip(outputNames, labels, noDataValues)):
            raster.dataset().setMetadataItem(key=outname, value=list(values.ravel()), domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' no data value', value=noDataValue, domain='ENVI')


    def asMask(self, minOverallCoverage=None):
        if minOverallCoverage is None:
            minOverallCoverage = self.minOverallCoverage()
        return Raster.asMask(self, noDataValues=self.noDataValues(), minOverallCoverage=minOverallCoverage)

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRegression('inregression', regression=self)
        applier.setOutputRaster('outregression', filename=filename)
        applier.apply(operatorType=_RegressionResample, regression=self)
        return Regression(filename=filename)


class _RegressionResample(ApplierOperator):
    def ufunc(self, regression):
        array = self.flowRegressionArray('inregression', regression=regression)
        self.outputRaster.raster(key='outregression').setArray(array=array)
        self.setFlowMetadataRegressionDefinition(name='outregression', noDataValues=regression.noDataValues(),
                                                 outputNames=regression.outputNames())


class Fraction(Regression):
    def __init__(self, filename, classDefinition=None, minOverallCoverage=0.5, minDominantCoverage=0.5):
        Raster.__init__(self, filename=filename)
        if classDefinition is None:
            classDefinition = ClassDefinition.fromENVIFraction(raster=self)
        self._classDefinition = classDefinition
        Regression.__init__(self, filename=filename, noDataValues=self.noDataValues(),
                            outputNames=classDefinition.names())
        self._minOverallCoverage = minOverallCoverage
        self._minDominantCoverage = minDominantCoverage

    def classDefinition(self):
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition

    def minOverallCoverage(self):
        return self._minOverallCoverage

    def minDominantCoverage(self):
        return self._minDominantCoverage

    def noDataValues(self):
        return [-1.] * self.classDefinition().classes()

    def __getstate__(self):
        return OrderedDict([('filename', self.filename()),
                            ('classDefinition', self.classDefinition())])

    @classmethod
    def fromClassification(cls, filename, classification, grid=None, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowClassification('classification', classification=classification)
        applier.setOutputRaster('fraction', filename=filename)
        applier.apply(operatorType=_FractionFromClassification, classification=classification)
        return Fraction(filename=filename)

    def toRasterMetadata(self, raster):
        assert isinstance(raster, Raster)

        labels = self.dataset().readAsArray()
        outputNames = self.outputNames()
        noDataValues = self.noDataValues()
        colors = self.classDefinition().colors()
        for i, (outname, values, noDataValue, color) in enumerate(zip(outputNames, labels, noDataValues, colors)):
            raster.dataset().setMetadataItem(key=outname, value=list(values.ravel()), domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' no data value', value=noDataValue, domain='ENVI')
            raster.dataset().setMetadataItem(key=outname + ' color', value=[color.red(), color.green(), color.blue()], domain='ENVI')

    def resample(self, filename, grid, **kwargs):
        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowFraction('infraction', fraction=self)
        applier.setOutputRaster('outfraction', filename=filename)
        applier.apply(operatorType=_FractionResample, fraction=self)
        return Fraction(filename=filename)

    def subsetClasses(self, filename, labels, **kwargs):
        indices = [label - 1 for label in labels]
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('fraction', raster=self)
        applier.setOutputRaster('fractionSubset', filename=filename)
        applier.apply(operatorType=_FractionSubsetClasses, indices=indices, fraction=self)
        return Fraction(filename=filename)

    def subsetClassesByName(self, filename, names, **kwargs):
        labels = [self.classDefinition().names().index(name) + 1 for name in names]
        return self.subsetClasses(filename=filename, labels=labels, **kwargs)

    def asClassColorRGBRaster(self, filename, filterById=None, filterByName=None, **kwargs):
        filter = []
        if filterById is not None:
            filter.extend(filterById)
        if filterByName is not None:
            filter.extend([self.classDefinition().names().index[name] for name in filterByName])
        applier = Applier(defaultGrid=self, **kwargs)
        applier.setFlowRaster('fraction', raster=self)
        applier.setOutputRaster('raster', filename=filename)
        applier.apply(operatorType=_FractionAsClassColorRGBRaster, fraction=self, filter=filter)
        return Raster(filename=filename)


class _FractionAsClassColorRGBRaster(ApplierOperator):
    def ufunc(self, filter, fraction):
        assert isinstance(fraction, Fraction)
        colors = fraction.classDefinition().colors()
        array = self.flowRasterArray('fraction', raster=fraction)
        rgb = self.full(value=0, bands=3, dtype=np.float32)
        for id, (band, color) in enumerate(zip(array, colors), start=1):
            if len(filter) > 0 and id not in filter: continue
            colorRGB = (color.red(), color.green(), color.blue())
            rgb += band * np.reshape(colorRGB, newshape=(3, 1, 1))
        np.uint8(np.clip(rgb, a_min=0, a_max=255, out=rgb))
        mask = np.any(rgb != 0, axis=0)
        np.clip(rgb, a_min=1, a_max=255, out=rgb)
        rgb *= mask
        self.outputRaster.raster(key='raster').setArray(array=np.uint8(rgb))


class _FractionFromClassification(ApplierOperator):
    def ufunc(self, classification):
        array = self.flowFractionArray('classification', fraction=classification)
        self.outputRaster.raster(key='fraction').setArray(array=array)
        self.setFlowMetadataFractionDefinition(name='fraction',
                                               classDefinition=classification.classDefinition())


class _FractionResample(ApplierOperator):
    def ufunc(self, fraction):
        array = self.flowFractionArray('infraction', fraction=fraction)
        self.outputRaster.raster(key='outfraction').setArray(array=array)
        self.setFlowMetadataFractionDefinition(name='outfraction', classDefinition=fraction.classDefinition())


class _FractionSubsetClasses(ApplierOperator):
    def ufunc(self, indices, fraction):
        classes = len(indices)
        colors = [fraction.classDefinition().color(label=index + 1) for index in indices]
        names = [fraction.classDefinition().name(label=index + 1) for index in indices]
        classDefinition = ClassDefinition(classes=classes, names=names, colors=colors)
        fractionSubset = self.inputRaster.raster(key='fraction').bandArray(indices=indices)
        self.outputRaster.raster(key='fractionSubset').setArray(array=fractionSubset)
        self.setFlowMetadataFractionDefinition(name='fractionSubset', classDefinition=classDefinition)


class FractionPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT):
        import sklearn.metrics
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes() == classDefinitionP.classes()
        assert isinstance(yP, np.ndarray)
        assert isinstance(yT, np.ndarray)
        assert yT.shape[1] == yP.shape[1]
        assert len(yT) == 1
        assert len(yP) == classDefinitionP.classes()

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP

        self.yP = yP.T
        self.yT = yT[0]
        self.n = yP.shape[1]
        self.log_loss = sklearn.metrics.log_loss(y_true=self.yT, y_pred=self.yP)
        self.roc_curves = dict()
        self.roc_auc_scores = dict()

        for i in range(1, self.classDefinitionT.classes() + 1):
            self.roc_curves[i] = sklearn.metrics.roc_curve(y_true=self.yT, y_score=self.yP[:, i - 1], pos_label=i,
                                                           drop_intermediate=True)
            self.roc_auc_scores[i] = sklearn.metrics.roc_auc_score(y_true=self.yT == i, y_score=self.yP[:, i - 1])

    def __getstate__(self):
        return OrderedDict([('yP', self.yP.T),
                            ('yT', self.yT[None]),
                            ('classDefinitionP', self.classDefinitionP),
                            ('classDefinitionT', self.classDefinitionT)])

    @classmethod
    def fromRaster(self, prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Fraction)
        assert isinstance(reference, Classification)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask], **kwargs)

        return FractionPerformance(yP=yP, yT=yT, classDefinitionP=prediction.classDefinition(),
                                   classDefinitionT=reference.classDefinition())

    def report(self):
        classes = self.classDefinitionT.classes()
        names = self.classDefinitionT.names()
        report = Report('Fraction Performance')
        report.append(ReportHeading('Performance Measures'))
        colHeaders = [['', 'AUC'], ['n', 'Log loss'] + names]
        colSpans = [[2, classes], [1] * (classes + 2)]
        roc_auc_scores_rounded = [round(elem, 3) for elem in self.roc_auc_scores.values()]
        data = [[str(self.n), numpy.round(self.log_loss, 2)] + roc_auc_scores_rounded]
        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        report.append(ReportHeading('Receiver Operating Characteristic (ROC) Curves'))

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(facecolor='white', figsize=(9, 6))
        for i in range(len(self.roc_curves)):
            # rgb = [v / 255. for v in self.classDefinitionP.color[i]]
            plt.plot(self.roc_curves[i + 1][0], self.roc_curves[i + 1][1]
                     , label=names[i])  # , color=rgb) # problem: plots do not show the correct RGB colors
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.legend(loc="lower right")
        fig.tight_layout()
        report.append(ReportPlot(fig, 'ROC Curves'))

        report.append(ReportHeading('Scikit-Learn Documentation'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/model_evaluation.html#roc-metrics',
                                      'ROC User Guide'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html',
                                      'ROC Curve'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html#sklearn.metrics.roc_auc_score',
            'AUC score'))
        report.append(ReportHyperlink('http://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html',
                                      'Log Loss Metric'))

        return report


class Sample(MapCollection):
    def __init__(self, raster, mask=None, grid=None):
        assert isinstance(raster, Raster)
        if grid is None:
            grid = raster.dataset().grid()
        assert isinstance(grid, Grid), repr(grid)
        MapCollection.__init__(self, maps=[raster])
        self._mask = mask
        self._grid = grid

    def __getstate__(self):
        return OrderedDict([('raster', self.raster()),
                            ('mask', self.mask()),
                            ('grid', self.grid())])

    def _initPickle(self):
        MapCollection._initPickle(self)
        if self._mask is not None:
            self._mask._initPickle()

    def raster(self):
        raster = self.maps()[0]
        assert isinstance(raster, Raster)
        return raster

    def mask(self):
        return self._mask

    def masks(self):
        return [self.raster(), self.mask()]

    def grid(self):
        assert isinstance(self._grid, Grid)
        return self._grid

    def extractAsArray(self, grid=None, masks=None, onTheFlyResampling=False, **kwargs):
        if grid is None:
            grid = self.grid()
        if masks is None:
            masks = self.masks()
        return MapCollection.extractAsArray(self, grid=grid, masks=masks, onTheFlyResampling=onTheFlyResampling, **kwargs)

    def extractAsRaster(self, filenames, grid=None, masks=None, onTheFlyResampling=False, **kwargs):
        if grid is None:
            grid = self.grid()
        if masks is None:
            masks = self.masks()
        return MapCollection.extractAsRaster(self, filenames=filenames, grid=grid, masks=masks,
                                             onTheFlyResampling=onTheFlyResampling, **kwargs)

class ClassificationSample(Sample):
    def __init__(self, raster, classification, mask=None, grid=None):
        Sample.__init__(self, raster=raster, mask=mask, grid=grid)
        assert isinstance(classification, Classification)
        self.maps().append(classification)

    def __getstate__(self):
        return OrderedDict([('raster', self.raster()),
                            ('classification', self.classification()),
                            ('mask', self.mask()),
                            ('grid', self.grid())])

    def masks(self):
        return Sample.masks(self) + [self.classification()]

    def classification(self):
        classification = self.maps()[1]
        assert isinstance(classification, Classification)
        return classification


    def synthMix(self, filenameFeatures, filenameFractions, mixingComplexities, classLikelihoods=None, n=10, **kwargs):

        classDefinition = self.classification().classDefinition()
        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods is 'proportional':
            statistics = self.classification().statistics(calcHistogram=True,
                                                          histogramBins=[classDefinition.classes()],
                                                          histogramRanges=[(1, classDefinition.classes() + 1)])
            histogram = statistics[0].histo.hist
            classLikelihoods = {i + 1: float(count) / sum(histogram) for i, count in enumerate(histogram)}
        elif classLikelihoods is 'equalized':
            classLikelihoods = {i + 1: 1. / classDefinition().classes() for i in range(classDefinition().classes())}

        assert isinstance(mixingComplexities, dict)
        assert isinstance(classLikelihoods, dict)

        features, labels = self.extractAsArray(**kwargs)
        classes = self.classification().classDefinition().classes()

        # cache label indices and setup 0%/100% fractions from class labels
        indices = dict()
        zeroOneFractions = np.zeros((classes, features.shape[1]), dtype=np.float32)
        for label in range(1, classes + 1):
            indices[label] = np.where(labels == label)[1]
            zeroOneFractions[label - 1, indices[label]] = 1.

        # create mixtures
        mixtures = list()
        fractions = list()
        for i in range(n):
            complexity = np.random.choice(list(mixingComplexities.keys()), p=list(mixingComplexities.values()))
            drawnLabels = np.random.choice(list(classLikelihoods.keys()), size=complexity, replace=True,
                                           p=list(classLikelihoods.values()))
            drawnIndices = [np.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]
            randomWeights = np.atleast_2d(np.float32(np.random.randint(low=1, high=100, size=complexity)))
            randomWeights /= randomWeights.sum()
            mixtures.append(np.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(np.sum(drawnFractions * randomWeights, axis=1))

        mixtures = np.atleast_3d(np.transpose(mixtures))
        fractions = np.atleast_3d(np.transpose(fractions))

        featuresDataset = createRasterDatasetFromArray(array=mixtures, filename=filenameFeatures,
                                                       driver=RasterDriver.fromFilename(filename=filenameFeatures))
        featuresDataset.flushCache().close()
        fractionsDataset = createRasterDatasetFromArray(array=fractions, filename=filenameFractions,
                                                        driver=RasterDriver.fromFilename(filename=filenameFractions))
        MetadataEditor.setFractionDefinition(rasterDataset=fractionsDataset, classDefinition=classDefinition)
        fractionsDataset.flushCache().close()

        return FractionSample(raster=Raster(filename=filenameFeatures),
                              fraction=Fraction(filename=filenameFractions))

    def synthMix2(self, filenameFeatures, filenameFractions, target, mixingComplexities, classLikelihoods=None,
                  n=10, includeEndmember=False, includeWithinclassMixtures=False, targetRange=(0, 1), **kwargs):

        classDefinition = self.classification().classDefinition()
        if classLikelihoods is None:
            classLikelihoods = 'proportional'
        if classLikelihoods == 'proportional':
            statistics = self.classification().statistics(calcHistogram=True,
                                                          histogramBins=[classDefinition.classes()],
                                                          histogramRanges=[(1, classDefinition.classes() + 1)])
            histogram = statistics[0].histo.hist
            classLikelihoods = {i + 1: float(count) / sum(histogram) for i, count in enumerate(histogram)}
        elif classLikelihoods == 'equalized':
            classLikelihoods = {i + 1: 1. / classDefinition.classes() for i in range(classDefinition.classes())}

        assert isinstance(mixingComplexities, dict)
        assert isinstance(classLikelihoods, dict)

        features, labels = self.extractAsArray(**kwargs)
        classes = classDefinition.classes()

        # cache label indices and setup 0%/100% fractions from class labels
        indices = dict()
        zeroOneFractions = np.zeros((classes, features.shape[1]), dtype=np.float32)
        for label in range(1, classes + 1):
            indices[label] = np.where(labels == label)[1]
            zeroOneFractions[label - 1, indices[label]] = 1.

        # create mixtures
        mixtures = list()
        fractions = list()

        classLikelihoods2 = {k: v / (1-classLikelihoods[target]) for k, v in classLikelihoods.items() if k != target}
        for i in range(n):
            complexity = np.random.choice(list(mixingComplexities.keys()), p=list(mixingComplexities.values()))
            drawnLabels = [target]

            if includeWithinclassMixtures:
                drawnLabels.extend(np.random.choice(list(classLikelihoods.keys()), size=complexity-1, replace=True,
                                                    p=list(classLikelihoods.values())))
            else:
                drawnLabels.extend(np.random.choice(list(classLikelihoods2.keys()), size=complexity - 1, replace=False,
                                                    p=list(classLikelihoods2.values())))

            drawnIndices = [np.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]

            randomWeights = list()
            for i in range(complexity-1):
                if i == 0:
                    weight = numpy.random.random() * (targetRange[1] - targetRange[0]) + targetRange[0]
                else:
                    weight = numpy.random.random() * (1.-sum(randomWeights))
                randomWeights.append(weight)
            randomWeights.append(1. - sum(randomWeights))

            assert sum(randomWeights) == 1.
            mixtures.append(np.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(np.sum(drawnFractions * randomWeights, axis=1)[target-1])

        if includeEndmember:
            mixtures.extend(features.T)
            fractions.extend(np.float32(labels == target)[0]) # 1. for target class, 0. for the rest

        mixtures = np.atleast_3d(np.transpose(mixtures))
        fractions = np.atleast_3d(np.transpose(fractions))

        featuresDataset = createRasterDatasetFromArray(array=mixtures, filename=filenameFeatures,
                                                       driver=RasterDriver.fromFilename(filename=filenameFeatures))
        featuresDataset.flushCache().close()
        fractionsDataset = createRasterDatasetFromArray(array=fractions, filename=filenameFractions,
                                                        driver=RasterDriver.fromFilename(
                                                            filename=filenameFractions))
        outClassDefinition = ClassDefinition(classes=1,
                                             names=[classDefinition.name(label=target)],
                                             colors=[classDefinition.color(label=target)])
        MetadataEditor.setFractionDefinition(rasterDataset=fractionsDataset, classDefinition=outClassDefinition)
        fractionsDataset.flushCache().close()

        return FractionSample(raster=Raster(filename=filenameFeatures),
                              fraction=Fraction(filename=filenameFractions))


class RegressionSample(Sample):
    def __init__(self, raster, regression, mask=None, grid=None):
        Sample.__init__(self, raster=raster, mask=mask, grid=grid)
        assert isinstance(regression, Regression)
        self.maps().append(regression)
        self._regression = regression

    def __getstate__(self):
        return OrderedDict([('raster', self.raster()),
                            ('regression', self.regression()),
                            ('mask', self.mask()),
                            ('grid', self.grid())])

    def masks(self):
        return Sample.masks(self) + [self.regression()]

    def regression(self):
        assert isinstance(self._regression, Regression)
        return self._regression


class FractionSample(RegressionSample):
    def __init__(self, raster, fraction, mask=None, grid=None):
        assert isinstance(fraction, Fraction)
        RegressionSample.__init__(self, raster=raster, regression=fraction, mask=mask, grid=grid)

    def __getstate__(self):
        return OrderedDict([('raster', self.raster()),
                            ('fraction', self.regression()),
                            ('mask', self.mask()),
                            ('grid', self.grid())])

    def fraction(self):
        return self.regression()


class Estimator(FlowObject):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Raster

    def __init__(self, sklEstimator, sample=None):
        self._sklEstimator = sklEstimator
        self._sample = sample

    def __getstate__(self):
        return OrderedDict([('sklEstimator', self.sklEstimator()),
                            ('sample', self.sample())])

    def _initPickle(self):
        if isinstance(self._sample, Sample):
            self._sample._initPickle()

    def sklEstimator(self):
        return self._sklEstimator

    def sample(self):
        assert isinstance(self._sample, (Sample, type(None)))
        return self._sample

    def _fit(self, sample):
        import sklearn.multioutput
        assert isinstance(sample, self.SAMPLE_TYPE)
        self._sample = sample

        if isinstance(sample, (ClassificationSample, RegressionSample, FractionSample)):
            features, labels = sample.extractAsArray()
            X = np.float64(features.T)
            if labels.shape[0] == 1 and not isinstance(self.sklEstimator(), sklearn.multioutput.MultiOutputEstimator):
                y = labels.ravel()
            else:
                y = labels.T
        elif isinstance(sample, Sample):
            features, = sample.extractAsArray()
            X = np.float64(features.T)
            y = None
        else:
            assert 0
        self.sklEstimator().fit(X=X, y=y)

        if isinstance(self, Clusterer):
            yTrain = self.sklEstimator().predict(X=X)
            self._classDefinition = ClassDefinition(classes=max(yTrain) + 1)
        return self

    def _predict(self, filename, raster, mask=None, **kwargs):

        if isinstance(raster, Raster):
            grid = raster.grid()
        elif isinstance(raster, RasterStack):
            grid = raster.raster(0).grid()
        else:
            assert 0

        applier = Applier(defaultGrid=grid, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setOutputRaster('prediction', filename=filename)
        applier.apply(operatorType=_EstimatorPredict, raster=raster, estimator=self, mask=mask)
        prediction = self.PREDICT_TYPE(filename=filename)
        assert isinstance(prediction, Raster)
        return prediction

    def _predictProbability(self, filename, raster, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        applier.setOutputRaster('fraction', filename=filename)
        applier.apply(operatorType=_EstimatorPredictProbability, raster=raster, estimator=self, mask=mask, mask2=mask2)
        fraction = Fraction(filename=filename)
        return fraction

    def _transform(self, filename, raster, inverse=False, mask=None, mask2=None, **kwargs):
        applier = Applier(defaultGrid=raster, **kwargs)
        applier.setFlowRaster('raster', raster=raster)
        applier.setFlowMask('mask', mask=mask)
        applier.setFlowMask('mask2', mask=mask2)
        applier.setOutputRaster('transformation', filename=filename)
        applier.apply(operatorType=_EstimatorTransform, estimator=self, raster=raster, mask=mask, mask2=mask2,
                      inverse=inverse)
        return Raster(filename=filename)

    def _inverseTransform(self, filename, raster, mask=None, mask2=None, **kwargs):
        return self._transform(filename=filename, raster=raster, inverse=True, mask=None, mask2=None, **kwargs)


class _EstimatorPredict(ApplierOperator):
    def ufunc(self, estimator, raster, mask):
        self.features = self.flowRasterArray('raster', raster=raster)
        etype, dtype, noutputs = self.getInfos(estimator)

        if isinstance(estimator, (Classifier, Clusterer)):
            noDataValues = [0]
        elif isinstance(estimator, Regressor):
            noDataValues = estimator.sample().regression().noDataValues()
        else:
            assert 0

        prediction = self.full(value=noDataValues, bands=noutputs, dtype=dtype)

        valid = self.maskFromArray(array=self.features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)

        if np.any(valid):
            X = np.float64(self.features[:, valid[0]].T)
            y = estimator.sklEstimator().predict(X=X)
            prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='prediction').setArray(array=prediction)

        if isinstance(estimator, Classifier):
            self.setFlowMetadataClassDefinition('prediction',
                                                classDefinition=estimator.sample().classification().classDefinition())
        elif isinstance(estimator, Clusterer):
            self.setFlowMetadataClassDefinition('prediction', classDefinition=estimator._classDefinition)
        elif isinstance(estimator, Regressor):
            if isinstance(estimator.sample(), FractionSample):
                self.setFlowMetadataFractionDefinition('prediction',
                                                       classDefinition=estimator.sample().fraction().classDefinition())
            else:
                self.outputRaster.raster(key='prediction').setNoDataValues(values=noDataValues)
            self.setFlowMetadataBandNames('prediction', bandNames=estimator.sample().regression().outputNames())

    def getInfos(self, estimator):
        etype = estimator.sklEstimator()._estimator_type
        if etype in ['classifier', 'clusterer']:
            noutputs = 1
            dtype = np.uint8
        elif etype == 'regressor':
            X0 = np.float64(np.atleast_2d(self.features[:, 0, 0]))
            y0 = estimator.sklEstimator().predict(X=X0)
            noutputs = max(y0.shape)
            dtype = np.float32
        else:
            raise Exception('unexpected estimator type')
        return etype, dtype, noutputs


class _EstimatorPredictProbability(ApplierOperator):
    def ufunc(self, estimator, raster, mask, mask2):
        assert isinstance(estimator, Classifier)
        self.features = self.flowRasterArray('raster', raster=raster)
        noutputs = estimator.sample().classification().classDefinition().classes()
        noDataValue = -1
        prediction = self.full(value=noDataValue, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=self.features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)
        valid *= self.flowMaskArray('mask2', mask=mask2)

        X = np.float64(self.features[:, valid[0]].T)
        y = estimator.sklEstimator().predict_proba(X=X)
        prediction[:, valid[0]] = y.reshape(X.shape[0], -1).T

        self.outputRaster.raster(key='fraction').setArray(array=prediction)
        self.setFlowMetadataFractionDefinition('fraction',
                                               classDefinition=estimator.sample().classification().classDefinition())


class _EstimatorTransform(ApplierOperator):
    def ufunc(self, estimator, raster, mask, mask2, inverse):
        if inverse:
            sklTransform = estimator.sklEstimator().inverse_transform
        else:
            sklTransform = estimator.sklEstimator().transform

        noDataValue = np.finfo(np.float32).min
        features = self.flowRasterArray('raster', raster=raster)

        X0 = np.float64(np.atleast_2d(features[:, 0, 0]))
        _, noutputs = sklTransform(X=X0).shape

        transformation = self.full(value=noDataValue, bands=noutputs, dtype=np.float32)

        valid = self.maskFromArray(array=features, noDataValueSource='raster')
        valid *= self.flowMaskArray('mask', mask=mask)
        valid *= self.flowMaskArray('mask2', mask=mask2)

        X = np.float64(features[:, valid[0]].T)
        y = sklTransform(X=X)
        transformation[:, valid[0]] = np.float32(y.reshape(-1, noutputs).T)

        self.outputRaster.raster(key='transformation').setArray(array=transformation)
        self.outputRaster.raster(key='transformation').setNoDataValue(value=noDataValue)


class Classifier(Estimator):
    SAMPLE_TYPE = ClassificationSample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    predictProbability = Estimator._predictProbability


class Regressor(Estimator):
    SAMPLE_TYPE = RegressionSample
    PREDICT_TYPE = Regression
    fit = Estimator._fit
    predict = Estimator._predict


class Transformer(Estimator):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Raster
    fit = Estimator._fit
    transform = Estimator._transform
    inverseTransform = Estimator._inverseTransform


class Clusterer(Estimator):
    SAMPLE_TYPE = Sample
    PREDICT_TYPE = Classification
    fit = Estimator._fit
    predict = Estimator._predict
    transform = Estimator._transform

    def __init__(self, sklEstimator, sample=None, classDefinition=None):
        Estimator.__init__(self, sklEstimator=sklEstimator, sample=sample)
        self._classDefinition = classDefinition

    def __getstate__(self):
        return OrderedDict([('sklEstimator', self.sklEstimator()),
                            ('sample', self.sample()),
                            ('classDefinition', self.classDefinition())])

    def classDefinition(self):
        if self._classDefinition is None:
            return ClassDefinition(classes=0)
        assert isinstance(self._classDefinition, ClassDefinition)
        return self._classDefinition


class ClassificationPerformance(FlowObject):
    def __init__(self, yP, yT, classDefinitionP, classDefinitionT, classProportions=None, N=0):
        assert isinstance(yP, np.ndarray) and yP.ndim == 1
        assert isinstance(yT, np.ndarray) and yT.shape == yP.shape
        assert isinstance(classDefinitionP, ClassDefinition)
        assert isinstance(classDefinitionT, ClassDefinition)
        assert classDefinitionT.classes() == classDefinitionP.classes()

        self.classDefinitionT = classDefinitionT
        self.classDefinitionP = classDefinitionP
        self.N = N

        import sklearn.metrics
        self.yP = yP
        self.yT = yT
        self.mij = np.int64(
            sklearn.metrics.confusion_matrix(yT, yP, labels=range(1, classDefinitionT.classes() + 1)).T)
        self.m = np.int64(yP.size)
        self.classProportions = self.Wi = classProportions
        self._assessPerformance()

    def __getstate__(self):
        return OrderedDict([('yP', self.yP),
                            ('yT', self.yT),
                            ('classDefinitionP', self.classDefinitionP),
                            ('classDefinitionT', self.classDefinitionT),
                            ('classProportions', self.classProportions),
                            ('N', self.N)])

    @staticmethod
    def fromRaster(prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)
        stratification = prediction
        classes = stratification.classDefinition().classes()
        histogram = stratification.statistics(calcHistogram=True,
                                              histogramBins=[classes],
                                              histogramRanges=[(1, classes + 1)], **kwargs)
        classProportions = [float(count) / sum(histogram) for i, count in enumerate(histogram)]
        N = sum(histogram)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return ClassificationPerformance(yP=yP[0], yT=yT[0],
                                         classDefinitionP=prediction.classDefinition(),
                                         classDefinitionT=reference.classDefinition(),
                                         classProportions=classProportions,
                                         N=N)

    def _assessPerformance(self):

        old_error_state = np.geterr()
        np.seterr(divide='ignore', invalid='ignore', over='raise', under='raise')

        # get some stats from the confusion matrix mij
        self.mi_ = np.sum(self.mij, axis=0, dtype=np.float64)  # class-wise sum over all prediction
        self.m_j = np.sum(self.mij, axis=1, dtype=np.float64)  # class-wise sum over references
        self.mii = np.diag(self.mij)  # main diagonal -> class-wise correctly classified samples

        # estimate mapped class proportions from the reference sample, if not provided by the user
        if self.Wi is None:
            self.Wi = self.mi_ / self.m  # note that in this case pij is reduced to pij=mij/m

        # pij is the proportion of area estimate
        # pij = Wi*mij/mi_
        self.pij = np.zeros_like(self.mij, dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                self.pij[i, j] = self.Wi[i] * self.mij[i, j] / self.mi_[i]

        self.pi_ = np.sum(self.pij, axis=0, dtype=np.float64)
        self.p_j = np.sum(self.pij, axis=1, dtype=np.float64)
        self.pii = np.diag(self.pij)

        # calculate performance measures
        self.ProducerAccuracy = self._fix(self.mii / self.mi_)
        self.UserAccuracy = self._fix(self.mii / self.m_j)

        self.F1Accuracy = self._fix(
            2 * self.UserAccuracy * self.ProducerAccuracy / (self.UserAccuracy + self.ProducerAccuracy))
        self.ConditionalKappaAccuracy = self._fix(
            (self.m * self.mii - self.mi_ * self.m_j) / (self.m * self.mi_ - self.mi_ * self.m_j))
        self.OverallAccuracy = self._fix(self.mii.sum() / float(self.m))
        self.KappaAccuracy = self._fix(
            (self.m * self.mii.sum() - np.sum(self.mi_ * self.m_j)) / (self.m ** 2 - np.sum(self.mi_ * self.m_j)))

        # calculate squared standard errors (SSE)

        self.OverallAccuracySSE = 0.
        for i in range(self.classDefinitionT.classes()): self.OverallAccuracySSE += self.pij[i, i] * (
            self.Wi[i] - self.pij[i, i]) / (self.Wi[i] * self.m)

        a1 = self.mii.sum() / self.m
        a2 = (self.mi_ * self.m_j).sum() / self.m ** 2
        a3 = (self.mii * (self.mi_ + self.m_j)).sum() / self.m ** 2
        a4 = 0.
        for i in range(self.classDefinitionT.classes()):
            for j in range(self.classDefinitionT.classes()):
                a4 += self.mij[i, j] * (self.mi_[j] + self.m_j[i]) ** 2
        a4 /= self.m ** 3
        b1 = a1 * (1 - a1) / (1 - a2) ** 2
        b2 = 2 * (1 - a1) * (2 * a1 * a2 - a3) / (1 - a2) ** 3
        b3 = (1 - a1) ** 2 * (a4 - 4 * a2 ** 2) / (1 - a2) ** 4
        self.KappaAccuracySSE = (b1 + b2 + b3) / self.m

        self.ProducerAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            sum = 0.
            for j in range(self.classDefinitionT.classes()):
                if i == j: continue
                sum += self.pij[i, j] * (self.Wi[j] - self.pij[i, j]) / (self.Wi[j] * self.m)
                self.ProducerAccuracySSE[i] = self.pij[i, i] * self.p_j[i] ** (-4) * (
                    self.pij[i, i] * sum + (self.Wi[i] - self.pij[i, i]) * (self.p_j[i] - self.pij[i, i]) ** 2 / (
                        self.Wi[i] * self.m))

        self.UserAccuracySSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for i in range(self.classDefinitionT.classes()):
            self.UserAccuracySSE[i] = self.pij[i, i] * (self.Wi[i] - self.pij[i, i]) / (self.Wi[i] ** 2 * self.m)

        self.F1AccuracySSE = self._fix(
            2 * self.UserAccuracySSE * self.ProducerAccuracySSE / (self.UserAccuracySSE + self.ProducerAccuracySSE))

        self.ConditionalKappaAccuracySSE = self.m * (self.mi_ - self.mii) / (self.mi_ * (self.m - self.m_j)) ** 3 * (
            (self.mi_ - self.mii) * (self.mi_ * self.m_j - self.m * self.mii) + self.m * self.mii * (
                self.m - self.mi_ - self.m_j + self.mii))

        self.ClassProportion = self.m_j / self.m
        self.ClassProportionSSE = np.zeros(self.classDefinitionT.classes(), dtype=np.float64)
        for j in range(self.classDefinitionT.classes()):
            for i in range(self.classDefinitionT.classes()):
                self.ClassProportionSSE[j] += self.Wi[i] ** 2 * (
                    (self.mij[i, j] / self.mi_[i]) * (1 - self.mij[i, j] / self.mi_[i])) / (self.mi_[i] - 1)

        np.seterr(**old_error_state)

    def _confidenceIntervall(self, mean, sse, alpha):
        import scipy.stats
        se = np.sqrt(np.clip(sse, 0, np.inf))
        lower = scipy.stats.norm.ppf(alpha / 2.) * se + mean
        upper = scipy.stats.norm.ppf(1 - alpha / 2.) * se + mean
        return lower, upper

    def _fix(self, a, fill=0):
        if isinstance(a, np.ndarray):
            a[np.logical_not(np.isfinite(a))] = 0
        else:
            if not np.isfinite(a):
                a = 0
        return a

    def report(self):

        report = Report('Classification Performance')

        report.append(ReportHeading('Class Overview'))
        colHeaders = None
        rowSpans = [[1, 2], [1, 1, 1]]
        rowHeaders = [['', 'Class Names'], ['Class ID', 'Reference', 'Prediction']]
        data = [np.hstack((range(1, self.classDefinitionT.classes() + 1))), self.classDefinitionT.names(),
                self.classDefinitionP.names()]

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders,
                                  colSpans=None, rowSpans=rowSpans))

        # Confusion Matrix Table
        report.append(ReportHeading('Confusion Matrix'))
        classNumbers = []
        for i in range(self.classDefinitionT.classes()): classNumbers.append('(' + str(i + 1) + ')')
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        classNamesColumn = []
        for i in range(self.classDefinitionT.classes()): classNamesColumn.append(
            '(' + str(i + 1) + ') ' + self.classDefinitionT.names()[i])
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(((np.hstack((self.mij, self.m_j[:, None]))), np.hstack((self.mi_, self.m)))).astype(
            int)

        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Accuracies Table
        report.append(ReportHeading('Accuracies'))
        colHeaders = [['Measure', 'Estimate [%]', '95 % Confidence Interval [%]']]
        colSpans = [[1, 1, 2]]
        rowHeaders = None
        data = [['Overall Accuracy', np.round(self.OverallAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[0] * 100),
                 round(self._confidenceIntervall(self.OverallAccuracy, self.OverallAccuracySSE, 0.05)[1] * 100, 2)],
                ['Kappa Accuracy', np.round(self.KappaAccuracy * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[0] * 100, 2),
                 np.round(self._confidenceIntervall(self.KappaAccuracy, self.KappaAccuracySSE, 0.05)[1] * 100, 2)],
                ['Mean F1 Accuracy', np.round(np.mean(self.F1Accuracy) * 100, 2), '-', '-']]
        report.append(ReportTable(data, '', colHeaders, rowHeaders, colSpans, rowSpans))

        # Class-wise Accuracies Table
        report.append(ReportHeading('Class-wise Accuracies'))
        colSpans = [[1, 3, 3, 3], [1, 1, 2, 1, 2, 1, 2]]
        colHeaders = [['', 'User\'s Accuracy [%]', 'Producer\'s Accuracy [%]', 'F1 Accuracy'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95% Interval', 'Estimate',
                       '95% Interval']]
        data = [classNamesColumn, np.round(self.UserAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.UserAccuracy, self.UserAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.ProducerAccuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.ProducerAccuracy, self.ProducerAccuracySSE, 0.05)[1] * 100, 2)
            , np.round(self.F1Accuracy * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[0] * 100, 2)
            , np.round(self._confidenceIntervall(self.F1Accuracy, self.F1AccuracySSE, 0.05)[1] * 100, 2)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, rowHeaders=rowHeaders, colSpans=colSpans))

        # Proportion Matrix Table
        report.append(ReportHeading('Proportion Matrix'))
        colHeaders = [['Reference Class'], classNumbers + ['Sum']]
        colSpans = [[self.classDefinitionT.classes()], np.ones(self.classDefinitionT.classes() + 1, dtype=int)]
        rowHeaders = [classNamesColumn + ['Sum']]
        data = np.vstack(
            ((np.hstack((self.pij, self.p_j[:, None]))), np.hstack((self.pi_, 1))))
        report.append(ReportTable(np.round(data, 4), '', colHeaders=colHeaders, rowHeaders=rowHeaders,
                                  colSpans=colSpans))

        # Class-wise Area Estimates
        report.append(ReportHeading('Class-wise Proportion and Area Estimates'))
        colSpans = [[1, 3, 3], [1, 1, 2, 1, 2]]
        colHeaders = [['', 'Proportion', 'Area [px]'],
                      ['Map class', 'Estimate', '95 % Interval', 'Estimate', '95 % Interval']]
        data = [classNamesColumn,
                np.round(self.ClassProportion, 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0], 4),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1], 4),
                np.round(self.ClassProportion * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[0] * self.N, 1),
                np.round(self._confidenceIntervall(self.ClassProportion, self.ClassProportionSSE, 0.05)[1] * self.N, 1)]
        data = [list(x) for x in zip(*data)]
        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans))

        return report


class RegressionPerformance(FlowObject):
    def __init__(self, yT, yP, outputNamesT, outputNamesP):
        import sklearn.metrics

        assert isinstance(yT, np.ndarray)
        assert isinstance(yP, np.ndarray)
        assert yT.ndim == 2
        assert yP.ndim == 2
        assert yT.shape == yP.shape

        self.yP = yP
        self.yT = yT
        self.outputNamesT = outputNamesT
        self.outputNamesP = outputNamesP
        self.residuals = self.yP - self.yT
        self.n = self.yT[0].size

        self.explained_variance_score = [sklearn.metrics.explained_variance_score(self.yT[i], self.yP[i]) for i, _ in
                                         enumerate(outputNamesT)]
        self.mean_absolute_error = [sklearn.metrics.mean_absolute_error(self.yT[i], self.yP[i]) for i, _ in
                                    enumerate(outputNamesT)]
        self.mean_squared_error = [sklearn.metrics.mean_squared_error(self.yT[i], self.yP[i]) for i, _ in
                                   enumerate(outputNamesT)]
        self.median_absolute_error = [sklearn.metrics.median_absolute_error(self.yT[i], self.yP[i]) for i, _ in
                                      enumerate(outputNamesT)]
        self.r2_score = [sklearn.metrics.r2_score(self.yT[i], self.yP[i]) for i, _ in enumerate(outputNamesT)]

    def __getstate__(self):
        return OrderedDict([('yP', self.yP),
                            ('yT', self.yT),
                            ('outputNamesT', self.outputNamesT),
                            ('outputNamesP', self.outputNamesP)])

    @classmethod
    def fromRaster(self, prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Regression)
        assert isinstance(reference, Regression)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask])

        return RegressionPerformance(yP=yP, yT=yT, outputNamesP=prediction.outputNames(),
                                     outputNamesT=reference.outputNames())

    def report(self):
        import matplotlib
        # matplotlib.use('QT4Agg')
        from matplotlib import pyplot

        report = Report('Regression Performance')

        report.append(ReportHeading('Outputs Overview'))
        colHeaders = [['Outputs']]
        colSpans = [[len(self.outputNamesT)]]
        rowHeaders = [['Reference', 'Prediction']]
        data = [self.outputNamesT, self.outputNamesP]

        report.append(ReportTable(data, '', colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders))

        report.append(ReportHeading('Metrics'))

        report.append(ReportParagraph('Number of samples: {}'.format(self.n)))

        colHeaders = [['Outputs'], self.outputNamesT]
        colSpans = [[len(self.outputNamesT)], [1] * len(self.outputNamesT)]
        rowHeaders = [['Explained variance score',
                       'Mean absolute error (MAE)',
                       'Mean squared error (MSE)',
                       'Root MSE (RMSE)',
                       'Median absolute error (MedAE)',
                       'Coefficient of determination (R^2)']]

        data = np.array([np.round(np.array(self.explained_variance_score).astype(float), 4),
                         np.round(np.array(self.mean_absolute_error).astype(float), 4),
                         np.round(np.array(self.mean_squared_error).astype(float), 4),
                         np.round(np.sqrt(np.array(self.mean_squared_error)).astype(float), 4),
                         np.round(np.array(self.median_absolute_error).astype(float), 4),
                         np.round(np.array(self.r2_score).astype(float), 4)])

        report.append(
            ReportTable(data, colHeaders=colHeaders, colSpans=colSpans, rowHeaders=rowHeaders, attribs_align='left'))

        report.append(
            ReportHyperlink(url=r'http://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics',
                            text='See Scikit-Learn documentation for details.'))

        report.append(ReportHeading('Scatter and Residuals Plots'))

        for i, name in enumerate(self.outputNamesT):
            fig, ax = pyplot.subplots(facecolor='white', figsize=(7, 7))
            # prepare 2x2 grid for plotting scatterplot on lower left, and adjacent histograms
            gs = matplotlib.gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 3])

            ax0 = pyplot.subplot(gs[0, 0])
            ax0.hist(self.yT[i], bins=100, edgecolor='None', )
            pyplot.xlim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.tick_params(which='both', direction='out', length=10, pad=10)
            # hide ticks and ticklabels
            ax0.set_xticklabels([])
            ax0.set_ylabel('counts')
            ax0.set_title(name)
            ax0.xaxis.set_ticks_position('bottom')
            ax0.yaxis.set_ticks_position('left')

            # plot only every second tick, starting with the second
            # for label in ax0.get_yticklabels()[1::2]: label.set_visible(False)
            # plot only first and last ticklabel
            # for label in ax0.get_yticklabels()[1:-1]: label.set_visible(False)

            ax1 = pyplot.subplot(gs[1, 1])
            ax1.hist(self.yP[i], orientation='horizontal', bins=100, edgecolor='None')
            pyplot.tick_params(which='both', direction='out', length=10, pad=10)
            pyplot.ylim([np.min(self.yT[i]), np.max(self.yT[i])])
            # hide ticks and ticklabels
            ax1.set_yticklabels([])
            ax1.set_xlabel('counts')
            ax1.yaxis.set_ticks_position('left')
            ax1.xaxis.set_ticks_position('bottom')
            # plot only every second tick, starting with the second
            # for label in ax1.get_xticklabels()[1::2]: label.set_visible(False)
            # plot only first and last ticklabel
            # for label in ax1.get_xticklabels()[1:-1]: label.set_visible(False)

            ax2 = pyplot.subplot(gs[1, 0])
            ax2.scatter(self.yT[i], self.yP[i], s=10, edgecolor='', color='navy')
            pyplot.xlim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.ylim([np.min(self.yT[i]), np.max(self.yT[i])])
            pyplot.tick_params(which='both', direction='out')
            pyplot.xlabel('Observed')
            pyplot.ylabel('Predicted')

            # 1:1 line
            pyplot.plot([np.min(self.yT[i]), np.max(self.yT[i])], [np.min(self.yT[i]), np.max(self.yT[i])],
                        'k-')

            # Colorbar
            # cbaxes = fig.add_axes([0.05, 0.1, 0.05, 0.35])
            # cBar = pyplot.colorbar(sct, ticklocation='left', extend='neither', drawedges=False,cax = cbaxes)
            # cBar.ax.set_ylabel('label')

            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

            fig, ax = pyplot.subplots(facecolor='white', figsize=(7, 5))
            ax.hist(self.residuals[i], bins=100, edgecolor='None')
            ax.set_title(name)
            ax.set_xlabel('Predicted - Observed')
            ax.set_ylabel('Counts')
            fig.tight_layout()
            report.append(ReportPlot(fig))
            pyplot.close()

        return report


class ClusteringPerformance(FlowObject):
    def __init__(self, yT, yP):
        import sklearn.metrics
        assert isinstance(yP, np.ndarray)
        assert isinstance(yT, np.ndarray)
        assert yT.shape == yP.shape
        assert len(yT) == 1 and len(yP) == 1
        self.yP = yP[0]
        self.yT = yT[0]
        self.n = yT.shape[1]
        self.adjusted_mutual_info_score = sklearn.metrics.cluster.adjusted_mutual_info_score(labels_true=self.yT,
                                                                                             labels_pred=self.yP)
        self.adjusted_rand_score = sklearn.metrics.cluster.adjusted_rand_score(labels_true=self.yT, labels_pred=self.yP)
        self.completeness_score = sklearn.metrics.cluster.completeness_score(labels_true=self.yT, labels_pred=self.yP)

    def __getstate__(self):
        return OrderedDict([('yP', self.yP[None]),
                            ('yT', self.yT[None])])

    @staticmethod
    def fromRaster(prediction, reference, mask=None, **kwargs):
        assert isinstance(prediction, Classification)
        assert isinstance(reference, Classification)

        yP, yT = MapCollection(maps=[prediction, reference]).extractAsArray(masks=[prediction, reference, mask],
                                                                            **kwargs)

        return ClusteringPerformance(yP=yP, yT=yT)



    def report(self):
        report = Report('Clustering Performance')
        report.append(ReportHeading('Performance Measures'))
        report.append(ReportParagraph('n = ' + str(self.n)))
        rowHeaders = [['Adjusted Mutual Information', 'Adjusted Rand Score', 'Completeness Score']]
        data = numpy.transpose([[numpy.round(self.adjusted_mutual_info_score, 3),
                                 numpy.round(self.adjusted_rand_score, 3), numpy.round(self.completeness_score, 3)]])
        report.append(ReportTable(data, '', rowHeaders=rowHeaders))
        report.append(ReportHeading('Scikit-Learn Documentation'))
        report.append(
            ReportHyperlink('http://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation',
                            'Clustering Performance Evaluation Overview'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_mutual_info_score.html#sklearn.metrics.adjusted_mutual_info_score',
            'Adjusted Mutual Information'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html#sklearn.metrics.adjusted_rand_score',
            'Adjusted Rand Score'))
        report.append(ReportHyperlink(
            'http://scikit-learn.org/stable/modules/generated/sklearn.metrics.completeness_score.html#sklearn.metrics.completeness_score',
            'Completeness Score'))

        return report


class StringParser():
    class Range():
        def __init__(self, start, end):
            self.start = int(start)
            self.end = int(end)
            self.step = np.sign(end - start)

        def range(self):
            return range(self.start, self.end + self.step, self.step)

    def eval(self, text):
        if text.startswith(r'\eval'):
            return eval(text.replace(r'\eval', ''))
        else:
            raise Exception(r'text must start with "\eval"')

    def range(self, text):
        # try resolve range syntax, e.g. 2-4 as [2,4] or -4--2 as [-4, -2]
        i = text.index('-', 1)
        return self.Range(start=int(text[:i]), end=int(text[i + 1:]))

    def value(self, text):

        # try to evaluate as int or float
        try:
            result = float(text)
            if str(int(text)) == str(result):
                result = int(result)
        except:
            # try to evaluate as range
            try:
                result = self.range(text)
            except:
                result = text
        return result

    def strlist(self, text):
        for c in '''[]{}()'",''':
            text = text.replace(c, ' ')

        if text == '':
            return None
        else:
            return text.split()

    def list(self, text, extendRanges=True):

        # try to evaluate as python expression
        try:
            result = self.eval(text)
            assert isinstance(result, list)
        except:
            strlist = self.strlist(text)
            if strlist is None:
                result = None
            else:
                result = list()
                for strvalue in strlist:
                    value = self.value(strvalue)
                    if isinstance(value, self.Range):
                        if extendRanges:
                            result.extend(value.range())
                        else:
                            result.append((value.start, value.end))
                    else:
                        result.append(value)
        return result


def extractPixels(inputs, masks, grid, **kwargs):
    applier = Applier(defaultGrid=grid, **kwargs)
    for i, input in enumerate(inputs):
        name = 'input' + str(i)
        applier.setFlowInput(name=name, input=input)

    for i, mask in enumerate(masks):
        name = 'mask' + str(i)
        applier.setFlowMask(name=name, mask=mask)

    results = applier.apply(operatorType=_ExtractPixels, inputs=inputs, masks=masks)
    return results


class _ExtractPixels(ApplierOperator):
    def ufunc(self, inputs, masks):

        # calculate overall mask
        marray = self.full(value=True)
        nothingToExtract = False
        for i, mask in enumerate(masks):
            name = 'mask' + str(i)
            imarray = self.flowMaskArray(name=name, mask=mask)
            np.logical_and(marray, imarray, out=marray)
            if not marray.any():
                nothingToExtract = True
                break

        # extract values for all masked pixels
        result = list()
        for i, input in enumerate(inputs):
            name = 'input' + str(i)
            if nothingToExtract:
                zsize = self.flowInputZSize(name=name, input=input)
                dtype = np.uint8
                profiles = np.empty(shape=(zsize, 0), dtype=dtype)
            else:
                array = self.flowInputArray(name=name, input=input)
                profiles = array[:, marray[0]]

            result.append(profiles)
        return result

    @staticmethod
    def aggregate(blockResults, grid, inputs, *args, **kwargs):
        result = list()
        for i, input in enumerate(inputs):
            profilesList = [r[i] for r in blockResults]
            profiles = np.concatenate(profilesList, axis=1)
            result.append(profiles)
        return result


class MetadataEditor(object):

    @staticmethod
    def setClassDefinition(rasterDataset, classDefinition):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert isinstance(classDefinition, ClassDefinition)

        names = ['unclassified'] + classDefinition.names()
        lookup = [0, 0, 0] + list(
            np.array([(c.red(), c.green(), c.blue()) for c in classDefinition.colors()]).flatten())

        rasterDataset.setNoDataValue(value=0)

        # setup in ENVI domain
        rasterDataset.setMetadataItem(key='classes', value=classDefinition.classes() + 1, domain='ENVI')
        rasterDataset.setMetadataItem(key='class names', value=names, domain='ENVI')
        rasterDataset.setMetadataItem(key='file type', value='ENVI Classification', domain='ENVI')
        rasterDataset.setMetadataItem(key='class lookup', value=lookup, domain='ENVI')

        # setup in GDAL data model
        colors = np.array(lookup).reshape(-1, 3)
        colors = [tuple(color) for color in colors]
        band = rasterDataset.band(0)
        band.setCategoryNames(names=names)
        band.setCategoryColors(colors=colors)
        band.setDescription('Classification')

    @classmethod
    def setFractionDefinition(cls, rasterDataset, classDefinition):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert isinstance(classDefinition, ClassDefinition)

        lookup = classDefinition.colorsFlatRGB()
        rasterDataset.setMetadataItem(key='band lookup', value=lookup, domain='ENVI')
        cls.setBandNames(rasterDataset=rasterDataset, bandNames=classDefinition.names())
        rasterDataset.setNoDataValue(value=-1)

    @classmethod
    def setRegressionDefinition(cls, rasterDataset, noDataValues, outputNames):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        rasterDataset.setNoDataValues(values=noDataValues)
        cls.setBandNames(rasterDataset=rasterDataset, bandNames=outputNames)

    @classmethod
    def setBandNames(cls, rasterDataset, bandNames):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        assert len(bandNames) == rasterDataset.zsize()
        rasterDataset.setMetadataItem(key='band names', value=bandNames, domain='ENVI')
        for band, bandName in zip(rasterDataset.bands(), bandNames):
            band.setDescription(value=bandName)

    @classmethod
    def setBandCharacteristics(cls, rasterDataset, bandNames=None, wavelength=None, fwhm=None, wavelengthUnits=None):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        if bandNames is not None:
            cls.setBandNames(rasterDataset=rasterDataset, bandNames=bandNames)
        if wavelength is not None:
            rasterDataset.setMetadataItem(key='wavelength', value=wavelength, domain='ENVI')
        if fwhm is not None:
            rasterDataset.setMetadataItem(key='fwhm', value=fwhm, domain='ENVI')
        if wavelengthUnits is not None:
            rasterDataset.setMetadataItem(key='wavelength units', value=wavelengthUnits, domain='ENVI')

    @classmethod
    def bandNames(cls, rasterDataset):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        return [band.description() for band in rasterDataset.bands()]

    @classmethod
    def bandCharacteristics(cls, rasterDataset):
        assert isinstance(rasterDataset, (RasterDataset, ApplierOutputRaster))
        return {'bandNames': cls.bandNames(rasterDataset=rasterDataset),
                'wavelength': rasterDataset.metadataItem(key='wavelength', domain='ENVI'),
                'fwhm': rasterDataset.metadataItem(key='fwhm', domain='ENVI'),
                'wavelengthUnits': rasterDataset.metadataItem(key='wavelength units', domain='ENVI')}