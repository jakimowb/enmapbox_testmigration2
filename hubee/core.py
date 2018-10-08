from os.path import join, basename, dirname, isdir
from os import listdir
import pickle
import time
import copy
import numpy as np
from osgeo import gdal, gdal_array

import ee
import ee.ee_string
import ee.ee_list
import ee.batch
from ee.apifunction import ApiFunction as eeApiFunction
from ee.computedobject import ComputedObject as eeComputedObject
import ee.ee_types

from hubdc.core import Grid, Projection, openRasterDataset, VRTDriver
import hubee.signatures


with open('ApiFunction.pkl', 'rb') as f:
    vars = pickle.load(file=f)

eeApiFunction._api = vars['ee.apifunction.ApiFunction._api']
eeApiFunction._bound_signatures = vars['ee.apifunction.ApiFunction._bound_signatures']

ee._InitializeGeneratedClasses()


class Export(object):

    class image(object):

        @staticmethod
        def toDrive(image, description='myExportImageTask', folder=None,
                    fileNamePrefix=None, dimensions=None, region=None,
                    scale=None, crs=None, crsTransform=None,
                    maxPixels=None, shardSize=None, fileDimensions=None,
                    skipEmptyTiles=None, fileFormat=None, formatOptions=None,
                    noDataValues=None):

            config = ee.batch._CopyDictFilterNone(locals())

            if 'fileNamePrefix' not in config:
                config['fileNamePrefix'] = description

            ee.batch._ConvertToServerParams(config, 'image', Task.ExportDestination.DRIVE)
            ee.batch.ConvertFormatSpecificParams(config)

            return Task(task_type=Task.Type.EXPORT_IMAGE, ee_object=image, description=description, config=config)


ee.batch.Export = Export

class Task(object):

    class Type(object):
        EXPORT_IMAGE = 'EXPORT_IMAGE'
        EXPORT_MAP = 'EXPORT_TILES'
        EXPORT_TABLE = 'EXPORT_FEATURES'
        EXPORT_VIDEO = 'EXPORT_VIDEO'

    class State(object):
        UNSUBMITTED = 'UNSUBMITTED'
        READY = 'READY'
        RUNNING = 'RUNNING'
        COMPLETED = 'COMPLETED'
        FAILED = 'FAILED'
        CANCEL_REQUESTED = 'CANCEL_REQUESTED'
        CANCELLED = 'CANCELLED'

    class ExportDestination(object):
        DRIVE = 'DRIVE'
        GCS = 'GOOGLE_CLOUD_STORAGE'
        ASSET = 'ASSET'

    def __init__(self, task_type, ee_object, description, config):
        self.task_type = task_type
        self.creation_timestamp_ms = int(round(time.time()*1000))
        self.ee_object = ee_object
        self.description = description
        self.config = config
        self.id = ''.join(np.random.choice(list('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 24))
        self._status = dict()

    def start(self):

        self._status = {'id': self.id, 'state': ee.batch.Task.State.COMPLETED,
                        'creation_timestamp_ms': self.creation_timestamp_ms, 'description': self.description,
                        'task_type': self.task_type, 'start_timestamp_ms': int(round(time.time()*1000))}
        object = fetch(self.ee_object)
        if self.task_type == ee.batch.Task.Type.EXPORT_IMAGE:

            # check object type
            if not isinstance(object, Image):
                raise Exception("Invalid argument: 'image' must be of type Image.")

            # check data type
            isinstance(object, Image)
            dataType0 = object.band(0).dataType()
            for band in object.bands():
                if not band.dataType().equal(dataType0):
                    raise Exception('Exported bands must have compatible data types; found inconsistent types: {} and {}'.format(band.dataType().precision(), dataType0.precision()))



            shardSize = self.config.get('shardSize', 256)
            description = self.config.get('description')
            folder = self.config.get('folder', '')
            fileNamePrefix = self.config.get('fileNamePrefix', description) # object.id().split('/')[-1])
            fileFormat = 'GTiff'
            fileExtension = '.tif'

            filename = join(r'c:\outputs\Google Drive', folder, fileNamePrefix + fileExtension)

            from hubdc.core import RasterDriver, Grid, Extent, SpatialExtent, Projection, Resolution, Size
            driver = RasterDriver(name=fileFormat)
            xScale, xShearing, xTranslation, yShearing, yScale, yTranslation = object.crsTransform()
            crs = object.crs()
            yScale *= -1

            if 'dimensions' in self.config:
                xSize, ySize = Size.parse(self.config['dimensions'])
            else:
                try:
                    xSize, ySize = object.dimension()
                except:
                    pass

            if 'scale' in self.config:
                resolution = Resolution.parse(self.config['scale'])
                xScale = resolution.x()
                yScale = resolution.y()

            if 'crs' in self.config:
                crs = self.config['crs']

            projection = Projection.fromEPSG(epsg=crs.split(':')[1])

            if 'region' in self.config:
                bounds = np.array(self.config['region'])[0]
                extentWgs84 = SpatialExtent(xmin=np.min(bounds[:, 0]), xmax=np.max(bounds[:, 0]),
                                            ymin=np.min(bounds[:, 1]), ymax=np.max(bounds[:, 1]),
                                            projection=Projection.WGS84())
                extent = extentWgs84.reproject(targetProjection=projection)

            else:
                extent = Extent(xmin=xTranslation, ymin=yTranslation - ySize * yScale,
                                xmax=xTranslation + xSize * xScale, ymax=yTranslation),

            if projection.equal(other=Projection.WGS84()):
                print('TODO: UMRECHNUNG GRAD -> m')
                resolution = Resolution(0.01)
            else:
                resolution = Resolution(x=xScale, y=yScale),

            grid = Grid(extent=extent, resolution=resolution, projection=projection)


            gdalType = gdal_array.NumericTypeCodeToGDALTypeCode(dataType0.dtype())
            ds = driver.create(grid=grid, bands=len(object), gdalType=gdalType,
                               filename=filename)

            noDataValues = self.config.get('noDataValues', [None] * len(object))

            for i in range(len(object)):
                print('*', end='')
                band = object.band(i)
                array, maskArray = band.compute(grid=grid)

                # EE masks are "fuzzy" booleans between 0 (False) and 1 (True)
                # When writing to a GDAL file, the fuzzyness is lost, by replaced 0 with the no data value.

                noDataValue = noDataValues[i]
                if noDataValue is not None:
                    print(noDataValue)
                    array[np.logical_not(maskArray)] = noDataValue
                    #ds.band(i).setNoDataValue(value=noDataValues[i]) did not work (?!)
                ds.band(i).writeArray(array=array)
                ds.setNoDataValues(noDataValues)
            self._status['output_url'] = [filename]

        else:
            assert 0

    def active(self):
        return False

    def status(self):
        return self._status

def fetch(obj):
    if isinstance(obj, (ComputedObject, str, int, float)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return type(obj)(fetch(item) for item in obj)
    elif isinstance(obj, ee.Number):
        return obj._number
    elif isinstance(obj, ee.String):
        return obj._string
    elif isinstance(obj, ee.List):
        return [fetch(item) for item in obj._list]
    elif isinstance(obj, ee.CustomFunction):
        return fetch(obj._body)
    elif isinstance(obj, (ee.Image, ee.ImageCollection, ee.Reducer)):
        if isinstance(obj.func, ee.ApiFunction):
            pass
        #elif obj.func is None:
        #    return obj.varName
        else:
            assert 0
        funcname = obj.func.getSignature()['name']
        cls, method = funcname.split('.')
        print(cls)
        cls = eval(cls)

        if funcname == 'Collection.map':
            collection = fetch(obj.args['collection'])
            args = dict()
            for i, signature in enumerate(obj.args['baseAlgorithm']._body.func._signature['args']):
                name = signature['name']
                if i == 0: continue
                if name in obj.args['baseAlgorithm']._body.args:
                    args[name] = fetch(obj.args['baseAlgorithm']._body.args[name])

            baseAlgorithm = eval(obj.args['baseAlgorithm']._body.func._signature['name'])
            algorithm = lambda image: baseAlgorithm(image, **args)
            fetched = collection.map(algorithm=algorithm, dropNulls=obj.args.get('dropNulls'))
        else:
            args = dict()
            for k, arg in obj.args.items():
                args[k] = fetch(arg)

            if method in ['and', 'or']:
                method = method.title()

            try:
                fetched = fetch(getattr(cls, method)(**args))
            except AttributeError:
                print('missing or corrupted EE backend function\n\n' + obj.func.getSignature()['name'] + '\n' + str(obj.func))
                raise
        returnCls = eval(obj.func.getSignature()['returns'])
        if not isinstance(fetched, returnCls):
            raise Exception('Wrong result type ({}), expected: {}'.format(type(fetched), returnCls))

        return fetched

    else:
        raise Exception('Can not fetch object: {}.'.format(obj))


def getInfo(obj):
    """Fetch and return information about this object."""
    fetched = fetch(obj)
    info = fetched.getInfo()
    return info

eeComputedObject.getInfo = getInfo

class PixelType(object):
    '''A representation of an Earth Engine pixel type.'''

    EE_TYPENAMES =    ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'byte', 'short', 'int', 'long', 'float', 'double']

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
        raise NotImplementedError

    def copy(self):
        return copy.deepcopy(self)


class Element(ComputedObject):
  """Base class for ImageCollection and FeatureCollection."""

  @staticmethod
  def name():
    return 'Element'


class Band(object):
    '''Representation for an Earth Engine Band.'''

    def __init__(self):
        self._mask = None

    def mask(self):
        if self._mask is None:
            return Image(ConstantBand(np.float32(1.)))
        assert isinstance(self._mask, Image)
        return self._mask

    def copy(self):
        return copy.deepcopy(self)

    def updateMask(self, mask):
        assert isinstance(mask, Image)
        assert len(mask) == 1
        result = self.copy()
        result._mask = mask.min(self.mask())
        return result

    def compute(self, grid, returnMaskArray=True):
        assert isinstance(grid, Grid)
        raise NotImplementedError

    def dataType(self):
        raise NotImplementedError

    def dimensions(self):
        raise NotImplementedError

    def crs(self):
        raise NotImplementedError

    def crsTransform(self):
        raise NotImplementedError

    def id(self):
        raise NotImplementedError

    def properties(self):
        raise NotImplementedError

class WrittenBand(Band):

    def __init__(self, filename, index, noDataValue, id, data_type, dimensions, crs, crs_transform):
        Band.__init__(self)
        self._filename = filename
        self._index = index
        self._noDataValue = noDataValue
        self._id = id
        self._data_type = data_type
        self._dimensions = dimensions
        self._crs = crs
        self._crs_transform = crs_transform

    def id(self):
        return self._id

    def dataType(self):
        return self._data_type

    def dimensions(self):
        return self._dimensions

    def crs(self):
        return self._crs

    def crsTransform(self):
        return self._crs_transform

    def compute(self, grid, returnMaskArray=True):
        assert isinstance(grid, Grid)
        projection = Projection.fromEPSG(self.crs().split(':')[1])
        ds = openRasterDataset(filename=self._filename)
        if not grid.projection().equal(projection):
            dsWarped = ds.warp(grid=grid, filename=join('/vsimem/', self._filename)+'.vrt', driver=VRTDriver(),
                               srcNodata=self._noDataValue, dstNodata=self._noDataValue)
        else:
            assert 0 # check if transpose is needed!
            dsWarped = ds
        array = dsWarped.band(self._index).readAsArray()

        if returnMaskArray:
            maskArray = self.mask().band(0).compute(grid=grid, returnMaskArray=False)
            return array, maskArray
        else:
            return array


class ConstantBand(Band):
    '''Representation for a constant Earth Engine Band.'''

    def __init__(self, constant):
        Band.__init__(self)
        self._constant = constant

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

    def compute(self, grid, returnMaskArray=True):
        assert isinstance(grid, Grid)
        array = np.full(shape=grid.shape(), fill_value=self._constant)
        if returnMaskArray:
            maskArray = self.mask().band(0).compute(grid=grid, returnMaskArray=False)
            return array, maskArray
        else:
            return array


class Image(Element):
    '''Representation for an Earth Engine Image.'''

    def __init__(self, args=None):
        self._id = None
        self._bands = list()
        self._properties = None

        if ee.types.isNumber(args):
            # A constant image.
            self.bands().append(ConstantBand(constant=args))
        elif ee.types.isString(args):
            # An ID.
            self._id = str(args)

            for bandid in ['B{}'.format(i+1) for i in range(11)] + ['pixel_qa', 'radsat_qa', 'sr_aerosol']:
                if bandid in ['B8', 'B9']: continue
                filename = join(r'C:\Work\data\EE', self.id(), '{}.{}.tif'.format(basename(self.id()), bandid))

                if bandid == 'B1':
                    ds = gdal.Open(filename)
                    dimensions = ds.RasterXSize, ds.RasterYSize
                    crs = str(ds.GetProjection())
                    crs = 'EPSG:' + ''.join([c for c in crs.split('EPSG')[-1] if c in '0123456789'])

                    # convert from GDAL GeoTransform tuple
                    # [xTranslation, xScale, xShearing, yTranslation, yShearing, yScale] ...
                    gdalGeoTransform = ds.GetGeoTransform()
                    # ... to EE tuple
                    # [xScale, xShearing, xTranslation, yShearing, yScale, yTranslation]
                    crs_transform = tuple([gdalGeoTransform[i] for i in [1, 2, 0, 4, 5, 3]])
                    data_type = PixelType(precision=gdal_array.GDALTypeCodeToNumericTypeCode(ds.GetRasterBand(1).DataType)().dtype.name)

                if bandid in ['pixel_qa', 'radsat_qa', 'sr_aerosol']:
                    noDataValue = 1
                else:
                    noDataValue = -9999

                self.bands().append(WrittenBand(filename=filename, index=0, noDataValue=noDataValue, id=bandid,
                                                data_type=data_type, dimensions=dimensions,
                                                crs=crs, crs_transform=crs_transform))

            import json
            filename = join(r'C:\Work\data\EE', self.id(), 'info.json')
            with open(filename) as f:
                info = json.load(f)
            self._properties = info['properties']
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
                bandInfo['dimensions'] = band.dimensions()
                bandInfo['crs'] = band.crs()
                bandInfo['crs_transform'] = band.crsTransform()
            else:
                assert 0
            info['bands'].append(bandInfo)

        info['properties'] = self.properties()
        return info

    def updateMask(image, mask):
        assert isinstance(mask, Image)

        result = image.copy()
        result._bands = list()
        for i, band in enumerate(image.bands()):
            if len(mask) == 1:
                mask_ = mask.select([0])
            elif len(mask) == len(image):
                mask_ = mask.select([i])
            else:
                raise Exception('Image.updateMask: Incompatible number of bands in the mask image: {}. Expected {} or 1.'.format(len(mask), len(image)))
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
        assert isinstance(bandSelectors, (list, tuple))
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
                    raise Exception("Image.select: Band selector Pattern '{}' did not match any bands.".format(bandSelector))
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

    def And(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.logical_and)

    def Or(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.logical_or)

    def bitwiseAnd(image1, image2):
        return image1._binaryMapOperator(image2=image2, function=np.bitwise_and)

    def _binaryMapOperator(image1, image2, function):

        n1, n2 = len(image1), len(image2)
        n = max(n1, n2)
        if n > 1:
            if n1 != n2:
                if n1 != 1 and n2 != 1:
                    raise Exception('Image.{}: Images must contain the same number of bands or only 1 band. Got {} and {}.'.format(function.__name__, n1, n2))

        if n1 == n:
            bandNames1 = image1.bandNames()
        else:
            bandNames1 = image1.bandNames() * n # replicate bands

        if n2 == n:
            if n1==n:
                try: # match by band names
                    bandNames2 = image2.select(image1.bandNames()).bandNames()
                except: # match by natural order
                    bandNames2 = image2.bandNames()
            else:
                bandNames2 = image2.bandNames()
        else:
            bandNames2 = image2.bands() * n # replicate bands

        result = Image()
        for b1, b2 in zip(bandNames1, bandNames2):
            result.addBands(srcImg=Image(MapBinaryValueWiseOperator(band1=image1.select([b1]).band(0),
                                                                    band2=image2.select([b2]).band(0),
                                                                    function=function)))
        return result



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

    def compute(self, grid, returnMaskArray=True):
        assert isinstance(grid, Grid)

        if returnMaskArray:
            array1, maskArray1 = self.band1.compute(grid=grid)
            array2, maskArray2 = self.band2.compute(grid=grid)
            array = self.function(array1, array2)
            maskArray = np.minimum(maskArray1, maskArray2)
            return array, maskArray
        else:
            array1 = self.band1.compute(grid=grid, returnMaskArray=False)
            array2 = self.band2.compute(grid=grid, returnMaskArray=False)
            array = self.function(array1, array2)
            return array

    def dataType(self, ):
        a = np.array([1], dtype=self.band1.dataType().dtype())
        b = np.array([1], dtype=self.band2.dataType().dtype())
        dtype = self.function(a, b).dtype
        if dtype == np.bool8:
            dtype = np.uint8

        return PixelType.fromNumpyType(dtype)

    def dimensions(self):
        return self.band1.dimensions()

    def crs(self):
        return self.band1.crs()

    def crsTransform(self):
        return self.band1.crsTransform()

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

    def compute(self, grid, returnMaskArray=True):
        assert isinstance(grid, Grid)

        nanarrays = list()
        maskArray = np.zeros(shape=grid.shape(), dtype=np.float32)
        for image in self.collection.features():
            assert len(image) == 1
            band = image.band(0)
            array, maskArray_ = band.compute(grid=grid)
            array = np.float32(array)
            array[np.logical_not(maskArray_)] = np.nan
            nanarrays.append(array)
            np.maximum(maskArray, maskArray_, out=maskArray) # calculate final mask inplace

        array = self.reducer.aggregate(array=nanarrays)
        if returnMaskArray:
            return array, maskArray
        else:
            return array

    def dataType(self):
        return PixelType.fromNumpyType(np.float32)

    def dimensions(self):
        return None

    def crs(self):
        return 'EPSG:4326'

    def crsTransform(self):
        return (1, 0, 0, 0, 1, 0)

    def id(self):
        return None


class Collection(Element):
    '''Base class for ImageCollection and FeatureCollection.'''

    def __init__(self):
        self._features = list()
        pass

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
        #return self._cast(apifunction.ApiFunction.call_('Collection.filter', self, new_filter))

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
    pass

class ImageCollection(FeatureCollection):
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
            eeDir = r'C:\Work\data\EE'
            for name in listdir(join(eeDir, self.id())):
                if isdir(join(eeDir, self.id(), name)):
                    self._features.append(Image.load(id='{}/{}'.format(self.id(), name)))

            import json
            filename = join(r'C:\Work\data\EE', self.id(), 'properties.json')
            with open(filename) as f:
                self._properties = json.load(f)

        elif isinstance(args, (list, tuple)):
            # A list of images.
            for arg in args:
                assert isinstance(arg, Image)
                self._features.append(arg.copy())
        elif isinstance(args, ee.List):
            # A computed list of images.
            assert 0
            #super(ImageCollection, self).__init__(apifunction.ApiFunction.lookup('ImageCollection.fromImages'), {'images': args})
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

    def getInfo(self):
        name = type(self).__name__.replace('Reducer', '')
        name = name[0].lower() + name[1:]
        info = {'type': 'Reducer.{}'.format(name)}
        for k, v in self.__dict__.items():
            info[k] = v
        return info

    def aggregate(self, array):
        raise NotImplementedError()

class ReducerMedian(Reducer):

    def __init__(self, maxBuckets=None, minBucketWidth=None, maxRaw=None):
        self.maxBuckets = maxBuckets
        self.minBucketWidth = minBucketWidth
        self.maxRaw = maxRaw

    def aggregate(self, array):
        return np.nanmedian(array, axis=0)
