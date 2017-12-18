from os import makedirs, remove
from os.path import dirname, exists, join, basename
import copy
import json
from random import randint
import tempfile
from osgeo import gdal, gdal_array, ogr, osr
import numpy as np
import hubdc.hubdcerrors as errors


def openRaster(filename, eAccess=gdal.GA_ReadOnly):
    if not exists(str(filename)):
        raise errors.FileNotExistError(str(filename))
    gdalDataset = gdal.Open(filename, eAccess)
    if gdalDataset is None:
        raise errors.InvalidGDALDatasetError(filename)
    return Raster(gdalDataset=gdalDataset)


def openVector(filename, layerNameOrIndex=0, update=False):
    if not exists(str(filename)):
        raise errors.FileNotExistError(str(filename))
    if str(layerNameOrIndex).isdigit():
        layerNameOrIndex = int(layerNameOrIndex)
    ogrDataSource = ogr.Open(filename, int(update))
    if ogrDataSource is None:
        raise errors.InvalidOGRDataSourceError(filename)

    return Vector(ogrDataSource=ogrDataSource, nameOrIndex=layerNameOrIndex)


def createRaster(grid, bands=1, gdalType=gdal.GDT_Float32, filename='', format='MEM', options=()):
    driver = Driver(name=format)
    return driver.create(grid, bands=bands, eType=gdalType, filename=filename, options=options)


def createRasterFromArray(grid, array, filename='', format='MEM', creationOptions=()):
    if isinstance(array, np.ndarray):
        if array.ndim == 2:
            array = array[None]
        assert array.ndim == 3
    elif isinstance(array, list):
        assert all([subarray.ndim == 2 for subarray in array])
    else:
        raise TypeError

    bands = len(array)
    dtype = array[0].dtype
    if dtype == np.bool:
        dtype = np.uint8
    eType = gdal_array.NumericTypeCodeToGDALTypeCode(dtype)
    dataset = createRaster(grid=grid, bands=bands, gdalType=eType, filename=filename, format=format,
                           options=creationOptions)
    dataset.writeArray(array=array, grid=grid)

    return dataset


def createVRT(filename, srcDSOrSrcDSTab, **kwargs):
    options = gdal.BuildVRTOptions(**kwargs)
    gdalDataset = gdal.BuildVRT(destName=filename, srcDSOrSrcDSTab=srcDSOrSrcDSTab, options=options)
    return Raster(gdalDataset=gdalDataset)


def buildOverviews(filename, minsize=None, levels=None, resampling='average'):
    assert resampling in ['average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp', 'average_magphase',
                          'mode']
    if levels is None:
        assert minsize is not None
        levels = []
        nextLevel = 2
        size = float(max(openRaster(filename=filename).shape))
        while size > minsize:
            levels.append(nextLevel)
            size /= 2
            nextLevel *= 2

    import subprocess
    subprocess.call(['gdaladdo', '-ro',
                     # '--config', 'COMPRESS_OVERVIEW', 'JPEG',
                     # '--config', 'JPEG_QUALITY_OVERVIEW 25'
                     # '--config', 'INTERLEAVE_OVERVIEW', 'BAND',
                     '-r', 'average',
                     '--config', 'COMPRESS_OVERVIEW', 'LZW',
                     filename, ' '.join(map(str, levels))])


class Driver(object):
    def __init__(self, name):
        self._name = name
        if self.gdalDriver() is None:
            raise errors.InvalidGDALDriverError()

    def gdalDriver(self):
        return gdal.GetDriverByName(self._name)

    def name(self):
        return self._name

    def equal(self, other):
        assert isinstance(other, Driver)
        return self.name() == other.name()

    def create(self, grid, bands=1, eType=gdal.GDT_Float32, filename='', options=()):
        assert isinstance(grid, Grid)
        assert isinstance(filename, str)
        if not self.equal(Driver('MEM')) and not exists(dirname(filename)):
            makedirs(dirname(filename))

        gdalDataset = self.gdalDriver().Create(filename, grid.size().x(), grid.size().y(), bands, eType, options)
        gdalDataset.SetProjection(grid.projection().wkt())
        gdalDataset.SetGeoTransform(grid.makeGeoTransform())
        return Raster(gdalDataset=gdalDataset)


class Extent(object):
    def __init__(self, xmin, xmax, ymin, ymax):
        self._xmin = float(xmin)
        self._xmax = float(xmax)
        self._ymin = float(ymin)
        self._ymax = float(ymax)
        assert self._xmax > self._xmin
        assert self._ymax > self._ymin

    def __repr__(self):
        return '{cls}(xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax})'.format(
            cls=self.__class__.__name__,
            xmin=repr(self.xmin()),
            xmax=repr(self.xmax()),
            ymin=repr(self.ymin()),
            ymax=repr(self.ymax()))

    @staticmethod
    def fromGeometry(geometry):
        assert isinstance(geometry, Geometry)
        xmin, xmax, ymin, ymax  = geometry.ogr().GetEnvelope()
        return Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    def xmin(self):
        return self._xmin

    def xmax(self):
        return self._xmax

    def ymin(self):
        return self._ymin

    def ymax(self):
        return self._ymax

    def geometry(self):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in zip([self.xmin(), self.xmax(), self.xmax(), self.xmin(), self.xmin()],
                        [self.ymax(), self.ymax(), self.ymin(), self.ymin(), self.ymax()]):
            ring.AddPoint(x, y)
        geometry = ogr.Geometry(ogr.wkbPolygon)
        geometry.AddGeometry(ring)
        return Geometry(wkt=geometry.ExportToWkt())

    def upperLeft(self):
        return Point(x=self.xmin(), y=self.ymax())

    def upperRight(self):
        return Point(x=self.xmax(), y=self.ymax())

    def lowerRight(self):
        return Point(x=self.xmax(), y=self.ymin())

    def lowerLeft(self):
        return Point(x=self.xmin(), y=self.ymin())

    def corners(self):
        return (self.upperLeft(), self.upperRight(), self.lowerRight(), self.lowerLeft())

    def reproject(self, sourceProjection, targetProjection):
        geometry = self.geometry().reproject(sourceProjection=sourceProjection, targetProjection=targetProjection)
        return Extent.fromGeometry(geometry=geometry)

    def intersects(self, other):
        assert isinstance(other, Extent)
        return self.geometry().intersects(other.geometry())

    def intersection(self, other):
        """
        Returns a new instance which is the intersection of self and other.
        """

        assert isinstance(other, Extent)
        xmin = max(self.xmin(), other.xmin())
        xmax = min(self.xmax(), other.xmax())
        ymin = max(self.ymin(), other.ymin())
        ymax = min(self.ymax(), other.ymax())

        if xmin >= xmax or ymin >= ymax:
            raise Exception('Extents do not intersect')

        return Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    def union(self, other):
        '''Returns a new instance which is the union of self with other.'''

        xmin = min(self.xmin(), other.xmin())
        xmax = max(self.xmax(), other.xmax())
        ymin = min(self.ymin(), other.ymin())
        ymax = max(self.ymax(), other.ymax())

        return Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    def size(self, resolution):
        '''Returns the grid size that corresponds to the given resolution.'''

        assert isinstance(resolution, Resolution)
        return Size(x=int(round(float(self.xmax() - self.xmin()) / resolution.x())),
                    y=int(round(float(self.ymax() - self.ymin()) / resolution.y())))


class SpatialExtent(Extent):
    def __init__(self, xmin, xmax, ymin, ymax, projection):
        assert isinstance(projection, Projection)
        Extent.__init__(self, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        self._projection = projection

    def __repr__(self):
        return '{cls}(extent={extent}, projection={projection})'.format(
            cls=self.__class__.__name__,
            extent=Extent.__repr__(self).replace('SpatialExtent', 'Extent'),
            projection=repr(self.projection()))

    @staticmethod
    def fromExtent(extent, projection):
        assert isinstance(extent, Extent)
        return SpatialExtent(xmin=extent.xmin(), xmax=extent.xmax(), ymin=extent.ymin(), ymax=extent.ymax(),
                             projection=projection)

    @staticmethod
    def fromGeometry(geometry):
        assert isinstance(geometry, SpatialGeometry)
        extent = Extent.fromGeometry(geometry=geometry)
        return SpatialExtent.fromExtent(extent=extent, projection=geometry.projection())


    def projection(self):
        return self._projection

    def upperLeft(self):
        return SpatialPoint(x=self.xmin(), y=self.ymax(), projection=self.projection())

    def upperRight(self):
        return SpatialPoint(x=self.xmax(), y=self.ymax(), projection=self.projection())

    def lowerRight(self):
        return SpatialPoint(x=self.xmax(), y=self.ymin(), projection=self.projection())

    def lowerLeft(self):
        return SpatialPoint(x=self.xmin(), y=self.ymin(), projection=self.projection())

    def reproject(self, targetProjection, sourceProjection=None):
        assert isinstance(targetProjection, Projection)
        if sourceProjection is not None:
            assert self.projection().equal(other=sourceProjection)
        extent = Extent.reproject(self, sourceProjection=self.projection(), targetProjection=targetProjection)
        return SpatialExtent.fromExtent(extent=extent, projection=targetProjection)

    def intersects(self, other):
        '''Returns wether self and other intersect.'''
        assert isinstance(other, SpatialExtent)
        assert self.projection().equal(other=other.projection())
        return SpatialExtent.fromExtent(extent=Extent.intersects(self, other=other), projection=self.projection())

    def intersection(self, other):
        '''Returns the intersection of self and other.'''
        assert isinstance(other, SpatialExtent)
        assert self.projection().equal(other=other.projection())
        return SpatialExtent.fromExtent(extent=Extent.intersection(self, other=other), projection=self.projection())

    def union(self, other):
        '''Returns the union of self and other.'''
        assert isinstance(other, SpatialExtent)
        assert self.projection().equal(other=other.projection())
        return SpatialExtent.fromExtent(extent=Extent.union(self, other=other), projection=self.projection())

    def geometry(self):
        geometry = Extent.geometry(self)
        return SpatialGeometry(wkt=geometry.wkt(), projection=self.projection())


class Resolution(object):
    def __init__(self, x, y):
        self._x = float(x)
        self._y = float(y)
        assert self._x > 0
        assert self._y > 0

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    def x(self):
        return self._x

    def y(self):
        return self._y

    def equal(self, other):
        assert isinstance(other, Resolution)
        return self.x() == other.x() and self.y() == other.y()


class Projection(object):
    def __init__(self, wkt):
        self._wkt = str(wkt)

    def __repr__(self):
        wkt = self.wkt().replace(' ', '').replace('\n', ' ')
        return '{cls}(wkt={wkt})'.format(cls=self.__class__.__name__, wkt=wkt)

    def wkt(self):
        return self._wkt

    @staticmethod
    def fromEPSG(epsg):
        projection = osr.SpatialReference()
        projection.ImportFromEPSG(int(epsg))
        return Projection(wkt=projection)

    @staticmethod
    def WGS84PseudoMercator():
        return Projection.fromEPSG(epsg=3857)

    @staticmethod
    def WGS84():
        return Projection.fromEPSG(epsg=4326)

    @classmethod
    def UTM(cls, zone, north=True):
        assert zone >= 1 and zone <= 60
        if north:
            return cls.fromEPSG(epsg=32600 + zone)
        else:
            return cls.fromEPSG(epsg=32722 + zone)

    def osrSpatialReference(self):
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.wkt())
        return srs

    def equal(self, other):
        '''
        Returns True if the projection of self is the same as the projection of other
        '''

        assert isinstance(other, Projection)
        return bool(self.osrSpatialReference().IsSame(other.osrSpatialReference()))


class Pixel(object):
    '''Pixel location.'''

    def __init__(self, x, y):
        self._x = int(x)
        self._y = int(y)

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    def x(self):
        return self._x

    def y(self):
        return self._y

class Geometry(object):
    '''Geometry'''

    def __init__(self, wkt):
        assert isinstance(wkt, str)
        self._wkt = wkt

    def wkt(self):
        return self._wkt

    def ogr(self):
        geometry = ogr.CreateGeometryFromWkt(self._wkt)
        return geometry

    def reproject(self, sourceProjection, targetProjection):
        transformation = osr.CoordinateTransformation(sourceProjection.osrSpatialReference(),
                                                      targetProjection.osrSpatialReference())

        ogrGeometry = self.ogr()
        ogrGeometry.Transform(transformation)
        return Geometry(wkt=ogrGeometry.ExportToWkt())

    def intersects(self, other):
        assert isinstance(other, Geometry)
        return self.ogr().Intersects(other.ogr())

    def intersection(self, other):
        assert isinstance(other, Geometry)
        ogrGeometry = self.ogr().Intersection(other.ogr())
        assert ogrGeometry is not None
        return Geometry(wkt=ogrGeometry.ExportToWkt())

class SpatialGeometry(Geometry):
    def __init__(self, wkt, projection):
        assert isinstance(projection, Projection)
        Geometry.__init__(self, wkt=wkt)
        self._projection = projection

    @staticmethod
    def fromVector(filename, layerNameOrIndex=0):
        vector = openVector(filename=filename, layerNameOrIndex=layerNameOrIndex)
        layer = vector.ogrLayer()
        ogrGeometry = ogr.Geometry(ogr.wkbMultiPolygon)
        for feature in layer:
            ogrGeometry.AddGeometry(feature.GetGeometryRef())
        ogrGeometry = ogrGeometry.UnionCascaded()

        return SpatialGeometry(wkt=ogrGeometry.ExportToWkt(), projection=vector.projection())

    def projection(self):
        return self._projection

    def reproject(self, targetProjection, sourceProjection=None):
        if sourceProjection is not None:
            assert self.projection().equal(other=sourceProjection)
        geometry = Geometry.reproject(self, sourceProjection=self.projection(), targetProjection=targetProjection)
        return SpatialGeometry(wkt=geometry.wkt(), projection=targetProjection)

    def intersects(self, other):
        assert isinstance(other, SpatialGeometry)
        assert self.projection().equal(other.projection())
        return Geometry.intersects(self, other=other)

    def intersection(self, other):
        assert isinstance(other, SpatialGeometry)
        assert self.projection().equal(other=other.projection())
        geometry = Geometry.intersection(self, other=other)
        return SpatialGeometry(wkt=geometry.wkt(), projection=self.projection())



class Point(object):
    '''Map location.'''

    def __init__(self, x, y):
        assert isinstance(x, (float, int))
        assert isinstance(y, (float, int))
        self._x = float(x)
        self._y = float(y)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def wkb(self):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(self.x(), self.y())
        return point

    def wkt(self):
        return self.wkb().ExportToWkt()

    def reproject(self, sourceProjection, targetProjection):
        assert isinstance(sourceProjection, Projection)
        assert isinstance(targetProjection, Projection)
        transformation = osr.CoordinateTransformation(sourceProjection.osrSpatialReference(),
                                                      targetProjection.osrSpatialReference())
        x, y, z = transformation.TransformPoint(self.x(), self.y())
        return Point(x=x, y=y)


class SpatialPoint(Point):
    '''Map location with associated projection.'''

    def __init__(self, x, y, projection):
        assert isinstance(projection, Projection)
        Point.__init__(self, x=x, y=y)
        self._projection = projection

    def projection(self):
        return self._projection

    def reproject(self, targetProjection, sourceProjection=None):
        assert isinstance(targetProjection, Projection)
        if sourceProjection is not None:
            assert self.projection().equal(other=sourceProjection)
        point = Point.reproject(self, sourceProjection=self.projection(), targetProjection=targetProjection)
        return SpatialPoint(x=point.x(), y=point.y(), projection=targetProjection)

    def withinExtent(self, extent):
        assert isinstance(extent, SpatialExtent)
        p = self.reproject(targetProjection=extent.projection())
        return p.wkb().Within(extent.wkb())


'''class Polygon(object):
    def __init__(self, points):
        for p in points:
            assert isinstance(p, Point)

        self._points = tuple(points)

    @staticmethod
    def fromGeometry(geometry):
        assert isinstance(geometry, Geometry)
        points = [Point(x=x, y=y) for x, y, z in json.loads(geometry.ogr().ExportToJson())['coordinates'][0]]
        return Polygon(points=points)

    def points(self):
        return self._points

    def reproject(self, sourceProjection, targetProjection):

        points = [p.reproject(sourceProjection=sourceProjection, targetProjection=targetProjection)
                  for p in self.points()]
        return Polygon(points=points)

    def geometry(self):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for p in self.points() + (self.points()[0],):
            ring.AddPoint(p.x(), p.y())
        geometry = ogr.Geometry(ogr.wkbPolygon)
        geometry.AddGeometry(ring)
        return Geometry(wkt=geometry.ExportToWkt())

    def intersects(self, other):
        assert isinstance(other, Polygon)
        return self.geometry().Intersects(other.wkb())

    def intersection(self, other):
        assert isinstance(other, Polygon)
        geometry = self.geometry().intersection(other.geometry())
        return Polygon.fromGeometry(geometry=geometry)


class SpatialPolygon(Polygon):
    def __init__(self, points, projection):
        assert isinstance(projection, Projection)
        for p in points:
            if isinstance(p, SpatialPoint):
                if not projection.equal(other=p.projection()):
                    raise Exception('mismatching projections')
        Polygon.__init__(self, points=points)
        self._projection = projection

    def projection(self):
        return self._projection

    def reproject(self, targetProjection, sourceProjection=None):
        if sourceProjection is not None:
            assert self.projection() == sourceProjection
        polygon = Polygon.reproject(self, sourceProjection=self.projection(), targetProjection=targetProjection)
        return SpatialPolygon(points=polygon.points(), projection=targetProjection)

    def intersects(self, other):
        assert isinstance(other, Polygon)
        return self.geometry().intersects(other.geometry())

    def intersection(self, other):
        assert isinstance(other, SpatialPolygon)
        assert self.projection().equal(other=other.projection())
        polygon = Polygon.intersection(self, other=other)
        return SpatialPolygon(points=polygon.points(), projection=self.projection())'''


class Size(object):
    def __init__(self, x, y):
        self._x = int(x)
        self._y = int(y)
        assert self._x > 0
        assert self._y > 0

    def __repr__(self):
        return '{cls}(x={x}, y={y})'.format(cls=self.__class__.__name__, x=repr(self.x()), y=repr(self.y()))

    def x(self):
        return self._x

    def y(self):
        return self._y

    def shape(self):
        return self.y(), self.x()


class Grid(object):
    def __init__(self, extent, resolution, projection=None):
        if isinstance(extent, SpatialExtent):
            projection = extent.projection()
        assert isinstance(extent, Extent)
        assert isinstance(resolution, Resolution)
        assert isinstance(projection, Projection)
        self._resolution = resolution

        size = extent.size(resolution=resolution)

        self._extent = Extent(xmin=extent.xmin(),
                              xmax=extent.xmin() + size.x() * resolution.x(),
                              ymin=extent.ymin(),
                              ymax=extent.ymin() + size.y() * resolution.y())
        self._projection = projection

    def __repr__(self):
        return '{cls}(extent={extent}, resolution={resolution}, projection={projection}'.format(
            cls=self.__class__.__name__,
            extent=repr(self.extent()),
            resolution=repr(self.resolution()),
            projection=repr(self.projection()))

    def extent(self):
        return self._extent

    def resolution(self):
        return self._resolution

    def projection(self):
        return self._projection

    def spatialExtent(self):
        return SpatialExtent.fromExtent(extent=self.extent(), projection=self.projection())

    def size(self):
        return self.extent().size(resolution=self.resolution())

    def shape(self):
        return self.size().shape()

    def xMapCoordinates(self):
        return [self.extent().xmin() + (x + 0.5) * self.resolution().x() for x in range(self.size().x())]

    def yMapCoordinates(self):
        return [self.extent().ymax() - (y + 0.5) * self.resolution().y() for y in range(self.size().y())]

    def xMapCoordinatesArray(self):
        return np.asarray(self.xMapCoordinates()).reshape(1, -1) * np.ones(shape=self.shape())

    def yMapCoordinatesArray(self):
        return np.asarray(self.yMapCoordinates()).reshape(-1, 1) * np.ones(shape=self.shape())

    def xPixelCoordinates(self, offset=0):
        return [x + offset for x in range(self.size().x())]

    def yPixelCoordinates(self, offset=0):
        return [y + offset for y in range(self.size().y())]

    def xPixelCoordinatesArray(self, offset=0):
        return np.int32(np.asarray(self.xPixelCoordinates(offset=offset)).reshape(1, -1) * np.ones(shape=self.shape()))

    def yPixelCoordinatesArray(self, offset=0):
        return np.int32(np.asarray(self.yPixelCoordinates(offset=offset)).reshape(-1, 1) * np.ones(shape=self.shape()))


    def makeGeoTransform(self):
        '''Returns a GDAL geotransform tuple from bounds and resolution'''

        geotransform = (
            self.extent().xmin(), self.resolution().x(), 0.0, self.extent().ymax(), 0.0, -self.resolution().y())
        return geotransform

    def equal(self, other):
        assert isinstance(other, Grid)
        return (self.projection().equal(other=other.projection()) and
                self.extent().upperLeft() == other.extent().upperLeft() and
                self.size().shape() == other.size().shape())

    def reproject(self, other):
        assert isinstance(other, Grid)
        extent = self.extent().reproject(sourceProjection=self.projection(), targetProjection=other.projection())
        grid = Grid(extent=extent, resolution=other.resolution(), projection=other.projection())
        grid = grid.anchor(point=Point(x=other.extent().xmin(), y=other.extent().ymin()))
        return grid

    def mapBuffer(self, buffer, north=True, west=True, south=True, east=True):
        assert isinstance(buffer, float)
        assert 0  # andern
        extent = copy.deepcopy(self.extent())
        # if west: extent.xmin() -= buffer
        # if east: extent.xmax() += buffer
        # if south: extent.ymin() -= buffer
        # if north: extent.ymax() += buffer
        return Grid(extent=extent, resolution=self.resolution(), projection=self.projection())

    def pixelBuffer(self, buffer, left=True, right=True, upper=True, lower=True):
        assert isinstance(buffer, int)
        extent = Extent(xmin=self.extent().xmin() - buffer * self.resolution().x() if left else 0,
                        xmax=self.extent().xmax() + buffer * self.resolution().x() if right else 0,
                        ymin=self.extent().ymin() - buffer * self.resolution().y() if lower else 0,
                        ymax=self.extent().ymax() + buffer * self.resolution().y() if upper else 0)
        return Grid(extent=extent, resolution=self.resolution(), projection=self.projection())

    def anchor(self, point):
        assert isinstance(point, Point)

        xminOff = (self.extent().xmin() - point.x()) % self.resolution().x()
        yminOff = (self.extent().ymin() - point.y()) % self.resolution().y()
        xmaxOff = (self.extent().xmax() - point.x()) % self.resolution().x()
        ymaxOff = (self.extent().ymax() - point.y()) % self.resolution().y()

        # round snapping offset
        if xminOff > self.resolution().x() / 2.: xminOff -= self.resolution().x()
        if yminOff > self.resolution().y() / 2.: yminOff -= self.resolution().y()
        if xmaxOff > self.resolution().x() / 2.: xmaxOff -= self.resolution().x()
        if ymaxOff > self.resolution().y() / 2.: ymaxOff -= self.resolution().y()

        anchoredExtent = Extent(xmin=self.extent().xmin() - xminOff,
                                ymin=self.extent().ymin() - yminOff,
                                xmax=self.extent().xmax() - xmaxOff,
                                ymax=self.extent().ymax() - ymaxOff)

        return Grid(extent=anchoredExtent, resolution=self.resolution(), projection=self.projection())

    def subset(self, offset, size, trim=False):
        assert isinstance(offset, Pixel)
        assert isinstance(size, Size)
        if trim:
            offset = Pixel(x=max(offset.x(), 0), y=max(offset.y(), 0))
            size = Size(x=min(size.x(), self.size().x() - offset.x()),
                        y=min(size.y(), self.size().y() - offset.y()))

        xmin = self.extent().xmin() + offset.x() * self.resolution().x()
        xmax = xmin + size.x() * self.resolution().x()
        ymax = self.extent().ymax() - offset.y() * self.resolution().y()
        ymin = ymax - size.y() * self.resolution().y()

        return Grid(projection=self.projection(),
                    resolution=self.resolution(),
                    extent=Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax))

    def subgrids(self, size):
        assert isinstance(size, Size)
        size = Size(x=min(size.x(), self.size().x()), y=min(size.y(), self.size().y()))
        result = list()

        offset = Pixel(x=0, y=0)
        i = iy = 0
        while offset.y() < self.size().y():
            offset = Pixel(x=0, y=offset.y())
            ix = 0
            while offset.x() < self.size().x():
                subgrid = self.subset(offset=offset, size=size)
                subgridTrimmed = Grid(extent=subgrid.extent().intersection(self.extent()),
                                      resolution=self.resolution(), projection=self.projection())
                result.append((subgridTrimmed, i, iy, ix))
                offset = Pixel(x=offset.x() + size.x(), y=offset.y())
                ix += 1
                i += 1
            offset = Pixel(x=offset.x(), y=offset.y() + size.y())
            iy += 1
        return result


class Raster(object):
    def __init__(self, gdalDataset):
        assert isinstance(gdalDataset, gdal.Dataset)
        self._gdalDataset = gdalDataset

    def projection(self):
        return Projection(wkt=self._gdalDataset.GetProjection())

    def resolution(self):
        gt = self._gdalDataset.GetGeoTransform()
        return Resolution(x=gt[1], y=abs(gt[5]))

    def extent(self):
        gt = self._gdalDataset.GetGeoTransform()
        xSize = self._gdalDataset.RasterXSize
        ySize = self._gdalDataset.RasterYSize
        return Extent(xmin=gt[0],
                      xmax=gt[0] + xSize * self.resolution().x(),
                      ymin=gt[3] - ySize * self.resolution().y(),
                      ymax=gt[3])

    def grid(self):
        return Grid(extent=self.extent(), resolution=self.resolution(), projection=self.projection())

    def spatialExtent(self):
        return self.grid().spatialExtent()

    def bands(self):
        for i in range(self.zsize()):
            yield self.band(i)

    def format(self):
        return self._gdalDataset.GetDriver().ShortName

    def readAsArray(self, grid=None, resample_alg=gdal.GRIORA_NearestNeighbour):
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
                                                  resample_alg=resample_alg)

        if array.ndim == 2:
            array = array[None]

        return array

    def writeArray(self, array, grid=None):
        assert len(array) == self.zsize()

        for band, bandArray in zip(self.bands(), array):
            band.writeArray(bandArray, grid=grid)

    def flushCache(self):
        self._gdalDataset.FlushCache()

    def close(self):
        self._gdalDataset = None

    def band(self, index):
        return Band(dataset=self, index=index)

    def setNoDataValues(self, values):
        for i, band in enumerate(self.bands()):
            band.setNoDataValue(values[i])

    def noDataValues(self, default=None):
        return [band.noDataValue(default=default) for band in self.bands()]

    def setNoDataValue(self, value):
        self.setNoDataValues(values=[value] * self.zsize())

    def noDataValue(self, default=None):
        noDataValues = self.noDataValues()
        if len(set(noDataValues)) != 1:
            raise Exception('there are multiple no data values, use getNoDataValues() instead')
        noDataValue = noDataValues[0]
        if noDataValue is None:
            noDataValue = default
        return noDataValue

    def setDescription(self, value):
        self._gdalDataset.SetDescription(value)

    def description(self):
        return self._gdalDataset.GetDescription()

    def metadataDomainList(self):
        domains = self._gdalDataset.GetMetadataDomainList()
        return domains if domains is not None else []

    def setMetadataItem(self, key, value, domain=''):
        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = _GDALStringFormatter.valueToGDALString(value)
        self._gdalDataset.SetMetadataItem(key, gdalString, domain)

    def metadataItem(self, key, domain='', dtype=str):
        key = key.replace(' ', '_')
        gdalString = self._gdalDataset.GetMetadataItem(key, domain)
        if gdalString is None:
            return None
        return _GDALStringFormatter.gdalStringToValue(gdalString, dtype=dtype)

    def metadataDict(self):
        metadataDict = dict()
        for domain in self.metadataDomainList():
            metadataDict[domain] = dict()
            for key, value in self.metadataDomain(domain=domain).items():
                metadataDict[domain][key] = self.metadataItem(key=key, domain=domain)
        return metadataDict

    def setMetadataDict(self, metadataDict):
        assert isinstance(metadataDict, dict)
        for domain in metadataDict:
            for key, value in metadataDict[domain].items():
                self.setMetadataItem(key=key, value=value, domain=domain)

    def metadataDomain(self, domain):
        domainDict = self._gdalDataset.GetMetadata(domain)
        assert isinstance(domainDict, dict)
        return domainDict

    def copyMetadata(self, other):
        assert isinstance(other, Raster)

        for domain in other.metadataDomainList():
            self._gdalDataset.SetMetadata(other.gdalDataset.GetMetadata(domain), domain)

        for band, otherBand in zip(self, other):
            for domain in otherBand.metadataDomainList():
                band.gdalBand.SetMetadata(otherBand.gdalBand.GetMetadata(domain), domain)

    def setAcquisitionTime(self, value):
        assert 0  # todo check if there is a GDAL metadata for this
        self.setMetadataItem('acquisition time', value, 'ENVI')

    def acquisitionTime(self, value):
        return self.metadataItem('acquisition time', value, 'ENVI')

    def writeENVIHeader(self):

        filename = self._gdalDataset.GetFileList()[0]
        format = self.format()
        if format == 'ENVI':
            fileType = self.metadataItem(key='file type', domain='ENVI')
            hdrfilename = self._gdalDataset.GetFileList()[-1]
        elif format == 'GTiff':
            fileType = 'TIFF'
            hdrfilename = filename + '.hdr'
        else:
            return

        envi = self.metadataDomain(domain='ENVI')

        envi['file type'] = fileType
        envi['samples'] = self._gdalDataset.RasterXSize
        envi['lines'] = self._gdalDataset.RasterYSize
        envi['bands'] = self._gdalDataset.RasterCount

        keys = ['description', 'samples', 'lines', 'bands', 'header_offset', 'file_type', 'data_type',
                'interleave', 'data_ignore_value',
                'sensor_type', 'byte_order', 'map_info', 'projection_info', 'coordinate_system_string',
                'acquisition_time',
                'wavelength_units', 'wavelength', 'band_names']

        from collections import OrderedDict
        orderedEnvi = OrderedDict()
        for key_ in keys:
            key = key_.replace('_', ' ')
            orderedEnvi[key_] = envi.pop(key_, envi.pop(key, None))

        # close dataset
        self._gdalDataset = None

        # read map info and coordinate system string written by GDAL
        if format == 'ENVI':
            with open(hdrfilename, 'r') as f:
                for line in f:
                    for key in ['map info', 'coordinate system string']:
                        if line.startswith(key):
                            orderedEnvi[key] = line.split('=')[-1].strip()

        # create ENVI header
        with open(hdrfilename, 'w') as f:
            f.write('ENVI\n')
            for key, value in zip(orderedEnvi.keys() + envi.keys(), orderedEnvi.values() + envi.values()):
                if value is not None:
                    f.write('{key} = {value}\n'.format(key=key.replace('_', ' '), value=value))

    def warp(self, grid, filename='', format='MEM', creationOptions=(), **kwargs):

        assert isinstance(grid, Grid)

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        outputBounds = (grid.extent().xmin(), grid.extent().ymin(), grid.extent().xmax(), grid.extent().ymax())
        warpOptions = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=grid.resolution().x(),
                                       yRes=grid.resolution().y(), dstSRS=grid.projection().wkt(),
                                       creationOptions=creationOptions, **kwargs)
        gdalDataset = gdal.Warp(destNameOrDestDS=filename, srcDSOrSrcDSTab=self._gdalDataset, options=warpOptions)

        return Raster(gdalDataset=gdalDataset)

    def warpOptions(self, grid, format, creationOptions, **kwargs):
        assert isinstance(grid, Grid)

        xRes, yRes, dstSRS = grid.resolution().x(), grid.resolution().y(), grid.projection().wkt()
        outputBounds = tuple(getattr(grid, key) for key in ('xmin', 'ymin', 'xmax', 'ymax'))

        options = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS,
                                   creationOptions=creationOptions, **kwargs)

        return options

    def translate(self, grid=None, filename='', format='MEM', creationOptions=(), **kwargs):

        if grid is None:
            grid = self.grid()

        assert isinstance(grid, Grid)
        assert self.grid().projection().equal(other=grid.projection())

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        ul = grid.extent().upperLeft()
        lr = grid.extent().lowerRight()
        xRes, yRes = grid.resolution().x(), grid.resolution().y()
        #            getattr(grid, key) for key in ('xmin', 'ymax', 'xmax', 'ymin', 'xRes', 'yRes'))

        # Note that given a projWin, it is not garantied that gdal.Translate will produce a dataset
        # with the same pixel extent as gdal.Warp!
        # The problem seams to only appear if the target resolution is smaller than the source resolution.

        if self.grid().resolution().x() > xRes or self.grid().resolution().y() > yRes:
            if format != 'MEM':
                raise Exception('spatial resolution oversampling is only supported for MEM format')

            # read one extra source column and line
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     projWin=[ul.x(), ul.y(), lr.x() + self.grid().resolution().x(),
                                                              lr.y() - self.grid().resolution().y()],
                                                     xRes=xRes, yRes=yRes, **kwargs)
            tmpGdalDataset = gdal.Translate(destName='', srcDS=self._gdalDataset, options=translateOptions)

            # subset to the exact target grid
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     srcWin=[0, 0, grid.size().x(), grid.size().y()])
            gdalDataset = gdal.Translate(destName='', srcDS=tmpGdalDataset, options=translateOptions)

        else:
            translateOptions = gdal.TranslateOptions(format=format, projWin=[ul.x(), ul.y(), lr.x(), lr.y()], xRes=xRes,
                                                     yRes=yRes,
                                                     creationOptions=creationOptions, **kwargs)
            gdalDataset = gdal.Translate(destName=filename, srcDS=self._gdalDataset, options=translateOptions)

        return Raster(gdalDataset=gdalDataset)

    def array(self, grid=None, resampleAlg=gdal.GRA_NearestNeighbour, noData=None, errorThreshold=0.,
              warpMemoryLimit=100 * 2 ** 20, multithread=False):
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
            grid = self.grid()

        if self.grid().projection().equal(other=grid.projection()):
            datasetResampled = self.translate(grid=grid, filename='', format='MEM', resampleAlg=resampleAlg,
                                              noData=noData)
        else:
            datasetResampled = self.warp(grid=grid, filename='', format='MEM', resampleAlg=resampleAlg,
                                         errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit,
                                         multithread=multithread, srcNodata=noData)

        array = datasetResampled.readAsArray()
        datasetResampled.close()
        return array

    def xsize(self):
        return self._gdalDataset.RasterXSize

    def ysize(self):
        return self._gdalDataset.RasterYSize

    def zsize(self):
        return self._gdalDataset.RasterCount

    def shape(self):
        return self.zsize(), self.ysize(), self.xsize()

    def dtype(self):
        return self._gdalDataset.GetRasterBand(1).ReadAsArray(win_xsize=1, win_ysize=1).dtype


class _GDALStringFormatter(object):
    @classmethod
    def valueToGDALString(cls, value):
        if isinstance(value, list):
            return cls._listToGDALString(value)
        else:
            return str(value)

    @classmethod
    def gdalStringToValue(cls, gdalString, dtype):
        gdalString.strip()
        if gdalString.startswith('{') and gdalString.endswith('}'):
            value = cls._gdalStringToList(gdalString, dtype)
        else:
            value = dtype(gdalString)
        return value

    @classmethod
    def _listToGDALString(cls, values):
        return '{' + ','.join([str(v) for v in values]) + '}'

    @classmethod
    def _gdalStringToList(cls, gdalString, type):
        values = [type(v) for v in gdalString[1:-1].split(',')]
        return values


class Band():
    def __init__(self, dataset, index):
        assert isinstance(dataset, Raster)
        if index < 0 or index > dataset.zsize() - 1:
            raise IndexError()

        self._dataset = dataset
        self._gdalBand = dataset._gdalDataset.GetRasterBand(index + 1)

    def readAsArray(self, grid=None, resample_alg=gdal.GRA_NearestNeighbour):

        if grid is None:
            # array = self.gdalBand.ReadAsArray(resample_alg=resample_alg)
            from osgeo import gdal_array
            array = gdal_array.BandReadAsArray(self._gdalBand, resample_alg=gdal.GRIORA_NearestNeighbour)
        else:
            assert isinstance(grid, Grid)
            resolution = self._dataset.grid().resolution()
            extent = self._dataset.grid().extent()
            xoff = round((grid.extent().xmin() - extent.xmin()) / resolution.x(), 0)
            yoff = round((extent.ymax() - grid.extent().ymax()) / resolution.y(), 0)
            xsize = round((grid.extent().xmax() - grid.extent().xmin()) / resolution.x(), 0)
            ysize = round((grid.extent().ymax() - grid.extent().ymin()) / resolution.y(), 0)
            buf_ysize, buf_xsize = grid.size().shape()
            array = self._gdalBand.ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize,
                                               buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                               resample_alg=resample_alg)
            if array is None or xoff < 0 or yoff < 0:  # ReadAsArray seams to accept xy offets of -1, which makes no sense, so we manually raise an error
                raise errors.AccessGridOutOfRangeError()

        assert isinstance(array, np.ndarray)
        return array

    def writeArray(self, array, grid=None):

        assert isinstance(array, np.ndarray)
        if array.ndim == 3:
            assert len(array) == 1
            array = array[0]

        if grid is None:
            grid = self._dataset.grid()

        assert isinstance(grid, Grid)
        if array.shape != grid.shape():
            raise errors.ArrayShapeMismatchError()

        assert self._dataset.grid().projection().equal(other=grid.projection())

        xoff = int(
            round((grid.extent().xmin() - self._dataset.grid().extent().xmin()) / self._dataset.grid().resolution().x(),
                  0))
        yoff = int(
            round((self._dataset.grid().extent().ymax() - grid.extent().ymax()) / self._dataset.grid().resolution().y(),
                  0))
        try:
            self._gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)
        except ValueError:
            raise errors.AccessGridOutOfRangeError

    def setMetadataItem(self, key, value, domain=''):
        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = _GDALStringFormatter.valueToGDALString(value)
        self._gdalBand.SetMetadataItem(key, gdalString, domain)

    def metadataItem(self, key, domain='', dtype=str):
        key = key.replace(' ', '_')
        gdalString = self._gdalBand.GetMetadataItem(key, domain)
        if gdalString is None:
            return None
        return _GDALStringFormatter.gdalStringToValue(gdalString, dtype=dtype)

    def copyMetadata(self, other):
        assert isinstance(other, Band)

        for domain in other.metadataDomainList():
            self._gdalBand.SetMetadata(other._gdalBand.GetMetadata(domain), domain)

    def setNoDataValue(self, value):
        if value is not None:
            self._gdalBand.SetNoDataValue(float(value))

    def noDataValue(self, default=None):
        noDataValue = self._gdalBand.GetNoDataValue()
        if noDataValue is None:
            noDataValue = default
        return noDataValue

    def setDescription(self, value):
        self._gdalBand.SetDescription(value)

    def description(self):
        return self._gdalBand.GetDescription()

    def metadataDomainList(self):
        domains = self._gdalBand.GetMetadataDomainList()
        return domains if domains is not None else []

    def fill(self, value):
        self._gdalBand.Fill(value)


class Vector(object):
    def __init__(self, ogrDataSource, nameOrIndex=0):
        assert isinstance(ogrDataSource, ogr.DataSource), str(ogrDataSource)
        self._ogrDataSource = ogrDataSource
        self._ogrLayer = ogrDataSource.GetLayer(iLayer=nameOrIndex)
        self._filename = self._ogrDataSource.GetDescription()

    def filename(self):
        return self._filename

    def ogrDataSource(self):
        return self._ogrDataSource

    def ogrLayer(self):
        assert isinstance(self._ogrLayer, ogr.Layer)
        return self._ogrLayer

    def close(self):
        self._ogrLayer = None
        self._ogrDataSource = None

    def projection(self):
        return Projection(wkt=self._ogrLayer.GetSpatialRef())

    def grid(self, xRes, yRes):
        xmin, xmax, ymin, ymax = self._ogrLayer.GetExtent()
        return Grid(extent=Extent(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax), resolution=Resolution(x=xRes, y=yRes),
                    projection=self.projection())

    def rasterize(self, grid, eType=gdal.GDT_Float32,
                  initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
                  filter=None, noDataValue=None,
                  filename='', format='MEM', creationOptions=()):

        assert isinstance(grid, Grid)

        if not self.projection().equal(other=grid.projection()):
            layer = self
        else:
            layer = self.reprojectOnTheFly(projection=grid.projection())

        layer._ogrLayer.SetAttributeFilter(filter)

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        driver = gdal.GetDriverByName(format)
        gdalDataset = driver.Create(filename, grid.size().x(), grid.size().y(), 1, eType, creationOptions)
        gdalDataset.SetProjection(grid.projection().wkt())
        gdalDataset.SetGeoTransform(grid.makeGeoTransform())
        dataset = Raster(gdalDataset=gdalDataset)
        if noDataValue is not None:
            dataset.setNoDataValue(noDataValue)
        dataset.band(0).fill(value=initValue)

        options = list()
        # special options controlling rasterization:
        #    "ATTRIBUTE": Identifies an attribute field on the features to be used for a burn in value. The value will be burned into all output bands. If specified, padfLayerBurnValues will not be used and can be a NULL pointer.
        #    "CHUNKYSIZE": The height in lines of the chunk to operate on. The larger the chunk size the less times we need to make a pass through all the shapes. If it is not set or set to zero the default chunk size will be used. Default size will be estimated based on the GDAL cache buffer size using formula: cache_size_bytes/scanline_size_bytes, so the chunk will not exceed the cache.
        #    "ALL_TOUCHED": May be set to TRUE to set all pixels touched by the line or polygons, not just those whose center is within the polygon or that are selected by brezenhams line algorithm. Defaults to FALSE.
        #    "BURN_VALUE_FROM": May be set to "Z" to use the Z values of the geometries. The value from padfLayerBurnValues or the attribute field value is added to this before burning. In default case dfBurnValue is burned as it is. This is implemented properly only for points and lines for now. Polygons will be burned using the Z value from the first point. The M value may be supported in the future.
        #    "MERGE_ALG": May be REPLACE (the default) or ADD. REPLACE results in overwriting of value, while ADD adds the new value to the existing raster, suitable for heatmaps for instance.
        if allTouched:
            options.append('ALL_TOUCHED=TRUE')
        if burnAttribute:
            options.append('ATTRIBUTE=' + burnAttribute)

        gdal.RasterizeLayer(dataset._gdalDataset, [1], layer._ogrLayer, burn_values=[burnValue], options=options)

        return dataset

    def reprojectOnTheFly(self, projection):
        # need to create a temp VRT
        vrtDefinition = ['<OGRVRTDataSource>\n',
                         '    <OGRVRTWarpedLayer>\n',
                         '        <OGRVRTLayer name="{}">\n'.format(basename(self.filename()).replace('.shp', '')),
                         '            <SrcDataSource>{ds}</SrcDataSource>\n'.format(ds=self.filename()),
                         '        </OGRVRTLayer>\n',
                         '        <TargetSRS>{}</TargetSRS>\n'.format(projection.wkt()),
                         '    </OGRVRTWarpedLayer>\n',
                         '</OGRVRTDataSource>\n']

        vrtFilename = join(tempfile.gettempdir(), str(randint(0, 10 ** 10)) + '.vrt')
        with open(vrtFilename, 'w') as f:
            f.writelines(vrtDefinition)

        ogrDataSource = ogr.Open(vrtFilename)
        assert ogrDataSource is not None
        layer = Vector(ogrDataSource=ogrDataSource, nameOrIndex=0)
        remove(vrtFilename)
        return layer

    def featureCount(self):
        return self._ogrLayer.GetFeatureCount()

    def fieldCount(self):
        return self._ogrLayer.GetLayerDefn().GetFieldCount()
