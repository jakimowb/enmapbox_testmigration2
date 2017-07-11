from os import makedirs, remove
from os.path import dirname, exists, join, basename
from random import randint
import tempfile
from osgeo import gdal, gdal_array, ogr, osr
import numpy
from rios.pixelgrid import PixelGridDefn, pixelGridFromFile
from hubdc.util import equalProjection

def Open(filename, eAccess=gdal.GA_ReadOnly):
    return Dataset(gdal.Open(filename, eAccess))

def OpenLayer(filename, layerNameOrIndex=0, update=False):
    return Layer(ogrDataSource=ogr.Open(filename, int(update)), nameOrIndex=layerNameOrIndex)

def Create(pixelGrid, bands=1, eType=gdal.GDT_Float32, dstName='', format='MEM', creationOptions=[]):

    if format != 'MEM' and not exists(dirname(dstName)):
        makedirs(dirname(dstName))

    driver = gdal.GetDriverByName(format)
    ysize, xsize = pixelGrid.getDimensions()
    gdalDataset = driver.Create(dstName, xsize, ysize, bands, eType, creationOptions)
    gdalDataset.SetProjection(pixelGrid.projection)
    gdalDataset.SetGeoTransform(pixelGrid.makeGeoTransform())
    return Dataset(gdalDataset=gdalDataset)

def CreateFromArray(pixelGrid, array, dstName='', format='MEM', creationOptions=[]):

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
    dataset = Create(pixelGrid, bands=bands, eType=eType, dstName=dstName, format=format, creationOptions=creationOptions)
    dataset.writeArray(array=array, pixelGrid=pixelGrid)

    return dataset

class PixelGrid(PixelGridDefn):

    @staticmethod
    def fromPixelGrid(pixelGrid):
        assert isinstance(pixelGrid, PixelGridDefn)
        nrows, ncols = pixelGrid.getDimensions()
        return PixelGrid(geotransform=pixelGrid.makeGeoTransform(),
                         nrows=nrows, ncols=ncols,
                         projection=pixelGrid.projection)

    @staticmethod
    def fromDataset(dataset):
        return PixelGrid(geotransform=dataset.gdalDataset.GetGeoTransform(),
                         nrows=dataset.gdalDataset.RasterYSize, ncols=dataset.gdalDataset.RasterXSize,
                         projection=dataset.gdalDataset.GetProjection())

    @classmethod
    def fromFile(clf, filename):
        if not exists(filename):
            raise Exception('file not found: '+str(filename))
        return clf.fromPixelGrid(pixelGridFromFile(filename))

    def __init__(self, geotransform=None, nrows=None, ncols=None, projection=None,
            xMin=None, xMax=None, yMin=None, yMax=None, xRes=None, yRes=None):

        def getProjectionWKT(projection):
            if projection.startswith('EPSG:'):
                epsg = int(projection[-4:])
                projection = osr.SpatialReference()
                projection.ImportFromEPSG(epsg)
                return projection.ExportToWkt()
            return projection

        def trimBoundsToResolutionMultipleAndCastGeoTransformToFloat(pixelGrid):
            geotransform = tuple(float(v) for v in pixelGrid.makeGeoTransform())
            nrows, ncols = pixelGrid.getDimensions()
            PixelGridDefn.__init__(self, geotransform=geotransform, nrows=nrows, ncols=ncols, projection=projection)

        projection = getProjectionWKT(str(projection))
        trimBoundsToResolutionMultipleAndCastGeoTransformToFloat(pixelGrid=PixelGridDefn(geotransform=geotransform, nrows=nrows, ncols=ncols,
                                                                                         projection=projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax,
                                                                                         xRes=xRes, yRes=yRes))

    @property
    def xSize(self):
        return int(round(float(self.xMax - self.xMin) / self.xRes))

    @property
    def ySize(self):
        return int(round(float(self.yMax-self.yMin)/self.yRes))

    def getDimensions(self):
        return self.ySize, self.xSize

    def equalUL(self, other):
        return (self.xMin == other.xMin and
                self.yMax == other.yMax)

    def equalDimensions(self, other):
        return self.getDimensions() == other.getDimensions()

    def equal(self, other):
        return (self.equalProjection(other=other) and
                self.equalUL(other=other) and
                self.equalPixSize(other=other) and
                self.equalDimensions(other=other))

    def intersection(self, other):
        return PixelGrid.fromPixelGrid(PixelGridDefn.intersection(self, other))

    def reproject(self, targetGrid):
        return PixelGrid.fromPixelGrid(PixelGridDefn.reproject(self, targetGrid))

    def reprojectExtent(self, targetProjection):

        targetProjection = osr.SpatialReference(str(targetProjection))
        selfProjection = osr.SpatialReference(str(self.projection))

        t = osr.CoordinateTransformation(selfProjection, targetProjection)

        (tl_x, tl_y, z) = t.TransformPoint(self.xMin, self.yMax)
        (bl_x, bl_y, z) = t.TransformPoint(self.xMin, self.yMin)
        (tr_x, tr_y, z) = t.TransformPoint(self.xMax, self.yMax)
        (br_x, br_y, z) = t.TransformPoint(self.xMax, self.yMin)

        xMin = min(tl_x, bl_x)
        xMax = max(tr_x, br_x)
        yMin = min(bl_y, br_y)
        yMax = max(tl_y, tr_y)

        return xMin, xMax, yMin, yMax

    def mapBuffer(self, buffer, north=True, west=True, south=True, east=True):
        buffered = self.copy()
        if west: buffered.xMin -= buffer
        if east: buffered.xMax += buffer
        if south: buffered.yMin -= buffer
        if north: buffered.yMax += buffer
        return PixelGrid.fromPixelGrid(buffered)

    def pixelBuffer(self, buffer, left=True, right=True, upper=True, lower=True):
        buffered = self.copy()
        if left: buffered.xMin -= buffer * self.xRes
        if right: buffered.xMax += buffer * self.xRes
        if lower: buffered.yMin -= buffer * self.yRes
        if upper: buffered.yMax += buffer * self.yRes
        return PixelGrid.fromPixelGrid(buffered)

    def anchor(self, xAnchor, yAnchor):
        anchored = self.copy()

        xMinOff = (anchored.xMin - xAnchor) % anchored.xRes
        yMinOff = (anchored.yMin - yAnchor) % anchored.yRes
        xMaxOff = (anchored.xMax - xAnchor) % anchored.xRes
        yMaxOff = (anchored.yMax - yAnchor) % anchored.yRes

        # round snapping offset
        if xMinOff > anchored.xRes / 2.: xMinOff -= anchored.xRes
        if yMinOff > anchored.yRes / 2.: yMinOff -= anchored.yRes
        if xMaxOff > anchored.xRes / 2.: xMaxOff -= anchored.xRes
        if yMaxOff > anchored.yRes / 2.: yMaxOff -= anchored.yRes

        anchored.xMin -= xMinOff
        anchored.yMin -= yMinOff
        anchored.xMax -= xMaxOff
        anchored.yMax -= yMaxOff

        return anchored

    def newResolution(self, xRes, yRes):

        pixelGrid = self.copy()
        pixelGrid.xRes = xRes
        pixelGrid.yRes = yRes
        return self.fromPixelGrid(pixelGrid)

    def copy(self):
        return self.fromPixelGrid(self)

    def subsetPixelWindow(self, xoff, yoff, width, height):
        xMin = self.xMin + xoff*self.xRes
        xMax = xMin + width*self.xRes
        yMax = self.yMax - yoff*self.yRes
        yMin = yMax - height*self.yRes
        pixelGrid = PixelGrid(projection=self.projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax, xRes=self.xRes, yRes=self.yRes)
        return pixelGrid

    def iterSubgrids(self, windowxsize, windowysize):
        ysize, xsize = self.getDimensions()
        yoff = 0
        while yoff < ysize:
            xoff = 0
            while xoff < xsize:
                pixelGridTile = self.subsetPixelWindow(xoff=xoff, yoff=yoff, width=windowxsize, height=windowysize)
                pixelGridTile = pixelGridTile.intersection(self) # ensures that tiles at the left and lower edges are trimmed
                yield pixelGridTile
                xoff += windowxsize
            yoff += windowysize

    def subgrids(self, windowxsize, windowysize):
        return list(self.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize))

class Dataset():

    def __init__(self, gdalDataset):
        assert isinstance(gdalDataset, gdal.Dataset)
        self.gdalDataset = gdalDataset
        self.pixelGrid = PixelGrid.fromDataset(self)

    def __iter__(self):
        for i in range(self.shape[0]):
            yield self.getBand(i+1)

    def getFormat(self):
        return self.gdalDataset.GetDriver().ShortName

    def readAsArray(self, pixelGrid=None, dtype=None, scale=None, resample_alg=gdal.GRIORA_NearestNeighbour):

        if pixelGrid is None:
            array = self.gdalDataset.ReadAsArray()
        else:
            assert isinstance(pixelGrid, PixelGrid)
            xoff = round((pixelGrid.xMin - self.pixelGrid.xMin) / self.pixelGrid.xRes, 0)
            yoff = round((self.pixelGrid.yMax - pixelGrid.yMax) / self.pixelGrid.yRes, 0)
            xsize = round((pixelGrid.xMax - pixelGrid.xMin) / self.pixelGrid.xRes, 0)
            ysize = round((pixelGrid.yMax - pixelGrid.yMin) / self.pixelGrid.yRes, 0)
            buf_ysize, buf_xsize = pixelGrid.getDimensions()
            array = self.gdalDataset.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize,
                                                 buf_xsize=buf_xsize, buf_ysize=buf_ysize,
                                                 resample_alg=resample_alg)

        array = array if array.ndim == 3 else array[None] # add third dimension if missing
        if dtype is not None:
            array = array.astype(dtype)
        if scale is not None:
            array *= scale

        return array

    def writeArray(self, array, pixelGrid=None):
        assert len(array) == self.shape[0]

        for band, bandArray in zip(self, array):
            band.writeArray(bandArray, pixelGrid=pixelGrid)

    def flushCache(self):
        self.gdalDataset.FlushCache()

    def close(self):
        self.gdalDataset = None

    def getBand(self, bandNumber):
        return Band(gdalBand=self.gdalDataset.GetRasterBand(bandNumber), pixelGrid=self.pixelGrid)

    def setNoDataValues(self, values):
        for band, value in zip(self, values):
            band.setNoDataValue(value)

    def getNoDataValues(self):
        return [band.getNoDataValue() for band in self]

    def setNoDataValue(self, value):
        self.setNoDataValues(values=[value]*self.zsize)

    def getNoDataValue(self):
        noDataValues = self.getNoDataValues()
        if len(set(noDataValues)) != 1:
            raise Exception('there are multiple no data values, use getNoDataValues() instead')
        return noDataValues[0]

    def getMetadataDomainList(self):
        domains = self.gdalDataset.GetMetadataDomainList()
        return domains if domains is not None else []

    def setMetadataItem(self, key, value, domain=''):
        key = key.replace(' ', '_')
        gdalString = _GDALStringFormatter.valueToGDALString(value)
        self.gdalDataset.SetMetadataItem(key, gdalString, domain)

    def getMetadataItem(self, key, domain='', type=str):
        key = key.replace(' ', '_')
        gdalString = self.gdalDataset.GetMetadataItem(key, domain)
        if gdalString is None:
            return None
        return _GDALStringFormatter.gdalStringToValue(gdalString, type=type)

    def getMetadata(self):
        meta = dict()
        for domain in self.getMetadataDomainList():
            meta[domain] = self.gdalDataset.GetMetadata(domain)
        return meta

    def setMetadata(self, meta):
        assert isinstance(meta, dict)
        for domain in meta:
            self.gdalDataset.SetMetadata(meta[domain], domain)

    def getMetadataDomain(self, domain):
        return self.gdalDataset.GetMetadata(domain)

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
            for key, value in zip(orderedEnvi.keys()+envi.keys(), orderedEnvi.values()+envi.values()):
                if value is not None:
                    f.write('{key} = {value}\n'.format(key=key.replace('_', ' '), value=value))

    def warp(self, dstPixelGrid, dstName='', format='MEM', creationOptions=[], **kwargs):

        assert isinstance(dstPixelGrid, PixelGrid)

        xRes, yRes, dstSRS = (getattr(dstPixelGrid, key) for key in ('xRes', 'yRes', 'projection'))
        outputBounds = tuple(getattr(dstPixelGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))

        if format != 'MEM' and not exists(dirname(dstName)):
            makedirs(dirname(dstName))

        warpOptions = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS,
                                       creationOptions=creationOptions, **kwargs)
        gdalDataset = gdal.Warp(destNameOrDestDS=dstName, srcDSOrSrcDSTab=self.gdalDataset, options=warpOptions)
        #gdalDataset = gdal.Warp(destNameOrDestDS=dstName, srcDSOrSrcDSTab=self.gdalDataset)#, options=warpOptions)

        return Dataset(gdalDataset=gdalDataset)


    def warpOptions(self, dstPixelGrid, format, creationOptions, **kwargs):
        assert isinstance(dstPixelGrid, PixelGrid)

        xRes, yRes, dstSRS = (getattr(dstPixelGrid, key) for key in ('xRes', 'yRes', 'projection'))
        outputBounds = tuple(getattr(dstPixelGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))

        options = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS,
                                       creationOptions=creationOptions, **kwargs)

        return options


    def translate(self, dstPixelGrid=None, dstName='', format='MEM', creationOptions=[], **kwargs):

        if dstPixelGrid is None:
            dstPixelGrid = self.pixelGrid

        assert isinstance(dstPixelGrid, PixelGrid)
        assert self.pixelGrid.equalProjection(dstPixelGrid)

        if format != 'MEM' and not exists(dirname(dstName)):
            makedirs(dirname(dstName))

        ulx, uly, lrx, lry, xRes, yRes = tuple(
            getattr(dstPixelGrid, key) for key in ('xMin', 'yMax', 'xMax', 'yMin', 'xRes', 'yRes'))

        # Note that given a projWin, it is not garantied that gdal.Translate will produce a dataset
        # with the same pixel extent as gdal.Warp!
        # The problem seams to only appear if the target resolution is smaller than the source resolution.

        if self.pixelGrid.xRes > dstPixelGrid.xRes or self.pixelGrid.yRes > dstPixelGrid.yRes:
            if format != 'MEM':
                raise Exception('spatial resolution oversampling is only supported for MEM format')

            # read one extra source column and line
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     projWin=[ulx, uly, lrx+self.pixelGrid.xRes, lry-self.pixelGrid.yRes],
                                                     xRes=xRes, yRes=yRes, **kwargs)
            tmpGdalDataset = gdal.Translate(destName='', srcDS=self.gdalDataset, options=translateOptions)

            # subset to the exact target grid
            translateOptions = gdal.TranslateOptions(format=format, creationOptions=creationOptions,
                                                     srcWin=[0, 0, dstPixelGrid.xSize, dstPixelGrid.ySize])
            gdalDataset = gdal.Translate(destName='', srcDS=tmpGdalDataset, options=translateOptions)

        else:
            translateOptions = gdal.TranslateOptions(format=format, projWin=[ulx, uly, lrx, lry], xRes=xRes, yRes=yRes,
                                                     creationOptions=creationOptions, **kwargs)
            gdalDataset = gdal.Translate(destName=dstName, srcDS=self.gdalDataset, options=translateOptions)

        # make sure, that the workaround is correct
        assert gdalDataset.RasterXSize == dstPixelGrid.xSize and gdalDataset.RasterYSize == dstPixelGrid.ySize

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
    def gdalStringToValue(cls, gdalString, type):
        gdalString.strip()
        if gdalString.startswith('{') and gdalString.endswith('}'):
            value = cls._gdalStringToList(gdalString, type)
        else:
            value = type(gdalString)
        return value

    @classmethod
    def _listToGDALString(cls, values):
        return '{'+','.join([str(v) for v in values])+'}'

    @classmethod
    def _gdalStringToList(cls, gdalString, type):
        values = [type(v) for v in gdalString[1:-1].split(',')]
        return values

class Band():

    def __init__(self, gdalBand, pixelGrid):
        assert isinstance(gdalBand, gdal.Band)
        assert isinstance(pixelGrid, PixelGrid)

        self.gdalBand = gdalBand
        self.pixelGrid = pixelGrid

    def readAsArray(self, dtype=None, ** kwargs):
        array = self.gdalBand.ReadAsArray(**kwargs)
        if dtype is not None:
            array = array.astype(dtype)
        return array

    def writeArray(self, array, pixelGrid=None):

        if pixelGrid is None:
            pixelGrid = self.pixelGrid

        assert array.shape == pixelGrid.getDimensions()
        assert isinstance(pixelGrid, PixelGrid)
        assert self.pixelGrid.equalProjection(pixelGrid), 'selfProjection: '+self.pixelGrid.projection+'\notherProjection: '+pixelGrid.projection
        assert self.pixelGrid.equalPixSize(pixelGrid)

        xoff=int(round((pixelGrid.xMin - self.pixelGrid.xMin)/self.pixelGrid.xRes, 0))
        yoff=int(round((self.pixelGrid.yMax - pixelGrid.yMax)/self.pixelGrid.yRes, 0))
        self.gdalBand.WriteArray(array, xoff=xoff, yoff=yoff)

    def setNoDataValue(self, value):
        self.gdalBand.SetNoDataValue(float(value))

    def getNoDataValue(self):
        return self.gdalBand.GetNoDataValue()

    def setDescription(self, value):
        self.gdalBand.SetDescription(value)

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
        self.projection = self.ogrLayer.GetSpatialRef()

    def close(self):
        self.ogrLayer = None
        self.ogrDataSource = None

    def makePixelGrid(self, xRes, yRes):
        xMin, xMax, yMin, yMax = self.ogrLayer.GetExtent()
        return PixelGrid(projection=self.projection, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax, xRes=xRes, yRes=yRes)

    def rasterize(self, dstPixelGrid, eType=gdal.GDT_Float32,
                  initValue=None, burnValue=1, burnAttribute=None, allTouched=False,
                  filter=None, noDataValue=None,
                  dstName='', format='MEM', creationOptions=[]):

        assert isinstance(dstPixelGrid, PixelGrid)

        if not equalProjection(self.ogrLayer.GetSpatialRef(), dstPixelGrid.projection):
            layer = self
        else:
            layer = self.reprojectOnTheFly(projection=dstPixelGrid.projection)

        layer.ogrLayer.SetAttributeFilter(filter)

        if format != 'MEM' and not exists(dirname(dstName)):
            makedirs(dirname(dstName))

        driver = gdal.GetDriverByName(format)
        ysize, xsize = dstPixelGrid.getDimensions()
        gdalDataset = driver.Create(dstName, xsize, ysize, 1, eType, creationOptions)
        gdalDataset.SetProjection(dstPixelGrid.projection)
        gdalDataset.SetGeoTransform(dstPixelGrid.makeGeoTransform())
        dataset = Dataset(gdalDataset=gdalDataset)
        if noDataValue is not None:
            dataset.setNoDataValue(noDataValue)
        if initValue is not None:
            dataset.getBand(1).fill(value=initValue)

        options = list()
        #special options controlling rasterization:
        #    "ATTRIBUTE": Identifies an attribute field on the features to be used for a burn in value. The value will be burned into all output bands. If specified, padfLayerBurnValues will not be used and can be a NULL pointer.
        #    "CHUNKYSIZE": The height in lines of the chunk to operate on. The larger the chunk size the less times we need to make a pass through all the shapes. If it is not set or set to zero the default chunk size will be used. Default size will be estimated based on the GDAL cache buffer size using formula: cache_size_bytes/scanline_size_bytes, so the chunk will not exceed the cache.
        #    "ALL_TOUCHED": May be set to TRUE to set all pixels touched by the line or polygons, not just those whose center is within the polygon or that are selected by brezenhams line algorithm. Defaults to FALSE.
        #    "BURN_VALUE_FROM": May be set to "Z" to use the Z values of the geometries. The value from padfLayerBurnValues or the attribute field value is added to this before burning. In default case dfBurnValue is burned as it is. This is implemented properly only for points and lines for now. Polygons will be burned using the Z value from the first point. The M value may be supported in the future.
        #    "MERGE_ALG": May be REPLACE (the default) or ADD. REPLACE results in overwriting of value, while ADD adds the new value to the existing raster, suitable for heatmaps for instance.
        if allTouched:
            options.append('ALL_TOUCHED=TRUE')
        if burnAttribute:
            options.append('ATTRIBUTE='+burnAttribute)

        gdal.RasterizeLayer(dataset.gdalDataset, [1], layer.ogrLayer, burn_values=[burnValue], options=options)

        return dataset

    def reprojectOnTheFly(self, projection):
        # need to create a temp VRT
        vrtDefinition = ['<OGRVRTDataSource>\n',
                        '    <OGRVRTWarpedLayer>\n',
                        '        <OGRVRTLayer name="{}">\n'.format(basename(self.filename).replace('.shp','')),
                        '            <SrcDataSource>{ds}</SrcDataSource>\n'.format(ds=self.filename),
                        '        </OGRVRTLayer>\n',
                        '        <TargetSRS>{}</TargetSRS>\n'.format(str(projection)),
                        '    </OGRVRTWarpedLayer>\n',
                        '</OGRVRTDataSource>\n']

        vrtFilename = join(tempfile.gettempdir(), str(randint(0, 10**10))+'.vrt')
        with open(vrtFilename, 'w') as f:
            f.writelines(vrtDefinition)

        layer = Layer(ogrDataSource=ogr.Open(vrtFilename), nameOrIndex=0)
        remove(vrtFilename)
        return layer
