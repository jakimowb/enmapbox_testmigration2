"""
Basic tools for setting up a function to be applied over a raster processing chain.
The :class:`~hubdc.applier.Applier` class is the main point of entry in this module.

See :doc:`ApplierExamples` for more information.

"""

from __future__ import print_function
import sys, os, pickle
from collections import OrderedDict
from multiprocessing import Pool
from timeit import default_timer as now
import numpy
from osgeo import gdal, osr, ogr
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from hubdc.model import *  # Open, OpenLayer, CreateFromArray, Dataset, Band, PixelGrid, Projection
import hubdc.model  # needed for sphinx
from hubdc.writer import Writer, WriterProcess, QueueMock
from hubdc.progressbar import CUIProgressBar


class Enum(object):
    '''Enumeration types.'''

    class AutoExtent(object):
        '''Options for automatic extent calculation.'''
        union = 0
        intersection = 1

    class AutoResolution(object):
        '''Options for automatic resolution calculation.'''
        minimum = 0
        maximum = 1
        average = 2


class Default(object):
    '''Defaults values for various settings used inside an applier processing chain.'''

    autoExtent = Enum.AutoExtent.intersection
    autoResolution = Enum.AutoResolution.minimum
    nworker = None
    nwriter = None
    blockSize = Size(x=256, y=256)
    writeENVIHeader = True
    format = 'ENVI'
    options = dict()
    options['ENVI'] = ['INTERLEAVE=BSQ']
    options['GTiff'] = ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256',
                        'SPARSE_OK=TRUE', 'BIGTIFF=YES']

    class GDALEnv(object):
        cacheMax = 100 * 2 ** 20
        swathSize = 100 * 2 ** 20
        disableReadDirOnOpen = True
        maxDatasetPoolSize = 100

    class GDALWarp(object):
        errorThreshold = 0.
        memoryLimit = 100 * 2 ** 20
        multithread = False


class ApplierInputRaster(object):
    '''Class for handling input raster dataset.'''

    @classmethod
    def fromDataset(cls, dataset):
        '''Create an input raster from an :class:`~hubdc.model.Dataset`.'''

        assert isinstance(dataset, Dataset)
        applierInputRaster = ApplierInputRaster(filename='')
        applierInputRaster._dataset = dataset
        return applierInputRaster

    def __init__(self, filename):
        '''

        :param filename: filename
        '''

        self.filename = filename
        self._dataset = None
        self._operator = None

    def __repr__(self):
        return '{cls}(filename={filename})'.format(cls=self.__class__.__name__, filename=str(self.filename))

    @property
    def operator(self):
        '''Returns the :class:`~hubdc.applier.ApplierOperator` object.'''
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        '''Sets the :class:`~hubdc.applier.ApplierOperator` object.'''
        assert isinstance(value, ApplierOperator)
        self._operator = value

    @property
    def dataset(self):
        '''Returns the :class:`~hubdc.model.Dataset` object associated with the input raster.'''
        if self._dataset is None:
            self._dataset = Open(filename=self.filename)
        assert isinstance(self._dataset, Dataset)
        return self._dataset

    def _freeUnpickableResources(self):
        self._dataset = None

    def getImageArray(self, overlap=0, resampleAlg=gdal.GRA_NearestNeighbour, noData=None,
                      errorThreshold=Default.GDALWarp.errorThreshold,
                      warpMemoryLimit=Default.GDALWarp.memoryLimit,
                      multithread=Default.GDALWarp.multithread,
                      grid=None):
        '''
        Returns image data as 3-d numpy array of shape = (bands, ysize, xsize).

        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param resampleAlg: GDAL resampling algorithm, e.g. gdal.GRA_NearestNeighbour
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :param warpMemoryLimit: size of working buffer in bytes
        :param multithread: whether to multithread computation and I/O operations
        :param grid: explicitly set the :class:`~hubdc.model.Grid`, for which image data is returned
        '''

        if grid is None:
            dstGrid = self.operator.subgrid.pixelBuffer(buffer=overlap)
        else:
            dstGrid = grid

        if self.operator.subgrid.equalProjection(self.dataset.grid):
            datasetResampled = self.dataset.translate(dstGrid=dstGrid, dstName='', format='MEM',
                                                      resampleAlg=resampleAlg,
                                                      noData=noData)
        else:
            datasetResampled = self.dataset.warp(dstGrid=dstGrid, dstName='', format='MEM',
                                                 resampleAlg=resampleAlg,
                                                 errorThreshold=errorThreshold,
                                                 warpMemoryLimit=warpMemoryLimit,
                                                 multithread=multithread,
                                                 srcNodata=noData)
        array = datasetResampled.readAsArray()
        datasetResampled.close()
        return array

    def getBandArray(self, indicies, overlap=0, resampleAlg=gdal.GRA_NearestNeighbour, noData=None,
                     errorThreshold=Default.GDALWarp.errorThreshold,
                     warpMemoryLimit=Default.GDALWarp.memoryLimit,
                     multithread=Default.GDALWarp.multithread):
        '''
        Returns a band subset of the image data as 3-d numpy array of shape = (indicies, ysize, xsize).

        :param indicies: list of band indicies
        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param resampleAlg: GDAL resampling algorithm, e.g. gdal.GRA_NearestNeighbour
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :param warpMemoryLimit: size of working buffer in bytes
        :param multithread: whether to multithread computation and I/O operations
        '''

        if isinstance(indicies, int):
            indicies = [indicies]

        bandList = [i + 1 for i in indicies]
        dstGrid = self.operator.subgrid.pixelBuffer(buffer=overlap)
        if self.operator.subgrid.equalProjection(self.dataset.grid):
            datasetResampled = self.dataset.translate(dstGrid=dstGrid, dstName='', format='MEM',
                                                      bandList=bandList,
                                                      resampleAlg=resampleAlg,
                                                      noData=noData)
        else:
            selfGridReprojected = self.operator.subgrid.reproject(self.dataset.grid)
            selfGridReprojectedWithBuffer = selfGridReprojected.pixelBuffer(buffer=1 + overlap)

            datasetClipped = self.dataset.translate(dstGrid=selfGridReprojectedWithBuffer, dstName='',
                                                    format='MEM',
                                                    bandList=bandList,
                                                    noData=noData)

            datasetResampled = datasetClipped.warp(dstGrid=dstGrid, dstName='', format='MEM',
                                                   resampleAlg=resampleAlg,
                                                   errorThreshold=errorThreshold,
                                                   warpMemoryLimit=warpMemoryLimit,
                                                   multithread=multithread,
                                                   srcNodata=noData)
            datasetClipped.close()

        array = datasetResampled.readAsArray()
        datasetResampled.close()
        return array

    def getFractionArray(self, categories, overlap=0, noData=None, index=None):
        '''
        Returns a stack of category fractions for the given ``categories`` as a 3-d numpy array of shape = (categories, ysize, xsize).

        :param categories: list of categories of interest
        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param index: index to the band holding the categories
        '''

        assert self.dataset.zsize == 1 or index is not None
        if index is None:
            index = 0
        grid = self.operator.subgrid.pixelBuffer(buffer=overlap)

        # create tmp dataset with binarized categories in original resolution
        gridInSourceProjection = grid.reproject(self.dataset.grid)
        tmpDataset = self.dataset.translate(dstGrid=gridInSourceProjection, dstName='', format='MEM',
                                            noData=noData, bandList=[index + 1])
        tmpArray = tmpDataset.readAsArray()

        binarizedArray = [numpy.float32(tmpArray[0] == category) for category in categories]
        binarizedDataset = CreateFromArray(pixelGrid=gridInSourceProjection, array=binarizedArray,
                                           dstName='', format='MEM', creationOptions=[])

        binarizedInputRaster = ApplierInputRaster.fromDataset(dataset=binarizedDataset)
        binarizedInputRaster.operator = self.operator

        array = binarizedInputRaster.getImageArray(overlap=overlap, resampleAlg=gdal.GRA_Average)
        return array

    def getImageSample(self, mask, resampleAlg=gdal.GRA_NearestNeighbour, noData=None,
                       errorThreshold=Default.GDALWarp.errorThreshold,
                       warpMemoryLimit=Default.GDALWarp.memoryLimit,
                       multithread=Default.GDALWarp.multithread):
        '''
        Returns all pixel profiles for which ``mask`` is True as a 2-d numpy array of shape = (bands, samples).

        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param resampleAlg: GDAL resampling algorithm, e.g. gdal.GRA_NearestNeighbour
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :param warpMemoryLimit: size of working buffer in bytes
        :param multithread: whether to multithread computation and I/O operations
        :param grid: explicitly set the :class:`~hubdc.model.Grid`, for which image data is returned
        '''

        assert isinstance(mask, numpy.ndarray)
        assert mask.dtype == numpy.bool
        assert mask.ndim == 3
        assert mask.shape[0] == 1
        assert mask.shape[1:] == self.operator.subgrid.shape

        ys, xs = numpy.indices(mask.shape[1:])[:, mask[0]]
        profiles = list()
        for y, x in zip(ys, xs):
            grid = self.operator.subgrid.subsetPixelWindow(xoff=x, yoff=y, width=1, height=1)
            profiles.append(self.getImageArray(resampleAlg=resampleAlg, noData=noData, errorThreshold=errorThreshold,
                                               warpMemoryLimit=warpMemoryLimit, multithread=multithread, grid=grid))
        if len(profiles) != 0:
            profiles = numpy.hstack(profiles)[:, :, 0]
        else:
            profiles = numpy.empty((0))
        return profiles

    def getMetadataItem(self, key, domain):
        """Return a metadata item."""
        return self.dataset.getMetadataItem(key=key, domain=domain)

    def getMetadataDict(self):
        """Return metadata as a dictionary."""
        meta = dict()
        for domain in self.dataset.getMetadataDomainList():
            meta[domain] = dict()
            for key in self.dataset.getMetadataDomain(domain):
                meta[domain][key] = self.getMetadataItem(key=key, domain=domain)
        return meta

    def getNoDataValue(self, default=None):
        '''Return single image no data value. Only valid to use if all bands have the same ne data value.'''
        return self.dataset.getNoDataValue(default=default)

    def getNoDataValues(self, default=None):
        """Return band no data values."""
        return self.dataset.getNoDataValues(default=default)


class ApplierInputVector(object):
    '''Class for handling the vector dataset given by it's ``filename`` and ``layerNameOrIndex``.'''

    def __init__(self, filename, layerNameOrIndex=0):
        '''

        :param filename: filename
        :param layerNameOrIndex: layer name or index
        :type layerNameOrIndex: str or int
        '''

        self.filename = filename
        self.layerNameOrIndex = layerNameOrIndex
        self._layer = None
        self._dataset = None
        self._operator = None

    def __repr__(self):
        return '{cls}(filename={filename}, layerNameOrIndex={layerNameOrIndex})'.format(
            cls=self.__class__.__name__,
            filename=str(self.filename),
            layerNameOrIndex=repr(self.layerNameOrIndex))

    @property
    def operator(self):
        '''Returns the :class:`~hubdc.applier.ApplierOperator` object.'''
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        '''Set the :class:`~hubdc.applier.ApplierOperator` object.'''
        assert isinstance(value, ApplierOperator)
        self._operator = value

    @property
    def layer(self):
        '''Return the :class:`~hubdc.model.Layer` object.'''
        if self._layer is None:
            self._layer = OpenLayer(filename=self.filename, layerNameOrIndex=self.layerNameOrIndex, update=False)
        return self._layer

    def _rasterize(self, initValue, burnValue, burnAttribute, allTouched, filterSQL, overlap, dtype, xRes, yRes):

        grid = self.operator.subgrid.pixelBuffer(buffer=overlap)
        gridOversampled = grid.newResolution(xRes=xRes, yRes=yRes)

        dataset = self.layer.rasterize(dstGrid=gridOversampled, eType=NumericTypeCodeToGDALTypeCode(dtype),
                                       initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute,
                                       allTouched=allTouched,
                                       filter=filterSQL, dstName='', format='MEM', creationOptions=[])
        raster = ApplierInputRaster.fromDataset(dataset=dataset)
        raster.operator = self.operator
        return raster

    def getImageArray(self, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, overlap=0,
                      dtype=numpy.float32):
        '''Returns the vector rasterization of the current block in form of a 3-d numpy array of shape = (1, ysize, xsize).

        :param initValue: value to pre-initialize the output array
        :param burnValue: value to burn into the output array for all objects; exclusive with ``burnAttribute``
        :param burnAttribute: identifies an attribute field on the features to be used for a burn-in value; exclusive with ``burnValue``
        :param allTouched: whether to enable that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :param filterSQL: set an SQL WHERE clause which will be used to filter vector features
        :param overlap: the number of pixels to additionally read along each spatial dimension
        '''

        raster = self._rasterize(initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute,
                                 allTouched=allTouched, filterSQL=filterSQL, overlap=overlap, dtype=dtype,
                                 xRes=self.operator.subgrid.xRes, yRes=self.operator.subgrid.yRes)
        return raster.dataset.readAsArray()

    def getFractionArray(self, categories, categoryAttribute=None, oversampling=10, xRes=None, yRes=None, overlap=0):
        '''Returns aggregated category fractions of the current block in form of a 3d numpy array of shape = (categories, ysize, xsize).

        :param categories: list of categories (numbers or names)
        :param categoryAttribute: attribute field on the features holding the categories
        :param oversampling: factor defining the relative degree of rasterization detail compared to the target resolution. If for example the target resolution is 30m and the oversampling factor is 10, then the categories are first rasterized at 3m, and finally aggregated to the target resolution.
        :param overlap: the number of pixels to additionally read along each spatial dimension
        '''

        if xRes is None:
            xRes = self.operator.subgrid.xRes / float(oversampling)
        if yRes is None:
            yRes = self.operator.subgrid.yRes / float(oversampling)

        array = list()
        for category in categories:
            filterSQL = str('"' + categoryAttribute + '" = ' + "'" + str(category) + "'")
            oversampledRaster = self._rasterize(initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                                                filterSQL=filterSQL,
                                                overlap=overlap * oversampling, dtype=numpy.float32,
                                                xRes=xRes, yRes=yRes)
            array.append(oversampledRaster.getImageArray(overlap=overlap, resampleAlg=gdal.GRA_Average))

        return numpy.vstack(array)


class ApplierOutputRaster(object):
    '''Class for creating and handling an output raster dataset.'''

    def __init__(self, filename, format=None, creationOptions=None):
        '''
        :param filename: destination filename for output raster
        :param format: GDAL file format, e.g. 'ENVI' or 'GTiff', also see http://www.gdal.org/formats_list.html.
        :type format: str
        :param creationOptions: GDAL creation options; e.g. ``['INTERLEAVE=BSQ']`` for ENVI band interleaved,
                                or ``['INTERLEAVE=BAND', 'TILED=YES', 'COMPRESS=LZW']`` for GTiff band interleaved, tiled and LZW compressed.
                                For ENVI and GTiff files also see http://www.gdal.org/frmt_various.html#ENVI and http://www.gdal.org/frmt_gtiff.html.

        :type creationOptions: list of str
        '''
        self._filename = filename
        if format is None:
            format = Default.FORMAT
        self.format = format
        if creationOptions is None:
            creationOptions = Default.CREATIONOPTIONS.get(self.format, [])
        self.creationOptions = creationOptions
        self._operator = None
        self._writerQueue = None
        self._bands = None

    def initialize(self, bands):
        """Specify the number of output bands. This is only required if the output is written band-wise."""
        self._bands = bands

    @property
    def filename(self):
        '''Returns the filename.'''
        return self._filename

    @property
    def operator(self):
        '''Returns the :class:`~hubdc.applier.ApplierOperator` object.'''

        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        '''Set the :class:`~hubdc.applier.ApplierOperator` object.'''

        assert isinstance(value, ApplierOperator)
        self._operator = value

    def getFlatList(self):
        '''Returns itself inside a list, i.e. ``[self]``.'''

        return [self]

    def getBand(self, index):
        '''Returns the :class:`~hubdc.applier.ApplierOutputRasterBand` for the given ``index``.'''

        if self._bands is None:
            raise Exception(
                'Output raster is not initialized. Use ApplierOutputRaster.initialize(bands) to specify the number of output bands.')
        return ApplierOutputRasterBand(parent=self, bandNumber=index + 1)

    def getBandIterator(self):
        '''Returns an iterator over all :class:`~hubdc.applier.ApplierOutputRasterBand`'s.'''

        for index in range(self._bands):
            yield self.getBand(index=index)

    def setImageArray(self, array, overlap=0):
        """
        Write data to the output raster.

        :param array: 3-d numpy array of shape = (bands, ysize, xsize) or 2-d numpy array of shape = (ysize, xsize)
        :param overlap: the amount of margin (number of pixels) to be removed from the image data block in each direction;
                        this is useful when the overlap keyword was also used during data reading.
        """

        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        self._writerQueue.put(
            (Writer.WRITE_IMAGEARRAY, self.filename, array, self.operator.subgrid, self.operator.grid,
             self.format, self.creationOptions))

        self.initialize(bands=len(array))

        return self

    def setMetadataItem(self, key, value, domain):
        '''Set image metadata item.'''

        self._callImageMethod(method=Dataset.setMetadataItem, key=key, value=value, domain=domain)

    def setMetadataDict(self, metadataDict):
        '''
        Set metadata dictionary.

        :param metadataDict: dictionary of dictionaries for different metadata domains, e.g. ``{'ENVI': {'wavelength' : [482, 561, 655, 865, 1609, 2201], 'wavelength_units' : 'nanometers', 'band_names' : ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']}}``
        '''

        assert isinstance(metadataDict, dict)
        for domain in metadataDict:
            assert isinstance(metadataDict[domain], dict)
            for key, value in metadataDict[domain].items():
                self.setMetadataItem(key=key, value=value, domain=domain)

    def setNoDataValue(self, value):
        """Set no data value to all bands."""
        self._callImageMethod(method=Dataset.setNoDataValue, value=value)

    def _callImageMethod(self, method, **kwargs):
        if self.operator.isFirstBlock():
            self._writerQueue.put((Writer.CALL_IMAGEMETHOD, self.filename, method, kwargs))


class ApplierOutputRasterBand(object):
    '''Class for handling an output raster band dataset.'''

    def __init__(self, parent, bandNumber):
        '''For internal use only.'''
        assert isinstance(parent, ApplierOutputRaster)
        self.parent = parent
        self.bandNumber = bandNumber

    def setArray(self, array, overlap=0):
        '''
        Write data to the output raster band.

        :param array: 3-d numpy array of shape = (1, ysize, xsize) or 2-d numpy array of shape = (ysize, xsize)
        :param overlap: the amount of margin (number of pixels) to be removed from the image data block in each direction;
                        this is useful when the overlap keyword was also used during data reading.
        '''
        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        assert array.shape[0] == 1

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        self.parent._writerQueue.put((Writer.WRITE_BANDARRAY, self.parent.filename, array, self.bandNumber,
                                      self.parent._bands, self.parent.operator.subgrid,
                                      self.parent.operator.grid,
                                      self.parent.format, self.parent.creationOptions))
        return self

    def _callMethod(self, method, **kwargs):
        if self.parent.operator.isFirstBlock():
            self.parent._writerQueue.put(
                (Writer.CALL_BANDMETHOD, self.parent.filename, self.bandNumber, method, kwargs))

    def setDescription(self, value):
        '''Set band description.'''
        self._callMethod(method=Band.setDescription, value=value)

    def setMetadataItem(self, key, value, domain=''):
        """Set metadata item."""
        self._callMethod(method=Band.setMetadataItem, key=key, value=value, domain=domain)

    def setNoDataValue(self, value):
        """Set no data value."""
        self._callMethod(method=Band.setNoDataValue, value=value)


class _ApplierIOGroup(object):
    def __init__(self):
        self.items = dict()
        self._operator = None

    def __repr__(self, key='ApplierIOGroup()', indent=0):
        space = 2
        result = '{indent}{key}\n'.format(indent=' ' * indent, key=key)
        for k, v in self.items.items():
            if isinstance(v, _ApplierIOGroup):
                result += v.__repr__(key=k, indent=indent + space)
            else:
                result += '{indent}{k} : '.format(indent=' ' * (indent + space), k=k)
                result += repr(v) + '\n'
        return result

    @property
    def operator(self):
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        assert isinstance(value, ApplierOperator)
        self._operator = value
        for item in self.items.values():
            item.operator = self._operator

    def _freeUnpickableResources(self):
        for item in self.items.values():
            item._freeUnpickableResources()

    def _getFlatValues(self):
        result = list()
        for value in self.items.values():
            if isinstance(value, self.__class__):
                result.extend(value._getFlatValues())
            else:
                result.append(value)
        return result

    def _getFlatKeys(self):
        result = list()
        for key, value in self.items.items():
            if isinstance(value, self.__class__):
                result.extend(['{}/{}'.format(key, key2) for key2 in value._getFlatKeys()])
            else:
                result.append(key)
        return result

    def setGroup(self, key, value):
        assert isinstance(value, self.__class__)

        keys = key.split('/')
        subgroup = self
        for k in keys[:-1]:
            subgroup.items[k] = subgroup.items.get(k, self.__class__())
            subgroup = subgroup.items[k]
        k = keys[-1]
        subgroup.items[k] = value
        return subgroup.items[k]

    def getGroup(self, key):
        groupkeys = key.split('/')
        group = self
        for groupkey in groupkeys:
            group = group.items[groupkey]
        assert isinstance(group, self.__class__)
        return group

    def _setItem(self, key, value):
        subkeys = key.split('/')
        groupkeys, iokey = subkeys[:-1], subkeys[-1]
        group = self
        for groupkey in groupkeys:
            group.items[groupkey] = group.items.get(groupkey, self.__class__())
            group = group.items[groupkey]
        group.items[iokey] = value
        return group.items[iokey]

    def _getItem(self, key):
        subkeys = key.split('/')
        groupkeys, iokey = subkeys[:-1], subkeys[-1]
        group = self
        for groupkey in groupkeys:
            group = group.items[groupkey]
        value = group.items[iokey]
        return value


class ApplierInputRasterGroup(_ApplierIOGroup):
    '''Container for :class:`~hubdc.applier.ApplierInputRaster` and :class:`~hubdc.applier.ApplierInputRasterGroup` objects.'''

    @classmethod
    def fromFolder(cls, folder, extensions, ufunc=None):
        '''
        Returns an input raster group containing all input rasters that are located relativ to the given ``folder``,
        matches one of the file ``extensions``, and (optionally) matches the user defined filter ``ufunc(dirname, basename, extension)``.
        In the result, the file system folder structure is preserved.

        :param folder: root folder
        :param extensions: only rasters that matches one of the given extensions are included, e.g. ['', '.bsq', '.tif', '.vrt'].
        :param ufunc: function of form ``ufunc(dirname, basename, extension)``; only files that pass the filter function (i.e. return True) are included
        '''
        assert isinstance(extensions, list)
        off = len(os.path._abspath_split(folder)[2])
        group = ApplierInputRasterGroup()
        for root, dirs, files in os.walk(folder):
            key = '/'.join(os.path._abspath_split(root)[2][off:])
            if key == '':
                subgroup = group
            else:
                subgroup = group.getGroup(key=key)
            for dir in dirs:
                subgroup.setGroup(key=dir, value=ApplierInputRasterGroup())
            for file in files:
                fileBasenameWithoutExtension, fileExtension = os.path.splitext(file)
                for extension in extensions:
                    if extension != '': assert extension[0] == '.'
                    if fileExtension.lower() != extension.lower():
                        continue
                    if ufunc is not None:
                        if not ufunc(dirname=root, basename=fileBasenameWithoutExtension, extension=fileExtension):
                            continue
                    subgroup.setRaster(key=fileBasenameWithoutExtension,
                                       value=ApplierInputRaster(filename=os.path.join(root, file)))
        return group

    @staticmethod
    def fromIndex(index):
        '''Returns an input raster group containing all input rasters contained in the :class:`~hubdc.applier.ApplierInputRasterIndex` given by ``index``.'''

        assert isinstance(index, ApplierInputRasterIndex)
        group = ApplierInputRasterGroup()
        for key, filename, extent in zip(index.key, index.filename, index.extent):
            group.setRaster(key=key, value=ApplierInputRaster(filename=filename))
        return group

    def setRaster(self, key, value):
        '''Add an :class:`~hubdc.applier.ApplierInputRaster` given by ``value`` and named ``key``.'''

        assert isinstance(value, ApplierInputRaster)
        return _ApplierIOGroup._setItem(self, key=key, value=value)

    def getRaster(self, key):
        '''Returns the :class:`~hubdc.applier.ApplierInputRaster` named ``key``.'''

        value = _ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierInputRaster)
        return value

    def getFlatRasters(self):
        '''Returns an iterator over all contained :class:`~hubdc.applier.ApplierInputRaster`'s. Traverses the group structure recursively.'''
        for input in _ApplierIOGroup._getFlatValues(self):
            assert isinstance(input, ApplierInputRaster)
            yield input

    def getFlatRasterKeys(self):
        '''Returns an iterator over the keys of all contained :class:`~hubdc.applier.ApplierInputRaster`'s. Traverses the group structure recursively.'''
        for key in _ApplierIOGroup._getFlatKeys(self):
            yield key

    def getGroups(self):
        '''Returns an iterator over all directly contained :class:`~hubdc.applier.ApplierInputRasterGroups`'s. No recursion.'''

        for v in self.items.values():
            if isinstance(v, ApplierInputRasterGroup):
                yield v

    def getGroupKeys(self):
        '''Returns an iterator over the keys of all directly contained :class:`~hubdc.applier.ApplierInputRasterGroups`'s. No recursion.'''

        for k, v in self.items.items():
            if isinstance(v, ApplierInputRasterGroup):
                yield k

    def getRasters(self):
        '''Returns an iterator over all directly contained :class:`~hubdc.applier.ApplierInputRaster`'s. No recursion.'''

        for v in self.items.values():
            if isinstance(v, ApplierInputRaster):
                yield v

    def getRasterKeys(self):
        '''Returns an iterator over the keys of all directly contained :class:`~hubdc.applier.ApplierInputRaster`'s. No recursion.'''

        for k, v in self.items.items():
            if isinstance(v, ApplierInputRaster):
                assert isinstance(k, str)
                yield k

    def findRaster(self, ufunc=lambda key, raster: False):
        '''Returns the first :class:`~hubdc.applier.ApplierInputRaster` for that the user defined function ``ufunc(key, raster)`` matches.
        Returns None in case of no match.'''

        for key in self.getRasterKeys():
            raster = self.getRaster(key=key)
            if ufunc(key=key, raster=raster):
                return raster
        return None

    def findRasterKey(self, filter=lambda key, raster: False):
        '''Returns the first key for that the ``filter`` function matches, or None in case of no match.'''

        for key in self.getRasterKeys():
            raster = self.getRaster(key=key)
            if filter(key=key, raster=raster):
                return key
        return None


class ApplierInputRasterIndex(object):
    WGS84PROJECTION = Projection.fromEPSG(epsg=4326)

    def __init__(self):
        self.key = list()
        self.filename = list()
        self.extent = list()

    def __repr__(self):

        result = 'ApplierInputRasterIndex\n'
        for key, filename, extent in zip(self.key, self.filename, self.extent):
            result += '  {} : {} {}\n'.format(key, filename, extent)
        return result

    @staticmethod
    def fromFolder(folder, extensions, ufunc=None):
        group = ApplierInputRasterGroup.fromFolder(folder=folder, extensions=extensions, ufunc=ufunc)
        index = ApplierInputRasterIndex()
        for key in group.getFlatRasterKeys():
            index.insertRaster(key=key, raster=group.getRaster(key=key))
        return index

    @staticmethod
    def unpickle(filename):
        with open(filename, 'rb') as f:
            index = pickle.load(file=f)
        assert isinstance(index, ApplierInputRasterIndex)
        return index

    def pickle(self, filename):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(obj=self, file=f, protocol=1)

    def insertRaster(self, key, raster):
        assert isinstance(raster, ApplierInputRaster)
        transformation = Transformation(sourceProjection=raster.dataset.projection,
                                        targetProjection=self.WGS84PROJECTION)
        self.insertFilename(key=key, filename=raster.filename,
                            extent=raster.dataset.grid.extent.transform(transformation=transformation))

    def insertFilename(self, key, filename, extent):
        self.key.append(key)
        self.filename.append(filename)
        self.extent.append(extent)

    def getIntersection(self, grid):
        assert isinstance(grid, Grid)

        transformation = Transformation(sourceProjection=grid.projection, targetProjection=self.WGS84PROJECTION)
        gridExtent = grid.extent.transform(transformation=transformation)

        index = ApplierInputRasterIndex()

        for key, filename, extent in zip(self.key, self.filename, self.extent):
            if extent.intersects(gridExtent):
                index.insertFilename(key=key, filename=filename, extent=extent)

        return index


class ApplierInputVectorGroup(_ApplierIOGroup):
    '''Container for :class:`~hubdc.applier.ApplierInputVector` and :class:`~hubdc.applier.ApplierInputVectorGroup` objects.'''

    def setVector(self, key, value):
        '''Add an :class:`~hubdc.applier.ApplierInputVector` given by ``value`` and named ``key``.'''

        assert isinstance(value, ApplierInputVector)
        return _ApplierIOGroup._setItem(self, key=key, value=value)

    def getVector(self, key):
        '''Returns the :class:`~hubdc.applier.ApplierInputVector` named ``key``.'''

        value = _ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierInputVector)
        return value

    def getFlatVectors(self):
        '''Returns an iterator over all contained :class:`~hubdc.applier.ApplierInputVector`'s. Traverses the group structure recursively.'''
        for input in _ApplierIOGroup._getFlatValues(self):
            assert isinstance(input, ApplierInputVector)
            yield input

    def getFlatVectorKeys(self):
        '''Returns an iterator over the keys of all contained :class:`~hubdc.applier.ApplierInputVectors`'s. Traverses the group structure recursively.'''
        for input in _ApplierIOGroup._getFlatKeys(self):
            assert isinstance(input, str)
            yield input


class ApplierOutputRasterGroup(_ApplierIOGroup):
    '''Container for :class:`~hubdc.applier.ApplierOutputRaster` and :class:`~hubdc.applier.ApplierOutputRasterGroup` objects.'''

    def setRaster(self, key, value):
        '''Add an :class:`~hubdc.applier.ApplierOutputRaster` given by ``value`` and named ``key``.'''

        assert isinstance(value, ApplierOutputRaster)
        return _ApplierIOGroup._setItem(self, key=key, value=value)

    def getRaster(self, key):
        '''Returns the :class:`~hubdc.applier.ApplierOutputRaster` named ``key``.'''

        value = _ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierOutputRaster)
        return value

    def getFlatRasters(self):
        '''Returns an iterator over all contained :class:`~hubdc.applier.ApplierOutputRaster`'s. Traverses the group structure recursively.'''

        for v in self._getFlatValues():
            assert isinstance(v, ApplierOutputRaster)
            yield v

    def getFlatRasterKeys(self):
        '''Returns an iterator over the keys of all contained :class:`~hubdc.applier.ApplierOutputRaster`'s. Traverses the group structure recursively.'''

        for key in _ApplierIOGroup._getFlatKeys(self):
            assert isinstance(key, str)
            yield key


class Applier(object):
    '''
    This class is the main point of entry in this module. For detailed usage examples see :doc:`ApplierExamples`.

    Attributes and properties are:
        * **inputRaster**          :class:`~hubdc.applier.ApplierInputRasterGroup` object containing all input rasters
        * **inputRasterArchive**   :class:`~hubdc.applier.ApplierInputRasterArchiveGroup` object containing all input raster archieves
        * **inputVector**          :class:`~hubdc.applier.ApplierInputVectorGroup` object containing all input vectors
        * **outputRaster**         :class:`~hubdc.applier.ApplierOutputRasterGroup` object containing all output rasters
        * **controls**             :class:`~hubdc.applier.ApplierControls` object containing all input rasters
        * **mainGrid**             :class:`~hubdc.model.Grid` object
    '''

    def __init__(self, controls=None):
        '''
        :param controls: an :class:`~hubdc.applier.ApplierControls` object
        '''

        self.inputRaster = ApplierInputRasterGroup()
        self.inputVector = ApplierInputVectorGroup()
        self.outputRaster = ApplierOutputRasterGroup()
        self.controls = controls if controls is not None else ApplierControls()
        self._grid = None

    @property
    def grid(self):
        '''Returns the output :class:`~hubdc.model.Grid` object.'''

        assert isinstance(self._grid, Grid)
        return self._grid

    def apply(self, operator=None, description=None, overwrite=True, *ufuncArgs, **ufuncKwargs):
        """
        Applies the ``operator`` blockwise over a raster processing chain and returns a list of results, one for each block.

        The ``operator`` must be a subclass of :class:`~hubdc.applier.ApplierOperator` and needs to implement the
        :meth:`~hubdc.applier.ApplierOperator.ufunc` method to specify the image processing.

        For example::

            class MyOperator(ApplierOperator):
                def ufunc(self):
                    # process the data

            applier.apply(operator=MyOperator)

        or::

            def my_ufunc(operator):
                # process the data

            applier.apply(operator=my_ufunc)

        For detailed usage examples see :doc:`ApplierExamples`.

        :param operator: applier operator
        :type operator: :class:`~hubdc.applier.ApplierOperator` or function
        :param description: short description that is displayed on the progress bar
        :param ufuncArgs: additional arguments that will be passed to the operators ufunc() method.
        :param ufuncKwargs: additional keyword arguments that will be passed to the operators ufunc() method.
        :return: list of results, one for each processed block
        """

        if description is None:
            description = operator.__name__

        if not overwrite:
            allExists = all([os.path.exists(raster.filename) for raster in self.outputRaster.getFlatRasters()])
            if allExists:
                self.controls.progressBar.setLabelText(
                    'skip {} (all outputs exist and OVERWRITE=FALSE)'.format(description))
                return

        import inspect
        if inspect.isclass(operator):
            self.ufuncClass = operator
            self.ufuncFunction = None
        elif callable(operator):
            self.ufuncClass = ApplierOperator
            self.ufuncFunction = operator
        else:
            raise ValueError('operator must be a class or callable')

        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        runT0 = now()
        self._grid = self.controls.deriveGrid(inputRasterGroup=self.inputRaster)

        self.controls.progressBar.setText(
            'start {} [{}x{}]'.format(description, self._grid.xSize, self._grid.ySize))
        self._runInitWriters()
        self._runInitPool()
        results = self._runProcessSubgrids()
        self._runClose()

        self.controls.progressBar.setPercentage(percentage=100)
        s = (now() - runT0);
        m = s / 60;
        h = m / 60

        self.controls.progressBar.setText(
            'done {description} in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s),
                                                                          m=round(m, 2), h=round(h, 2)))
        return results

    def _runInitWriters(self):
        self.writers = list()
        self.queues = list()
        self.queueMock = QueueMock()
        if self.controls._multiwriting:
            for w in range(max(1, self.controls.nwriter)):
                w = WriterProcess()
                w.start()
                self.writers.append(w)
                self.queues.append(w.queue)
        self._assignQueues()

    def _runInitPool(self):
        if self.controls._multiprocessing:
            # exclude non-pickable members
            # - writers arn't pickable, need to detache them before passing self to Pool initializer
            writers, self.writers = self.writers, None
            # - free cached gdal datasets
            self.inputRaster._freeUnpickableResources()

            self.pool = Pool(processes=self.controls.nworker, initializer=_pickableWorkerInitialize, initargs=(self,))
            self.writers = writers  # put writers back
        else:
            _Worker.initialize(applier=self)

    def _runProcessSubgrids(self):

        subgrids = list(
            self._grid.subgrids(windowSize=self.controls.windowxsize, windowysize=self.controls.windowysize))
        n = ny = nx = 0
        for workingGrid, i, iy, ix in subgrids:
            n += 1
            ny = max(ny, iy + 1)
            nx = max(nx, ix + 1)

        self.nsubgrids = n
        if self.controls._multiprocessing:
            applyResults = list()
        else:
            results = list()

        for workingGrid, i, iy, ix in subgrids:
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'iy': iy,
                      'ix': ix,
                      'ny': ny,
                      'nx': nx,
                      'workingGrid': workingGrid}

            if self.controls._multiprocessing:
                applyResults.append(self.pool.apply_async(func=_pickableWorkerProcessSubgrid, kwds=kwargs))
            else:
                results.append(_Worker.processSubgrid(**kwargs))

        if self.controls._multiprocessing:
            results = [applyResult.get() for applyResult in applyResults]

        return results

    def _assignQueues(self):

        def lessFilledQueue():
            lfq = self.queues[0]
            for q in self.queues:
                if lfq.qsize() > q.qsize():
                    lfq = q
            return lfq

        for output in self.outputRaster.getFlatRasters():
            assert isinstance(output, ApplierOutputRaster)
            if self.controls._multiwriting:
                output._writerQueue = lessFilledQueue()
            else:
                output._writerQueue = self.queueMock

    def _runClose(self):
        if self.controls._multiprocessing:
            self.pool.close()
            self.pool.join()

        if self.controls._multiwriting:
            for writer in self.writers:
                writer.queue.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])
                writer.queue.put([Writer.CLOSE_WRITER, None])
                writer.join()
        else:
            self.queueMock.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])


class _Worker(object):
    """
    For internal use only.
    """

    # queues = list()
    inputRaster = None
    inputVector = None
    outputRaster = None
    applier = None
    operator = None

    def __init__(self):
        raise Exception('singleton class')

    @classmethod
    def initialize(cls, applier):
        gdal.SetCacheMax(applier.controls.cacheMax)
        gdal.SetConfigOption('GDAL_SWATH_SIZE', str(applier.controls.swathSize))
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', str(applier.controls.disableReadDirOnOpen))
        gdal.SetConfigOption('GDAL_MAX_DATASET_POOL_SIZE', str(applier.controls.maxDatasetPoolSize))

        assert isinstance(applier, Applier)
        cls.applier = applier
        cls.inputRaster = applier.inputRaster
        cls.inputVector = applier.inputVector
        cls.outputRaster = applier.outputRaster

        # create operator
        cls.operator = applier.ufuncClass(mainGrid=applier.grid,
                                          inputRaster=cls.inputRaster,
                                          inputVector=cls.inputVector,
                                          outputRaster=cls.outputRaster,
                                          controls=applier.controls,
                                          ufuncFunction=applier.ufuncFunction, ufuncArgs=applier.ufuncArgs,
                                          ufuncKwargs=applier.ufuncKwargs)

    @classmethod
    def processSubgrid(cls, i, n, iy, ix, ny, nx, workingGrid):
        cls.operator.progressBar.setPercentage(float(i) / n * 100)
        return cls.operator._apply(workingGrid=workingGrid, iblock=i, nblock=n, yblock=iy, xblock=ix, nyblock=ny,
                                   nxblock=nx)


def _pickableWorkerProcessSubgrid(**kwargs):
    return _Worker.processSubgrid(**kwargs)


def _pickableWorkerInitialize(*args):
    return _Worker.initialize(*args)


class ApplierOperator(object):
    """
    This is the baseclass for an user defined applier operator.
    For details on user defined operators see :meth:`hubdc.applier.Applier.apply`
    """

    def __init__(self, mainGrid, inputRaster, inputVector, outputRaster,
                 controls, ufuncArgs, ufuncKwargs, ufuncFunction=None):
        assert isinstance(mainGrid, Grid)
        assert isinstance(inputRaster, ApplierInputRasterGroup)
        assert isinstance(inputVector, ApplierInputVectorGroup)
        assert isinstance(outputRaster, ApplierOutputRasterGroup)
        assert isinstance(controls, ApplierControls)

        self._subgrid = None
        self._grid = mainGrid

        self.inputRaster = inputRaster
        self.inputVector = inputVector
        self.outputRaster = outputRaster

        self.inputRaster.operator = self
        self.inputVector.operator = self
        self.outputRaster.operator = self

        self._controls = controls
        self._ufuncArgs = ufuncArgs
        self._ufuncKwargs = ufuncKwargs
        self._ufuncFunction = ufuncFunction
        self.iblock = 0
        self.nblock = 0

    @property
    def subgrid(self):
        """
        Returns the current block :class:`~hubdc.applier.Grid`.
        """
        assert isinstance(self._subgrid, Grid)
        return self._subgrid

    @property
    def grid(self):
        """
        Returns the :class:`~hubdc.applier.Grid`.
        """
        assert isinstance(self._grid, Grid)
        return self._grid

    def _setWorkingGrid(self, grid):
        assert isinstance(grid, Grid)
        self._subgrid = grid

    @property
    def progressBar(self):
        """
        Returns the :class:`~hubdc.progressbar.ProgressBar`.
        """
        return self._controls.progressBar

    def isFirstBlock(self):
        """
        Returns wether or not the current block is the first one.
        """
        return self.iblock == 0

    def isLastBlock(self):
        """
        Returns wether or not the current block is the last one.
        """
        return self.iblock == self.nblock - 1

    def isLastYBlock(self):
        """
        Returns wether or not the current block is the last block in y direction.
        """
        return self.yblock == self.nyblock - 1

    def isLastXBlock(self):
        """
        Returns wether or not the current block is the last block in x direction.
        """
        return self.xblock == self.nxblock - 1

    def getFull(self, value, bands=1, dtype=None, overlap=0):
        '''Returns a 3-d numpy array of shape = (bands, ysize+2*overlap, xsize+2*overlap) filled with constant ``value``.'''

        return numpy.full(shape=(bands, self.subgrid.ySize + 2 * overlap, self.subgrid.xSize + 2 * overlap),
                          fill_value=value, dtype=dtype)

    def _apply(self, workingGrid, iblock, nblock, yblock, xblock, nyblock, nxblock):
        self.iblock = iblock
        self.nblock = nblock
        self.yblock = yblock
        self.xblock = xblock
        self.nyblock = nyblock
        self.nxblock = nxblock

        self._setWorkingGrid(workingGrid)
        return self.ufunc(*self._ufuncArgs, **self._ufuncKwargs)

    def ufunc(self, *args, **kwargs):
        '''Overwrite this method to specify the image processing. See :doc:`ApplierExamples` for more information.'''

        if self._ufuncFunction is None:
            raise NotImplementedError()
        else:
            return self._ufuncFunction(self, *args, **kwargs)


class ApplierControls(object):
    '''Class for controlling various details of the applier processing.'''

    def __init__(self):

        self.setBlockSize()
        self.setWindowYSize()
        self.setNumThreads()
        self.setNumWriter()
        self.setWriteENVIHeader()
        self.setAutoExtent()
        self.setAutoResolution()
        self.setResolution()
        self.setExtent()
        self.setProjection()
        self.setGrid()
        # self.setDisableWindowTrimToFootprint()
        self.setGDALCacheMax()
        self.setGDALSwathSize()
        self.setGDALDisableReadDirOnOpen()
        self.setGDALMaxDatasetPoolSize()
        # self.setGDALWarpErrorThreshold()
        # self.setGDALWarpMemoryLimit()
        # self.setGDALWarpMultithread()
        self.setProgressBar()

    def setProgressBar(self, progressBar=None):
        """
        Set the progress display object. Default is an :class:`~hubdc.progressbar.CUIProgress` object.
        For suppressing outputs use an :class:`~hubdc.progressbar.SilentProgress` object
        """
        if progressBar is None:
            progressBar = CUIProgressBar()

        self.progressBar = progressBar
        return self

    def setBlockSize(self, size=Default.blockSize):
        """
        Set the block size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowxsize = windowxsize
        return self

    def setWindowYSize(self, windowysize=Default.windowysize):
        """
        Set the Y size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowysize = windowysize
        return self

    def setWindowFullSize(self):
        """
        Set the block size to full extent.
        """

        veryLargeNumber = 10 ** 20
        self.setBlockSize(veryLargeNumber)
        self.setWindowYSize(veryLargeNumber)
        return self

    def setNumThreads(self, nworker=Default.nworker):
        """
        Set the number of pool worker for multiprocessing. Set to None to disable multiprocessing (recommended for debugging).
        """
        if nworker == -1:
            import multiprocessing
            nworker = multiprocessing.cpu_count()

        self.nworker = nworker
        return self

    def setNumWriter(self, nwriter=Default.nwriter):
        """
        Set the number of writer processes. Set to None to disable multiwriting (recommended for debugging).
        """
        self.nwriter = nwriter
        return self

    def setWriteENVIHeader(self, createEnviHeader=Default.writeENVIHeader):
        """
        Set to True to create additional ENVI header files for all output rasters.
        The header files store all metadata items from the GDAL PAM ENVI domain,
        so that the images can be correctly interpreted by the ENVI software.
        Currently only the native ENVI format and the GTiff format is supported.
        """
        self.createEnviHeader = createEnviHeader
        return self

    def setAutoExtent(self, autoExtent=Default.autoExtent):
        """
        Define how the grid extent is derived from the input rasters.
        Possible options are listed in :class:`~hubdc.applier.Enum.AutoExtent`.
        """
        self.autoExtent = autoExtent
        return self

    def setAutoResolution(self, autoResolution=Default.autoResolution):
        """
        Define how the grid resolution is derived from the input rasters.
        Possible options are listed in :class:`~hubdc.applier.Enum.AutoResolution`.
        """
        self.autoResolution = autoResolution
        return self

    def setResolution(self, resolution=None):
        """
        Set the grid :class:`~hubdc.applier.Resolution`.
        """
        if resolution is not None:
            assert isinstance(resolution, Resolution)
        self.resolution = resolution
        return self

    def setExtent(self, extent=None):
        """
        Set the grid :class:`~hubdc.applier.Extent`.
        """
        if extent is not None:
            assert isinstance(extent, Extent)
        self.extent = extent
        return self

    def setProjection(self, projection=None):
        """
        Set the grid :class:`~hubdc.applier.Projection`.
        """
        if projection is not None:
            assert isinstance(projection, Projection)
        self.projection = projection
        return self

    def setGrid(self, grid=None):
        """
        Set the :class:`~hubdc.model.Grid`.
        """
        if grid is None:
            self.setExtent()
            self.setResolution()
            self.setProjection()
        else:
            assert grid is None or isinstance(grid, Grid)
            self.setExtent(extent=grid.extent)
            self.setResolution(resolution=grid.resolution)
            self.setProjection(projection=grid.projection)
        return self

    #    def setDisableWindowTrimToFootprint(self, disable=False):
    #        self.disableWindowTrimToFootprint = disable

    def setGDALCacheMax(self, bytes=Default.GDALEnv.cacheMax):
        """
        For details see the `GDAL_CACHEMAX Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_CACHEMAX>`_.
        """
        self.cacheMax = bytes
        return self

    def setGDALSwathSize(self, bytes=Default.GDALEnv.swathSize):
        """
        For details see the `GDAL_SWATH_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_SWATH_SIZE>`_.
        """
        self.swathSize = bytes
        return self

    def setGDALDisableReadDirOnOpen(self, disable=Default.GDALEnv.disableReadDirOnOpen):
        """
        For details see the `GDAL_DISABLE_READDIR_ON_OPEN Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_DISABLE_READDIR_ON_OPEN>`_.
        """
        self.disableReadDirOnOpen = disable
        return self

    def setGDALMaxDatasetPoolSize(self, nfiles=Default.GDALEnv.maxDatasetPoolSize):
        """
        For details see the `GDAL_MAX_DATASET_POOL_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_MAX_DATASET_POOL_SIZE>`_.
        """
        self.maxDatasetPoolSize = nfiles
        return self

    # def setGDALWarpErrorThreshold(self, errorThreshold=Default.GDALWARP_ERRORTHRESHOLD):
    #    self.gdalWarpErrorThreshold = errorThreshold

    # def setGDALWarpMemoryLimit(self, memoryLimit=Default.GDALWARP_MEMORYLIMIT):
    #    self.gdalWarpMemoryLimit = memoryLimit

    # def setGDALWarpMultithread(self, multithread=Default.GDALWARP_MULTITHREAD):
    #    self.gdalWarpMultithread = multithread

    @property
    def _multiprocessing(self):
        return self.nworker is not None

    @property
    def _multiwriting(self):
        return self._multiprocessing or (self.nwriter is not None)

    def deriveGrid(self, inputRasterGroup):
        assert isinstance(inputRasterGroup, ApplierInputRasterGroup)
        grids = [inputRaster.dataset.grid for inputRaster in inputRasterGroup.getFlatRasters()]
        projection = self.deriveProjection(grids)
        return Grid(projection=projection,
                    extent=self.deriveExtent(grids, projection),
                    resolution=self.deriveResolution(grids))

    def deriveProjection(self, grids):

        if self.projection is None:
            if len(grids) == 0:
                raise Exception('projection not defined')
            projection = grids[0].projection
            for grid in grids:
                if not grid.projection.equal(other=projection):
                    raise Exception('input projections do not match')
        else:
            projection = self.projection
        return projection

    def deriveExtent(self, grids, projection):

        if self.extent is None:

            if len(grids) == 0:
                raise Exception('footprint not defined')

            extent = grids[0].extent.transform(transformation=Transformation(sourceProjection=grids[0].projection,
                                                                             targetProjection=projection))

            for grid in grids:
                extent_ = grid.extent.transform(transformation=Transformation(sourceProjection=grid.projection,
                                                                              targetProjection=projection))
                if self.autoExtent == Enum.AutoExtent.union:
                    extent = extent.union(other=extent_)
                elif self.autoExtent == Enum.AutoExtent.intersection:
                    extent = extent.intersection(other=extent_)
                else:
                    raise Exception('unknown extent type')

        else:
            extent = self.extent

        return extent

    def deriveResolution(self, grids):

        if self.resolution is None:

            if self.autoResolution == Enum.AutoResolution.minimum:
                f = numpy.min
            elif self.autoResolution == Enum.AutoResolution.maximum:
                f = numpy.max
            elif self.autoResolution == Enum.AutoResolution.average:
                f = numpy.mean
            else:
                raise ValueError('unknown resolution type')
            resolution = Resolution(xRes=f([grid.resolution.xRes for grid in grids]),
                                    yRes=f([grid.resolution.yRes for grid in grids]))

        else:
            resolution = self.resolution

        return resolution
