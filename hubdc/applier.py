"""
Basic tools for setting up a function to be applied over a raster processing chain.
The :class:`~hubdc.applier.Applier` class is the main point of entry in this module.

See :doc:`ApplierExamples` for more information.

"""

from __future__ import print_function
import sys, os
from collections import OrderedDict
from multiprocessing import Pool
from timeit import default_timer as now
import numpy
from osgeo import gdal, osr, ogr
from osgeo.gdal_array import NumericTypeCodeToGDALTypeCode
from hubdc.model import Open, OpenLayer, CreateFromArray, Dataset, Band, PixelGrid
import hubdc.model # needed for sphinx
from hubdc.writer import Writer, WriterProcess, QueueMock
from hubdc.progressbar import CUIProgressBar, ProgressBarDelegate

class Enum(object):
    '''Enumerats for various settings used inside an applier processing chain.'''
    class Footprint(object):
        UNION = 0
        INTERSECTION = 1
    class Resolution(object):
        MINIMUM = 0
        MAXIMUM = 1
        AVERAGE = 2

class Default(object):
    '''Defaults values for various settings used inside an applier processing chain.'''
    CREATEENVIHEADER = True
    CREATIONOPTIONS = dict()
    CREATIONOPTIONS['ENVI'] = ['INTERLEAVE=BSQ']
    CREATIONOPTIONS['GTiff'] = ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'SPARSE_OK=TRUE', 'BIGTIFF=YES']
    GDAL_CACHEMAX = 100*2**20
    GDAL_SWATHSIZE = 100*2**20
    GDAL_DISABLEREADDIRONOPEN = True
    GDAL_MAXDATASETPOOLSIZE = 100
    GDALWARP_ERRORTHRESHOLD = 0.
    GDALWARP_MEMORYLIMIT = 100 * 2 ** 20
    GDALWARP_MULTITHREAD = False
    FOOTPRINTTYPE = Enum.Footprint.INTERSECTION
    FORMAT = 'ENVI'
    NWORKER = None
    NWRITER = None
    RESOLUTIONTYPE = Enum.Resolution.MINIMUM
    WINDOWXSIZE = 256
    WINDOWYSIZE = 256

class ApplierInputRaster(object):
    '''Class for handling the raster dataset given by it's ``filename``.'''

    @classmethod
    def fromDataset(cls, dataset):
        '''Create an input raster from an :class:`~hubdc.model.Dataset`.'''

        assert isinstance(dataset, Dataset)
        applierInputRaster = ApplierInputRaster(filename='')
        applierInputRaster._dataset = dataset
        return applierInputRaster

    def __init__(self, filename):
        self.filename = filename
        self._dataset = None
        self._operator = None

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
                      errorThreshold=Default.GDALWARP_ERRORTHRESHOLD,
                      warpMemoryLimit=Default.GDALWARP_MEMORYLIMIT,
                      multithread=Default.GDALWARP_MULTITHREAD,
                      grid=None):
        '''
        Returns image data as 3-d numpy array.

        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param resampleAlg: GDAL resampling algorithm, e.g. gdal.GRA_NearestNeighbour
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :param warpMemoryLimit: size of working buffer in bytes
        :param multithread: whether to multithread computation and I/O operations
        :param grid: explicitly set the :class:`~hubdc.model.PixelGrid`, for which image data is returned
        '''

        if grid is None:
            dstGrid = self.operator.workingGrid.pixelBuffer(buffer=overlap)
        else:
            dstGrid = grid

        if self.operator.workingGrid.equalProjection(self.dataset.pixelGrid):
            datasetResampled = self.dataset.translate(dstPixelGrid=dstGrid, dstName='', format='MEM',
                                                      resampleAlg=resampleAlg,
                                                      noData=noData)
        else:
            datasetResampled = self.dataset.warp(dstPixelGrid=dstGrid, dstName='', format='MEM',
                                                 resampleAlg=resampleAlg,
                                                 errorThreshold=errorThreshold,
                                                 warpMemoryLimit=warpMemoryLimit,
                                                 multithread=multithread,
                                                 srcNodata=noData)
        array = datasetResampled.readAsArray()
        datasetResampled.close()
        return array

    def getBandArray(self, indicies, overlap=0, resampleAlg=gdal.GRA_NearestNeighbour, noData=None,
                     errorThreshold=Default.GDALWARP_ERRORTHRESHOLD,
                     warpMemoryLimit=Default.GDALWARP_MEMORYLIMIT,
                     multithread=Default.GDALWARP_MULTITHREAD):
        '''
        Returns a band subset of the image data as 3-d numpy array.

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
        dstGrid = self.operator.workingGrid.pixelBuffer(buffer=overlap)
        if self.operator.workingGrid.equalProjection(self.dataset.pixelGrid):
            datasetResampled = self.dataset.translate(dstPixelGrid=dstGrid, dstName='', format='MEM',
                                                 bandList=bandList,
                                                 resampleAlg=resampleAlg,
                                                 noData=noData)
        else:
            selfGridReprojected = self.operator.workingGrid.reproject(self.dataset.pixelGrid)
            selfGridReprojectedWithBuffer = selfGridReprojected.pixelBuffer(buffer=1+overlap)

            datasetClipped = self.dataset.translate(dstPixelGrid=selfGridReprojectedWithBuffer, dstName='', format='MEM',
                                               bandList=bandList,
                                               noData=noData)

            datasetResampled = datasetClipped.warp(dstPixelGrid=dstGrid, dstName='', format='MEM',
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
        Returns a stack of category fractions for the given ``categories`` as a 3-d numpy array.

        :param categories: list of categories of interest
        :param overlap: the number of pixels to additionally read along each spatial dimension
        :param noData: explicitely set the noDataValue used for reading; this overwrites the noDataValue defined by the raster itself
        :param index: index to the band holding the categories
        '''

        assert self.dataset.zsize == 1 or index is not None
        if index is None:
            index = 0
        grid = self.operator.workingGrid.pixelBuffer(buffer=overlap)

        # create tmp dataset with binarized categories in original resolution
        gridInSourceProjection = grid.reproject(self.dataset.pixelGrid)
        tmpDataset = self.dataset.translate(dstPixelGrid=gridInSourceProjection, dstName='', format='MEM', noData=noData, bandList=[index+1])
        tmpArray = tmpDataset.readAsArray()

        binarizedArray = [numpy.float32(tmpArray[0] == category) for category in categories]
        binarizedDataset = CreateFromArray(pixelGrid=gridInSourceProjection, array=binarizedArray,
                                         dstName='', format='MEM', creationOptions=[])

        binarizedInputRaster = ApplierInputRaster.fromDataset(dataset=binarizedDataset)
        binarizedInputRaster.operator = self.operator

        array = binarizedInputRaster.getImageArray(overlap=overlap, resampleAlg=gdal.GRA_Average)
        return array

    def getImageSample(self, mask, resampleAlg=gdal.GRA_NearestNeighbour, noData=None,
                      errorThreshold=Default.GDALWARP_ERRORTHRESHOLD,
                      warpMemoryLimit=Default.GDALWARP_MEMORYLIMIT,
                      multithread=Default.GDALWARP_MULTITHREAD):

        assert isinstance(mask, numpy.ndarray)
        assert mask.dtype == numpy.bool
        assert mask.ndim == 3
        assert mask.shape[0] == 1
        assert mask.shape[1:] == self.operator.workingGrid.shape

        ys, xs = numpy.indices(mask.shape[1:])[:, mask[0]]
        profiles = list()
        for y, x in zip(ys, xs):
            grid = self.operator.workingGrid.subsetPixelWindow(xoff=x, yoff=y, width=1, height=1)
            profiles.append(self.getImageArray(resampleAlg=resampleAlg, noData=noData, errorThreshold=errorThreshold,
                            warpMemoryLimit=warpMemoryLimit, multithread=multithread, grid=grid))
        profiles = numpy.hstack(profiles)[:,:,0]
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
        """Return image no data value."""
        return self.dataset.getNoDataValue(default=default)

    def getNoDataValues(self, default=None):
        """Return band no data values"""
        return self.dataset.getNoDataValues(default=default)


class ApplierInputRasterArchive(object):

    def __init__(self, folder, extensions, filter=None, overwrite=False):
        assert isinstance(extensions, (list, tuple))
        self.folder = folder
        self.extensions = extensions
        self.filter = filter
        self.indexFilename = os.path.join(folder, '.spatialindex')
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(4326) # WGS84
        self.projection = str(projection)
        self._createIndex(overwrite=overwrite)
        self._operator = None

    @property
    def operator(self):
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        assert isinstance(value, ApplierOperator)
        self._operator = value

    def _createIndex(self, overwrite):
        import rtree

        for ext in ['.dat', '.idx']:
            f = self.indexFilename+ext
            if overwrite and os.path.exists(f):
                os.remove(f)

        create = not os.path.exists(self.indexFilename+'.idx') or overwrite
        if create:
            try:
                index = rtree.index.Index(self.indexFilename, interleaved=False)
                id=0
                for root, dirs, files in os.walk(self.folder):
                    for file in files:
                        for extension in self.extensions:
                            if file.endswith(extension):
                                filename = os.path.join(root, file)
                                print(filename)
                                grid = PixelGrid.fromFile(filename=filename)
                                coordinates = grid.reprojectExtent(targetProjection=self.projection)
                                index.insert(id, coordinates, obj=filename)
                                id += 1
                print('RTree index created ({})'.format(self.indexFilename))
            except:
                self.filenames = list()
                for root, dirs, files in os.walk(self.folder):
                    for file in files:
                        for extension in self.extensions:
                            if file.endswith(extension):
                                filename = os.path.join(root, file)
                                self.filenames.append(filename)

    def _getIntersectionByPixelGrid(self, grid):
        assert isinstance(grid, PixelGrid)
        coordinates = grid.reprojectExtent(self.projection)
        try:
            import rtree
            index = rtree.index.Index(self.indexFilename, interleaved=False)
            filenames = [item.object for item in index.intersection(coordinates=coordinates, objects=True)]
            index.close()
        except:
            print('rtree error')
            filenames = self.filenames
        group = ApplierInputRasterGroup()
        for f in filenames:
            if self.filter is not None:
                if not self.filter(f):
                    continue
            k = os.path.splitext('/'.join(os.path._abspath_split(f[len(self.folder):])[2]))[0]
            group.setRaster(key=k, value=ApplierInputRaster(filename=f))

        return group

    def getIntersection(self):
        group = self._getIntersectionByPixelGrid(grid=self.operator.workingGrid)
        group.operator = self.operator
        assert isinstance(group, ApplierInputRasterGroup)
        return group

class ApplierInputVector(object):

    def __init__(self, filename, layerNameOrIndex=0):
        self.filename = filename
        self.layerNameOrIndex = layerNameOrIndex
        self._layer = None
        self._dataset = None
        self._operator = None

    @property
    def operator(self):
        '''Return the parent :class:`~hubdc.applier.ApplierOperator` object'''
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        '''Set the parent :class:`~hubdc.applier.ApplierOperator` object'''
        assert isinstance(value, ApplierOperator)
        self._operator = value

    @property
    def layer(self):
        '''Return the :class:`~hubdc.model.Layer` object'''
        if self._layer is None:
            self._layer = OpenLayer(filename=self.filename, layerNameOrIndex=self.layerNameOrIndex, update=False)
        return self._layer

    def _rasterize(self, initValue, burnValue, burnAttribute, allTouched, filterSQL, overlap, dtype, xRes, yRes):
        '''For internal use only.'''

        grid = self.operator.workingGrid.pixelBuffer(buffer=overlap)
        gridOversampled = grid.newResolution(xRes=xRes, yRes=yRes)

        dataset = self.layer.rasterize(dstPixelGrid=gridOversampled, eType=NumericTypeCodeToGDALTypeCode(dtype),
                                       initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute,
                                       allTouched=allTouched,
                                       filter=filterSQL, dstName='', format='MEM', creationOptions=[])
        raster = ApplierInputRaster.fromDataset(dataset=dataset)
        raster.operator = self.operator
        return raster

    def getImageArray(self, initValue=0, burnValue=1, burnAttribute=None, allTouched=False, filterSQL=None, overlap=0, dtype=numpy.float32):
        '''Returns the vector rasterization of the current block in form of a 3-d numpy array.

        :param initValue: value to pre-initialize the output array
        :param burnValue: value to burn into the output array for all objects; exclusive with ``burnAttribute``
        :param burnAttribute: identifies an attribute field on the features to be used for a burn-in value; exclusive with ``burnValue``
        :param allTouched: whether to enable that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :param filterSQL: set an SQL WHERE clause which will be used to filter vector features
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        '''

        raster = self._rasterize(initValue=initValue, burnValue=burnValue, burnAttribute=burnAttribute, allTouched=allTouched, filterSQL=filterSQL, overlap=overlap, dtype=dtype,
                                 xRes=self.operator.workingGrid.xRes, yRes=self.operator.workingGrid.yRes)
        return raster.dataset.readAsArray()

    def getFractionArray(self, categories, categoryAttribute=None, oversampling=10, xRes=None, yRes=None, overlap=0):
        '''Returns aggregated category fractions of the current block in form of a 3d numpy array.

        :param categories: list of categories (numbers or names)
        :param categoryAttribute: attribute field on the features holding the categories
        :param oversampling: factor defining the relative degree of rasterization detail compared to the target resolution. If for example the target resolution is 30m and the oversampling factor is 10, then the categories are first rasterized at 3m, and finally aggregated to the target resolution.
        :param overlap: the amount of margin (number of pixels) added to the image data block in each direction, so that the blocks will overlap; this is important for spatial operators like filters.
        '''

        if xRes is None:
            xRes = self.operator.workingGrid.xRes / float(oversampling)
        if yRes is None:
            yRes = self.operator.workingGrid.yRes / float(oversampling)

        array = list()
        for category in categories:
            filterSQL = str('"' + categoryAttribute + '" = ' + "'"+str(category)+"'")
            oversampledRaster = self._rasterize(initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                                                filterSQL=filterSQL,
                                                overlap=overlap*oversampling, dtype=numpy.float32,
                                                xRes=xRes, yRes=yRes)
            array.append(oversampledRaster.getImageArray(overlap=overlap, resampleAlg=gdal.GRA_Average))

        return numpy.vstack(array)

class ApplierOutputRaster(object):

    def __init__(self, filename, format=None, creationOptions=None):
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
        return self._filename

    @property
    def operator(self):
        assert isinstance(self._operator, ApplierOperator)
        return self._operator

    @operator.setter
    def operator(self, value):
        assert isinstance(value, ApplierOperator)
        self._operator = value

    def getFlatList(self):
        return [self]

    def getBand(self, index):
        if self._bands is None:
            raise Exception('Output raster is not initialized. Use ApplierOutputRaster.initialize(bands) to specify the number of output bands.')
        return ApplierOutputRasterBand(parent=self, bandNumber=index+1)

    def getBandIterator(self):
        for index in range(self._bands):
            yield self.getBand(index=index)

    def setImageArray(self, array, overlap=0):
        """
        Write data to an output raster image.
        The ``name`` identifier must match the identifier used with :meth:`hubdc.applier.Applier.setOutput`.

        :param name:  output raster name
        :param array: 3-d or 2-d numpy array to be written
        :param overlap: the amount of margin (number of pixels) to be removed from the image data block in each direction;
                        this is useful when the overlap keyword was also used with :meth:`~hubdc.applier.ApplierOperator.getArray`
        """

        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        self._writerQueue.put((Writer.WRITE_IMAGEARRAY, self.filename, array, self.operator.workingGrid, self.operator.mainGrid,
                               self.format, self.creationOptions))

        self.initialize(bands=len(array))

        return self

    def setMetadataItem(self, key, value, domain):
        """Set image metadata item."""
        self._callImageMethod(method=Dataset.setMetadataItem, key=key, value=value, domain=domain)

    def setMetadataDict(self, metadataDict):
        """Set metadata dictionary."""
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

    def __init__(self, parent, bandNumber):
        assert isinstance(parent, ApplierOutputRaster)
        self.parent = parent
        self.bandNumber = bandNumber

    def setArray(self, array, overlap=0):

        if not isinstance(array, numpy.ndarray):
            array = numpy.array(array)

        if array.ndim == 2:
            array = array[None]

        if overlap > 0:
            array = array[:, overlap:-overlap, overlap:-overlap]

        self.parent._writerQueue.put((Writer.WRITE_BANDARRAY, self.parent.filename, array, self.bandNumber, self.parent._bands, self.parent.operator.workingGrid, self.parent.operator.mainGrid,
                               self.parent.format, self.parent.creationOptions))

        return self


    def _callMethod(self, method, **kwargs):
        if self.parent.operator.isFirstBlock():
            self.parent._writerQueue.put((Writer.CALL_BANDMETHOD, self.parent.filename, self.bandNumber, method, kwargs))

    def setDescription(self, value):
        self._callMethod(method=Band.setDescription, value=value)

    def setMetadataItem(self, key, value, domain=''):
        """Set metadata item."""
        self._callMethod(method=Band.setMetadataItem, key=key, value=value, domain=domain)

    def setNoDataValue(self, value):
        """Set no data value."""
        self._callMethod(method=Band.setNoDataValue, value=value)

class ApplierIOGroup(object):

    def __init__(self):
        self.items = dict()
        self._operator = None

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
                result.extend(value._getFlatKeys())
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

class ApplierInputRasterGroup(ApplierIOGroup):

    @classmethod
    def fromFolder(cls, folder, extensions, filter=None):
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
                    if fileExtension[1:].lower() != extension.lower():
                        continue
                    if filter is not None:
                        if not filter(root=root, basename=fileBasenameWithoutExtension, extension=fileExtension):
                            continue
                    subgroup.setRaster(key=fileBasenameWithoutExtension, value=ApplierInputRaster(filename=os.path.join(root, file)))
        return group

    def setRaster(self, key, value):
        assert isinstance(value, ApplierInputRaster)
        return ApplierIOGroup._setItem(self, key=key, value=value)

    def getRaster(self, key):
        value = ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierInputRaster)
        return value

    def getFlatRasters(self):
        for input in ApplierIOGroup._getFlatValues(self):
            assert isinstance(input, ApplierInputRaster)
            yield input

    def getFlatRasterKeys(self):
        for input in ApplierIOGroup._getFlatKeys(self):
            yield input

    def getGroups(self):
        for v in self.items.values():
            if isinstance(v, ApplierInputRasterGroup):
                yield v

    def getGroupKeys(self):
        for k, v in self.items.items():
            if isinstance(v, ApplierInputRasterGroup):
                yield k

    def getRasters(self):
        for v in self.items.values():
            if isinstance(v, ApplierInputRaster):
                yield v

    def getRasterKeys(self):
        for k, v in self.items.items():
            if isinstance(v, ApplierInputRaster):
                assert isinstance(k, str)
                yield k

    def findRaster(self, endswith=None):
        for basename in self.getRasterKeys():
            if basename.endswith(endswith):
                return basename
        return None

class ApplierInputRasterArchiveGroup(ApplierIOGroup):

    def setArchive(self, key, value):
        assert isinstance(value, ApplierInputRasterArchive)
        return ApplierIOGroup._setItem(self, key=key, value=value)

    def getArchive(self, key):
        value = ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierInputRasterArchive)
        return value

class ApplierInputVectorGroup(ApplierIOGroup):

    def setVector(self, key, value):
        assert isinstance(value, ApplierInputVector)
        return ApplierIOGroup._setItem(self, key=key, value=value)

    def getVector(self, key):
        value = ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierInputVector)
        return value

    def getFlatVectors(self):
        for input in ApplierIOGroup._getFlatValues(self):
            assert isinstance(input, ApplierInputVector)
            yield input

    def getFlatVectorKeys(self):
        for input in ApplierIOGroup._getFlatKeys(self):
            assert isinstance(input, str)
            yield input

class ApplierOutputRasterGroup(ApplierIOGroup):

    def setRaster(self, key, value):
        assert isinstance(value, ApplierOutputRaster)
        return ApplierIOGroup._setItem(self, key=key, value=value)

    def getRaster(self, key):
        value = ApplierIOGroup._getItem(self, key=key)
        assert isinstance(value, ApplierOutputRaster)
        return value

    def getFlatRasterKeys(self):
        for key in ApplierIOGroup._getFlatKeys(self):
            assert isinstance(key, str)
            yield key

    def getFlatRasters(self):
        for v in self._getFlatValues():
            assert isinstance(v, ApplierOutputRaster)
            yield v

class Applier(object):

    def __init__(self, controls=None):
        self.inputRaster = ApplierInputRasterGroup()
        self.inputRasterArchive = ApplierInputRasterArchiveGroup()
        self.inputVector = ApplierInputVectorGroup()
        self.outputRaster = ApplierOutputRasterGroup()
        self.controls = controls if controls is not None else ApplierControls()
        self._mainGrid = None

    @property
    def mainGrid(self):
        assert isinstance(self._mainGrid, PixelGrid)
        return self._mainGrid

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
                self.controls.progressBar.setLabelText('skip {} (all outputs exist and OVERWRITE=FALSE)'.format(description))
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
        self._runCreateGrid()
        self.controls.progressBar.setLabelText('start {} [{}x{}]'.format(description, self._mainGrid.xSize, self._mainGrid.ySize))
        self._runInitWriters()
        self._runInitPool()
        results = self._runProcessSubgrids()
        self._runClose()

        self.controls.progressBar.setProgress(self.nsubgrids)
        s = (now()-runT0); m = s/60; h = m/60

        self.controls.progressBar.setLabelText('done {description} in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s), m=round(m, 2), h=round(h, 2)))
        return results

    def _runCreateGrid(self):

        if self.controls.referenceGrid is not None:
            self._mainGrid = self.controls.referenceGrid
        else:
            self._mainGrid = self.controls._makeAutoGrid(inputRasterContainer=self.inputRaster)
        if self.controls.xRes is not None: self._mainGrid.xRes = self.controls.xRes
        if self.controls.yRes is not None: self._mainGrid.yRes = self.controls.yRes

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

        subgrids = list(self._mainGrid.subgrids(windowxsize=self.controls.windowxsize, windowysize=self.controls.windowysize,
                                           trim=not self.controls.disableWindowTrimToFootprint))
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

        self.controls.progressBar.setTotalSteps(n)

        for workingGrid, i, iy, ix in subgrids:
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'iy' : iy,
                      'ix' : ix,
                      'ny' : ny,
                      'nx' : nx,
                      'workingGrid': workingGrid}

            if self.controls._multiprocessing:
                applyResults.append(self.pool.apply_async(func=_pickableWorkerProcessSubgrid, kwds=kwargs))
            else:
                results.append(_Worker.processSubgrid(**kwargs))

        if self.controls._multiprocessing:
            results = [applyResult.get() for applyResult in applyResults]

        return results

    '''def _getQueueByFilenameDict(self):

        def lessFilledQueue():
            lfq = self.queues[0]
            for q in self.queues:
                if lfq.qsize() > q.qsize():
                    lfq = q
            return lfq

        queueByFilename = dict()
        for output in self.outputRaster.values():
            if self.controls._multiwriting:
                queueByFilename[output.filename] = lessFilledQueue()
            else:
                queueByFilename[output.filename] = self.queueMock
            output.queue = queueByFilename[output.filename]
        return queueByFilename'''

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

    #queues = list()
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
        cls.inputRasterArchive = applier.inputRasterArchive
        cls.inputVector = applier.inputVector
        cls.outputRaster = applier.outputRaster

        # create operator
        try:
            cls.operator = applier.ufuncClass(mainGrid=applier.mainGrid,
                                              inputRaster=cls.inputRaster,
                                              inputRasterArchive=cls.inputRasterArchive,
                                              inputVector=cls.inputVector,
                                              outputRaster=cls.outputRaster,
                                              controls=applier.controls,
                                              ufuncFunction=applier.ufuncFunction, ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)
        except:
            import traceback
            traceback.print_exc()

    @classmethod
    def processSubgrid(cls, i, n, iy, ix, ny, nx, workingGrid):
        cls.operator.progressBar.setTotalSteps(n)
        cls.operator.progressBar.setProgress(i)
        return cls.operator._apply(workingGrid=workingGrid, iblock=i, nblock=n, yblock=iy, xblock=ix, nyblock=ny, nxblock=nx)

def _pickableWorkerProcessSubgrid(**kwargs):
    return _Worker.processSubgrid(**kwargs)

def _pickableWorkerInitialize(*args):
    return _Worker.initialize(*args)

class ApplierOperator(object):
    """
    This is the baseclass for an user defined applier operator.
    For details on user defined operators see :meth:`hubdc.applier.Applier.apply`
    """

    def __init__(self, mainGrid, inputRaster, inputRasterArchive, inputVector, outputRaster,
                 controls, ufuncArgs, ufuncKwargs, ufuncFunction=None):
        assert isinstance(mainGrid, PixelGrid)
        assert isinstance(inputRaster, ApplierInputRasterGroup)
        assert isinstance(inputRasterArchive, ApplierInputRasterArchiveGroup)
        assert isinstance(inputVector, ApplierInputVectorGroup)
        assert isinstance(outputRaster, ApplierOutputRasterGroup)
        assert isinstance(controls, ApplierControls)

        self._workingGrid = None
        self._mainGrid = mainGrid

        self.inputRaster = inputRaster
        self.inputRasterArchive = inputRasterArchive
        self.inputVector = inputVector
        self.outputRaster = outputRaster

        self.inputRaster.operator = self
        self.inputRasterArchive.operator = self
        self.inputVector.operator = self
        self.outputRaster.operator = self

        self._controls = controls
        self._ufuncArgs = ufuncArgs
        self._ufuncKwargs = ufuncKwargs
        self._ufuncFunction = ufuncFunction
        self.iblock = 0
        self.nblock = 0

    @property
    def workingGrid(self):
        """
        Returns the :class:`~hubdc.applier.PixelGrid` of the currently processed block.
        """
        assert isinstance(self._workingGrid, PixelGrid)
        return self._workingGrid

    @property
    def mainGrid(self):
        """
        Returns the :class:`~hubdc.applier.PixelGrid`.
        """
        assert isinstance(self._mainGrid, PixelGrid)
        return self._mainGrid

    def _setWorkingGrid(self, grid):
        assert isinstance(grid, PixelGrid)
        self._workingGrid = grid

    @property
    def progressBar(self):
        """
        Returns the progress bar.
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
        return numpy.full(shape=(bands, self.workingGrid.ySize+2*overlap, self.workingGrid.xSize+2*overlap),
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
        """
        Overwrite this method to specify the image processing.

        See :doc:`ApplierExamples` for more information.
        """
        if self._ufuncFunction is None:
            raise NotImplementedError()
        else:
            return self._ufuncFunction(self, *args, **kwargs)


class ApplierControls(object):

    def __init__(self):

        self.setWindowXSize()
        self.setWindowYSize()
        self.setNumThreads()
        self.setNumWriter()
        self.setCreateEnviHeader()
        self.setAutoFootprint()
        self.setAutoResolution()
        self.setResolution()
        self.setFootprint()
        self.setProjection()
        self.setReferenceGrid()
        self.setDisableWindowTrimToFootprint()
        self.setGDALCacheMax()
        self.setGDALSwathSize()
        self.setGDALDisableReadDirOnOpen()
        self.setGDALMaxDatasetPoolSize()
        self.setGDALWarpErrorThreshold()
        self.setGDALWarpMemoryLimit()
        self.setGDALWarpMultithread()
        self.setProgressBar()

    def setProgressBar(self, progressBar=None):
        """
        Set the progress display object. Default is an :class:`~hubdc.progressbar.CUIProgress` object.
        For suppressing outputs use an :class:`~hubdc.progressbar.SilentProgress` object
        """
        if progressBar is None:
            progressBar = CUIProgressBar()

        self.progressBar = ProgressBarDelegate(progressBar=progressBar)
        return self

    def setWindowXSize(self, windowxsize=Default.WINDOWXSIZE):
        """
        Set the X size of the blocks used. Images are processed in blocks (windows)
        of 'windowxsize' columns, and 'windowysize' rows.
        """

        self.windowxsize = windowxsize
        return self

    def setWindowYSize(self, windowysize=Default.WINDOWYSIZE):
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

        veryLargeNumber = 10**20
        self.setWindowXSize(veryLargeNumber)
        self.setWindowYSize(veryLargeNumber)
        return self

    def setNumThreads(self, nworker=Default.NWORKER):
        """
        Set the number of pool worker for multiprocessing. Set to None to disable multiprocessing (recommended for debugging).
        """
        if nworker==-1:
            import multiprocessing
            nworker = multiprocessing.cpu_count()

        self.nworker = nworker
        return self

    def setNumWriter(self, nwriter=Default.NWRITER):
        """
        Set the number of writer processes. Set to None to disable multiwriting (recommended for debugging).
        """
        self.nwriter = nwriter
        return self

    def setCreateEnviHeader(self, createEnviHeader=Default.CREATEENVIHEADER):
        """
        Set to True to create additional ENVI header files for all output rasters.
        The header files store all metadata items from the GDAL PAM ENVI domain,
        so that the images can be correctly interpreted by the ENVI software.
        Currently only the native ENVI format and the GTiff format is supported.
        """
        self.createEnviHeader = createEnviHeader
        return self

    def setAutoFootprint(self, footprintType=Default.FOOTPRINTTYPE):
        """
        Derive extent of the reference pixel grid from input files. Possible options are 'union' or 'intersect'.
        """
        self.footprintType = footprintType
        return self

    def setAutoResolution(self, resolutionType=Default.RESOLUTIONTYPE):
        """
        Derive resolution of the reference pixel grid from input files. Possible options are 'minimum', 'maximum' or 'average'.
        """
        self.resolutionType = resolutionType
        return self

    def setResolution(self, xRes=None, yRes=None):
        """
        Set resolution of the reference pixel grid.
        """
        self.xRes = xRes
        self.yRes = yRes
        return self

    def setFootprint(self, xMin=None, xMax=None, yMin=None, yMax=None):
        """
        Set spatial footprint of the reference pixel grid.
        """
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        return self

    def setProjection(self, projection=None):
        """
        Set projection of the reference pixel grid.
        """
        self.projection = projection
        return self

    def setProjectionFromEPSG(self, epsg=None):
        """
        Set projection of the reference pixel grid .
        """
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(int(epsg))
        self.setProjection(projection=projection)
        return self

    def setReferenceGrid(self, grid=None):
        """
        Set the reference pixel grid. Pass an instance of the :py:class:`~hubdc.model.PixelGrid.PixelGrid` class.
        """
        assert grid is None or isinstance(grid, PixelGrid)
        self.referenceGrid = grid
        return self

    def setReferenceGridByImage(self, filename=None):
        """
        Set an image defining the reference pixel grid.
        """
        if filename is None:
            self.setReferenceGrid(grid=None)
        else:
            self.setReferenceGrid(grid=PixelGrid.fromFile(filename))
        return self

    def setReferenceGridByVector(self, filename, xRes, yRes, layerNameOrIndex=0):
        """
        Set a vector layer defining the reference pixel grid footprint and projection.
        """

        layer = OpenLayer(filename=filename, layerNameOrIndex=layerNameOrIndex)
        grid = layer.makePixelGrid(xRes=xRes, yRes=yRes)
        self.setReferenceGrid(grid=grid)
        return self

    def setDisableWindowTrimToFootprint(self, disable=False):
        self.disableWindowTrimToFootprint = disable

    def setGDALCacheMax(self, bytes=Default.GDAL_CACHEMAX):
        """
        For details see the `GDAL_CACHEMAX Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_CACHEMAX>`_.
        """
        self.cacheMax = bytes
        return self

    def setGDALSwathSize(self, bytes=Default.GDAL_SWATHSIZE):
        """
        For details see the `GDAL_SWATH_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_SWATH_SIZE>`_.
        """
        self.swathSize = bytes
        return self

    def setGDALDisableReadDirOnOpen(self, disable=Default.GDAL_DISABLEREADDIRONOPEN):
        """
        For details see the `GDAL_DISABLE_READDIR_ON_OPEN Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_DISABLE_READDIR_ON_OPEN>`_.
        """
        self.disableReadDirOnOpen = disable
        return self

    def setGDALMaxDatasetPoolSize(self, nfiles=Default.GDAL_MAXDATASETPOOLSIZE):
        """
        For details see the `GDAL_MAX_DATASET_POOL_SIZE Configuration Option <https://trac.osgeo.org/gdal/wiki/ConfigOptions#GDAL_MAX_DATASET_POOL_SIZE>`_.
        """
        self.maxDatasetPoolSize = nfiles
        return self

    def setGDALWarpErrorThreshold(self, errorThreshold=Default.GDALWARP_ERRORTHRESHOLD):
        self.gdalWarpErrorThreshold = errorThreshold

    def setGDALWarpMemoryLimit(self, memoryLimit=Default.GDALWARP_MEMORYLIMIT):
        self.gdalWarpMemoryLimit = memoryLimit

    def setGDALWarpMultithread(self, multithread=Default.GDALWARP_MULTITHREAD):
        self.gdalWarpMultithread = multithread

    @property
    def _multiprocessing(self):
        return self.nworker is not None

    @property
    def _multiwriting(self):
        return self._multiprocessing or (self.nwriter is not None)

    def _makeAutoGrid(self, inputRasterContainer):
        assert isinstance(inputRasterContainer, ApplierInputRasterGroup)
        grids = [inputRaster.dataset.pixelGrid for inputRaster in inputRasterContainer.getFlatRasters()]

        projection = self._deriveProjection(grids)
        xMin, xMax, yMin, yMax = self._deriveFootprint(grids, projection)
        xRes, yRes = self._deriveResolution(grids)
        return PixelGrid(projection=projection, xRes=xRes, yRes=yRes, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)

    def _deriveProjection(self, grids):

        if self.projection is None:
            if len(grids) == 0:
                raise Exception('projection not defined')
            for grid in grids:
                if not grid.equalProjection(grids[0]):
                    raise Exception('input projections do not match')
            projection = grids[0].projection
        else:
            projection = self.projection
        return projection

    def _deriveFootprint(self, grids, projection):

        if None in [self.xMin, self.xMax, self.yMin, self.yMax]:

            if len(grids) == 0:
                raise Exception('footprint not defined')

            xMins, xMaxs, yMins, yMaxs = numpy.array([grid.reprojectExtent(targetProjection=projection) for grid in grids]).T


            if self.footprintType == Enum.Footprint.UNION:
                xMin = xMins.min()
                xMax = xMaxs.max()
                yMin = yMins.min()
                yMax = yMaxs.max()
            elif self.footprintType == Enum.Footprint.INTERSECTION:
                xMin = xMins.max()
                xMax = xMaxs.min()
                yMin = yMins.max()
                yMax = yMaxs.min()
                if xMax <= xMin or yMax <= yMin:
                    raise Exception('input extents do not intersect')
            else:
                raise ValueError('unknown footprint type')

        else:
            xMin, xMax, yMin, yMax = self.xMin, self.xMax, self.yMin, self.yMax

        return xMin, xMax, yMin,yMax

    def _deriveResolution(self, grids):

        if self.xRes is None or self.yRes is None:
            xResList = numpy.array([grid.xRes for grid in grids])
            yResList = numpy.array([grid.yRes for grid in grids])
            if self.resolutionType == Enum.Resolution.MINIMUM:
                xRes = xResList.min()
                yRes = yResList.min()
            elif self.resolutionType == Enum.Resolution.MAXIMUM:
                xRes = xResList.max()
                yRes = yResList.max()
            elif self.resolutionType == Enum.Resolution.AVERAGE:
                xRes = xResList.mean()
                yRes = yResList.mean()
            else:
                raise ValueError('unknown resolution type')
        else:
            xRes = self.xRes
            yRes = self.yRes

        return xRes, yRes
