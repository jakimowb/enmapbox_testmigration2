from osgeo import gdal_array
import numpy as np
import dask.array as da
from dask.delayed import delayed
from hubdc.model import *
import multiprocessing

DEFAULT_XCHUNK = 256
DEFAULT_YCHUNK = 256


def createSlicableRaster(grid, bands=1, gdalType=gdal.GDT_Float32, filename='', format='MEM', options=()):
    dataset = createRaster(grid=grid, bands=bands, gdalType=gdalType, filename=filename, format=format, options=options)
    dataset.close()
    return SlicableRaster(filename=filename, grid=grid)


class SlicableRaster(object):
    def __init__(self, filename, grid=None, **kwargs):

        raster = openRaster(filename=filename, eAccess=gdal.GA_ReadOnly)
        assert isinstance(raster, Raster)
        if grid is None:
            grid = raster.grid()
        assert isinstance(grid, Grid)

        self._filename = filename
        self._grid = grid
        self.shape = (raster.zsize(),) + grid.shape()
        self.dtype = raster.dtype()
        self._noDataValue = raster.noDataValue()
        self._metadataDict = raster.metadataDict()
        self._kwargs = kwargs

    def grid(self):
        return self._grid

    def noDataValue(self):
        return self._noDataValue

    def metadataDict(self):
        return self._metadataDict

    def __getitem__(self, slices):
        ds = openRaster(filename=self._filename, eAccess=gdal.GA_ReadOnly)
        grid, bandIndicies = self._evaluateSlices(slices=slices)
        if len(bandIndicies) == ds.zsize():
            #array = ds.warp(grid=grid, **self._kwargs).readAsArray()
            array = ds.array(grid=grid, **self._kwargs)
        elif len(bandIndicies) == 1:
            array = ds.array(grid=grid, **self._kwargs)[bandIndicies[0]]
        else:
            assert 0 # todo: do not read all bands if only a subset is required

        ds.close()
        return array

    def __setitem__(self, slices, array):
        ds = openRaster(filename=self._filename, eAccess=gdal.GA_Update)
        grid, bandIndicies = self._evaluateSlices(slices=slices)

        # workaround: dask sometimes passes a 4d array, when a 3d array is expected, not sure why this happens
        if array.ndim == 4:
            assert array.shape[0] == 1  # check if it is save to skip the leading dimension
            array = array[0]

        assert array.ndim == 3
        assert len(bandIndicies) == len(array)
        zchunk = len(array)
        for bandIndex in bandIndicies:
            arrayIndex = bandIndex % zchunk
            rb = ds.band(index=bandIndex)
            rb.writeArray(array=array[arrayIndex], grid=grid)
        ds.close()

    def _evaluateSlices(self, slices):
        if len(slices) == 2:
            slices = (slice(0, 1, None),) + slices
        assert len(slices) == 3
        zslice, yslice, xslice = slices
        assert isinstance(yslice, slice)
        assert isinstance(xslice, slice)
        assert yslice.step is None
        assert xslice.step is None
        grid = self._grid.subset(offset=Pixel(x=xslice.start, y=yslice.start),
                                 size=Size(x=xslice.stop - xslice.start,
                                           y=yslice.stop - yslice.start),
                                 trim=True)

        if isinstance(zslice, slice):
            assert zslice.step is None
            bandIndicies = range(zslice.start, zslice.stop)
        elif isinstance(zslice, int):
            bandIndicies = [zslice]
        else:
            assert 0

        return grid, bandIndicies


class SlicableVector(object):
    def __init__(self, filename, grid, layerNameOrIndex=0, dtype=np.float32, noDataValue=None, **kwargs):
        vector = openVector(filename=filename, layerNameOrIndex=layerNameOrIndex, update=False)
        assert isinstance(vector, Vector)
        assert isinstance(grid, Grid)

        self._filename = filename
        self._layerNameOrIndex = layerNameOrIndex
        self._grid = grid
        self.shape = (1,) + grid.shape()
        self.dtype = dtype
        self._noDataValue = noDataValue
        self._kwargs = kwargs
        self._metadataDict = {'': kwargs}

    def grid(self):
        return self._grid

    def noDataValue(self):
        return self._noDataValue

    def metadataDict(self):
        return self._metadataDict

    def __getitem__(self, slices):
        ds = openVector(filename=self._filename, layerNameOrIndex=self._layerNameOrIndex, update=False)
        grid, return2d = self._evaluateSlices(slices=slices)

        array = ds.rasterize(grid=grid, eType=gdal_array.NumericTypeCodeToGDALTypeCode(self.dtype), noDataValue=self.noDataValue(),
                             **self._kwargs).readAsArray()
        assert array.ndim == 3
        if return2d:
            array = array[0]
        ds.close()
        return array

    def _evaluateSlices(self, slices):
        assert len(slices) == 3
        zslice, yslice, xslice = slices
        grid = self._grid.subset(offset=Pixel(x=xslice.start, y=yslice.start),
                                 size=Size(x=xslice.stop - xslice.start, y=yslice.stop - yslice.start),
                                 trim=True)
        return2d = isinstance(zslice, int)
        return grid, return2d

da.corrcoef
class DaskRaster(da.Array):
    def __new__(cls, daskArray, grid=None, noDataValue=None, metadataDict=None):
        assert len(daskArray.shape) == 3
        self = super(DaskRaster, cls).__new__(cls, daskArray.dask, daskArray.name, daskArray.chunks, daskArray.dtype,
                                              shape=daskArray.shape)
        if isinstance(daskArray, DaskRaster):
            grid = daskArray.grid()
        self.setGrid(grid=grid)
        self.setNoDataValue(noDataValue=noDataValue)
        self.setMetadataDict(metadataDict=metadataDict)
        return self

    def __repr__(self):
        return '{cls}(daskArray={daskArray},\n  grid={grid},\n  noDataValue={noDataValue},\n  metadataDict={metadataDict})'.format(
            cls=self.__class__.__name__,
            daskArray=da.Array.__repr__(self),
            grid=repr(self.grid()),
            noDataValue=repr(self.noDataValue()),
            metadataDict=repr(self.metadataDict()))

    @staticmethod
    def stack(rasters):
        assert len(rasters) > 0
        grid = rasters[0].grid()
        for raster in rasters:
            assert isinstance(raster, DaskRaster)
            raster.grid().equal(other=grid)

        return DaskRaster(da.stack([raster[0] for raster in rasters]), grid=grid)

    def astype(self, dtype, **kwargs):
        return DaskRaster(da.Array.astype(self, dtype=dtype, **kwargs), grid=self.grid())

    def grid(self):
        assert isinstance(self._grid, Grid)
        return self._grid

    def noDataValue(self, default=None):
        if self._noDataValue is None:
            return default
        else:
            return self._noDataValue

    def metadataDict(self):
        return self._metadataDict

    def setGrid(self, grid):
        assert isinstance(grid, Grid)
        self._grid = grid

    def setNoDataValue(self, noDataValue):
        self._noDataValue = noDataValue

    def setMetadataDict(self, metadataDict):
        if metadataDict is None:
            metadataDict = dict()
        assert isinstance(metadataDict, dict)
        self._metadataDict = metadataDict

    def buildMask(self, keep, inverse=True):
        mask = da.stack([self == value for value in keep]).any(axis=0)
        if inverse:
            mask = da.logical_not(mask)
        return DaskRaster(mask, grid=self.grid())

    def fillnan(self, value, inplace=False):
        if inplace:
            raster = self
        else:
            raster = self.copy()

        raster[da.isnan(raster)] = value
        return DaskRaster(raster, grid=self.grid())

    def sample(self, mask):
        assert len(mask.shape) == 3
        assert mask.dtype == np.bool
        assert mask.shape[0] == 1
        assert mask.shape[1:] == self.shape[1:]
        return [self[i][mask[0]] for i in range(self.shape[0])]

    def nanmean(self):
        return DaskRaster(da.nanmean(self, axis=0, keepdims=True), grid=self.grid())

    def nanstd(self):
        return DaskRaster(da.nanstd(self, axis=0, keepdims=True), grid=self.grid())

    def isnan(self):
        return DaskRaster(da.isnan(self), grid=self.grid())


def openDaskRaster(filename, grid=None, xchunk=None, ychunk=None, name=None, resampleAlg=gdal.GRA_NearestNeighbour, **kwargs):

    slicableRaster = SlicableRaster(filename=filename, grid=grid, resampleAlg=resampleAlg, **kwargs)
    zchunk = slicableRaster.shape[0]
    if xchunk is None:
        xchunk = DEFAULT_XCHUNK
    if ychunk is None:
        ychunk = DEFAULT_YCHUNK

    if name is None:
        name = basename(filename)

    daskArray = da.from_array(x=slicableRaster, chunks=(zchunk, ychunk, xchunk), name=name)
    return DaskRaster(daskArray=daskArray, grid=slicableRaster.grid(), noDataValue=slicableRaster.noDataValue(),
                      metadataDict=slicableRaster.metadataDict())


def openDaskVector(filename, grid, layerNameOrIndex=0, xchunk=None, ychunk=None, name=None,
                   dtype=np.float32, noDataValue=None,
                   initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filter=None):
    slicableVector = SlicableVector(filename=filename, layerNameOrIndex=layerNameOrIndex, grid=grid,
                                    dtype=dtype, noDataValue=noDataValue,
                                    initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute,
                                    allTouched=allTouched, filter=filter)
    zchunk = 1
    if xchunk is None:
        xchunk = DEFAULT_XCHUNK
    if ychunk is None:
        ychunk = DEFAULT_YCHUNK

    daskArray = da.from_array(x=slicableVector, chunks=(zchunk, ychunk, xchunk), name=name)
    return DaskRaster(daskArray=daskArray, grid=slicableVector.grid(), noDataValue=slicableVector.noDataValue(),
                      metadataDict=slicableVector.metadataDict())


def storeDaskRasters(rasters, filenames, format='ENVI', options=()):
    assert isinstance(rasters, (list, tuple))
    assert isinstance(filenames, (list, tuple))

    targets = list()
    for i, (raster, filename) in enumerate(zip(rasters, filenames)):
        assert isinstance(raster, DaskRaster)
        if raster.ndim == 2:
            raster = raster[None]
        assert raster.ndim == 3

        gdalType = gdal_array.NumericTypeCodeToGDALTypeCode(raster.dtype)
        target = createSlicableRaster(grid=raster.grid(), bands=raster.shape[0], gdalType=gdalType,
                                      filename=filename, format=format, options=options)
        ds = openRaster(filename=filename)
        ds.setNoDataValue(raster.noDataValue())
        ds.setMetadataDict(raster.metadataDict())
        targets.append(target)
        rasters[i] = raster
    lock = multiprocessing.Manager().Lock()
    da.store(sources=rasters, targets=targets, lock=lock)
    for filename in filenames:
        ds = openRaster(filename=filename)
        ds.writeENVIHeader()
        ds.close()

@delayed
def estimatorFit(estimator, X, y):
    zsize = len(X)
    X = numpy.array(X).reshape(zsize, -1).T
    y = numpy.array(y).T
    if y.shape[1] == 1:
        y = y.ravel()
    #print('sample X:', X.shape)
    #print('sample y:', y.shape)

    estimator.fit(X=X, y=y)
    return estimator

def _mapEstimatorPredict(estimator, array, marray=None, noDataValue=0):
    assert isinstance(array, np.ndarray)
    zsize, ysize, xsize = array.shape
    if marray is None:
        marray = np.full(shape=(ysize, xsize), fill_value=True)
    assert isinstance(marray, np.ndarray)
    assert marray.dtype == np.bool

    if marray.ndim == 3:
        assert marray.shape[0] == 1
        marray = marray[0]
    assert marray.ndim == 2

    X = array[:, marray].T
#    X = array.reshape((zsize, -1)).T
    y = estimator.predict(X=X)

    prediction = np.full(shape=(1, ysize, xsize), fill_value=noDataValue)
    prediction[:, marray] = y
    return prediction

def estimatorPredict(estimator, raster, mask=None, dtype=np.uint8):
    assert isinstance(raster, DaskRaster)
    assert isinstance(mask, (type(None), da.Array))
    chunks = (1,) + raster.chunks[1:]
    daskArray = da.map_blocks(_mapEstimatorPredict, estimator, raster, mask, dtype=dtype, chunks=chunks)
    return DaskRaster(daskArray, grid=raster.grid())
