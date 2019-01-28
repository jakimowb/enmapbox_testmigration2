try:
    import matplotlib.pyplot as plt
except:
    import matplotlib
    matplotlib.use('QT5Agg')
    import matplotlib.pyplot as plt

from collections import OrderedDict
from os import makedirs, remove
from os.path import dirname, exists, join, basename, splitext, abspath, isabs
from shutil import copyfile, rmtree
import datetime
from random import randint
import tempfile
from osgeo import gdal, gdal_array, ogr, osr
import numpy as np
import hubdc.hubdcerrors as errors

gdal.UseExceptions()

class RasterDriver(object):
    '''Class for managing raster drivers'''

    def __init__(self, name, options=None):
        '''Create instance from GDAL driver name and (optional) a list of default creation options.'''

        self._name = name
        self._options = options
        if self.gdalDriver() is None:
            raise errors.InvalidGDALDriverError()

    def __repr__(self):
        return '{cls}(name={name})'.format(cls=self.__class__.__name__, name=repr(self.name()))

    @classmethod
    def fromFilename(cls, filename):

        ext = splitext(filename)[1][1:].lower()
        if ext in ['bsq', 'sli', 'esl']:
            driver = EnviDriver()
        elif ext == 'bil':
            driver = EnviDriver()
            driver.setOptions(options=[EnviDriver.Option.INTERLEAVE.BIL])
        elif ext == 'bip':
            driver = EnviDriver()
            driver.setOptions(options=[EnviDriver.Option.INTERLEAVE.BIP])
        elif ext in ['tif', 'tiff']:
            driver = GTiffDriver()
        elif ext == 'img':
            driver = ErdasDriver()
        elif ext == 'vrt':
            driver = VrtDriver()
        else:
            driver = EnviDriver()
        return driver

    def gdalDriver(self):
        '''Returns the GDAL driver object.'''

        return gdal.GetDriverByName(self._name)

    def name(self):
        '''Returns the driver name.'''

        return self._name

    def options(self):
        '''Returns default creation options.'''
        if self._options is None:
            options = list()
        else:
            options = self._options
        assert isinstance(options, list)
        return options

    def setOptions(self, options=None):
        '''Set the default options.'''
        assert isinstance(options, (list, type(None)))
        self._options = options

    def equal(self, other):
        '''Returns whether self is equal to the other driver.'''

        assert isinstance(other, RasterDriver), other
        return self.name() == other.name()

    def create(self, grid, bands=1, gdalType=gdal.GDT_Float32, filename='', options=None):
        '''
        Creates a new raster file with extent, resolution and projection given by ``grid``.

        :param grid:
        :type grid: hubdc.core.Grid
        :param bands: number of raster bands
        :type bands: int
        :param gdalType: one of the ``gdal.GDT_*`` data types, or use gdal_array.NumericTypeCodeToGDALTypeCode
        :type gdalType: int
        :param filename: output filename
        :type filename: str
        :param options: raster creation options
        :type options: list
        :return:
        :rtype: hubdc.core.RasterDataset
        '''

        assert isinstance(grid, Grid)
        if options is None:
            options = self.options()
        assert isinstance(options, list)

        filename = self.prepareCreation(filename)

        gdalDataset = self.gdalDriver().Create(filename, grid.size().x(), grid.size().y(), bands, gdalType, options)
        gdalDataset.SetProjection(grid.projection().wkt())
        gdalDataset.SetGeoTransform(grid.geoTransform())
        return RasterDataset(gdalDataset=gdalDataset)

    def prepareCreation(self, filename):
        '''Returns absolute filename and creates root folders if not existing.'''

        assert isinstance(filename, str)
        if not self.equal(MemDriver()) and not filename.startswith('/vsimem/'):
            if not isabs(filename):
                filename = abspath(filename)
            if not exists(dirname(filename)):
                makedirs(dirname(filename))

        return filename

class MemDriver(RasterDriver):
    '''MEM driver.'''

    def __init__(self):
        RasterDriver.__init__(self, name='MEM')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class VrtDriver(RasterDriver):
    '''VRT driver.'''

    def __init__(self):
        RasterDriver.__init__(self, name='VRT')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class EnviDriver(RasterDriver):
    '''ENVI driver.'''

    def __init__(self):
        RasterDriver.__init__(self, name='ENVI')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)

    class Option(object):

        class INTERLEAVE(object):
            BSQ = 'INTERLEAVE=BSQ'
            BIL = 'INTERLEAVE=BIL'
            BIP = 'INTERLEAVE=BIP'


        class SUFFIX(object):
            REPLACE = 'SUFFIX=REPLACE'
            ADD = 'SUFFIX=ADD'


class GTiffDriver(RasterDriver):
    '''GTiff driver.'''

    def __init__(self):
        RasterDriver.__init__(self, name='GTiff', options=[self.Option.INTERLEAVE.BAND])

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)

    class Option(object):

        class INTERLEAVE(object):
            BAND = 'INTERLEAVE=BAND'
            PIXEL = 'INTERLEAVE=PIXEL'

        class TILED(object):
            YES = 'TILED=YES'
            NO = 'TILED=NO'

        @staticmethod
        def BLOCKXSIZE(n=256):
            return 'BLOCKXSIZE={}'.format(n)

        @staticmethod
        def BLOCKYSIZE(n=256):
            return 'BLOCKYSIZE={}'.format(n)

        @staticmethod
        def NBITS(n):
            return 'NBITS={}'.format(n)

        class PREDICTOR(object):
            NONE = 'PREDICTOR=1'
            HorizontalDifferencing = 'PREDICTOR=2'
            FloatingPoint = 'PREDICTOR=3'

        class SPARSE_OK(object):
            TRUE = 'SPARSE_OK=TRUE'
            FALSE = 'SPARSE_OK=FALSE'

        @staticmethod
        def JPEG_QUALITY(n=75):
            assert n >= 1 and n <= 100
            return 'JPEG_QUALITY={}'.format(n)

        @staticmethod
        def ZLEVEL(n=6):
            assert n >= 1 and n <= 9
            return 'ZLEVEL={}'.format(n)

        @staticmethod
        def ZSTD_LEVEL(n=9):
            assert n >= 1 and n <= 22
            return 'ZSTD_LEVEL={}'.format(n)

        @staticmethod
        def MAX_Z_ERROR(threshold=0):
            assert threshold >= 0
            return 'MAX_Z_ERROR={}'.format(threshold)

        @staticmethod
        def WEBP_LEVEL(n=75):
            assert n >= 1 and n <= 100
            return 'WEBP_LEVEL={}'.format(n)

        class WEBP_LOSSLESS(object):
            TRUE = 'WEBP_LOSSLESS=TRUE'
            FALSE = 'WEBP_LOSSLESS=FALSE'

        class PHOTOMETRIC(object):
            MINISBLACK = 'PHOTOMETRIC=MINISBLACK'
            MINISWHITE = 'PHOTOMETRIC=MINISWHITE'
            RGB = 'PHOTOMETRIC=RGB'
            CMYK = 'PHOTOMETRIC=CMYK'
            YCBCR = 'PHOTOMETRIC=YCBCR'
            CIELAB = 'PHOTOMETRIC=CIELAB'
            ICCLAB = 'PHOTOMETRIC=ICCLAB'
            ITULAB = 'PHOTOMETRIC=ITULAB'

        class ALPHA(object):
            YES = 'ALPHA=YES'
            NON_PREMULTIPLIED = 'ALPHA=NON-PREMULTIPLIED'
            PREMULTIPLIED = 'ALPHA=PREMULTIPLIED'
            UNSPECIFIED = 'ALPHA=UNSPECIFIED'

        class PROFILE(object):
            GDALGeoTIFF = 'PROFILE=GDALGeoTIFF'
            GeoTIFF = 'PROFILE=GeoTIFF'
            BASELINE = 'PROFILE=BASELINE'

        class BIGTIFF(object):
            YES = 'BIGTIFF=YES'
            NO = 'BIGTIFF=NO'
            IF_NEEDED = 'BIGTIFF=IF_NEEDED'
            IF_SAFER = 'BIGTIFF=IF_SAFER'

        class PIXELTYPE(object):
            DEFAULT = 'PIXELTYPE=DEFAULT'
            SIGNEDBYTE = 'PIXELTYPE=SIGNEDBYTE'

        class COPY_SRC_OVERVIEWS(object):
            YES = 'COPY_SRC_OVERVIEWS=YES'
            NO = 'COPY_SRC_OVERVIEWS=NO'

        class GEOTIFF_KEYS_FLAVOR(object):
            STANDARD = 'GEOTIFF_KEYS_FLAVOR=STANDARD'
            ESRI_PE = 'GEOTIFF_KEYS_FLAVOR=ESRI_PE'

        @staticmethod
        def NUM_THREADS(n='ALL_CPUS'):
            return 'NUM_THREADS={}'.format(n)

        class COMPRESS(object):
            JPEG = 'COMPRESS=JPEG'
            LZW = 'COMPRESS=LZW'
            PACKBITS = 'COMPRESS=JPEG'
            DEFLATE = 'COMPRESS=PACKBITS'
            CCITTRLE = 'COMPRESS=CCITTRLE'
            CCITTFAX3 = 'COMPRESS=CCITTFAX3'
            CCITTFAX4 = 'COMPRESS=CCITTFAX4'
            LZMA = 'COMPRESS=LZMA'
            ZSTD = 'COMPRESS=ZSTD'
            LERC = 'COMPRESS=LERC'
            LERC_DEFLATE = 'COMPRESS=LERC_DEFLATE'
            LERC_ZSTD = 'COMPRESS=LERC_ZSTD'
            WEBP = 'COMPRESS=WEBP'
            NONE = 'COMPRESS=NONE'


class ErdasDriver(RasterDriver):
    '''Erdas Imagine driver.'''

    def __init__(self):
        RasterDriver.__init__(self, name='HFA')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class VectorDriver(object):
    '''Class for managing OGR Drivers'''

    def __init__(self, name):
        '''
        :param name: e.g. 'ESRI Shapefile' or 'GPKG'
        :type name: str
        '''

        self._name = name
        if self.ogrDriver() is None:
            raise errors.InvalidOGRDriverError()

    def __repr__(self):
        return '{cls}(name={name})'.format(cls=self.__class__.__name__, name=repr(self.name()))

    @classmethod
    def fromFilename(cls, filename):
        ext = splitext(filename)[1][1:].lower()
        if ext == 'shp':
            driver = ESRIShapefileDriver()
        elif ext == 'gpkg':
            driver = GeoPackageDriver()
        else:
            if filename == '':
                driver = MemoryDriver()
            else:
                raise errors.InvalidOGRDriverError()

        return driver

    def ogrDriver(self):
        '''Returns the OGR driver object.'''
        return ogr.GetDriverByName(self._name)

    def name(self):
        '''Returns the driver name.'''

        return self._name

    def equal(self, other):
        '''Returns whether self is equal to the other driver.'''

        assert isinstance(other, VectorDriver)
        return self.name() == other.name()

    def prepareCreation(self, filename):
        '''Deletes filename if it already exist and creates subfolders if needed.'''

        assert isinstance(filename, str)
        if (not self.equal(MemoryDriver()) and not filename.startswith('/vsimem/')):
            if not isabs(filename):
                filename = abspath(filename)
            if not exists(dirname(filename)):
                makedirs(dirname(filename))
            if exists(filename):
                result = self.ogrDriver().DeleteDataSource(filename)

        return filename


class ESRIShapefileDriver(VectorDriver):
    '''ESRI Shapefile driver.'''

    def __init__(self):
        VectorDriver.__init__(self, name='ESRI Shapefile')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class GeoPackageDriver(VectorDriver):
    '''ESRI Shapefile driver.'''

    def __init__(self):
        VectorDriver.__init__(self, name='GPKG')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class MemoryDriver(VectorDriver):
    '''Memory driver.'''

    def __init__(self):
        VectorDriver.__init__(self, name='Memory')

    def __repr__(self):
        return '{cls}()'.format(cls=self.__class__.__name__)


class Extent(object):
    '''Class for managing extents (i.e. bounding boxes).'''

    def __init__(self, xmin, xmax, ymin, ymax, projection):
        '''
        :param xmin:
        :type xmin: number
        :param xmax:
        :type xmax: number
        :param ymin:
        :type ymin: number
        :param ymax:
        :type ymax: number
        :param projection:
        :type projection: hubdc.core.Projection
        '''
        assert isinstance(projection, Projection)
        self._xmin = float(xmin)
        self._xmax = float(xmax)
        self._ymin = float(ymin)
        self._ymax = float(ymax)
        assert self._xmax > self._xmin
        assert self._ymax > self._ymin

        self._projection = projection

    def __repr__(self):
        return '{cls}(xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}, projection={projection})'.format(
            cls=self.__class__.__name__,
            xmin=repr(self.xmin()),
            xmax=repr(self.xmax()),
            ymin=repr(self.ymin()),
            ymax=repr(self.ymax()),
            projection=repr(self.projection()))

    @staticmethod
    def fromGeometry(geometry):
        '''Create an extent from the bounding box a :class:`~hubdc.model.Geometry`.'''

        assert isinstance(geometry, Geometry)
        xmin, xmax, ymin, ymax = geometry.ogrGeometry().GetEnvelope()
        return Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, projection=geometry.projection())

    def xmin(self):
        '''Returns the xmin.'''
        return self._xmin

    def xmax(self):
        '''Returns the xmax.'''
        return self._xmax

    def ymin(self):
        '''Returns the ymin.'''
        return self._ymin

    def ymax(self):
        '''Returns the ymax.'''
        return self._ymax

    def projection(self):
        '''Returns the :class:`~hubdc.model.Projection`.'''
        return self._projection

    def equal(self, other, tol=0.):
        '''Returns wether self is equal to other.'''
        assert isinstance(other, Extent)
        equal = abs(self.xmin() - other.xmin()) <= tol
        equal &= abs(self.xmax() - other.xmax()) <= tol
        equal &= abs(self.ymin() - other.ymin()) <= tol
        equal &= abs(self.ymax() - other.ymax()) <= tol
        equal &= self.projection().equal(other=other.projection())
        return equal

    def geometry(self):
        '''Returns self as a :class:`~hubdc.model.Geometry`.'''
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in zip([self.xmin(), self.xmax(), self.xmax(), self.xmin(), self.xmin()],
                        [self.ymax(), self.ymax(), self.ymin(), self.ymin(), self.ymax()]):
            ring.AddPoint(x, y)
        geometry = ogr.Geometry(ogr.wkbPolygon)
        geometry.AddGeometry(ring)
        return Geometry(wkt=geometry.ExportToWkt(), projection=self.projection())

    def upperLeft(self):
        '''Returns the upper left corner.'''
        return Point(x=self.xmin(), y=self.ymax(), projection=self.projection())

    def upperRight(self):
        '''Returns the upper right corner.'''
        return Point(x=self.xmax(), y=self.ymax(), projection=self.projection())

    def lowerRight(self):
        '''Returns the lower right corner.'''
        return Point(x=self.xmax(), y=self.ymin(), projection=self.projection())

    def lowerLeft(self):
        '''Returns the lower left corner.'''
        return Point(x=self.xmin(), y=self.ymin(), projection=self.projection())

    def intersects(self, other):
        '''Returns whether self and other intersects.'''
        assert isinstance(other, Extent)
        geometry = other.geometry().reproject(projection=self.projection())
        return self.geometry().intersects(geometry)

    def intersection(self, other):
        """Returns a new instance which is the intersection of self and other in the projection of self."""
        assert isinstance(other, Extent)
        return Extent.fromGeometry(geometry=self.geometry().intersection(other=other.geometry()))

    def union(self, other):
        '''Returns a new instance which is the union of self with other in the projection of self.'''
        assert isinstance(other, Extent)
        return Extent.fromGeometry(geometry=self.geometry().union(other=other.geometry()))

    def centroid(self):
        '''Returns the centroid.'''
        ogrCentroid =  self.geometry().ogrGeometry().Centroid()
        return Point(x=ogrCentroid.GetX(), y=ogrCentroid.GetY(), projection=self.projection())

    def reproject(self, projection):
        '''Reproject self into the given ``projection``.'''

        assert isinstance(projection, Projection)
        return Extent.fromGeometry(geometry=self.geometry().reproject(projection=projection))


class Resolution(object):
    '''Class for managing pixel resolutions.'''

    def __init__(self, x, y):
        '''
        :param x: resolution in x dimension
        :type x: float > 0
        :param y: resolution in y dimension
        :type y: float > 0
        '''

        self._x = float(x)
        self._y = float(y)
        assert self._x > 0
        assert self._y > 0

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    def __truediv__(self, f):

        if isinstance(f, (int, float, str)):
            fx = fy = float(f)
        elif len(f) == 2:
            fx, fy = map(float, f)
        else:
            raise errors.TypeError(f)

        return Resolution(x=self.x()/fx, y=self.y()/fy)

    def __mul__(self, f):

        if isinstance(f, (int, float, str)):
            fx = fy = float(f)
        elif len(f) == 2:
            fx, fy = map(float, f)
        else:
            raise errors.TypeError(f)

        return Resolution(x=self.x()*fx, y=self.y()*fy)

    @staticmethod
    def parse(obj):
        '''Create new instance from given Resolution object, number or (number, number) object.'''

        if isinstance(obj, Resolution):
            resolution = obj
        elif isinstance(obj, (int, float, str)):
            resolution = Resolution(x=float(obj), y=float(obj))
        elif isinstance(obj, (list, tuple)) and len(obj) == 2:
            resolution = Resolution(x=float(obj[0]), y=float(obj[1]))
        else:
            raise errors.ObjectParserError(obj, Resolution)
        return resolution

    def x(self):
        '''Returns x resolution.'''
        return self._x

    def y(self):
        '''Returns y resolution.'''
        return self._y

    def equal(self, other, tol=0.):
        '''Returns whether self is equal to other.'''
        assert isinstance(other, Resolution)
        equal = abs(self.x() - other.x()) <= tol
        equal &= abs(self.y() - other.y()) <= tol
        return equal


class Projection(object):
    '''Class for managing projections.'''

    def __init__(self, wkt):
        '''Create by given well known text string.'''
        self._wkt = str(wkt)

    def __repr__(self):
        wkt = self.wkt().replace(' ', ' ').replace('\n', ' ')
        return '{cls}(wkt={wkt})'.format(cls=self.__class__.__name__, wkt=wkt)

    def wkt(self):
        '''Returns the well known text string.'''
        return self._wkt

    @staticmethod
    def fromEpsg(epsg):
        '''Create by given ``epsg`` authority ID.'''
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(int(epsg))
        return Projection(wkt=projection)

    @staticmethod
    def wgs84WebMercator():
        '''Create WGS84 Web Mercator projection (epsg=3857), also see http://spatialreference.org/ref/sr-org/7483/'''
        return Projection.fromEpsg(epsg=3857)

    @staticmethod
    def wgs84():
        '''Create WGS84 projection (epsg=4326), also see http://spatialreference.org/ref/epsg/wgs-84/'''
        return Projection.fromEpsg(epsg=4326)

    @classmethod
    def utm(cls, zone, north=True):
        '''Create UTM projection of given ``zone``.'''
        assert zone >= 1 and zone <= 60
        if north:
            return cls.fromEpsg(epsg=32600 + zone)
        else:
            return cls.fromEpsg(epsg=32700 + zone)

    def osrSpatialReference(self):
        '''Returns osr.SpatialReference object.'''
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.wkt())
        return srs

    def equal(self, other):
        '''Returns whether self is equal to other.'''

        assert isinstance(other, Projection)
        return bool(self.osrSpatialReference().IsSame(other.osrSpatialReference()))


class Pixel(object):
    '''Class for managing image pixel location.'''

    def __init__(self, x, y):
        '''
        :param x:
        :type x: int
        :param y:
        :type y: int
        '''
        self._x = int(x)
        self._y = int(y)

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    @staticmethod
    def parse(obj):
        '''Create instance from given Pixel or (number, number) object.'''

        if isinstance(obj, Pixel):
            pixel = obj
        elif isinstance(obj, (list, tuple)) and len(obj) == 2:
            pixel = Pixel(x=obj[0], y=obj[1])
        else:
            raise errors.ObjectParserError(obj, Pixel)

        return pixel

    def x(self):
        '''Returns pixel x coordinate.'''
        return self._x

    def y(self):
        '''Returns pixel y coordinate.'''
        return self._y


class Column(object):
    '''Class for managing image column location.'''

    def __init__(self, x, z):
        '''
        :param x:
        :type x: int
        :param z:
        :type z: int
        '''
        self._x = int(x)
        self._z = int(z)

    def __repr__(self):
        return '{cls}(x={x}, z={z})'.format(cls=self.__class__.__name__, x=repr(self.x()), z=repr(self.z()))

    def x(self):
        '''Returns column x coordinate.'''
        return self._x

    def z(self):
        '''Returns column z coordinate.'''
        return self._z


class Row(object):
    '''Class for managing image row location.'''

    def __init__(self, y, z):
        '''
        :param y:
        :type y: int
        :param z:
        :type z: int
        '''
        self._y = int(y)
        self._z = int(z)

    def __repr__(self):
        return '{cls}(y={y}, z={z})'.format(cls=self.__class__.__name__, y=repr(self.y()), z=repr(self.z()))

    def y(self):
        '''Returns row y coordinate.'''
        return self._y

    def z(self):
        '''Returns row z coordinate.'''
        return self._z

class Geometry(object):
    '''Class for managing geometries.'''

    def __init__(self, wkt, projection):
        '''Create by given well known text string and :class:`~hubdc.model.Projection`.'''

        assert isinstance(wkt, str)
        assert isinstance(projection, Projection)
        self._wkt = wkt
        self._projection = projection

    def __repr__(self):
        return '{cls}(wkt={wkt}, projection={projection})'.format(cls=self.__class__.__name__, wkt=repr(self.wkt()),
                                                                  projection=repr(self.projection()))

    def wkt(self):
        '''Returns well known text string.'''
        return self._wkt

    def projection(self):
        '''Returns the :class:`~hubdc.model.Projection`.'''
        return self._projection

    def ogrGeometry(self):
        '''Returns ogr.Geometry object.'''
        ogrGeometry = ogr.CreateGeometryFromWkt(self._wkt)
        return ogrGeometry

    def intersects(self, other):
        '''Returns whether self and other intersect.'''
        assert isinstance(other, Geometry)
        geometry = other.reproject(projection=self.projection())
        return self.ogrGeometry().Intersects(geometry.ogrGeometry())

    def intersection(self, other):
        '''Returns the intersection of self and other.'''
        assert isinstance(other, Geometry)
        geometry = other.reproject(projection=self.projection())
        ogrGeometry = self.ogrGeometry().Intersection(geometry.ogrGeometry())
        if ogrGeometry is None:
            raise errors.GeometryIntersectionError()
        return Geometry(wkt=ogrGeometry.ExportToWkt(), projection=self.projection())

    def union(self, other):
        '''Returns the union of self and other.'''
        assert isinstance(other, Geometry)
        geometry = other.reproject(projection=self.projection())
        ogrGeometry = self.ogrGeometry().Union(geometry.ogrGeometry())
        assert ogrGeometry is not None
        return Geometry(wkt=ogrGeometry.ExportToWkt(), projection=self.projection())

    def within(self, other):
        '''Returns whether self is within other.'''
        assert isinstance(other, Geometry)
        geometry = other.reproject(projection=self.projection())
        return self.ogrGeometry().Within(geometry.ogrGeometry())

    def reproject(self, projection):
        '''Reproject self into given ``projection``.'''

        transformation = osr.CoordinateTransformation(self.projection().osrSpatialReference(),
                                                      projection.osrSpatialReference())
        ogrGeometry = self.ogrGeometry()
        ogrGeometry.Transform(transformation)
        return Geometry(wkt=ogrGeometry.ExportToWkt(), projection=projection)


class Point(Geometry):
    '''Class for managing map locations.'''

    def __init__(self, x, y, projection):
        '''Create point geometry by ``x`` and ``y`` coordinates and ``projection``.'''

        assert isinstance(projection, Projection)
        self._x = float(x)
        self._y = float(y)
        self._projection = projection
        Geometry.__init__(self, wkt='POINT({} {})'.format(float(x), float(y)), projection=projection)

    def __repr__(self):
        return '{cls}(x={x}, y={y}, projection={projection})'.format(cls=self.__class__.__name__,
                                                                     x=repr(self.x()),
                                                                     y=repr(self.y()),
                                                                     projection=repr(self.projection()))

    def x(self):
        '''Returns map x coordinate.'''
        return self._x

    def y(self):
        '''Returns map y coordinate.'''
        return self._y

    def projection(self):
        '''Returns the :class:`~hubdc.model.Projection`.'''
        return self._projection

    def reproject(self, projection):
        '''Reproject self into given ``projection``.'''
        geometry = Geometry.reproject(self, projection=projection)
        ogrGeometry = geometry.ogrGeometry()
        return Point(x=ogrGeometry.GetX(), y=ogrGeometry.GetY(), projection=projection)

class RasterSize(object):
    '''Class for managing image sizes.'''

    def __init__(self, x, y):
        '''
        :param x:
        :type x: number
        :param y:
        :type y: number
        '''

        self._x = int(x)
        self._y = int(y)
        if self._x <= 0:
            raise errors.InvalidRasterSize('raster x size must be greater then zero, got {} '.format(self._x))
        if self._y <= 0:
            raise errors.InvalidRasterSize('raster y size must be greater then zero, got {} '.format(self._y))

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    @staticmethod
    def parse(obj):
        '''Create instance by parsing the given RasterSize object, a (number, number) tuple or list '''

        if isinstance(obj, RasterSize):
            size = obj
        elif isinstance(obj, (tuple, list)) and len(obj) == 2:
            size = RasterSize(*obj)
        else:
            raise errors.ObjectParserError(obj=obj, type=RasterSize)
        return size

    def x(self):
        '''Returns the x size.'''
        return self._x

    def y(self):
        '''Returns the y size.'''
        return self._y


class Grid(object):
    '''Class for managing raster grids in terms of extent, resolution and projection.'''

    def __init__(self, extent, resolution):
        '''
        :param extent:
        :type extent: hubdc.core.Extent
        :param resolution:
        :type resolution: hubdc.core.Resolution
        '''

        assert isinstance(extent, Extent)
        resolution = Resolution.parse(resolution)
        self._resolution = resolution

        # round extent to fit into a multiple of the given resolution
        xsize = int(round(float(extent.xmax() - extent.xmin()) / resolution.x()))
        ysize = int(round(float(extent.ymax() - extent.ymin()) / resolution.y()))
        self._extent = Extent(xmin=extent.xmin(),
                              xmax=extent.xmin() + xsize * resolution.x(),
                              ymin=extent.ymin(),
                              ymax=extent.ymin() + ysize * resolution.y(),
                              projection=extent.projection())

    def __repr__(self):
        return '{cls}(extent={extent}, resolution={resolution}, projection={projection}'.format(
            cls=self.__class__.__name__,
            extent=repr(self.extent()),
            resolution=repr(self.resolution()),
            projection=repr(self.projection()))

    def extent(self):
        '''Returns the :class:`~hubdc.model.Extent`.'''
        return self._extent

    def resolution(self):
        '''Returns the :class:`~hubdc.model.Resolution`.'''
        return self._resolution

    def projection(self):
        '''Returns the :class:`~hubdc.model.Projection`.'''
        return self.extent().projection()

    def size(self):
        '''Returns the :class:`~hubdc.model.Size`.'''
        return RasterSize(x=round((self.extent().xmax() - self.extent().xmin()) / self.resolution().x()),
                          y=round((self.extent().ymax() - self.extent().ymin()) / self.resolution().y()))

    def shape(self):
        '''Returns size as ``(ysize, xsize)`` tuple.'''
        size = self.size()
        return size.y(), size.x()

    def atResolution(self, resolution):
        '''Return grid with same extent and projection, but new resolution.'''
        return Grid(extent=self.extent(), resolution=resolution)

    def xMapCoordinates(self):
        '''Returns the list of map coordinates in x dimension.'''
        return [self.extent().xmin() + (x + 0.5) * self.resolution().x() for x in range(self.size().x())]

    def yMapCoordinates(self):
        '''Returns the list of map coordinates in y dimension.'''
        return [self.extent().ymax() - (y + 0.5) * self.resolution().y() for y in range(self.size().y())]

    def xMapCoordinatesArray(self):
        '''Returns the 2d array of map x coordinates.'''
        return np.asarray(self.xMapCoordinates()).reshape(1, -1) * np.ones(shape=self.shape())

    def yMapCoordinatesArray(self):
        '''Returns the 2d array of map y coordinates.'''
        return np.asarray(self.yMapCoordinates()).reshape(-1, 1) * np.ones(shape=self.shape())

    def xPixelCoordinates(self, offset=0):
        '''Returns the list of pixel coordinates in x dimension with optional ``offset``.'''
        return [x + offset for x in range(self.size().x())]

    def yPixelCoordinates(self, offset=0):
        '''Returns the list of pixel coordinates in y dimension with optional ``offset``.'''
        return [y + offset for y in range(self.size().y())]

    def xPixelCoordinatesArray(self, offset=0):
        '''Returns the 2d array of pixel x coordinates with optional ``offset``.'''
        return np.int32(np.asarray(self.xPixelCoordinates(offset=offset)).reshape(1, -1) * np.ones(shape=self.shape()))

    def yPixelCoordinatesArray(self, offset=0):
        '''Returns the 2d array of pixel y coordinates with optional ``offset``.'''
        return np.int32(np.asarray(self.yPixelCoordinates(offset=offset)).reshape(-1, 1) * np.ones(shape=self.shape()))

    def geoTransform(self):
        '''Returns a GDAL  georeferencing transform tuple ``(xmin, xres, 0, ymax, 0, -yres)`` from bounds and resolution,
         without any rotation or shearing.'''

        geotransform = (self.extent().xmin(), self.resolution().x(), 0.0, self.extent().ymax(), 0.0,
                        -self.resolution().y())
        return geotransform

    def equal(self, other, tol=0.):
        '''Returns whether self is equal to other.'''
        assert isinstance(other, Grid)
        equal = self.projection().equal(other=other.projection())
        equal &= self.extent().equal(other=other.extent(), tol=tol)
        equal &= self.resolution().equal(other=other.resolution(), tol=tol)
        return equal

    def reproject_OLD(self, other):
        '''
        Returns a new instance with:
        a) extent reprojected into the projection of other,
        b) resolution of other, and
        c) anchored to other.
        '''
        assert isinstance(other, Grid)
        extent = self.extent().reproject(projection=other.projection())
        grid = Grid(extent=extent, resolution=other.resolution())
        grid = grid.anchor(point=other.extent().upperLeft())
        return grid

    def clip_OLD(self, extent):
        '''Return self clipped by given extent.'''
        assert isinstance(extent, Extent)
        extent = self.extent().intersection(other=extent)
        return Grid(extent=extent, resolution=self.resolution()).anchor(point=self.extent().upperLeft())

    def pixelBuffer(self, buffer, left=True, right=True, up=True, down=True):
        '''Returns a new instance with a pixel buffer applied in different directions.

        :param buffer: number of pixels to be buffered (can also be negativ)
        :type buffer: int
        :param left: whether to buffer to the left/west
        :type left: bool
        :param right: whether to buffer to the right/east
        :type right: bool
        :param up: whether to buffer upwards/north
        :type up: bool
        :param down: whether to buffer downwards/south
        :type down: bool
        :return:
        :rtype: hubdc.core.Grid
        '''
        assert isinstance(buffer, int)
        extent = Extent(xmin=self.extent().xmin() - buffer * (self.resolution().x() if left else 0),
                        xmax=self.extent().xmax() + buffer * (self.resolution().x() if right else 0),
                        ymin=self.extent().ymin() - buffer * (self.resolution().y() if down else 0),
                        ymax=self.extent().ymax() + buffer * (self.resolution().y() if up else 0),
                        projection = self.projection())
        return Grid(extent=extent, resolution=self.resolution())

    def anchor(self, point):
        '''Returns a new instance that is anchored to the given ``point``.
        Anchoring will result in a subpixel shift.
        See the source code for implementation details.'''
        assert isinstance(point, Point)
        point = point.reproject(projection=self.projection())
        xoff = (self.extent().xmin() - point.x()) % self.resolution().x()
        yoff = (self.extent().ymin() - point.y()) % self.resolution().y()

        # round snapping offset
        if xoff > self.resolution().x() / 2.:
            xoff -= self.resolution().x()
        if yoff > self.resolution().y() / 2.:
            yoff -= self.resolution().y()

        # return new instance
        extent = Extent(xmin=self.extent().xmin() - xoff,
                        ymin=self.extent().ymin() - yoff,
                        xmax=self.extent().xmax() - xoff,
                        ymax=self.extent().ymax() - yoff,
                        projection=self.projection())
        return Grid(extent=extent, resolution=self.resolution())

    def subset(self, offset, size, trim=False):
        '''
        Returns a new instance that is a subset given by an ``offset`` location and a raster ``size``.
        Optionally set ``trim=True`` to restrain the grid extent to the extent of self.
        '''
        offset = Pixel.parse(offset)
        size = RasterSize.parse(size)
        assert isinstance(offset, Pixel)
        assert isinstance(size, RasterSize)
        if trim:
            offset = Pixel(x=max(offset.x(), 0), y=max(offset.y(), 0))
            size = RasterSize(x=min(size.x(), self.size().x() - offset.x()),
                              y=min(size.y(), self.size().y() - offset.y()))

        xmin = self.extent().xmin() + offset.x() * self.resolution().x()
        xmax = xmin + size.x() * self.resolution().x()
        ymax = self.extent().ymax() - offset.y() * self.resolution().y()
        ymin = ymax - size.y() * self.resolution().y()

        return Grid(extent=Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, projection=self.projection()),
                    resolution=self.resolution())

    def subgrids(self, size):
        '''
        Returns the decomposition of self into subgrids of given ``size``.
        Subgrids at the border are trimmed to the extent of self.
        '''
        assert isinstance(size, RasterSize)
        size = RasterSize(x=min(size.x(), self.size().x()), y=min(size.y(), self.size().y()))
        result = list()
        offset = Pixel(x=0, y=0)
        i = iy = 0
        while offset.y() < self.size().y():
            offset = Pixel(x=0, y=offset.y())
            ix = 0
            while offset.x() < self.size().x():
                subgrid = self.subset(offset=offset, size=size, trim=True)
                result.append((subgrid, i, iy, ix))
                offset = Pixel(x=offset.x() + size.x(), y=offset.y())
                ix += 1
                i += 1
            offset = Pixel(x=offset.x(), y=offset.y() + size.y())
            iy += 1
        return result

class RasterDataset(object):
    '''Class for managing raster datasets files.'''

    def __init__(self, gdalDataset):
        '''Create an instance by a given gdal.Dataset.'''
        assert isinstance(gdalDataset, gdal.Dataset), str(gdalDataset)
        self._gdalDataset = gdalDataset

        projection = Projection(wkt=self._gdalDataset.GetProjection())
        geotransform = self._gdalDataset.GetGeoTransform()
        resolution = Resolution(x=geotransform[1], y=abs(geotransform[5]))
        extent = Extent(xmin=geotransform[0],
                        xmax=geotransform[0] + self._gdalDataset.RasterXSize * resolution.x(),
                        ymin=geotransform[3] - self._gdalDataset.RasterYSize * resolution.y(),
                        ymax=geotransform[3],
                        projection=projection)

        self._grid = Grid(extent=extent, resolution=resolution)

    def __repr__(self):
        return '{cls}(gdalDataset={gdalDataset})'.format(cls=self.__class__.__name__,
                                                         gdalDataset=repr(self.gdalDataset()))

    @staticmethod
    def fromArray(array, grid=None, filename='', driver=MemDriver(), options=None):
        '''
        Creates a new raster file with content, data type and number of bands given by ``array``
        and with extent, resolution and projection given by ``grid``.

        :param array:
        :type array: numpy.ndarray
        :param grid:
        :type grid: hubdc.core.Grid
        :param filename: output filename
        :type filename: str
        :param driver:
        :type driver: hubdc.core.RasterDriver
        :param options: raster creation options
        :type options: list
        :return:
        :rtype: hubdc.core.RasterDataset
        '''

        if isinstance(array, list):
            array = np.array(array)

        if grid is None:
            grid = PseudoGrid.fromArray(array)

        if isinstance(array, np.ndarray):
            if array.ndim == 2:
                array = array[None]
            assert array.ndim == 3
        elif isinstance(array, list):
            assert all([subarray.ndim == 2 for subarray in array])
        else:
            raise TypeError()

        bands = len(array)
        dtype = array[0].dtype
        if dtype == np.bool:
            dtype = np.uint8

        gdalType = gdal_array.NumericTypeCodeToGDALTypeCode(dtype)
        rasterDataset = driver.create(grid=grid, bands=bands, gdalType=gdalType, filename=filename, options=options)
        rasterDataset.writeArray(array=array, grid=grid)
        rasterDataset.flushCache()
        return rasterDataset

    def gdalDataset(self):
        '''Return the gdal.Dataset.'''
        return self._gdalDataset

    def filenames(self):
        '''Return gdal dataset file list`` '''
        return self._gdalDataset.GetFileList()

    def filename(self):
        '''Return filename.'''
        filenames = self.filenames()
        if filenames is None:
            filename = None
        else:
            filename = filenames[0]
        return filename

    def grid(self):
        '''Return the :class:`~hubdc.model.Grid`.'''
        return self._grid

    def projection(self):
        '''Return the :class:`~hubdc.model.Projection`.'''
        return self._grid.projection()

    def extent(self):
        '''Return the :class:`~hubdc.model.Extent`.'''
        return self._grid.extent()

    def band(self, index):
        '''Return the :class:`~hubdc.model.RasterBandDataset` given by ``index``.'''
        return RasterBandDataset(raster=self, index=index)

    def bands(self):
        '''Returns an iterator over each :class:`~hubdc.model.RasterBandDataset`.'''
        for i in range(self.zsize()):
            yield self.band(i)

    def driver(self):
        '''Return the :class:`~hubdc.model.Driver`.'''
        return RasterDriver(name=self._gdalDataset.GetDriver().ShortName)

    def readAsArray(self, grid=None, resampleAlg=gdal.GRA_NearestNeighbour):
        '''
        Returns raster data as 3d array.

        :param grid: if provided, only data inside the grid extent is returned
        :type grid: hubdc.core.Grid
        :param resampleAlg: one of the GDAL resampling algorithms (i.e. gdal.GRA_*)
        :type resampleAlg: int
        :return:
        :rtype: numpy.ndarray
        '''

        if grid is None:
            array = self._gdalDataset.ReadAsArray()
        else:
            assert isinstance(grid, Grid)
            xoff = int(round((grid.extent().xmin() - self.grid().extent().xmin()) / self.grid().resolution().x(), 0))
            yoff = int(round((self.grid().extent().ymax() - grid.extent().ymax()) / self.grid().resolution().y(), 0))
            xsize = int(round((grid.extent().xmax() - grid.extent().xmin()) / self.grid().resolution().x(), 0))
            ysize = int(round((grid.extent().ymax() - grid.extent().ymin()) / self.grid().resolution().y(), 0))

            buf_ysize, buf_xsize = grid.shape()
            array = self._gdalDataset.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize,
                                                  buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                                  resample_alg=resampleAlg)

        if array.ndim == 2:
            array = array[None]

        return array

    def writeArray(self, array, grid=None):
        '''
        Writes raster data.

        :param array:
        :type array: 3d array | list of 2d arrays
        :param grid: if provided, data is written to the location given by the grid extent
        :type grid: hubdc.core.Grid
        '''

        assert len(array) == self.zsize()
        for band, bandArray in zip(self.bands(), array):
            band.writeArray(bandArray, grid=grid)

    def flushCache(self):
        '''Flush the cache.'''
        self._gdalDataset.FlushCache()
        return self

    def close(self):
        '''Close the gdal.Dataset.'''
        self._gdalDataset = None

    def setNoDataValues(self, values):
        '''Set band no data values.'''
        if values is not None:
            for i, band in enumerate(self.bands()):
                band.setNoDataValue(values[i])
        self.flushCache()

    def noDataValues(self, default=None, required=False):
        '''Returns band no data values. For bands without a no data value, ``default`` is returned,
        or if ``required`` is True, an error is raised'''
        return [band.noDataValue(default=default, required=required) for band in self.bands()]

    def setNoDataValue(self, value):
        '''Set a single no data value to all bands.'''
        if value is not None:
            self.setNoDataValues(values=[value] * self.zsize())
            if self.driver().equal(other=RasterDriver(name='ENVI')):
                self.setMetadataItem(key='data ignore value', value=value, domain='ENVI')
            self.flushCache()
        return self

    def noDataValue(self, default=None, required=False):
        '''
        Returns no data value.
        Returns ``default`` if all band no data values are undefined, or raises
        Raises an exception if not all bands share the same no data value.

        If all bands are without a no data value, ``default`` is returned.
        '''
        noDataValues = self.noDataValues()
        if len(set(noDataValues)) != 1:
            raise errors.HubDcError('there are multiple no data values, use noDataValues() instead')
        noDataValue = noDataValues[0]
        if noDataValue is None:
            noDataValue = default
        if required and noDataValue is None:
            raise errors.MissingNoDataValueError(filename=self.filename(), index='all')

        return noDataValue

    def setDescription(self, value):
        '''Set the description.'''
        self._gdalDataset.SetDescription(value)
        self.flushCache()

    def description(self):
        '''Returns the description.'''
        return self._gdalDataset.GetDescription()

    def metadataDomainList(self):
        '''Returns the list of metadata domain names.'''
        domains = self._gdalDataset.GetMetadataDomainList()
        return domains if domains is not None else []

    def metadataItem(self, key, domain='', dtype=str, required=False, default=None):
        '''Returns the value (casted to a specific ``dtype``) of a metadata item.'''
        key = key.replace(' ', '_')
        gdalString = self._gdalDataset.GetMetadataItem(key, domain)
        if gdalString is None:
            if required:
                raise errors.MissingMetadataItemError(key=key, domain=domain)
            return default
        return MetadataFormatter.stringToValue(gdalString, dtype=dtype)

    def metadataDomain(self, domain=''):
        '''Returns the metadata dictionary for the given ``domain``.'''
        metadataDomain = dict()
        for key in self._gdalDataset.GetMetadata(domain):
            key = key.replace('_', ' ')
            metadataDomain[key] = self.metadataItem(key=key, domain=domain)
        return metadataDomain

    def metadataDict(self):
        '''Returns the metadata dictionary for all domains.'''
        metadataDict = dict()
        for domain in self.metadataDomainList():
            metadataDict[domain] = self.metadataDomain(domain=domain)
        return metadataDict

    def setMetadataItem(self, key, value, domain):
        '''Set a metadata item. ``value`` can be a string, a number or a list of strings or numbers.'''
        if value is None:
            return
        key = key.replace(' ', '_').strip()
        if domain.upper() == 'ENVI' and key.lower() == 'file_compression':
            return
        gdalString = MetadataFormatter.valueToString(value)
        self._gdalDataset.SetMetadataItem(key, gdalString, domain)
        self.flushCache()

    def setMetadataDomain(self, metadataDomain, domain):
        '''Set the metadata domain'''
        assert isinstance(metadataDomain, dict)
        for key, value in metadataDomain.items():
            self.setMetadataItem(key=key, value=value, domain=domain)
        self.flushCache()

    def setMetadataDict(self, metadataDict):
        '''Set the metadata dictionary'''
        assert isinstance(metadataDict, dict)
        for domain, metadataDomain in metadataDict.items():
            self.setMetadataDomain(metadataDomain=metadataDomain, domain=domain)
        self.flushCache()

    def copyMetadata(self, other):
        '''Copy raster and raster band metadata from other to self.'''

        assert isinstance(other, RasterDataset)

        for domain in other.metadataDomainList():
            self.gdalDataset().SetMetadata(other.gdalDataset().GetMetadata(domain), domain)

        for band, otherBand in zip(self.bands(), other.bands()):
            for domain in otherBand.metadataDomainList():
                band.gdalBand().SetMetadata(otherBand.gdalBand().GetMetadata(domain), domain)
        self.flushCache()

    def setAcquisitionTime(self, acquisitionTime):
        '''Set the acquisition time. Store it as 'acquisition time' metadata item inside the 'ENVI' domain.

        :param acquisitionTime:
        :type acquisitionTime:  datetime.datetime
        '''

        assert isinstance(acquisitionTime, datetime.datetime)
        self.setMetadataItem(key='acquisition time', value=str(acquisitionTime), domain='ENVI')
        self.flushCache()

    def acquisitionTime(self):
        '''Returns the acquisition time. Restore it from 'acquisition time' metadata item inside the 'ENVI' domain.

        :return:
        :rtype: datetime.datetime
        '''

        value = self.metadataItem(key='acquisition time', domain='ENVI')
        year, month, day = value[0:10].split('-')
        hour, minute, second = value[11:19].split(':')
        acquisitionTime = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour),
                                            minute=int(minute), second=int(second))
        return acquisitionTime

    def warp(self, grid=None, filename='', driver=MemDriver(), options=None, **kwargs):
        '''Returns a new instance of self warped into the given ``grid`` (default is self.grid()).

        :param grid:
        :type grid: hubdc.core.Grid
        :param filename: output filename
        :type filename: str
        :param driver:
        :type driver: hubdc.core.RasterDriver
        :param options: creation options
        :type options: list
        :param kwargs: passed to gdal.WarpOptions
        :type kwargs:
        :return:
        :rtype: hubdc.core.RasterDataset
        '''

        if grid is None:
            grid = self.grid()
        assert isinstance(grid, Grid)
        assert isinstance(driver, RasterDriver)
        if options is None:
            options = driver.options()
        assert isinstance(options, list)

        filename = driver.prepareCreation(filename=filename)

        outputBounds = (grid.extent().xmin(), grid.extent().ymin(), grid.extent().xmax(), grid.extent().ymax())
        warpOptions = gdal.WarpOptions(format=driver.name(), outputBounds=outputBounds, xRes=grid.resolution().x(),
                                       yRes=grid.resolution().y(), dstSRS=grid.projection().wkt(),
                                       creationOptions=options, **kwargs)
        gdalDataset = gdal.Warp(destNameOrDestDS=filename, srcDSOrSrcDSTab=self._gdalDataset, options=warpOptions)

        return RasterDataset(gdalDataset=gdalDataset)

    def translate(self, grid=None, filename='', driver=MemDriver(), options=None, **kwargs):
        '''Returns a new instance of self translated into the given ``grid`` (default is self.grid()).

        :param grid:
        :type grid: hubdc.core.Grid
        :param filename:
        :type filename: str
        :param driver:
        :type driver: hubdc.core.RasterDriver
        :param options: raster creation options
        :type options: list
        :param kwargs: passed to gdal.TranslateOptions
        :type kwargs:
        :return:
        :rtype: hubdc.core.RasterDataset
        '''

        if grid is None:
            grid = self.grid()

        assert isinstance(grid, Grid)
        assert self.grid().projection().equal(other=grid.projection())
        assert isinstance(driver, RasterDriver)
        if options is None:
            options = driver.options()
        assert isinstance(options, list)

        filename = driver.prepareCreation(filename)

        ul = grid.extent().upperLeft()
        lr = grid.extent().lowerRight()
        xRes, yRes = grid.resolution().x(), grid.resolution().y()

        # Note that given a projWin, it is not garantied that gdal.Translate will produce a dataset
        # with the same extent as gdal.Warp!
        # The problem seams to only appear if the target resolution is smaller than the source resolution.

        isOversamplingCase = self.grid().resolution().x() > xRes or self.grid().resolution().y() > yRes
        if isOversamplingCase:
            if not driver.equal(other=MemDriver()):
                # todo: solve this problem with /vsimem/
                raise Exception('spatial resolution oversampling is only supported for MEM format')

            # read one extra source column and line
            translateOptions = gdal.TranslateOptions(format=driver.name(), creationOptions=options,
                                                     projWin=[ul.x(), ul.y(), lr.x() + self.grid().resolution().x(),
                                                              lr.y() - self.grid().resolution().y()],
                                                     xRes=xRes, yRes=yRes, **kwargs)
            tmpGdalDataset = gdal.Translate(destName='', srcDS=self._gdalDataset, options=translateOptions)

            # subset to the exact target grid
            translateOptions = gdal.TranslateOptions(format=driver.name(), creationOptions=options,
                                                     srcWin=[0, 0, grid.size().x(), grid.size().y()])
            gdalDataset = gdal.Translate(destName='', srcDS=tmpGdalDataset, options=translateOptions)

        else:

            translateOptions = gdal.TranslateOptions(format=driver.name(), creationOptions=options,
                                                     projWin=[ul.x(), ul.y(), lr.x(), lr.y()],
                                                     xRes=xRes, yRes=yRes, **kwargs)
            gdalDataset = gdal.Translate(destName=filename, srcDS=self._gdalDataset, options=translateOptions)

        rasterDataset = RasterDataset(gdalDataset=gdalDataset)
#        assert grid.equal(other=rasterDataset.grid())

        # fix grid extent (should only appear with NearestNeighbour resampling
        if not grid.equal(other=rasterDataset.grid()):
            if kwargs.get('resampleAlg', gdal.GRA_NearestNeighbour) == gdal.GRA_NearestNeighbour:
                rasterDataset.setGrid(grid)
            else:
                assert 0, 'unknown condition'

        return rasterDataset

    def array(self, indices=None, grid=None, resampleAlg=gdal.GRA_NearestNeighbour, noDataValue=None, errorThreshold=0.,
              warpMemoryLimit=100 * 2 ** 20, multithread=False):
        '''
        Returns raster data as 3d array of shape = (zsize, ysize, xsize) for the given ``grid``,
        where zsize is the number of raster bands, and ysize, xsize = grid.shape().

        :param indices: band indices to read (default is all bands)
        :type indices: list
        :param grid: if not specified self.grid() is used
        :type grid: hubdc.core.Grid
        :param resampleAlg: one of the GDAL resampling algorithms gdal.GRA_*
        :type resampleAlg: int
        :param noDataValue: if not specified, no data value of self is used
        :type noDataValue: float
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :type errorThreshold: float
        :param warpMemoryLimit: size of working buffer in bytes
        :type warpMemoryLimit: int
        :param multithread: whether to multithread computation and I/O operations
        :type multithread: bool
        :return:
        :rtype: numpy.ndarray
        '''

        if grid is None:
            grid = self.grid()

        if indices is not None:
            bandList = [i+1 for i in indices]
        else:
            bandList = None

        if self.grid().projection().equal(other=grid.projection()):
            datasetResampled = self.translate(grid=grid, filename='', driver=MemDriver(), resampleAlg=resampleAlg,
                                              noData=noDataValue,
                                              bandList=bandList) # subset via bandList
        else:
            if bandList is None:
                datasetResampled = self.warp(grid=grid, filename='', driver=MemDriver(), resampleAlg=resampleAlg,
                                             errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit,
                                             multithread=multithread, srcNodata=noDataValue)
            else:
                # subset bands via in-memory VRT
                datasetSubsetted = self.translate(filename='/vsimem/hubdc.core.RasterDataset.array.vrt',
                                                  driver=VrtDriver(), noData=noDataValue, bandList=bandList)
                datasetResampled = self.warp(grid=grid, filename='', driver=MemDriver(), resampleAlg=resampleAlg,
                                             errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit,
                                             multithread=multithread, srcNodata=noDataValue)
                gdal.Unlink(datasetSubsetted.filename())


        array = datasetResampled.readAsArray()
        datasetResampled.close()
        return array

    def xsize(self):
        '''Returns raster x size in pixels.'''
        return self._gdalDataset.RasterXSize

    def ysize(self):
        '''Returns raster y size in pixels.'''
        return self._gdalDataset.RasterYSize

    def zsize(self):
        '''Returns raster z size in terms of number of raster bands.'''
        return self._gdalDataset.RasterCount

    def shape(self):
        '''Returns the ``(zsize, ysize, xsize)`` tuple.'''
        return self.zsize(), self.ysize(), self.xsize()

    def dtype(self):
        '''Returns the raster data type.'''
        return self._gdalDataset.GetRasterBand(1).ReadAsArray(win_xsize=1, win_ysize=1).dtype.type

    def xprofile(self, row):
        '''
        Returns raster data as 1d array for the given ``row``.
        '''
        assert isinstance(row, Row)
        return self.band(index=row.z()).xprofile(y=row.y())

    def yprofile(self, column):
        '''
        Returns raster data as 1d array for the given ``column``.
        '''
        assert isinstance(column, Column)
        return self.band(index=column.z()).yprofile(x=column.x())

    def zprofile(self, pixel):
        '''
        Returns raster data as 1d array for the given ``pixel``.
        '''
        grid = self.grid().subset(offset=pixel, size=RasterSize(x=1, y=1))
        profile = self.readAsArray(grid=grid).flatten()
        return profile

    def plotZProfile(self, pixel, plotWidget=None, spectral=False, xscale=1., yscale=1., **kwargs):
        import pyqtgraph as pg
        assert isinstance(pixel, Pixel)

        if plotWidget is None:
            plotWidget = pg.plot()

        if spectral:
            X = np.array(self.metadataItem(key='wavelength', domain='ENVI', required=True), dtype=np.float) * xscale
        else:
            X = None
        Y = self.zprofile(pixel=pixel) * yscale

        plotWidget.plot(x=X, y=Y, **kwargs)
        return plotWidget

    def plotXProfile(self, row, plotWidget=None, yscale=1., **kwargs):
        import pyqtgraph as pg
        assert isinstance(row, Row)

        if plotWidget is None:
            plotWidget = pg.plot()

        Y = self.xprofile(row=row) * yscale

        plotWidget.plot(y=Y, **kwargs)
        return plotWidget

    def plotYProfile(self, column, plotWidget=None, yscale=1., **kwargs):
        import pyqtgraph as pg
        assert isinstance(column, Column)

        if plotWidget is None:
            plotWidget = pg.plot()

        Y = self.yprofile(column=column) * yscale

        plotWidget.plot(y=Y, **kwargs)
        return plotWidget

    def mapViewer(self):
        mapViewer = MapViewer()
        mapViewer.addLayer(layer=self.mapLayer())
        return mapViewer

    def mapLayer(self):
        from qgis.core import QgsRasterLayer
        if self.driver().equal(MemDriver()):
            raise NotImplementedError()
        return MapLayer(QgsRasterLayer(self.filename()))

    def show(self):
        self.mapViewer().show()

    def plotSinglebandGrey(self, index=0, vmin=None, vmax=None, pmin=None, pmax=None, cmap='gray', noPlot=False,
                           showPlot=True):
        '''
        cmap see https://matplotlib.org/examples/color/colormaps_reference.html
        https://matplotlib.org/api/_as_gen/matplotlib.pyplot.imshow.html
        '''
        def stretch(band, vmin=None, vmax=None, pmin=None, pmax=None):
            if pmin is not None:
                vmin = np.nanpercentile(band, pmin)
            if pmax is not None:
                vmax = np.nanpercentile(band, pmax)
            if vmin is None:
                if band.dtype == np.uint8:
                    vmin = 0
                else:
                    vmin = np.nanmin(band)
            if vmax is None:
                if band.dtype == np.uint8:
                    vmax = 255
                else:
                    vmax = np.nanmax(band)

            grey = np.float32(band-vmin)
            grey /= vmax-vmin
            np.clip(grey, 0, 1, grey)
            return grey

        band = self.band(index=index).readAsArray().astype(dtype=np.float32)
        noDataValue = self.band(index=index).noDataValue()
        if noDataValue is not None:
            band[band==noDataValue] = np.nan


        grey = stretch(band, vmin, vmax, pmin, pmax)

        if not noPlot:
            fig = plt.imshow(grey, cmap=cmap)
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            if showPlot:
                plt.show()

        return grey

    def plotMultibandColor(self, rgbindex=(0, 1, 2), rgbvmin=(None, None, None), rgbvmax=(None, None, None),
                           rgbpmin=(None, None, None), rgbpmax=(None, None, None), noPlot=False, showPlot=True):

        def toTupel(v):
            if not isinstance(v, (list, tuple)):
                v = (v, v, v)
            return v

        rgb = [self.plotSinglebandGrey(index=index, vmin=vmin, vmax=vmax, pmin=pmin, pmax=pmax, noPlot=True)
               for index, vmin, vmax, pmin, pmax in zip(rgbindex, toTupel(rgbvmin), toTupel(rgbvmax),
                                                       toTupel(rgbpmin), toTupel(rgbpmax))]

        if not noPlot:
            fig = plt.imshow(np.array(rgb).transpose((1, 2, 0)))
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            if showPlot:
                plt.show()

        return rgb

    def plotCategoryBand(self, index=0, noPlot=False, showPlot=True):

        from matplotlib.colors import LinearSegmentedColormap
        colors = np.array(self.band(index=index).categoryColors())[1:,0:3]
        array = self.band(index=index).readAsArray()
        ar = np.zeros_like(array)
        ag = np.zeros_like(array)
        ab = np.zeros_like(array)
        for i, (cr, cg, cb) in enumerate(colors):
            valid = array == i+1
            ar[valid] = cr
            ag[valid] = cg
            ab[valid] = cb
        rgb = np.array([ar, ag, ab]) / 255.

        if not noPlot:
            fig = plt.imshow(np.array(rgb).transpose((1,2,0)))
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            if showPlot:
                plt.show()

        return rgb

class MetadataFormatter(object):
    '''Class for managing GDAL metadata value formatting.'''

    @classmethod
    def valueToString(cls, value):
        '''Returns a string representation of value.'''

        if isinstance(value, (list, tuple)):
            return cls._listToString(value)
        else:
            return str(value)

    @classmethod
    def stringToValue(cls, string, dtype):
        '''
        Returns a representation of ``string`` as value of given ``dtype``.
        If ``string`` represents a list of values in curly brackets (e.g. ``{1, 2, 3}``),
        a list of values is returned.
        '''

        string.strip()
        if string.startswith('{') and string.endswith('}'):
            value = cls._stringToList(string, dtype)
        else:
            value = dtype(string)
        return value

    @classmethod
    def _listToString(cls, values):
        return '{' + ', '.join([str(v) for v in values]) + '}'

    @classmethod
    def _stringToList(cls, string, type):
        values = [type(v.strip()) for v in string[1:-1].split(',')]
        return values


class RasterBandDataset():
    '''Class for managing raster band datasets.'''

    def __init__(self, raster, index):
        '''Creating a new instance given a :class:`~hubdc.model.Raster` and a raster band ``index``.'''
        assert isinstance(raster, RasterDataset)
        if index < 0 or index > raster.zsize() - 1:
            raise errors.IndexError(index=index, min=0, max=raster.zsize()-1)

        self._raster = raster
        self._index = index
        self._gdalBand = raster._gdalDataset.GetRasterBand(index + 1)

    def __repr__(self):
        return '{cls}(raster={raster}, index={index})'.format(
            cls=self.__class__.__name__,
            raster=repr(self.raster()),
            index=repr(self.index()))

    def raster(self):
        '''Returns the :class:`~hubdc.core.RasterDataset`.'''
        assert isinstance(self._raster, RasterDataset)
        return self._raster

    def index(self):
        '''Returns the raster band index.'''
        return self._index

    def gdalBand(self):
        '''Return the gdal.Band.'''
        return self._gdalBand

    def flushCache(self):
        '''Flush the cache.'''
        self.gdalBand().FlushCache()

    def readAsArray(self, grid=None, resample_alg=gdal.GRA_NearestNeighbour):
        '''Returns raster band data as 2d array.

        :param grid: if provided, only data inside the grid extent is returned.
        :type grid: hubdc.core.Grid
        :param resampleAlg: one of the GDAL resampling algorithms (i.e. gdal.GRA_*)
        :type resampleAlg: int
        :return:
        :rtype: numpy.ndarray
        '''

        if grid is None:
            array = self._gdalBand.ReadAsArray(resample_alg=resample_alg)
        else:
            assert isinstance(grid, Grid)
            resolution = self._raster.grid().resolution()
            extent = self._raster.grid().extent()
            xoff = round((grid.extent().xmin() - extent.xmin()) / resolution.x(), 0)
            yoff = round((extent.ymax() - grid.extent().ymax()) / resolution.y(), 0)
            xsize = round((grid.extent().xmax() - grid.extent().xmin()) / resolution.x(), 0)
            ysize = round((grid.extent().ymax() - grid.extent().ymin()) / resolution.y(), 0)
            buf_ysize, buf_xsize = grid.shape()
            array = self._gdalBand.ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize,
                                               buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                               resample_alg=resample_alg)
            if array is None or xoff < 0 or yoff < 0:  # ReadAsArray seams to accept xy offets of -1, which makes no sense, so we manually raise an error
                raise errors.AccessGridOutOfRangeError()

        assert isinstance(array, np.ndarray)
        assert array.ndim == 2
        return array

    def array(self, grid=None, resampleAlg=gdal.GRA_NearestNeighbour, noData=None, errorThreshold=0.,
              warpMemoryLimit=100 * 2 ** 20, multithread=False):
        '''
        Returns raster band data as 2d array of shape = (ysize, xsize) for the given ``grid``,
        where zsize is the number of raster bands, and ysize, xsize = grid.shape().

        :param grid: if not specified self.grid() is used
        :type grid: hubdc.core.Grid
        :param resampleAlg: one of the GDAL resampling algorithms gdal.GRA_*
        :type resampleAlg: int
        :param noData: if not specified, no data value of self is used
        :type noData: float
        :param errorThreshold: error threshold for approximation transformer (in pixels)
        :type errorThreshold: float
        :param warpMemoryLimit: size of working buffer in bytes
        :type warpMemoryLimit: int
        :param multithread: whether to multithread computation and I/O operations
        :type multithread: bool
        :return:
        :rtype: numpy.ndarray
        '''

        if grid is None:
            grid = self.raster().grid()

        # make single band in-memory VRT raster and re-use RasterDataset.array
        filename = '/vsimem/hubdc.core.RasterBandDataset.array.vrt'
        vrt = self.raster().translate(filename=filename, driver=VrtDriver(), bandList=[self.index()+1])
        array = vrt.array(grid=grid, resampleAlg=resampleAlg, noData=noData, errorThreshold=errorThreshold,
                          warpMemoryLimit=warpMemoryLimit, multithread=multithread)
        gdal.Unlink(filename)
        return array[0]

    def writeArray(self, array, grid=None):
        '''Writes raster data.

        :param array:
        :type array: 3d array | list of 2d arrays
        :param grid: if provided, data is written to the location given by the grid extent
        :type grid: hubdc.core.Grid
        '''

        assert isinstance(array, np.ndarray)
        if array.ndim == 3:
            assert len(array) == 1
            array = array[0]

        if grid is None:
            grid = self._raster.grid()

        assert isinstance(grid, Grid)
        if array.shape != grid.shape():
            raise errors.ArrayShapeMismatchError()

        assert self._raster.grid().projection().equal(other=grid.projection())

        xoff = int(round((grid.extent().xmin() - self._raster.grid().extent().xmin()) /
                         self._raster.grid().resolution().x(), 0))
        yoff = int(round((self._raster.grid().extent().ymax() - grid.extent().ymax()) /
                         self._raster.grid().resolution().y(), 0))
        try:
            self._gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)
        except ValueError:
            raise errors.AccessGridOutOfRangeError
        self.flushCache()

    def fill(self, value):
        '''Write constant ``value`` to the whole raster band.'''
        self._gdalBand.Fill(value)

    def setMetadataItem(self, key, value, domain=''):
        '''Set a metadata item. ``value`` can be a string, a number or a list of strings or numbers.'''

        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = MetadataFormatter.valueToString(value)
        self._gdalBand.SetMetadataItem(key, gdalString, domain)
        self.flushCache()

    def metadataItem(self, key, domain='', default=None, required=False, dtype=str):
        '''Return the metadata item.'''
        key = key.replace(' ', '_')
        gdalString = self._gdalBand.GetMetadataItem(key, domain)
        if gdalString is None:
            if required:
                raise errors.MissingMetadataItemError(key=key, domain=domain)
            return default

        return MetadataFormatter.stringToValue(gdalString, dtype=dtype)

    def metadataDomain(self, domain=''):
        '''Return the metadata dictionary for the given ``domain``.'''
        metadataDomain = dict()
        for key in self._gdalBand.GetMetadata(domain):
            key = key.replace('_', ' ')
            metadataDomain[key] = self.metadataItem(key=key, domain=domain)
        return metadataDomain

    def metadataDict(self):
        '''Return the metadata dictionary for all domains.'''
        metadataDict = dict()
        for domain in self.metadataDomainList():
            metadataDict[domain] = self.metadataDomain(domain=domain)
        return metadataDict

    def copyMetadata(self, other):
        '''Copy raster and raster band metadata from self to other '''

        assert isinstance(other, RasterBandDataset)

        for domain in other.metadataDomainList():
            self._gdalBand.SetMetadata(other._gdalBand.GetMetadata(domain), domain)

    def setNoDataValue(self, value):
        '''Set no data value.'''
        if value is not None:
            self._gdalBand.SetNoDataValue(float(value))
            self.flushCache()

    def noDataValue(self, default=None, required=False):
        '''Returns band no data value. Returns ``default`` if no data value is undefined, or raises an error if ``required``.'''
        noDataValue = self._gdalBand.GetNoDataValue()
        if noDataValue is None:
            noDataValue = default
        if noDataValue is None and required:
            raise errors.MissingNoDataValueError(filename=self.raster().filename(), index=self.index()+1)
        return noDataValue

    def setDescription(self, value):
        '''Set band description.'''
        self._gdalBand.SetDescription(value)
        self.flushCache()

    def description(self):
        '''Returns band description.'''
        return self._gdalBand.GetDescription()

    def setCategoryNames(self, names):
        '''Set band category names.'''
        if names is not None:
            self._gdalBand.SetCategoryNames(names)
            self.flushCache()

    def categoryNames(self):
        '''Returns band category names.'''
        names = self._gdalBand.GetCategoryNames()
        return names

    def setCategoryColors(self, colors):
        '''Set band category colors from list of rgba tuples.'''
        if colors is not None:
            colorTable = gdal.ColorTable()
            for i, color in enumerate(colors):
                assert isinstance(color, tuple)
                if len(color)==3:
                    color = color + (255,)
                assert len(color) == 4
                colorTable.SetColorEntry(i, color)
            self._gdalBand.SetColorTable(colorTable)
            self.flushCache()

    def categoryColors(self):
        '''Returns band category colors as list of rgba tuples.'''
        colorTable = self._gdalBand.GetColorTable()
        if colorTable is not None:
            colors = list()
            for i in range(colorTable.GetCount()):
                rgba = colorTable.GetColorEntry(i)
                colors.append(rgba)
        else:
            colors = None
        return colors

    def metadataDomainList(self):
        '''Returns the list of metadata domain names.'''
        domains = self._gdalBand.GetMetadataDomainList()
        return domains if domains is not None else []

    def xprofile(self, y):
        '''
        Returns raster data as 1d array for the given row ``y``.
        '''
        grid = self.raster().grid().subset(offset=Pixel(x=0, y=y), size=RasterSize(x=self.raster().xsize(), y=1))
        profile = self.readAsArray(grid=grid).flatten()
        return profile

    def yprofile(self, x):
        '''
        Returns raster data as 1d array for the given column ``x``.
        '''
        grid = self.raster().grid().subset(offset=Pixel(x=x, y=0), size=RasterSize(x=1, y=self.raster().ysize()))
        profile = self.readAsArray(grid=grid).flatten()
        return profile

    def mapLayer(self):
        from qgis.core import QgsRasterLayer
        filename = '/vsimem/mapLayer/{}_{}.vrt'.format(self.raster().filename(), self.index())
        rasterDataset = self.raster().translate(bandList=[self.index()+1], filename=filename, driver=VrtDriver())
        return rasterDataset.mapLayer()

    def show(self):
        MapViewer().addLayer(layer=self.mapLayer()).show()

class VectorDataset(object):
    '''Class for managing vector layer datasets.'''

    def __init__(self, ogrDataSource, layerNameOrIndex=0):
        '''Creates new instance from given ogr.DataSource and layer name or index given by ``nameOrIndex``.'''

        #assert isinstance(ogrDataSource, ogr.DataSource), str(ogrDataSource)
        assert isinstance(ogrDataSource, (gdal.Dataset, ogr.DataSource)), str(ogrDataSource)

        self._ogrDataSource = ogrDataSource
        if isinstance(layerNameOrIndex, int):
            self._ogrLayer = ogrDataSource.GetLayerByIndex(layerNameOrIndex)
        elif isinstance(layerNameOrIndex, str):
            self._ogrLayer = ogrDataSource.GetLayerByName(layerNameOrIndex)
        else:
            raise errors.ObjectParserError(obj=layerNameOrIndex, type=[int, str])

        if self._ogrLayer is None:
            raise errors.InvalidOGRLayerError(layerNameOrIndex)
        self._filename = self._ogrDataSource.GetDescription()
        self._layerNameOrIndex = layerNameOrIndex
        self._reprojectionCache = dict()

    def __repr__(self):

        return '{cls}(ogrDataSource={ogrDataSource}, layerNameOrIndex={layerNameOrIndex})'.format(
            cls=self.__class__.__name__,
            ogrDataSource=repr(self.ogrDataSource()),
            layerNameOrIndex=repr(self.layerNameOrIndex()))

    @staticmethod
    def fromPoints(points, filename='', driver=MemoryDriver()):
        '''Create instance from given ``points``. Projection is taken from the first point.'''

        assert isinstance(driver, VectorDriver)
        assert isinstance(points[0], Point)
        projection = points[0].projection()
        driver.prepareCreation(filename=filename)
        ogrDriver = driver.ogrDriver()
        ogrDataSource = ogrDriver.CreateDataSource(filename)
        ogrLayer = ogrDataSource.CreateLayer('points', projection.osrSpatialReference(), ogr.wkbPoint)

        for p in points:
            assert isinstance(p, Point)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(p.x(), p.y())
            ogrFeature = ogr.Feature(ogrLayer.GetLayerDefn())
            ogrFeature.SetGeometry(point)
            ogrLayer.CreateFeature(ogrFeature)
            ogrFeature = None
            point = None

        if driver.equal(other=MemoryDriver()):
            vectorDataset = VectorDataset(ogrDataSource=ogrDataSource)
        else:
            ogrDataSource = None
            vectorDataset = openVectorDataset(filename=filename)

        return vectorDataset


    def filename(self):
        '''Returns the filename.'''
        return self._filename

    def layerNameOrIndex(self):
        '''Returns the layer name/index.'''
        return self._layerNameOrIndex

    def ogrDataSource(self):
        '''Returns the ogr.DataSource.'''
        return self._ogrDataSource

    def ogrLayer(self):
        '''Returns the ogr.Layer.'''
        assert isinstance(self._ogrLayer, ogr.Layer)
        return self._ogrLayer

    def close(self):
        '''Closes the ogr.DataSourse and ogr.Layer'''
        self._ogrLayer = None
        self._ogrDataSource = None

    def projection(self):
        '''Returns the :class:`~hubdc.model.Projection`.'''
        return Projection(wkt=self._ogrLayer.GetSpatialRef())

    def geometryTypeName(self):
        '''Return the geometry type name.'''
        return ogr.GeometryTypeToName(self.ogrLayer().GetGeomType())

    def extent(self):
        '''Returns the :class:`~hubdc.model.Extent`.'''
        xmin, xmax, ymin, ymax = self._ogrLayer.GetExtent()
        return Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, projection=self.projection())

    def grid(self, resolution):
        '''Returns grid with extent of self and given resolution.'''
        return Grid(extent=self.extent(), resolution=resolution)

    def rasterize(self, grid, gdalType=gdal.GDT_Float32,
                  initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                  filterSQL=None, noDataValue=None,
                  filename='', driver=MemDriver(), options=None):
        '''Returns a :class:`~hubdc.model.Raster` that is the rasterization of self into the given ``grid`` as.

        :param grid:
        :type grid: hubdc.core.Grid
        :param gdalType: one of the GDAL data types gdal.GDT_*
        :type gdalType: int
        :param initValue: value to pre-initialize the output array
        :type initValue: int
        :param burnValue: value to burn into the output array for all objects; exclusive with ``burnAttribute``
        :type burnValue: int
        :param burnAttribute: identifies an attribute field on the features to be used for a burn-in value; exclusive with ``burnValue``
        :type burnAttribute: str
        :param allTouched: whether to enable that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon
        :type allTouched: bool
        :param filterSQL: set an SQL WHERE clause which will be used to filter vector features
        :type filterSQL: str
        :param noDataValue: output raster no data value
        :type noDataValue: float
        :param filename: output filename
        :type filename: str
        :param driver:
        :type driver: hubdc.core.RasterDriver
        :param options: raster creation options
        :type options: list
        :return:
        :rtype: hubdc.core.RasterDataset
        '''

        assert isinstance(grid, Grid)
        assert isinstance(driver, RasterDriver)
        if options is None:
            options = driver.options()
        assert isinstance(options, list)

        if self.projection().equal(other=grid.projection()):
            vector = self
        else:
            if not grid.projection().wkt() in self._reprojectionCache:
                self._reprojectionCache[grid.projection().wkt()] = self.reproject(projection=grid.projection())
            vector = self._reprojectionCache[grid.projection().wkt()]

        vector.ogrLayer().SetAttributeFilter(filterSQL)
        vector.ogrLayer().SetSpatialFilter(grid.extent().geometry().ogrGeometry())

        raster = driver.create(grid=grid, bands=1, gdalType=gdalType, filename=filename, options=options)
        if noDataValue is not None:
            raster.setNoDataValue(noDataValue)
        raster.band(index=0).fill(value=initValue)

        rasterizeLayerOptions = list()
        # special options controlling rasterization:
        #    "ATTRIBUTE": Identifies an attribute field on the features to be used for a burn in value. The value will be burned into all output bands. If specified, padfLayerBurnValues will not be used and can be a NULL pointer.
        #    "CHUNKYSIZE": The height in lines of the chunk to operate on. The larger the chunk size the less times we need to make a pass through all the shapes. If it is not set or set to zero the default chunk size will be used. Default size will be estimated based on the GDAL cache buffer size using formula: cache_size_bytes/scanline_size_bytes, so the chunk will not exceed the cache.
        #    "ALL_TOUCHED": May be set to TRUE to set all pixels touched by the line or polygons, not just those whose center is within the polygon or that are selected by brezenhams line algorithm. Defaults to FALSE.
        #    "BURN_VALUE_FROM": May be set to "Z" to use the Z values of the geometries. The value from padfLayerBurnValues or the attribute field value is added to this before burning. In default case dfBurnValue is burned as it is. This is implemented properly only for points and lines for now. Polygons will be burned using the Z value from the first point. The M value may be supported in the future.
        #    "MERGE_ALG": May be REPLACE (the default) or ADD. REPLACE results in overwriting of value, while ADD adds the new value to the existing raster, suitable for heatmaps for instance.
        if allTouched:
            rasterizeLayerOptions.append('ALL_TOUCHED=TRUE')
        if burnAttribute:
            rasterizeLayerOptions.append('ATTRIBUTE=' + burnAttribute)

        gdal.RasterizeLayer(raster.gdalDataset(), [1], vector.ogrLayer(), burn_values=[burnValue],
                            options=rasterizeLayerOptions)
        vector.ogrLayer().SetAttributeFilter(None)
        return raster

    def metadataDomainList(self):
        '''Returns the list of metadata domain names.'''
        domains = self._ogrLayer.GetMetadataDomainList()
        return domains if domains is not None else []

    def metadataItem(self, key, domain='', dtype=str, required=False, default=None):
        '''Returns the value (casted to a specific ``dtype``) of a metadata item.'''
        key = key.replace(' ', '_')
        gdalString = self._ogrLayer.GetMetadataItem(key, domain)
        if gdalString is None:
            if required:
                raise Exception('missing metadata item: key={}, domain={}'.format(key, domain))
            return default
        return MetadataFormatter.stringToValue(gdalString, dtype=dtype)

    def metadataDomain(self, domain=''):
        '''Returns the metadata dictionary for the given ``domain``.'''
        metadataDomain = dict()
        for key in self._ogrLayer.GetMetadata(domain):
            key = key.replace('_', ' ')
            metadataDomain[key] = self.metadataItem(key=key, domain=domain)
        return metadataDomain

    def metadataDict(self):
        '''Returns the metadata dictionary for all domains.'''
        metadataDict = dict()
        for domain in self.metadataDomainList():
            metadataDict[domain] = self.metadataDomain(domain=domain)
        return metadataDict

    def setMetadataItem(self, key, value, domain=''):
        '''Set a metadata item. ``value`` can be a string, a number or a list of strings or numbers.'''
        if value is None:
            return
        key = key.replace(' ', '_').strip()
        if domain.upper() == 'ENVI' and key.lower() == 'file_compression':
            return
        gdalString = MetadataFormatter.valueToString(value)
        self._ogrLayer.SetMetadataItem(key, gdalString, domain)

    def setMetadataDomain(self, metadataDomain, domain):
        '''Set the metadata domain'''
        assert isinstance(metadataDomain, dict)
        for key, value in metadataDomain.items():
            self.setMetadataItem(key=key, value=value, domain=domain)

    def setMetadataDict(self, metadataDict):
        '''Set the metadata dictionary'''
        assert isinstance(metadataDict, dict)
        for domain, metadataDomain in metadataDict.items():
            self.setMetadataDomain(metadataDomain=metadataDomain, domain=domain)
            #for key, value in metadataDict[domain].items():
            #    self.setMetadataItem(key=key, value=value, domain=domain)

    def reproject(self, projection, filename='', driver=MemoryDriver(), **kwargs):
        '''Returns a reprojection of self into the given projection. Optional kwargs are passed to gdal.VectorTranslateOptions.'''

        assert isinstance(driver, VectorDriver)
        filename = driver.prepareCreation(filename)
        options = gdal.VectorTranslateOptions(format=driver.name(), dstSRS=projection.wkt(), **kwargs)
        ogrDataSource = gdal.VectorTranslate(destNameOrDestDS=filename, srcDS=self.ogrDataSource(), options=options)
        vectorDataset = VectorDataset(ogrDataSource=ogrDataSource, layerNameOrIndex=self.layerNameOrIndex())
        return vectorDataset

    def featureCount(self):
        '''Returns the number of features.'''
        return self._ogrLayer.GetFeatureCount()

    def fieldCount(self):
        '''Returns the number of attribute fields.'''
        return self._ogrLayer.GetLayerDefn().GetFieldCount()

    def fieldNames(self):
        '''Returns the attribute field names.'''
        names = [self._ogrLayer.GetLayerDefn().GetFieldDefn(i).GetName() for i in range(self.fieldCount())]
        return names

    def fieldTypeNames(self):
        '''Returns the attribute field data type names.'''
        typeNames = [self._ogrLayer.GetLayerDefn().GetFieldDefn(i).GetTypeName() for i in range(self.fieldCount())]
        return typeNames

    def zsize(self):
        '''Returns number of layers (i.e. 1).'''
        return 1

    def mapViewer(self):
        mapViewer = MapViewer()
        mapViewer.addLayer(layer=self.mapLayer())
        return mapViewer

    def mapLayer(self):
        from qgis.core import QgsVectorLayer
        return MapLayer(QgsVectorLayer(self.filename()))

    def show(self):
        self.mapViewer().show()



def openRasterDataset(filename, eAccess=gdal.GA_ReadOnly):
    '''
    Opens the raster given by ``filename``.

    :param filename: input filename
    :type filename: str
    :param eAccess: access mode ``gdal.GA_ReadOnly`` or ``gdal.GA_Update``
    :type eAccess: int
    :return:
    :rtype: hubdc.core.RasterDataset
    '''

    assert isinstance(filename, str), type(filename)
    if not filename.startswith('/vsimem/') and not exists(filename):
        raise errors.FileNotExistError(filename)

    try:
        gdalDataset = gdal.Open(filename, eAccess)
    except RuntimeError:
        raise errors.InvalidGDALDatasetError(filename)

    if gdalDataset is None:
        raise errors.InvalidGDALDatasetError(filename)

    if gdalDataset.GetProjection() == '':
        #import warnings
        #warnings.warn('missing SRS for GDAL dataset {}; WGS84 is used'.format(filename), UserWarning)

        # create vrt with WGS84 projection
        filenameVRT = filename + '.wgs84.vrt'
        filenameVRT = '/vsimem/{}.wgs84.vrt'.format(filename)

        gdalDataset2 = gdal.Translate(filenameVRT, filename, format='VRT', outputSRS=Projection.wgs84().wkt())
        gdalDataset2.SetGeoTransform((0.0, 1.0, 0.0, 0.0, 0.0, -1.0))
        rasterDataset = RasterDataset(gdalDataset=gdalDataset2)
        rasterDataset.copyMetadata(other=RasterDataset(gdalDataset=gdalDataset))
        rasterDataset.flushCache()
    else:
        rasterDataset = RasterDataset(gdalDataset=gdalDataset)

    return rasterDataset


def openVectorDataset(filename, layerNameOrIndex=None, update=False):
    '''
    Opens the vector layer given by ``filename`` and ``layerNameOrIndex``.

    :param filename: input filename
    :type filename: str
    :param layerNameOrIndex: layer index or name
    :type layerNameOrIndex: int | str
    :param update: whether to open in update mode
    :type update: bool
    :return:
    :rtype: hubdc.core.VectorDataset
    '''

    assert isinstance(filename, str), type(filename)

    # evaluate "<filename> | layername=<layername>" pattern used by QGIS
    if len(filename.split('|')) == 2:
        tmp = filename.split('|')
        filename = tmp[0].strip()
        layerNameOrIndex = tmp[1].split('=')[1].strip()

    if layerNameOrIndex is None:
        layerNameOrIndex = 0

    if str(layerNameOrIndex).isdigit():
        layerNameOrIndex = int(layerNameOrIndex)
    #ogrDataSource = ogr.Open(filename, int(update))
    ogrDataSource = gdal.OpenEx(filename, gdal.OF_VECTOR)

    if ogrDataSource is None:
        raise errors.InvalidOGRDataSourceError(filename)

    return VectorDataset(ogrDataSource=ogrDataSource, layerNameOrIndex=layerNameOrIndex)

def createVRTDataset(rasterDatasetsOrFilenames, filename='', **kwargs):
    '''
    Creates a virtual raster file (VRT) from raster datasets or filenames given by ``rastersOrFilenames``.

    :param filename: output filename
    :type filename: str
    :param rastersOrFilenames: list of filenames or rasters
    :type rastersOrFilenames: Union[Tuple, List]
    :param kwargs: all additional keyword arguments are passed to gdal.BuildVRTOptions
    :type kwargs:
    :return:
    :rtype: hubdc.core.RasterDataset
    '''

    srcDSOrSrcDSTab = list()
    for rasterDatasetsOrFilename in rasterDatasetsOrFilenames:
        if isinstance(rasterDatasetsOrFilename, RasterDataset):
            srcDSOrSrcDSTab.append(rasterDatasetsOrFilename.gdalDataset())
        elif isinstance(rasterDatasetsOrFilename, str):
            srcDSOrSrcDSTab.append(rasterDatasetsOrFilename)
        else:
            assert 0

    options = gdal.BuildVRTOptions(**kwargs)
    gdalDataset = gdal.BuildVRT(destName=filename, srcDSOrSrcDSTab=srcDSOrSrcDSTab, options=options)
    gdalDataset = None
    return openRasterDataset(filename=filename)

class PseudoGrid(Grid):
    def __init__(self, size):
        size = RasterSize.parse(size)
        res = 1 / 3600. # 1 second of arc
        extent = Extent(xmin=0, xmax=size.x() * res, ymin=0, ymax=size.y() * res, projection=Projection.wgs84())
        Grid.__init__(self, extent=extent, resolution=Resolution(x=res, y=res))

    @staticmethod
    def fromArray(array):
        isinstance(array, np.ndarray)
        size = RasterSize(x=array.shape[-1], y=array.shape[-2])
        return PseudoGrid(size=size)

class ENVI():

    SPATIAL_KEYS = ['lines', 'samples', 'map info', 'projection info', 'coordinate system string']

    @staticmethod
    def numpyType(enviType):
        typeMap = {1: np.uint8, 2: np.int16, 3: np.int32, 4: np.float32, 5: np.float64, 6: np.complex64,
                   9: np.complex128, 12: np.uint16, 13: np.uint32, 14: np.int64, 15: np.uint64}
        return typeMap[enviType]

    @classmethod
    def gdalType(cls, enviType):
        numpyType = cls.numpyType(enviType=enviType)
        return gdal_array.NumericTypeCodeToGDALTypeCode(numpyType)

    @staticmethod
    def typeSize(enviType):
        typeMap = {1: 8, 2: 16, 3: 32, 4: 32, 5: 64, 6: 64, 9: 128, 12: 16, 13: 32, 14: 64, 15: 64}
        bits = typeMap[enviType]
        bytes = bits/8
        return bytes


    @staticmethod
    def findHeader(filenameBinary, ext='.hdr'):
        for filename in [filenameBinary + ext, splitext(filenameBinary)[0] + ext]:
            if exists(filename):
                return filename
        return None

    @staticmethod
    def readHeader(filenameHeader):
        text = list()
        with open(filenameHeader, 'r') as f:
            for line in f:
                line = line.strip()
                if line == 'ENVI' or line == '':
                    newline = line
                else:
                    key, *value = line.split('=')
                    value = '='.join(value).strip()
                    if (value[0] != '{') or (value[0] == '{' and value[-1] == '}'): # item in single line
                        newline = line
                    else: # item on multiple lines
                        newline = line
                        while True:
                            newline += f.readline()
                            if newline.strip()[-1] == '}':
                                break
                text.append(newline)

        result = OrderedDict()
        for line in text:
            if line == 'ENVI' or line == '':
                continue
            else:
                key, *value = line.split('=')
                value = '='.join(value).replace('\n', ' ').strip()
                result[key.strip()] = value

        return result

    @staticmethod
    def writeHeader(filenameHeader, metadata):

        metadata = metadata.copy()
        keys = ['description', 'samples', 'lines', 'bands', 'header_offset', 'file_type', 'data_type',
                'interleave', 'data_ignore_value',
                'sensor_type', 'byte_order', 'map_info', 'projection_info', 'coordinate_system_string',
                'acquisition_time',
                'wavelength_units', 'wavelength', 'fwhm', 'band_names']

        def writeItem(key, value):
            if value is not None:
                value = MetadataFormatter.valueToString(value=value)
                f.write('{key} = {value}\n'.format(key=key.replace('_', ' '), value=value))

        with open(filenameHeader, 'w') as f:
            f.write('ENVI\n')
            for key in keys + list(metadata.keys()):
                if key not in metadata:
                    key = key.replace('_', ' ')
                writeItem(key=key, value=metadata.pop(key, None))

def buildOverviews(filename, levels=None, minsize=1024, resampling='average'):
    '''
    Build image overviews (a.k.a. image pyramid) for raster given by ``filename``.
    If the list of overview ``levels`` is not specified, overviews are generated for levels of powers of 2
    (i.e. levels=[2, 4, 8...]) up to the level where the size of the overview is smaller than ``minsize``.

    :param filename: input filename
    :type filename: str
    :param minsize: defines the levels (powers of 2) in the case where ``levels`` is None
    :type minsize: int
    :param levels: list of overview levels
    :type levels: Union[Tuple, List]
    :param resampling: one of those: ``'average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp', 'average_magphase', 'mode'``
    :type resampling: str
    '''

    assert resampling in ['average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp', 'average_magphase',
                          'mode']
    if levels is None:
        assert minsize is not None
        levels = []
        nextLevel = 2
        size = float(max(openRasterDataset(filename=filename).shape()))
        while size > minsize:
            levels.append(nextLevel)
            size /= 2
            nextLevel *= 2

    if len(levels) == 0:
        return

    import subprocess
    subprocess.call(['gdaladdo', '-ro',
                     # '--config', 'COMPRESS_OVERVIEW', 'JPEG',
                     # '--config', 'JPEG_QUALITY_OVERVIEW 25'
                     # '--config', 'INTERLEAVE_OVERVIEW', 'BAND',
                     '-r', 'average',
                     '--config', 'COMPRESS_OVERVIEW', 'LZW',
                     filename, ' '.join(map(str, levels))])

class MapViewer():

    def __init__(self):

        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsApplication
        self.app = QgsApplication([], True)
        self.app.initQgis()
        self.canvas = QgsMapCanvas()
        self.layers = list()
        self._printExtent = False
        self._extentSet = False
        self._projectionSet = False

    def addLayer(self, layer):
        from qgis.core import QgsProject
        assert isinstance(layer, MapLayer)
        self.layers.append(layer)
        qgsLayers = [layer.qgsMapLayer() for layer in self.layers]
        QgsProject.instance().addMapLayers(qgsLayers)
        self.canvas.setLayers(qgsLayers)
        return self

    def setExtent(self, extent):
        assert isinstance(extent, Extent)
        self._extentSet = True
        from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem
        rectangle = QgsRectangle(extent.xmin(), extent.ymin(), extent.xmax(), extent.ymax())
        crs = QgsCoordinateReferenceSystem()
        crs.createFromWkt(extent.projection().wkt())
        self.canvas.setExtent(rectangle)
        self.canvas.setDestinationCrs(crs)
        return self

    def setProjection(self, projection):
        from qgis.core import QgsCoordinateReferenceSystem
        assert isinstance(projection, Projection)
        self._projectionSet = True
        crs = QgsCoordinateReferenceSystem()
        crs.createFromWkt(projection.wkt())
        self.canvas.setDestinationCrs(crs)
        return self

    def _prepareShowOrSave(self):
        from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem
        if not self._extentSet:
            if not self._projectionSet:
                crs = self.layers[0].qgsMapLayer().crs()
                self.canvas.setDestinationCrs(crs)
            self.canvas.setExtent(self.canvas.fullExtent())

    def show(self):
        self._prepareShowOrSave()
        self.canvas.waitWhileRendering()
        if self._printExtent:
            self.canvas.extentsChanged.connect(lambda: print(self.canvas.extent()))
        self.canvas.show()
        self.app.exec_()
        return self

    def save(self, filename):
        # implemented as described here https://gis.stackexchange.com/questions/245840/wait-for-canvas-to-finish-rendering-before-saving-image
        self._prepareShowOrSave()
        from PyQt5.QtGui import QImage, QPainter, QColor
        from qgis.core import QgsMapRendererCustomPainterJob
        size = self.canvas.size()
        image = QImage(size, QImage.Format_RGB32)
        image.fill(QColor('white'))
        painter = QPainter(image)
        settings = self.canvas.mapSettings()
        job = QgsMapRendererCustomPainterJob(settings, painter)
        job.renderSynchronously()
        painter.end()
        filename = abspath(filename)
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
#        self.app.exit(0)
        image.save(filename)
        #self.app.exec_()
#        self.app.exit(0)
        return self


class MapLayer(object):

    def __init__(self, qgsMapLayer):
        from qgis.core import QgsMapLayer
        assert isinstance(qgsMapLayer, QgsMapLayer)
        self._qgsMapLayer = qgsMapLayer

    def qgsMapLayer(self):
        from qgis.core import QgsMapLayer
        assert isinstance(self._qgsMapLayer, QgsMapLayer)
        return self._qgsMapLayer

