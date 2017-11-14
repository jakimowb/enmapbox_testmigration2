from os import makedirs, remove
from os.path import dirname, exists, join, basename
import copy
from random import randint
import tempfile
from osgeo import gdal, gdal_array, ogr, osr
import numpy


def Open(filename, eAccess=gdal.GA_ReadOnly):
    assert exists(str(filename)), filename
    return Dataset(gdal.Open(filename, eAccess))


def OpenLayer(filename, layerNameOrIndex=0, update=False):
    if str(layerNameOrIndex).isdigit():
        layerNameOrIndex = int(layerNameOrIndex)
    return Layer(ogrDataSource=ogr.Open(filename, int(update)), nameOrIndex=layerNameOrIndex)


def Create(grid, bands=1, eType=gdal.GDT_Float32, filename='', format='MEM', creationOptions=[]):
    assert isinstance(grid, Grid)
    if format != 'MEM' and not exists(dirname(filename)):
        makedirs(dirname(filename))

    driver = gdal.GetDriverByName(format)
    if driver.ShortName in ['PNG']:
        tmpdriver = gdal.GetDriverByName('MEM')
        tmpds = tmpdriver.Create('', grid.xSize, grid.ySize, bands, eType)
        strict = 0
        gdalDataset = driver.CreateCopy(filename, tmpds, strict, creationOptions)
    else:
        gdalDataset = driver.Create(filename, grid.xSize, grid.ySize, bands, eType, creationOptions)
    gdalDataset.SetProjection(grid.projection.wkt)
    gdalDataset.SetGeoTransform(grid.makeGeoTransform())
    return Dataset(gdalDataset=gdalDataset)


def CreateFromArray(grid, array, filename='', format='MEM', creationOptions=[]):
    if isinstance(array, numpy.ndarray):
        if array.ndim == 2:
            array = array[None]
        assert array.ndim == 3
    elif isinstance(array, list):
        assert all([subarray.ndim == 2 for subarray in array])
    else:
        raise TypeError

    bands = len(array)
    dtype = array[0].dtype
    if dtype == numpy.bool:
        dtype = numpy.uint8
    eType = gdal_array.NumericTypeCodeToGDALTypeCode(dtype)
    dataset = Create(grid=grid, bands=bands, eType=eType, filename=filename, format=format,
                     creationOptions=creationOptions)
    dataset.writeArray(array=array, pixelGrid=grid)

    return dataset


def CreateVRT(filename, srcDSOrSrcDSTab, **kwargs):
    options = gdal.BuildVRTOptions(**kwargs)
    gdalDataset = gdal.BuildVRT(destName=filename, srcDSOrSrcDSTab=srcDSOrSrcDSTab, options=options)
    return Dataset(gdalDataset=gdalDataset)


def buildOverviews(filename, minsize=None, levels=None, resampling='average'):
    assert resampling in ['average', 'gauss', 'cubic', 'cubicspline', 'lanczos', 'average_mp', 'average_magphase',
                          'mode']
    if levels is None:
        assert minsize is not None
        levels = []
        nextLevel = 2
        size = float(max(Open(filename=filename).shape))
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


class Extent(object):
    def __init__(self, xMin, xMax, yMin, yMax):
        self.xMin = float(xMin)
        self.xMax = float(xMax)
        self.yMin = float(yMin)
        self.yMax = float(yMax)
        assert self.xMax > self.xMin
        assert self.yMax > self.yMin

    @property
    def ogrGeometry(self):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in zip([self.xMin, self.xMax, self.xMax, self.xMin, self.xMin],
                        [self.yMax, self.yMax, self.yMin, self.yMin, self.yMax]):
            ring.AddPoint(x, y)
        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(ring)
        return polygon

    @property
    def ul(self):
        return self.xMin, self.yMax

    @property
    def lr(self):
        return self.xMax, self.yMin

    @property
    def wkt(self):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in zip([self.xMin, self.xMax, self.xMax, self.xMin, self.xMin],
                        [self.yMax, self.yMax, self.yMin, self.yMin, self.yMax]):
            ring.AddPoint(x, y)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        wkt = poly.ExportToWkt()
        return wkt

    def reproject(self, sourceProjection, targetProjection):
        assert isinstance(sourceProjection, Projection)
        assert isinstance(targetProjection, Projection)
        t = osr.CoordinateTransformation(sourceProjection.osrSpatialReference, targetProjection.osrSpatialReference)
        (tl_x, tl_y, z) = t.TransformPoint(self.xMin, self.yMax)
        (bl_x, bl_y, z) = t.TransformPoint(self.xMin, self.yMin)
        (tr_x, tr_y, z) = t.TransformPoint(self.xMax, self.yMax)
        (br_x, br_y, z) = t.TransformPoint(self.xMax, self.yMin)
        return Extent(xMin=min(tl_x, bl_x), xMax=max(tr_x, br_x), yMin=min(bl_y, br_y), yMax=max(tl_y, tr_y))

    def intersects(self, other):
        assert isinstance(other, Extent)
        return self.ogrGeometry.Intersects(other.ogrGeometry)

    def intersection(self, other):
        """
        Returns a new instance which is the intersection of self and other.
        """

        assert isinstance(other, Extent)
        xMin = max(self.xMin, other.xMin)
        xMax = min(self.xMax, other.xMax)
        yMin = max(self.yMin, other.yMin)
        yMax = min(self.yMax, other.yMax)

        if xMin >= xMax or yMin >= yMax:
            msg = "Images don't intersect"
            raise Exception(msg)

        return Extent(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)

    def union(self, other):
        '''Returns a new instance which is the union of self with other.'''

        xMin = min(self.xMin, other.xMin)
        xMax = max(self.xMax, other.xMax)
        yMin = min(self.yMin, other.yMin)
        yMax = max(self.yMax, other.yMax)

        return Extent(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)


class SpatialExtent(Extent):
    def __init__(self, extent, projection):
        assert isinstance(extent, Extent)
        assert isinstance(projection, Projection)
        Extent.__init__(self, xMin=extent.xMin, xMax=extent.xMax, yMin=extent.yMin, yMax=extent.yMax)
        self.projection = projection

    def reproject(self, targetProjection):
        assert isinstance(targetProjection, Projection)
        extent = Extent.reproject(self, sourceProjection=self.projection, targetProjection=targetProjection)
        return SpatialExtent(extent=extent, projection=targetProjection)


class Resolution(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        assert self.x > 0
        assert self.y > 0


class Projection(object):

    def __init__(self, wkt):
        self.wkt = str(wkt)

    def __repr__(self):
        wkt = self.wkt.replace(' ', '').replace('\n', ' ')
        return '{cls}(wkt={wkt})'.format(cls=self.__class__.__name__, wkt=wkt)

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

    @property
    def osrSpatialReference(self):
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.wkt)
        return srs

    def equal(self, other):
        '''
        Returns True if the projection of self is the same as the
        projection of other
        '''

        assert isinstance(other, Projection), other
        return bool(self.osrSpatialReference.IsSame(other.osrSpatialReference))


class Offset(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)


class Size(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        assert self.x > 0
        assert self.y > 0


class Grid(object):
    def __init__(self, extent, resolution, projection):
        assert isinstance(extent, Extent)
        assert isinstance(resolution, Resolution), resolution
        assert isinstance(projection, Projection), projection
        self.resolution = resolution
        self.size = Size(x=int(round(float(extent.xMax - extent.xMin) / resolution.x)),
                         y=int(round(float(extent.yMax - extent.yMin) / resolution.y)))
        self.extent = Extent(xMin=extent.xMin,
                             xMax=extent.xMin + self.size.x * resolution.x,
                             yMin=extent.yMin,
                             yMax=extent.yMin + self.size.y * resolution.y)
        self.projection = projection

    @property
    def spatialExtent(self):
        return SpatialExtent(extent=self.extent, projection=self.projection)

    @property
    def xSize(self):
        return self.size.x

    @property
    def ySize(self):
        return self.size.y

    @property
    def shape(self):
        return self.ySize, self.xSize

    def makeGeoTransform(self):
        '''Returns a GDAL geotransform tuple from bounds and resolution'''

        geotransform = (self.extent.xMin, self.resolution.x, 0.0, self.extent.yMax, 0.0, -self.resolution.y)
        return geotransform

    def equal(self, other):
        assert isinstance(other, Grid)
        return (self.projection.equal(other=other.projection) and
                self.extent.ul == other.extent.ul and
                self.shape == other.shape)

    def reproject(self, other):
        assert isinstance(other, Grid)
        extent = self.extent.reproject(sourceProjection=self.projection, targetProjection=other.projection)
        grid = Grid(extent=extent, resolution=other.resolution, projection=other.projection)
        return grid.anchor(x=other.extent.xMin, y=other.extent.yMin)

    def mapBuffer(self, buffer, north=True, west=True, south=True, east=True):
        assert isinstance(buffer, float)
        extent = copy.deepcopy(self.extent)
        if west: extent.xMin -= buffer
        if east: extent.xMax += buffer
        if south: extent.yMin -= buffer
        if north: extent.yMax += buffer
        return Grid(extent=extent, resolution=self.resolution, projection=self.projection)

    def pixelBuffer(self, buffer, left=True, right=True, upper=True, lower=True):
        assert isinstance(buffer, int)
        extent = copy.deepcopy(self.extent)
        if left: extent.xMin -= buffer * self.resolution.x
        if right: extent.xMax += buffer * self.resolution.x
        if lower: extent.yMin -= buffer * self.resolution.y
        if upper: extent.yMax += buffer * self.resolution.y
        return Grid(extent=extent, resolution=self.resolution, projection=self.projection)

    def anchor(self, x, y):

        xMinOff = (self.extent.xMin - x) % self.resolution.x
        yMinOff = (self.extent.yMin - y) % self.resolution.y
        xMaxOff = (self.extent.xMax - x) % self.resolution.x
        yMaxOff = (self.extent.yMax - y) % self.resolution.y

        # round snapping offset
        if xMinOff > self.resolution.x / 2.: xMinOff -= self.resolution.x
        if yMinOff > self.resolution.y / 2.: yMinOff -= self.resolution.y
        if xMaxOff > self.resolution.x / 2.: xMaxOff -= self.resolution.x
        if yMaxOff > self.resolution.y / 2.: yMaxOff -= self.resolution.y

        anchored = copy.deepcopy(self)
        anchored.extent.xMin -= xMinOff
        anchored.extent.yMin -= yMinOff
        anchored.extent.xMax -= xMaxOff
        anchored.extent.yMax -= yMaxOff

        return anchored

    def newResolution(self, resolution):
        return Grid(extent=self.extent, resolution=resolution, projection=self.projection)

    def subset(self, offset, size):
        xMin = self.extent.xMin + offset.x * self.resolution.x
        xMax = xMin + size.x * self.resolution.x
        yMax = self.extent.yMax - offset.y * self.resolution.y
        yMin = yMax - size.y * self.resolution.y
        return Grid(projection=self.projection,
                    resolution=self.resolution,
                    extent=Extent(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax))

    def subgrids(self, size):
        assert isinstance(size, Size)
        size = Size(x=min(size.x, self.size.x), y=min(size.y, self.size.y))
        result = list()

        offset = Offset(x=0, y=0)
        i = iy = 0
        while offset.y < self.size.y:
            offset.x = 0
            ix = 0
            while offset.x < self.size.x:
                subgrid = self.subset(offset=offset, size=size)
                subgrid.extent = subgrid.extent.intersection(self.extent)
                result.append((subgrid, i, iy, ix))
                offset.x += size.x
                ix += 1
                i += 1
            offset.y += size.y
            iy += 1
        return result


class Dataset():
    def __init__(self, gdalDataset):
        assert isinstance(gdalDataset, gdal.Dataset)
        self.gdalDataset = gdalDataset

    def __iter__(self):
        for i in range(self.shape[0]):
            yield self.getBand(i + 1)

    @property
    def projection(self):
        return Projection(wkt=self.gdalDataset.GetProjection())

    @property
    def resolution(self):
        gt = self.gdalDataset.GetGeoTransform()
        return Resolution(x=gt[1], y=abs(gt[5]))

    @property
    def extent(self):
        gt = self.gdalDataset.GetGeoTransform()
        xSize = self.gdalDataset.RasterXSize
        ySize = self.gdalDataset.RasterYSize
        return Extent(xMin=gt[0],
                      xMax=gt[0] + xSize * self.resolution.x,
                      yMin=gt[3] - ySize * self.resolution.y,
                      yMax=gt[3])

    @property
    def grid(self):
        return Grid(extent=self.extent, resolution=self.resolution, projection=self.projection)

    @property
    def spatialExtent(self):
        return self.grid.spatialExtent

    def getFormat(self):
        return self.gdalDataset.GetDriver().ShortName

    def readAsArray(self, pixelGrid=None, resample_alg=gdal.GRIORA_NearestNeighbour):
        if pixelGrid is None:
            array = self.gdalDataset.ReadAsArray()
        else:
            assert isinstance(pixelGrid, Grid)
            xoff = int(round((pixelGrid.xMin - self.grid.xMin) / self.grid.xRes, 0))
            yoff = int(round((self.grid.yMax - pixelGrid.yMax) / self.grid.yRes, 0))
            xsize = int(round((pixelGrid.xMax - pixelGrid.xMin) / self.grid.xRes, 0))
            ysize = int(round((pixelGrid.yMax - pixelGrid.yMin) / self.grid.yRes, 0))

            buf_ysize, buf_xsize = pixelGrid.getDimensions()
            array = self.gdalDataset.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize,
                                                 buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                                 resample_alg=resample_alg)

        if array.ndim == 2:
            array = array[None]

        return array

    def writeArray(self, array, pixelGrid=None):
        assert len(array) == self.shape[0]

        for band, bandArray in zip(self, array):
            band.writeArray(bandArray, grid=pixelGrid)

    def flushCache(self):
        self.gdalDataset.FlushCache()

    def close(self):
        self.gdalDataset = None

    def getBand(self, bandNumber):
        return Band(gdalBand=self.gdalDataset.GetRasterBand(bandNumber), grid=self.grid)

    def setNoDataValues(self, values):
        for band, value in zip(self, values):
            band.setNoDataValue(value)

    def getNoDataValues(self, default=None):
        return [band.getNoDataValue(default=default) for band in self]

    def setNoDataValue(self, value):
        self.setNoDataValues(values=[value] * self.zsize)

    def getNoDataValue(self, default=None):
        noDataValues = self.getNoDataValues()
        if len(set(noDataValues)) != 1:
            raise Exception('there are multiple no data values, use getNoDataValues() instead')
        noDataValue = noDataValues[0]
        if noDataValue is None:
            noDataValue = default
        return noDataValue

    def setDescription(self, value):
        self.gdalDataset.SetDescription(value)

    def getDescription(self):
        return self.gdalDataset.GetDescription()

    def getMetadataDomainList(self):
        domains = self.gdalDataset.GetMetadataDomainList()
        return domains if domains is not None else []

    def setMetadataItem(self, key, value, domain=''):
        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = _GDALStringFormatter.valueToGDALString(value)
        self.gdalDataset.SetMetadataItem(key, gdalString, domain)

    def getMetadataItem(self, key, domain='', dtype=str):
        key = key.replace(' ', '_')
        gdalString = self.gdalDataset.GetMetadataItem(key, domain)
        if gdalString is None:
            return None
        return _GDALStringFormatter.gdalStringToValue(gdalString, dtype=dtype)

    def getMetadataDict(self):
        metadataDict = dict()
        for domain in self.getMetadataDomainList():
            metadataDict[domain] = dict()
            for key, value in self.getMetadataDomain(domain=domain).items():
                metadataDict[domain][key] = self.getMetadataItem(key=key, domain=domain)
        return metadataDict

    def setMetadataDict(self, metadataDict):
        assert isinstance(metadataDict, dict)
        for domain in metadataDict:
            for key, value in metadataDict[domain].items():
                self.setMetadataItem(key=key, value=value, domain=domain)

    def getMetadataDomain(self, domain):
        domainDict = self.gdalDataset.GetMetadata(domain)
        assert isinstance(domainDict, dict)
        return domainDict

    def copyMetadata(self, other):
        assert isinstance(other, Dataset)

        for domain in other.getMetadataDomainList():
            self.gdalDataset.SetMetadata(other.gdalDataset.GetMetadata(domain), domain)

        for band, otherBand in zip(self, other):
            for domain in otherBand.getMetadataDomainList():
                band.gdalBand.SetMetadata(otherBand.gdalBand.GetMetadata(domain), domain)

    def setENVIAcquisitionTime(self, value):
        self.setMetadataItem('acquisition time', value, 'ENVI')

    def writeENVIHeader(self):

        filename = self.gdalDataset.GetFileList()[0]
        format = self.getFormat()
        if format == 'ENVI':
            fileType = self.getMetadataItem(key='file type', domain='ENVI')
            hdrfilename = self.gdalDataset.GetFileList()[-1]
        elif format == 'GTiff':
            fileType = 'TIFF'
            hdrfilename = filename + '.hdr'
        else:
            return

        envi = self.getMetadataDomain(domain='ENVI')

        envi['file type'] = fileType
        envi['samples'] = self.gdalDataset.RasterXSize
        envi['lines'] = self.gdalDataset.RasterYSize
        envi['bands'] = self.gdalDataset.RasterCount

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
        self.gdalDataset = None

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

    def warp(self, grid, filename='', format='MEM', creationOptions=[], **kwargs):

        assert isinstance(grid, Grid)

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        outputBounds = tuple(getattr(grid.extent, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))
        warpOptions = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=grid.resolution.x,
                                       yRes=grid.resolution.y, dstSRS=grid.projection.wkt,
                                       creationOptions=creationOptions, **kwargs)
        gdalDataset = gdal.Warp(destNameOrDestDS=filename, srcDSOrSrcDSTab=self.gdalDataset, options=warpOptions)

        return Dataset(gdalDataset=gdalDataset)

    def warpOptions(self, grid, format, creationOptions, **kwargs):
        assert isinstance(grid, Grid)

        xRes, yRes, dstSRS = (getattr(grid, key) for key in ('xRes', 'yRes', 'projection'))
        outputBounds = tuple(getattr(grid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))

        options = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS,
                                   creationOptions=creationOptions, **kwargs)

        return options

    def translate(self, grid=None, filename='', format='MEM', creationOptions=[], **kwargs):

        if grid is None:
            grid = self.grid

        assert isinstance(grid, Grid)
        assert self.grid.projection.equal(other=grid.projection)

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        ulx, uly = grid.extent.ul
        lrx, lry = grid.extent.lr
        xRes, yRes = grid.resolution.x, grid.resolution.y
        #            getattr(grid, key) for key in ('xMin', 'yMax', 'xMax', 'yMin', 'xRes', 'yRes'))

        # Note that given a projWin, it is not garantied that gdal.Translate will produce a dataset
        # with the same pixel extent as gdal.Warp!
        # The problem seams to only appear if the target resolution is smaller than the source resolution.

        if self.grid.resolution.x > xRes or self.grid.resolution.y > yRes:
            if format != 'MEM':
                raise Exception('spatial resolution oversampling is only supported for MEM format')

            # read one extra source column and line
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     projWin=[ulx, uly, lrx + self.grid.resolution.x,
                                                              lry - self.grid.resolution.y],
                                                     xRes=xRes, yRes=yRes, **kwargs)
            tmpGdalDataset = gdal.Translate(destName='', srcDS=self.gdalDataset, options=translateOptions)

            # subset to the exact target grid
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     srcWin=[0, 0, grid.xSize, grid.ySize])
            gdalDataset = gdal.Translate(destName='', srcDS=tmpGdalDataset, options=translateOptions)

        else:
            translateOptions = gdal.TranslateOptions(format=format, projWin=[ulx, uly, lrx, lry], xRes=xRes, yRes=yRes,
                                                     creationOptions=creationOptions, **kwargs)
            gdalDataset = gdal.Translate(destName=filename, srcDS=self.gdalDataset, options=translateOptions)

        # make sure, that the workaround is correct
        assert gdalDataset.RasterXSize == grid.xSize and gdalDataset.RasterYSize == grid.ySize

        return Dataset(gdalDataset=gdalDataset)

    @property
    def xsize(self):
        return self.gdalDataset.RasterXSize

    @property
    def ysize(self):
        return self.gdalDataset.RasterYSize

    @property
    def zsize(self):
        return self.gdalDataset.RasterCount

    @property
    def shape(self):
        return self.gdalDataset.RasterCount, self.gdalDataset.RasterYSize, self.gdalDataset.RasterXSize


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
    def __init__(self, gdalBand, grid):
        assert isinstance(gdalBand, gdal.Band)
        assert isinstance(grid, Grid)

        self.gdalBand = gdalBand
        self.grid = grid

    def readAsArray(self, pixelGrid=None, resample_alg=gdal.GRIORA_NearestNeighbour):

        if pixelGrid is None:
            array = self.gdalBand.ReadAsArray(resample_alg=resample_alg)
        else:
            assert isinstance(pixelGrid, Grid)
            xoff = round((pixelGrid.xMin - self.grid.xMin) / self.grid.xRes, 0)
            yoff = round((self.grid.yMax - pixelGrid.yMax) / self.grid.yRes, 0)
            xsize = round((pixelGrid.xMax - pixelGrid.xMin) / self.grid.xRes, 0)
            ysize = round((pixelGrid.yMax - pixelGrid.yMin) / self.grid.yRes, 0)

            # fix for out of bounds error (not sure if I want to use it!)
            # xsize = min(xsize, self.pixelGrid.xSize)
            # ysize = min(ysize, self.pixelGrid.ySize)

            buf_ysize, buf_xsize = pixelGrid.getDimensions()
            array = self.gdalBand.ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize,
                                              buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                              resample_alg=resample_alg)

        return array

    def writeArray(self, array, grid=None):

        assert isinstance(array, numpy.ndarray)
        if array.ndim == 3:
            assert len(array) == 1
            array = array[0]

        if grid is None:
            grid = self.grid

        assert isinstance(grid, Grid)
        assert array.shape == grid.shape, (array.shape, grid.shape)
        assert self.grid.projection.equal(other=grid.projection)

        xoff = int(round((grid.extent.xMin - self.grid.extent.xMin) / self.grid.resolution.x, 0))
        yoff = int(round((self.grid.extent.yMax - grid.extent.yMax) / self.grid.resolution.y, 0))
        self.gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)

    def setMetadataItem(self, key, value, domain=''):
        if value is None:
            return
        key = key.replace(' ', '_')
        gdalString = _GDALStringFormatter.valueToGDALString(value)
        self.gdalBand.SetMetadataItem(key, gdalString, domain)

    def getMetadataItem(self, key, domain='', dtype=str):
        key = key.replace(' ', '_')
        gdalString = self.gdalBand.GetMetadataItem(key, domain)
        if gdalString is None:
            return None
        return _GDALStringFormatter.gdalStringToValue(gdalString, dtype=dtype)

    def copyMetadata(self, other):
        assert isinstance(other, Band)

        for domain in other.getMetadataDomainList():
            self.gdalBand.SetMetadata(other.gdalBand.GetMetadata(domain), domain)

    def setNoDataValue(self, value):
        self.gdalBand.SetNoDataValue(float(value))

    def getNoDataValue(self, default=None):
        noDataValue = self.gdalBand.GetNoDataValue()
        if noDataValue is None:
            noDataValue = default
        return noDataValue

    def setDescription(self, value):
        self.gdalBand.SetDescription(value)

    def getDescription(self):
        return self.gdalBand.GetDescription()

    def getMetadataDomainList(self):
        domains = self.gdalBand.GetMetadataDomainList()
        return domains if domains is not None else []

    def fill(self, value):
        self.gdalBand.Fill(value)


class Layer(object):
    def __init__(self, ogrDataSource, nameOrIndex=0):
        assert isinstance(ogrDataSource, ogr.DataSource)
        self.ogrDataSource = ogrDataSource
        self.ogrLayer = ogrDataSource.GetLayer(iLayer=nameOrIndex)
        self.filename = self.ogrDataSource.GetDescription()
        self.projection = Projection(wkt=self.ogrLayer.GetSpatialRef())

    def close(self):
        self.ogrLayer = None
        self.ogrDataSource = None

    def makePixelGrid(self, xRes, yRes):
        xMin, xMax, yMin, yMax = self.ogrLayer.GetExtent()
        return Grid(projection=self.projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax, xRes=xRes, yRes=yRes)

    def rasterize(self, grid, eType=gdal.GDT_Float32,
                  initValue=None, burnValue=1, burnAttribute=None, allTouched=False,
                  filter=None, noDataValue=None,
                  filename='', format='MEM', creationOptions=[]):

        assert isinstance(grid, Grid)

        if not self.projection.equal(other=grid.projection):
            layer = self
        else:
            layer = self.reprojectOnTheFly(projection=grid.projection)

        layer.ogrLayer.SetAttributeFilter(filter)

        if format != 'MEM' and not exists(dirname(filename)):
            makedirs(dirname(filename))

        driver = gdal.GetDriverByName(format)
        gdalDataset = driver.Create(filename, grid.xSize, grid.ySize, 1, eType, creationOptions)
        gdalDataset.SetProjection(grid.projection.wkt)
        gdalDataset.SetGeoTransform(grid.makeGeoTransform())
        dataset = Dataset(gdalDataset=gdalDataset)
        if noDataValue is not None:
            dataset.setNoDataValue(noDataValue)
        if initValue is not None:
            dataset.getBand(1).fill(value=initValue)

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

        gdal.RasterizeLayer(dataset.gdalDataset, [1], layer.ogrLayer, burn_values=[burnValue], options=options)

        return dataset

    def reprojectOnTheFly(self, projection):
        # need to create a temp VRT
        vrtDefinition = ['<OGRVRTDataSource>\n',
                         '    <OGRVRTWarpedLayer>\n',
                         '        <OGRVRTLayer name="{}">\n'.format(basename(self.filename).replace('.shp', '')),
                         '            <SrcDataSource>{ds}</SrcDataSource>\n'.format(ds=self.filename),
                         '        </OGRVRTLayer>\n',
                         '        <TargetSRS>{}</TargetSRS>\n'.format(str(projection)),
                         '    </OGRVRTWarpedLayer>\n',
                         '</OGRVRTDataSource>\n']

        vrtFilename = join(tempfile.gettempdir(), str(randint(0, 10 ** 10)) + '.vrt')
        with open(vrtFilename, 'w') as f:
            f.writelines(vrtDefinition)

        layer = Layer(ogrDataSource=ogr.Open(vrtFilename), nameOrIndex=0)
        remove(vrtFilename)
        return layer

    def getFeatureCount(self):
        return self.ogrLayer.GetFeatureCount()

    def getFieldCount(self):
        return self.ogrLayer.GetLayerDefn().GetFieldCount()

        #        ldefn = layer.GetLayerDefn()
        #    for n in range(ldefn.GetFieldCount()):
        #        fdefn = ldefn.GetFieldDefn(n)
        #        schema.append(fdefn.name)
