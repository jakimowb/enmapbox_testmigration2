import warnings
from os.path import join, basename, dirname, isdir, splitext, exists
from os import listdir
from collections import OrderedDict, namedtuple
import json
import fnmatch
import random
import pickle
import time
import copy
import numpy as np
from osgeo import gdal, gdal_array, ogr, osr

import ee
import ee.ee_string
import ee.ee_list
import ee.batch
from ee.apifunction import ApiFunction as eeApiFunction
from ee.computedobject import ComputedObject as eeComputedObject
import ee.ee_types

from types import MethodType

# add methods to ee.Image
# class eeImage(object):

#    def cache(self):
#        name = 'Image.cache'
#        signature = dict(args=[], description='', returns='Image', type='Algorithm', hidden=False, name=name)
#        return ee.Image(func=eeApiFunction(name=name, opt_signature=signature), args=[])

# setattr(ee.Image, 'cache', eeImage.cache)

import dask
import dask.distributed
from hubdc.core import Grid, Projection, openRasterDataset, RasterDataset, RasterDriver, VrtDriver, createVRTDataset
import hubee.signatures

with open('ApiFunction.pkl', 'rb') as f:
    vars = pickle.load(file=f)

eeApiFunction._api = vars['ee.apifunction.ApiFunction._api']
eeApiFunction._bound_signatures = vars['ee.apifunction.ApiFunction._bound_signatures']

# add api functions that are not present in GEE
name = 'Image.cache'
eeApiFunction._bound_signatures.add(name)
eeApiFunction._api[name] = eeApiFunction(name=name,
                                         opt_signature=dict(args=[dict(description='', name='image', type='Image'),
                                                                  dict(description='', name='key', type='String')],
                                                            description='', returns='Image', type='Algorithm',
                                                            hidden=False, name=name))

ee._InitializeGeneratedClasses()


class Environment(object):
    debug = False

    class Force(object):

        _idPrefix = 'force/'
        _root = ''
        _tiles = list()

        class Tile(object):

            def __init__(self, name, grid):
                assert isinstance(name, str)
                assert isinstance(grid, Grid)
                self.name = name
                self.grid = grid

        @classmethod
        def idPrefix(cls):
            return cls._idPrefix

        @classmethod
        def root(cls):
            if not exists(cls._root):
                raise Exception(
                    'Invalid Force root folder: {}\nUse Environment.Force.setRoot to define the root folder'.format(
                        cls._root))
            return cls._root

        @classmethod
        def setRoot(cls, path):
            cls._root = path

        @classmethod
        def tiles(cls):
            for tile in cls._tiles:
                assert isinstance(tile, cls.Tile), tile
                yield tile

        @classmethod
        def setTiles(cls, tiles, extend=True):

            for tile in tiles:
                assert isinstance(tile, cls.Tile)

            if extend:
                cls._tiles.extend(tiles)
            else:
                cls._tiles = tiles

    class Cache(object):

        _enabled = True
        _arrays = dict()
        _maskArrays = dict()

        @classmethod
        def clear(cls):
            cls._arrays = dict()
            cls._maskArrays = dict()

        @classmethod
        def enable(cls, bool=True):
            cls._enabled = bool

        @classmethod
        def setArray(cls, obj, value):
            if obj._hashKey is None:
                assert 0
            if cls._enabled:
                cls._arrays[obj._hashKey] = value

        @classmethod
        def setMaskArray(cls, obj, value):
            if obj._hashKey is None:
                assert 0
            if cls._enabled:
                cls._maskArrays[obj._hashKey] = value

        @classmethod
        def array(cls, obj):
            if obj._hashKey in cls._arrays:
                return cls._arrays[obj._hashKey]
            else:
                return None

        @classmethod
        def maskArray(cls, obj):
            if obj._hashKey in cls._maskArrays:
                return cls._maskArrays[obj._hashKey]
            else:
                return None

    class Debug(object):

        enabled = False

        @classmethod
        def print(cls, *args, **kwargs):
            if cls.enabled:
                print(*args, **kwargs)


def computeImage(eeObject, filename, noDataValues=None):
    image = fetch(eeObject)

    # check object type
    if not isinstance(image, Image):
        raise Exception("Invalid argument: 'image' must be of type Image.")

    # check data type
    isinstance(image, Image)
    dataType0 = image.band(0).dataType()
    for band in image.bands():
        if not band.dataType().equal(dataType0):
            raise Exception(
                'Exported bands must have compatible data types; found inconsistent types: {} and {}'.format(
                    band.dataType().precision(), dataType0.precision()))

    if noDataValues is None:
        noDataValues = [None] * len(image)
    else:
        if not len(noDataValues) == len(image):
            raise Exception('Number of bands ({}) does not match number of no data values ({}).'.format(len(image), len(
                noDataValues)))

    jobs = list()
    for tile in Environment.Force.tiles():
        jobs.append(computeImageTile(image, noDataValues, filename, tile))

    # compute jobs
    if Environment.debug:
        filenames, = dask.compute(jobs, scheduler="single-threaded")
    else:
        client = dask.distributed.Client(set_as_default=True, processes=True)
        print(client)
        filenames, = dask.compute(jobs)  # , scheduler="single-threaded")

    filenames = [f for f in filenames if f is not None]  # remove tiles that are not covered

    if len(filenames) != 0:
        filename_ = filename.format(tilename='.', band='.vrt')
        createVRTDataset(filenames, filename=filename_)
    else:
        filename_ = None
        warnings.warn('Not a single tile is covered. {} is not created.'.format(filename))

    return filename_


@dask.delayed
def computeImageTile(image, noDataValues, filename, tile):
    Environment.Cache.clear()

    assert isinstance(tile, Environment.Force.Tile)

    Environment.Debug.print('Tile: {}'.format(tile.name))
    filenames = list()
    tileNotCovered = False
    for i in range(len(image)):

        band = image.band(i)
        array, maskArray = band.compute(tile=tile)

        if array is None or maskArray is None:
            # Do not create a file if the current tile is not covered.
            # (Or should we create an empty file with no data values?)
            # If this happens in one band it should happen in all bands,
            # so we can break out of the loop and do not create the VRT stack

            tileNotCovered = True
            warnings.warn('Tile {} not covered. Tile is skipped and no output file is created.'.format(tile.name))
            break

        # EE masks are "fuzzy" booleans between 0 (False) and 1 (True)
        # When writing to a GDAL file, the fuzzyness is lost, by replacing zero-pixels with the no data value.

        noDataValue = noDataValues[i]
        if noDataValue is not None:
            array[np.logical_not(maskArray)] = noDataValue
            # ds.band(i).setNoDataValue(value=noDataValues[i]) did not work (?!)

        filename_ = filename.format(tilename=tile.name, band='.{}.bsq'.format(band.id()))
        driver = RasterDriver.fromFilename(filename_)
        rasterDataset = RasterDataset.fromArray(array=array, grid=tile.grid, filename=filename_, driver=driver)
        # ds.band(i).writeArray(array=array)
        rasterDataset.band(0).setNoDataValue(noDataValue)
        if band.id() is None:
            print('WARNING: band id not set:', filename_)
            assert 0
        else:
            rasterDataset.band(0).setDescription(band.id())
        rasterDataset.close()
        filenames.append(filename_)

    if tileNotCovered:
        filename_ = None
    else:
        filename_ = filename.format(tilename=tile.name, band='.vrt')
        rasterDataset = createVRTDataset(filenames, filename=filename_, separate=True)
        rasterDataset.setNoDataValues(noDataValues)
        for i in range(len(image)):
            if band.id() is None:
                print('WARNING: band id not set:', filename_)
            else:
                rasterDataset.band(i).setDescription(image.band(i).id())

    return filename_


def fetch(obj):
    if isinstance(obj, (ComputedObject, str, int, float)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return type(obj)(fetch(item) for item in obj)
    elif isinstance(obj, dict):
        return obj
        # return {k: fetch(v) for k, v in obj.items()} # do we need to fetch dict values?
    elif isinstance(obj, ee.Number):
        return obj._number
    elif isinstance(obj, ee.String):
        return obj._string
    elif isinstance(obj, ee.List):
        return [fetch(item) for item in obj._list]
    elif isinstance(obj, ee.CustomFunction):
        return fetch(obj._body)
    elif isinstance(obj, (ee.Geometry, ee.Feature, ee.Image, ee.Collection,
                          ee.Reducer, ee.Classifier)):

        if not isinstance(obj.func, ee.ApiFunction):
            if isinstance(obj, ee.Image):
                if obj.varName == '_MAPPING_VAR_0_0':
                    return lambda image: image
                else:
                    assert 0
            elif isinstance(obj, ee.Geometry):
                return Geometry(obj.toGeoJSON())
            else:
                assert 0

        funcname = obj.func.getSignature()['name']

        if funcname.startswith('reduce.'):
            collection = fetch(obj.args['collection'])
            assert isinstance(collection, ImageCollection)
            reducerName = funcname.split('.')[1]
            reducer = getattr(Reducer, reducerName)()
            fetched = collection.reduce(reducer=reducer)

        elif funcname == 'Collection.map':
            collection = fetch(obj.args['collection'])

            # fetch map function
            def fetchMapFunction(obj):
                if isinstance(obj, ee.CustomFunction):
                    if obj._body.varName == '_MAPPING_VAR_0_0':
                        mapFunction = lambda image: image
                    else:
                        mapFunction = fetchMapFunction(obj._body)
                elif isinstance(obj, ee.Image):
                    if obj.varName == '_MAPPING_VAR_0_0':
                        mapFunction = lambda image: image
                    elif obj.varName is None:
                        method = obj.func._signature['name'].split('.')[-1]

                        args = dict()

                        signatures = obj.func._signature['args']
                        for i, signature in enumerate(signatures):
                            name = signature['name']
                            # if i == 0:
                            #    continue
                            if name in obj.args:
                                args[name] = fetchMapFunction(obj.args[name])

                        def mapFunction(image):
                            fetchedArgs = dict()
                            for k, f in args.items():
                                fetchedArgs[k] = f(image)

                            if type(getattr(image,
                                            method)).__name__ == 'method':  # skip first arg in case of instance method
                                #    fetchedArgs.pop(signatures[0]['name'])
                                result = getattr(Image, method)(**fetchedArgs)
                            else:
                                result = getattr(image, method)(**fetchedArgs)

                            return result

                        mapFunction = mapFunction

                    else:
                        assert 0
                elif isinstance(obj, ee.ApiFunction):
                    mapFunction = lambda image: image

                elif isinstance(obj, (int, float, ee.List, ee.Number, ee.String)):
                    obj = fetch(obj)
                    mapFunction = lambda image: obj

                else:
                    assert 0, obj

                return mapFunction
                # mapFunction = lambda image:

            algorithm = fetchMapFunction(obj.args['baseAlgorithm'])

            fetched = collection.map(algorithm=algorithm, dropNulls=obj.args.get('dropNulls'))

        else:

            args = dict()
            for k, arg in obj.args.items():
                args[k] = fetch(arg)

            tmp = funcname.split('.')
            if len(tmp) == 1:  # class constructor
                cls = eval(funcname)
                method = cls
            elif len(tmp) == 2:  # class methode
                cls = eval(tmp[0])
                method = getattr(cls, tmp[1])
                if method in ['and', 'or']:
                    method = method.title()
            else:
                assert 0, funcname

            try:
                fetched = fetch(method(**args))
            except AttributeError:
                print('missing or corrupted EE backend function\n\n' + obj.func.getSignature()['name'] + '\n' + str(
                    obj.func))
                raise
        returnCls = eval(obj.func.getSignature()['returns'])
        if not isinstance(fetched, returnCls):
            raise Exception('Wrong result type ({}), expected: {}'.format(type(fetched), returnCls))

        return fetched

    else:
        raise Exception('Can not fetch object: {}.'.format(obj))


def getInfo(obj):
    """Fetch and return information about this object."""

    if obj is None:
        return None

    fetched = fetch(obj)
    info = fetched.getInfo()
    return info


eeComputedObject.getInfo = getInfo


class PixelType(object):
    '''A representation of an Earth Engine pixel type.'''

    EE_TYPENAMES = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'byte', 'short', 'int', 'long',
                    'float', 'double']

    def __init__(self, precision):

        if not precision in self.EE_TYPENAMES:
            raise Exception('Unknown pixel type "{}", use one of these: {}'.format(precision, self.EE_TYPENAMES))

        self._precision = precision

    @classmethod
    def fromNumpyType(cls, dtype):
        for eetype in cls.EE_TYPENAMES:
            if eetype == 'float':
                name = 'float32'
            elif eetype == 'double':
                name = 'float64'
            elif eetype == 'byte':
                name = 'uint8'
            else:
                name = eetype

            if dtype == eval('np.{}'.format(name)):
                return PixelType(precision=eetype)
        raise Exception('Unknown numpy type: {}'.format(dtype))

    def precision(self):
        return self._precision

    def dtype(self):
        '''Return numpy data type.'''

        if self.precision == 'float':
            return np.float32
        else:
            return np.dtype(self.precision())

    def equal(self, other):
        assert isinstance(other, PixelType)
        return self.precision() == other.precision()


class ComputedObject(object):
    '''
    A representation of an Earth Engine computed object.

    This is a base class for most API objects.
    '''

    def getInfo(self):
        raise NotImplementedError('getInfo is not implemented for {}'.format(self.__class__))

    def copy(self):
        return copy.deepcopy(self)


class Element(ComputedObject):
    """Base class for ImageCollection and FeatureCollection."""

    def __init__(self):
        self._properties = dict()

    @staticmethod
    def name():
        return 'Element'

    def _shallowCopy(self):
        raise NotImplementedError('{}._shallowCopy not implemented'.format(self.__class__.__name__))
        return Element()

    def properties(self):
        return self._properties

    def set(object, key, value):
        element = object._shallowCopy()
        assert isinstance(element, object.__class__)
        element.properties()[key] = value
        return element

    def get(self):
        assert 0


class Band(object):
    '''Representation for an Earth Engine Band.'''

    def __init__(self):
        self._mask = None
        self._cache = False
        self._hashKey = None

    def cache(self, key, enabled=True):
        self._cache = enabled
        self._hashKey = key

    def mask(self):
        if self._mask is None:
            return self._defaultMask()
        assert isinstance(self._mask, Image)
        return self._mask

    def _defaultMask(self):
        return Image(ConstantBand(np.float32(1.)))

    def copy(self):
        return copy.deepcopy(self)

    def updateMask(self, mask):
        assert isinstance(mask, Image)
        assert len(mask) == 1
        result = self.copy()
        result._mask = mask.min(self.mask())
        return result

    def compute(self, tile, returnMaskArray=True):
        raise NotImplementedError

    def dataType(self):
        raise NotImplementedError

    def id(self):
        raise NotImplementedError

    def properties(self):
        raise NotImplementedError


class WrittenBand(Band):

    def __init__(self, filename, index, noDataValue, id, data_type):
        Band.__init__(self)
        self._filename = filename
        self._index = index
        self._noDataValue = noDataValue
        self._id = id
        self._data_type = data_type
        self._hashKey = '{}[{}]'.format(self._filename, self._id)

    def __repr__(self):
        return '{}[{}]'.format(basename(self._filename), self._id)

    def id(self):
        return self._id

    def dataType(self):
        return self._data_type

    def _defaultMask(self):
        assert self._noDataValue is not None
        return Image(self).neq(self._noDataValue)

    def compute(self, tile, returnMaskArray=True, raiseFileNotFoundError=False):

        # key = self._filename, self._index, tile[0]

        array = Environment.Cache.array(self)
        if array is None:
            filename = self._filename.format(tilename=tile.name)

            if exists(filename):
                ds = gdal.Open(filename)
                array = ds.GetRasterBand(self._index + 1).ReadAsArray()
                Environment.Cache.setArray(self, array)
            else:
                if raiseFileNotFoundError:
                    raise FileNotFoundError(
                        '{}: No such file or directory. You may want to set raiseFileNotFoundError=False to return None instead of raising an error.'.format(
                            filename))
                array = None

            # Debug.print(self._filename.format(tilename=tile[0]), self._index + 1)

        if returnMaskArray:
            maskArray = Environment.Cache.maskArray(self)
            if maskArray is None:
                maskArray = self.mask().band(0).compute(tile=tile, returnMaskArray=False)
                Environment.Cache.setMaskArray(self, maskArray)
            return array, maskArray
        else:
            return array


class ConstantBand(Band):
    '''Representation for a constant Earth Engine Band.'''

    def __init__(self, constant):
        Band.__init__(self)
        self._constant = constant

    def __repr__(self):
        return str(self._constant)

    def id(self):
        return 'constant'

    def dataType(self):
        return PixelType.fromNumpyType(np.array(self._constant).dtype)

    def dimensions(self):
        return None

    def crs(self):
        return 'EPSG:4326'

    def crsTransform(self):
        return (1, 0, 0, 0, 1, 0)

    def compute(self, tile, returnMaskArray=True):
        assert isinstance(tile, Environment.Force.Tile)
        array = np.full(shape=tile.grid.shape(), fill_value=self._constant)
        if returnMaskArray:
            maskArray = self.mask().band(0).compute(tile=tile, returnMaskArray=False)
            return array, maskArray
        else:
            return array


class Geometry(Element):
    '''Representation for an Earth Engine Geometry.'''

    def __init__(self, type, coordinates):
        self.type = type
        self.coordinates = coordinates

    def json(self):
        return json.dumps(self.__dict__)

    def getInfo(self):
        return self.json()


class Feature(Element):
    '''Representation for an Earth Engine Feature.'''

    def __init__(self, geometry=None, metadata=None):

        if isinstance(geometry, (Geometry, type(None))):
            self._geometry = geometry
            self._properties = metadata
        elif isinstance(geometry, (ComputedObject, Feature, Geometry)):
            raise NotImplementedError(str(geometry))
        else:
            assert 0

    def properties(self):
        return self._properties

    def getInfo(self):
        return {'geometry': getInfo(self._geometry),
                'properties': self._properties}


class Image(Element):
    '''Representation for an Earth Engine Image.'''

    def __init__(self, args=None):
        Element.__init__(self)

        self._id = None
        self._bands = list()

        if ee.types.isNumber(args):
            # A constant image.
            self.bands().append(ConstantBand(constant=args))
        elif ee.types.isString(args):
            # An ID.
            self._id = str(args)

            if self._id.startswith('force/'):
                root = Environment.Force.root()  # r'C:\Work\data\FORCE\crete'
                date, level, sensor = basename(self._id).split('_')

                # BOA
                data_type = PixelType(precision=np.int16().dtype.name)
                noDataValue = -9999
                filename = join(root, level.lower(), '{tilename}', '{}_BOA.tif'.format(basename(self._id)))
                for index, bandid in enumerate(['B{}'.format(i + 1) for i in range(6)]):
                    self.bands().append(WrittenBand(filename=filename, index=index, noDataValue=noDataValue, id=bandid,
                                                    data_type=data_type))
                    self._properties['system:time_start'] = date

                #  QAI
                filename = join(root, level.lower(), '{tilename}', '{}_QAI.tif'.format(basename(self._id)))
                self.bands().append(WrittenBand(filename=filename, index=0, noDataValue=1, id='QAI',
                                                data_type=PixelType(precision=np.int16().dtype.name)))

                #  CLD
                filename = join(root, level.lower(), '{tilename}', '{}_CLD.tif'.format(basename(self._id)))
                self.bands().append(WrittenBand(filename=filename, index=0, noDataValue=-9999, id='CLD',
                                                data_type=PixelType(precision=np.int16().dtype.name)))

            else:
                assert 0

        elif isinstance(args, (list, tuple)):
            # Make an image out of each element.
            assert 0
        elif isinstance(args, Band):
            self.bands().append(args)
        elif isinstance(args, Image):
            self.__dict__ = args.__dict__
        elif args is None:
            # Make empty image
            pass
        else:
            raise Exception('Unrecognized argument type to convert to an Image: {}'.format(args))

        # assert self.id() is not None
        for band in self.bands():
            assert band.id() is not None

    '''elif isinstance(args, computedobject.ComputedObject):
      if args.name() == 'Array':
        # A constant array image.
        super(Image, self).__init__(
            apifunction.ApiFunction.lookup('Image.constant'), {'value': args})
      else:
        # A custom object to reinterpret as an Image.
        super(Image, self).__init__(args.func, args.args, args.varName)
    elif args is None:
      super(Image, self).__init__(
          apifunction.ApiFunction.lookup('Image.mask'),
          {'image': Image(0), 'mask': Image(0)})
    else:
      raise ee_exception.EEException(
          'Unrecognized argument type to convert to an Image: %s' % args)

    '''

    def __len__(self):
        return len(self._bands)

    def _shallowCopy(self):
        image = Image()
        image._id = self._id
        image._bands = self._bands
        image._properties = copy.deepcopy(self._properties)
        return image

    def cache(image, key):
        for band in image.bands():
            band.cache(key)
        return image

    def bands(self):
        return self._bands

    def band(self, index):
        band = self._bands[index]
        if not isinstance(band, (Band, ConstantBand, MapOperator)):
            assert 0
        return band

    def properties(self):
        return self._properties

    def crs(self):
        return self.band(0).crs()

    def crsTransform(self):
        '''Return geo transform [xScale, xShearing, xTranslation, yShearing, yScale, yTranslation] tuple.'''
        return self.band(0).crsTransform()

    @staticmethod
    def load(id):
        return Image(args=id)

    @staticmethod
    def constant(value):
        return Image(args=value)

    @staticmethod
    def name():
        return 'Image'

    def id(self):
        return self._id

    def dimension(self):
        return self.band(0).dimensions()

    def getInfo(self):
        info = dict()
        info['type'] = self.name()
        if hasattr(self, 'id'):
            info['id'] = self.id()

        info['bands'] = list()
        for band in self.bands():
            bandInfo = dict()
            if isinstance(band, (Band, MapOperator)):
                if hasattr(band, 'id'):
                    bandInfo['id'] = band.id()
                bandInfo['data_type'] = {'type': 'PixelType',
                                         'precision': band.dataType().precision()}
            else:
                assert 0
            info['bands'].append(bandInfo)

        info['properties'] = self.properties()
        return info

    def updateMask(image, mask):
        assert isinstance(mask, Image)
        # Debug.print('Image.updateMask', image.id(), [band.id() for band in image.bands()])
        result = image.copy()
        result._bands = list()
        for i, band in enumerate(image.bands()):
            if len(mask) == 1:
                mask_ = mask.select([0])
            elif len(mask) == len(image):
                mask_ = mask.select([i])
            else:
                raise Exception(
                    'Image.updateMask: Incompatible number of bands in the mask image: {}. Expected {} or 1.'.format(
                        len(mask), len(image)))
            result.addBands(Image(band.updateMask(mask=mask_)))
        return result.rename(image.bandNames())

    def mask(image):
        mask = Image()
        for band in image.bands():
            mask.bands().append(band.mask().band(0))
        return mask

    def addBands(dstImg, srcImg, names=None, overwrite=None):
        assert isinstance(srcImg, Image)
        if names is not None:
            raise NotImplementedError
        if overwrite is not None:
            raise NotImplementedError

        dstImg.bands().extend(srcImg.copy().bands())
        return dstImg

    def bandNames(image):
        result = list()
        for band in image.bands():
            result.append(band.id())
        return result

    def rename(input, names):
        result = copy.deepcopy(input)
        for band, name in zip(result.bands(), names):
            band._id = name
        return result

    def select(input, bandSelectors, newNames=None):
        assert isinstance(bandSelectors, (list, tuple)), bandSelectors
        result = Image()
        if hasattr(input, 'id'):
            result._id = input.id()

        if isinstance(input, str):
            assert 0
        result.properties = input.properties

        for bandSelector in bandSelectors:
            if isinstance(bandSelector, int):
                i = bandSelector
            elif isinstance(bandSelector, str):
                try:
                    i = input.bandNames().index(bandSelector)
                except:
                    raise Exception(
                        "Image.select: Band selector Pattern '{}' did not match any bands.".format(bandSelector))
            else:
                assert 0
            result.bands().append(copy.deepcopy(input.bands()[i]))

        if newNames is not None:
            result = result.rename(names=newNames)

        return result

    def normalizedDifference(input, bandNames=None):
        if bandNames is None:
            bandNames = [0, 1]
        result = Image(MapNormalizedDifference(image=input.select(bandSelectors=bandNames)))
        return result

    def add(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.add)

    def multiply(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.multiply)

    def min(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.minimum)

    def eq(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.equal)

    def neq(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.not_equal)

    def gt(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.greater)

    def And(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.logical_and)

    def Or(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.logical_or)

    def bitwiseAnd(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.bitwise_and)

    def _binaryMapOperator(image1, image2, function):

        if not isinstance(image2, Image):
            image2 = Image(image2)

        n1, n2 = len(image1), len(image2)
        n = max(n1, n2)
        if n > 1:
            if n1 != n2:
                if n1 != 1 and n2 != 1:
                    raise Exception(
                        'Image.{}: Images must contain the same number of bands or only 1 band. Got {} and {}.'.format(
                            function.__name__, n1, n2))

        if n1 == n:
            bandNames1 = image1.bandNames()
        else:
            bandNames1 = image1.bandNames() * n  # replicate bands

        if n2 == n:
            if n1 == n:
                try:  # match by band names
                    bandNames2 = image2.select(image1.bandNames()).bandNames()
                except:  # match by natural order
                    bandNames2 = image2.bandNames()
            else:
                bandNames2 = image2.bandNames()
        else:
            bandNames2 = image2.bandNames() * n  # replicate bands

        result = Image()
        for b1, b2 in zip(bandNames1, bandNames2):
            result.addBands(srcImg=Image(MapBinaryValueWiseOperator(band1=image1.select([b1]).band(0),
                                                                    band2=image2.select([b2]).band(0),
                                                                    function=function)))
        return result

    def int16(value):
        raise NotImplementedError()

    def sampleRegions(image, collection, properties=None, scale=None, projection=None, tileScale=1, geometries=True):
        '''
        Samples the pixels of an image in one or more regions, returning them as a FeatureCollection.
        Each output feature will have 1 property per band in the input image, as well as any specified properties
        copied from the input feature. Note that geometries will be snapped to pixel centers.

        Arguments:

            image (Image):
            The image to sample.

            collection (FeatureCollection):
            The regions to sample over.

            properties (List, default: null):
            The list of properties to copy from each input feature. Defaults to all non-system properties.

            scale (Float, default: null):
            A nominal scale in meters of the projection to sample in. If unspecified,the scale of the image's first band is used.

            projection (Projection, default: null):
            The projection in which to sample. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale.

            tileScale (Float, default: 1):
            A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default.

            geometries (Boolean, default: false):
            If true, the results will include a geometry per sampled pixel. Otherwise, geometries will be omitted (saving memory).

            Returns: FeatureCollection
        '''

        if scale is not None or projection is not None or tileScale != 1 or geometries is not True:
            raise NotImplementedError()

        if properties is None:
            if collection.features()[0].properties() is not None:
                properties = list(collection.features()[0].properties().keys())
            else:
                properties = list()

            # create vector layer

        def rasterizeFID(grid):

            assert isinstance(grid, Grid)
            sr = osr.SpatialReference(grid.projection().wkt())
            from hubdc.core import VectorDataset, RasterDriver, EnviDriver

            # Create a memory layer to rasterize from.
            ds = ogr.GetDriverByName('Memory').CreateDataSource('wrk')
            layer = ds.CreateLayer('layer', srs=sr)
            field = ogr.FieldDefn('fid', ogr.OFTInteger)
            layer.CreateField(field)

            for fid, feature in enumerate(collection.features()):
                ogrFeature = ogr.Feature(layer.GetLayerDefn())
                ogrGeometry = ogr.CreateGeometryFromJson(feature._geometry.json())
                ogrFeature.SetGeometryDirectly(ogrGeometry)
                ogrFeature.SetField('fid', fid)
                layer.CreateFeature(ogrFeature)

            vectorDataset = VectorDataset(ogrDataSource=ds)
            rasterDataset = vectorDataset.rasterize(grid=grid, gdalType=gdal.GDT_Int32,
                                                    initValue=-1, burnAttribute='fid')
            fidArray = rasterDataset.readAsArray()[0]
            rasterDataset.close()
            return fidArray

        # sample data
        print('NOTE: in Image.sampleRegion, maybe only calculate the image at the pixels of interest?')
        print('NOTE: in Image.sampleRegion, how to consider mask information?')

        fids = list()
        values = {name: list() for name in image.bandNames()}
        maskValues = {name: list() for name in image.bandNames()}

        for tile in Environment.Force.tiles():
            fidArray = rasterizeFID(tile.grid)
            valid = np.where(fidArray != -1)
            assert len(valid[0]) != 0  # handle empty tile (better not even rasterize the fid)
            fids.extend(fidArray[valid])

            for band in image.bands():
                bandName = band.id()
                array, maskArray = band.compute(tile=tile)
                if array is None:
                    assert 0  # handle missing tile case
                values[band.id()].extend(array[valid])
                maskValues[band.id()].extend(maskArray[valid])

        features = [Feature(geometry=None,
                            metadata={key: collection.features()[fid].properties()[key] for key in properties})
                    for fid in fids]

        for name in image.bandNames():
            for value, maskValue, feature in zip(values[name], maskValues[name], features):
                feature.properties()[name] = value

        featureCollection = FeatureCollection(features=features).set('band_order', image.bandNames())
        return featureCollection


class MapVariable(Image):
    pass


class MapOperator(Band):

    def inputCount(self):
        raise NotImplementedError

    def outputCount(self):
        raise NotImplementedError


class MapNormalizedDifference(MapOperator):

    def __init__(self, image):
        assert isinstance(image, Image)
        MapOperator.__init__(self)
        self.image = image

    def dataType(self, ):
        return PixelType(precision='float')

    def dimensions(self):
        return self.image.bands()[0].dimensions()

    def crs(self):
        return self.image.crs()

    def crsTransform(self):
        return self.image.crsTransform()

    def id(self):
        return 'nd'

    def properties(self):
        return {self.image.properties().get(k) for k in ['system:footprint'] if k in self.image.properties()}


class MapBinaryValueWiseOperator(MapOperator):

    def __init__(self, band1, band2, function):
        MapOperator.__init__(self)
        assert isinstance(band1, Band)
        assert isinstance(band2, Band)
        self.band1 = band1
        self.band2 = band2
        self.function = function

    def __repr__(self):
        return '{}({}, {})'.format(self.function.__name__, self.band1, self.band2)

    def compute(self, tile, returnMaskArray=True):

        Environment.Debug.print(self)
        if returnMaskArray:
            array = Environment.Cache.array(self)
            maskArray = Environment.Cache.maskArray(self)
            if array is None or maskArray is None:
                array1, maskArray1 = self.band1.compute(tile=tile)
                array2, maskArray2 = self.band2.compute(tile=tile)
                if array1 is None or array2 is None:
                    array = None
                else:
                    array = self.function(array1, array2)
                if maskArray1 is None or maskArray2 is None:
                    maskArray = None
                else:
                    maskArray = np.minimum(maskArray1, maskArray2)
                if self._cache:
                    Environment.Cache.setArray(self, array)
                    Environment.Cache.setMaskArray(self, maskArray)
            return array, maskArray
        else:
            array1 = self.band1.compute(tile=tile, returnMaskArray=False)
            array2 = self.band2.compute(tile=tile, returnMaskArray=False)
            if array1 is None or array2 is None:
                array = None
            else:
                array = self.function(array1, array2)
            return array

    def dataType(self, ):
        a = np.array([1], dtype=self.band1.dataType().dtype())
        b = np.array([1], dtype=self.band2.dataType().dtype())
        dtype = self.function(a, b).dtype
        if dtype == np.bool8:
            dtype = np.uint8

        return PixelType.fromNumpyType(dtype)

    def id(self):
        if isinstance(self.band1, ConstantBand):
            return self.band2.id()
        else:
            return self.band1.id()


class MapReduceOperator(MapOperator):

    def __init__(self, collection, reducer):
        MapOperator.__init__(self)
        assert isinstance(collection, ImageCollection)
        assert isinstance(reducer, Reducer)
        self.collection = collection
        self.reducer = reducer

    def compute(self, tile, returnMaskArray=True):
        assert isinstance(tile, Environment.Force.Tile)
        print('TODO: cache inside MapReduceOperator.compute')
        nanarrays = list()
        maskArray = np.zeros(shape=tile.grid.shape(), dtype=np.float32)
        for image in self.collection.features():
            assert len(image) == 1
            band = image.band(0)
            array, maskArray_ = band.compute(tile=tile)

            if array is None or maskArray_ is None:
                # Just skip missing datasets. This is equivalent to treating all pixels as nan, but faster!
                continue

            array = np.float32(array)
            array[np.logical_not(maskArray_)] = np.nan
            nanarrays.append(array)
            np.maximum(maskArray, maskArray_, out=maskArray)  # calculate final mask inplace

        array = self.reducer.aggregate(array=nanarrays)
        if returnMaskArray:
            return array, maskArray
        else:
            return array

    def dataType(self):
        return PixelType.fromNumpyType(np.float32)

    def id(self):
        return '{}_{}'.format(self.collection.first().band(0).id(), self.reducer.name())


class Collection(Element):
    '''Base class for ImageCollection and FeatureCollection.'''

    def __init__(self, features):
        assert isinstance(features, list)
        Element.__init__(self)
        self._id = None
        self._features = features
        self.__class__ = FeatureCollection
        assert isinstance(self, FeatureCollection)  # a bit strange to cast to a sub type, but that is what GEE demands

    def __len__(self):
        return len(self.features())

    @staticmethod
    def loadTable(tableId, geometryColumn=None, version=None):
        '''
        Args:
            tableId: The ID of the table to load. Either an asset ID or a
                Fusion Table DocID prefixed with 'ft:'.
            geometryColumn: The name of the column to use as the
                main feature geometry. Not used if tableId is an
                asset ID.
            version: The version of the asset. -1 signifies the latest
                version. Ignored unless tableId is an asset ID.
        '''

        if geometryColumn is not None or version is not None:
            raise NotImplementedError()

        # from hubflow.core import VectorDataset
        # VectorDataset.geometryTypeName()
        ds = ogr.Open(tableId)
        if ds is None:
            raise Exception('Invalid vector dataset: {}'.format(tableId))
        layer = ds.GetLayer(0)
        geometryTypeName = ogr.GeometryTypeToName(layer.GetGeomType())

        # assert geometryTypeName in

        # names = [self._ogrLayer.GetLayerDefn().GetFieldDefn(i).GetName() for i in range(self.fieldCount())]
        #    return names

        features = list()
        for ogrFeature in layer:
            jsonDict = ogrFeature.ExportToJson(as_object=True, options=None)
            features.append(Feature(geometry=Geometry(**jsonDict['geometry']), metadata=jsonDict['properties']))

        return FeatureCollection(features=features)

    def features(self):
        return self._features

    def getInfo(self):
        """Returns all the known information about this collection.

        This function makes an REST call to to retrieve all the known information
        about this collection.

        Returns:
          The return contents vary but will include at least:
           features: an array containing metadata about the items in the
               collection that passed all filters.
           properties: a dictionary containing the collection's metadata
               properties.
        """
        return super(Collection, self).getInfo()

    def first(collection):
        """Returns the first entry from a given collection.

        Returns:
          The first entry from the collection.
        """

        if len(collection._features) == 0:
            raise Exception('Empty collection has no first element.')
        return copy.deepcopy(collection._features[0])

    def filter(self, new_filter):
        """Apply a filter to this collection.

        Args:
            new_filter: Filter to add to this collection.

        Returns:
            The filtered collection object.
        """
        if not new_filter:
            raise Exception('Empty filters.')
        assert 0
        # return self._cast(apifunction.ApiFunction.call_('Collection.filter', self, new_filter))

    def filterMetadata(self, name, operator, value):
        raise NotImplementedError

    def filterBounds(self, geometry):
        """Shortcut to add a geometry filter to a collection.

        Items in the collection with a footprint that fails to intersect
        the given geometry will be excluded when the collection is evaluated.
        This is equivalent to self.filter(Filter().geometry(...)).

        Args:
          geometry: The boundary to filter to either as a GeoJSON geometry,
              or a FeatureCollection, from which a geometry will be extracted.

        Returns:
          The filter object.
        """
        return self.filter(filter.Filter.geometry(geometry))

    def filterDate(self, start, opt_end=None):
        """Shortcut to filter a collection with a date range.

        Items in the collection with a time_start property that doesn't
        fall between the start and end dates will be excluded.
        This is equivalent to self.filter(Filter().date(...)).

        Args:
          start: The start date as a Date object, a string representation of
              a date, or milliseconds since epoch.
          opt_end: The end date as a Date object, a string representation of
              a date, or milliseconds since epoch.

        Returns:
          The filter object.
        """
        return self.filter(filter.Filter.date(start, opt_end))

    def limit(self, maximum, opt_property=None, opt_ascending=None):
        """Limit a collection to the specified number of elements.

        This limits a collection to the specified number of elements, optionally
        sorting them by a specified property first.

        Args:
           maximum: The number to limit the collection to.
           opt_property: The property to sort by, if sorting.
           opt_ascending: Whether to sort in ascending or descending order.
               The default is true (ascending).

        Returns:
           The collection.
        """
        assert 0
        args = {'collection': self, 'limit': maximum}
        if opt_property is not None:
            args['key'] = opt_property
        if opt_ascending is not None:
            args['ascending'] = opt_ascending
        return self._cast(apifunction.ApiFunction.apply_('Collection.limit', args))

    def sort(self, prop, opt_ascending=None):
        """Sort a collection by the specified property.

        Args:
           prop: The property to sort by.
           opt_ascending: Whether to sort in ascending or descending
               order.  The default is true (ascending).

        Returns:
           The collection.
        """
        assert 0
        args = {'collection': self, 'key': prop}
        if opt_ascending is not None:
            args['ascending'] = opt_ascending
        return self._cast(apifunction.ApiFunction.apply_('Collection.limit', args))

    @staticmethod
    def name():
        return 'Collection'

    @staticmethod
    def elementType():
        """Returns the type of the collection's elements."""
        return Element

    def map(self, algorithm, dropNulls=False):
        """Maps an algorithm over a collection.

        Args:
            algorithm: The operation to map over the images or features of the
                collection, a Python function that receives an image or features and
                returns one. The function is called only once and the result is
                captured as a description, so it cannot perform imperative operations
                or rely on external state.
            opt_dropNulls: If true, the mapped algorithm is allowed to return nulls,
                and the elements for which it returns nulls will be dropped.

        Returns:
            The mapped collection.

        Raises:
            Exception: if algorithm is not a function.
        """

        collection = type(self)(None)
        for element in self.features():
            assert isinstance(element, Element)
            element_type = self.elementType()
            mapped = algorithm(element_type(element))
            if mapped is not None:
                collection._features.append(mapped)
            else:
                if not dropNulls:
                    raise ValueError()

        return collection

    def iterate(self, algorithm, first=None):
        """Iterates over a collection with an algorithm.

        Applies a user-supplied function to each element of a collection. The
        user-supplied function is given two arguments: the current element, and
        the value returned by the previous call to iterate() or the first argument,
        for the first iteration. The result is the value returned by the final
        call to the user-supplied function.

        Args:
          algorithm: The function to apply to each element. Must take two
              arguments - an element of the collection and the value from the
              previous iteration.
          first: The initial state.

        Returns:
          The result of the Collection.iterate() call.

        Raises:
          ee_exception.EEException: if algorithm is not a function.
        """
        assert 0
        element_type = self.elementType()
        with_cast = lambda e, prev: algorithm(element_type(e), prev)
        return apifunction.ApiFunction.call_('Collection.iterate', self, with_cast, first)


class FeatureCollection(Collection):
    '''Representation for an Earth Engine FeatureCollection.'''

    def _shallowCopy(self):
        collection = FeatureCollection(features=[])
        collection._id = self._id
        collection._features = self._features
        collection._properties = copy.deepcopy(self._properties)
        return collection

    def getInfo(self):
        info = dict()
        info['type'] = self.name()
        info['id'] = self.id()
        info['properties'] = self.properties()
        info['features'] = list()
        for feature in self._features:
            assert isinstance(feature, Feature)
            info['features'].append(feature.getInfo())
        return info

    @staticmethod
    def name():
        return 'FeatureCollection'

    def id(self):
        return self._id


class ImageCollection(Collection):
    '''Representation for an Earth Engine ImageCollection.'''

    def __init__(self, args):
        """ImageCollection constructor.

        Args:
           args: ImageCollections can be constructed from the following arguments:
               1) A string: assumed to be the name of a collection,
               2) An array of images, or anything that can be used to construct an
                  image.
               3) A single image.
               5) A computed object - reinterpreted as a collection.

        Raises:
          EEException: if passed something other than the above.
        """

        self._properties = dict()
        self._features = list()
        self._id = None

        # Wrap single images in an array.
        if isinstance(args, Image):
            args = [args]

        if ee.types.isString(args):
            # An ID.
            self._id = args

            if self._id.startswith(Environment.Force.idPrefix()):
                level, sensor = basename(self._id).split('_')
                if len(sensor) == 3:
                    pattern = '*{}*_BOA.tif'.format(basename(self._id))
                elif len(sensor) == 5:
                    pattern = '*{}_BOA.tif'.format(basename(self._id))
                else:
                    raise Exception('Invalid collection id.')

                print('WARNING: products are found by looking into the tile X0107_Y0102')
                for name in listdir(join(Environment.Force.root(), level.lower(), 'X0107_Y0102')):
                    if fnmatch.fnmatch(name, pattern):

                        if not name.startswith('1984'):
                            continue

                        id = '{}{}'.format(Environment.Force.idPrefix(), name[:-8])
                        self._features.append(Image.load(id=id))

        elif isinstance(args, (list, tuple)):
            # A list of images.
            for arg in args:
                assert isinstance(arg, Image)
                self._features.append(arg.copy())
        elif isinstance(args, ComputedObject):
            # A custom object to reinterpret as a ImageCollection.
            super(ImageCollection, self).__init__(args.func, args.args, args.varName)
        elif args is None:
            pass
        else:
            raise Exception('Unrecognized argument type to convert to a ImageCollection: {}'.format(args))

    def id(self):
        return self._id

    def properties(self):
        return self._properties

    @staticmethod
    def load(id, version=None):
        assert isinstance(id, str)
        return ImageCollection(id)

    @staticmethod
    def fromImages(images):
        assert ee.types.isArray(images)
        return ImageCollection(images)

    def getInfo(self):
        info = dict()
        info['type'] = self.name()
        info['id'] = self.id()
        info['features'] = list()
        for image in self._features:
            assert isinstance(image, Image)
            info['features'].append(image.getInfo())
        info['properties'] = self.properties()
        return info

    def select(self, selectors, opt_names=None, *args):
        """Select bands from each image in a collection.

        Args:
          selectors: An array of names, regexes or numeric indices specifying
              the bands to select.
          opt_names: An array of strings specifying the new names for the
              selected bands.  If supplied, the length must match the number
              of bands selected.
          *args: Selector elements as varargs.

        Returns:
          The image collection with selected bands.
        """
        return self.map(lambda image: image.select(selectors, opt_names, *args))

    @staticmethod
    def name():
        return 'ImageCollection'

    @staticmethod
    def elementType():
        return Image

    def reduce(collection, reducer, parallelScale=None):
        '''
        Applies a reducer across all of the images in a collection. If the reducer
        has a single input, it will be applied separately to each band of the
        collection; otherwise it must have the same number of inputs as the
        collection has bands. The reducer output names determine the names of the
        output bands: reducers with multiple inputs will use the output names
        directly, while reducers with a single input will prefix the output name
        with the input band name (e.g. '10_mean', '20_mean', etc.).

        Args:
          collection: The image collection to reduce.
          reducer: The reducer to apply to the given collection.
          parallelScale: A scaling factor used to limit memory
              use; using a larger parallelScale (e.g. 2 or 4) may
              enable computations that run out of memory with the
              default.
        '''
        assert isinstance(reducer, Reducer)

        if parallelScale is not None:
            raise NotImplementedError

        bandNames = collection.first().bandNames()

        reduction = Image()
        for bandName in bandNames:
            band = MapReduceOperator(collection=collection.select([bandName]), reducer=reducer)
            reduction.addBands(Image(band))

        return reduction


class Reducer(ComputedObject):

    @staticmethod
    def median(**kwargs):
        return ReducerMedian(**kwargs)

    @staticmethod
    def mean():
        return ReducerMean()

    def getInfo(self):
        name = type(self).__name__.replace('Reducer', '')
        name = name[0].lower() + name[1:]
        info = {'type': 'Reducer.{}'.format(name)}
        for k, v in self.__dict__.items():
            info[k] = v
        return info

    def aggregate(self, array):
        raise NotImplementedError()

    def name(self):
        return self.__class__.__name__.replace('Reducer', '').lower()


class ReducerMedian(Reducer):

    def __init__(self, maxBuckets=None, minBucketWidth=None, maxRaw=None):
        self.maxBuckets = maxBuckets
        self.minBucketWidth = minBucketWidth
        self.maxRaw = maxRaw

    def aggregate(self, array):
        return np.nanmedian(array, axis=0)


class ReducerMean(Reducer):

    def __init__(self):
        pass

    def aggregate(self, array):
        return np.nanmean(array, axis=0)


class Classifier(ComputedObject):

    @staticmethod
    def randomForest(**kwargs):
        return ClassifierRandomForest(**kwargs)

    def train(classifier, features, classProperty, inputProperties=None):

        assert isinstance(features, FeatureCollection)
        assert isinstance(classProperty, str)

        if inputProperties is None:
            if 'band_order' in features.properties():
                inputProperties = features.properties()['band_order']
            else:
                raise Exception('inputProperties not defined')

        from sklearn.ensemble import RandomForestClassifier

        X = np.zeros(shape=(len(features), len(inputProperties)))


        assert 0

    def getInfo(self):
        name = type(self).__name__.replace('Classifier', '')
        name = name[0].lower() + name[1:]
        info = {'type': 'Classifier.{}'.format(name)}
        for k, v in self.__dict__.items():
            info[k] = v
        return info


class ClassifierRandomForest(Classifier):

    def __init__(self, numberOfTrees):
        self.numberOfTrees = numberOfTrees

