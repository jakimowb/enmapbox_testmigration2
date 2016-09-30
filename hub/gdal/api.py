from __future__ import print_function
import gdal, numpy, osgeo, hub.file, hub.envi
import collections
from hub.datetime import Date
#from gdalconst import *
#from hub.collections import Bunch

def geoInfo(file):
    result = dict()
    dataset = gdal.Open(file, gdal.GA_ReadOnly)
    result.geoTransform = numpy.array(dataset.GetGeoTransform())
    result.projection = dataset.GetProjection()
    result.rasterSize = numpy.array((dataset.RasterXSize, dataset.RasterYSize))
    result.pixelSize = result.geoTransform[[1,5]]
    result.pixelTie  = result.geoTransform[[2,4]]
    result.geoTie  = result.geoTransform[[0,3]]
    result.ul = result.geoTie+result.rasterSize*result.pixelTie
    result.lr = result.ul+result.rasterSize*result.pixelSize
    result.boundingBox = numpy.append(result.ul, result.lr)
    return result

def readCube(filename):
    driver = gdal.GetDriverByName('MEM')
    dataset = driver.CreateCopy('', gdal.Open(filename))
    cube = dataset.ReadAsArray(xoff=0, yoff=0, xsize=dataset.RasterXSize, ysize=dataset.RasterYSize)
    return cube

def writeCube(cube, filename, srsfilename=None, nodatavalue=None, format='ENVI'):

    hub.file.mkfiledir(filename)

    if srsfilename == None:
        # create file without SRS (spatial reference system)
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format=format)
    else:
        # use SRS (spatial reference system) from another image
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format=format, prototype=gdal.Open(srsfilename))

    # set no data value
    if nodatavalue != None:
        # set GDAL no data value
        for band in [datasource.GetRasterBand(b+1) for b in range(datasource.RasterCount)]:
            band.SetNoDataValue(nodatavalue)
        # set ENVI data ignore value
        datasource.SetMetadataItem('data_ignore_value', str(nodatavalue), 'ENVI')
        datasource.FlushCache()
    datasource = None

class GDALMetaDomain():

    def __init__(self, name):
        self.name = name
        self.meta = dict()

    def formatKey(self, key):
        return key.lower().replace(' ', '_')

    def setMetadataDict(self, metaDict, update=True):

        if update is False:
            self.meta = dict()
        for key, value in metaDict.items():
            self.setMetadataItem(key, value)

    def setMetadataDictAsString(self, meta, update=True):

        if update is False:
            self.meta = dict()
        for key, value in meta.items():
            self.setMetadataItemAsString(key, value)

    def setMetadataItem(self, key, value):

        key = self.formatKey(key)
        self.meta[key] = value
        if value is None:
            del self.meta[key]

    def delMetadataItem(self, key):
        self.setMetadataItem(key=key, value=None)

    def setMetadataItemAsString(self, key, string):

        key = self.formatKey(key)
        value = self.convertStringToValue(key, string)
        self.setMetadataItem(key, value)

    def convertStringToValue(self, key, string):

        key = self.formatKey(key)

        if key == 'coordinate_system_string':
            return string[1:-1]

        # convert arrays
        if string.startswith('{') and string.endswith('}'):
            return string[1:-1].split(',')

        return string.strip(' ')

    def convertValueToString(self, key, value):

        key = self.formatKey(key)

        if key == 'coordinate_system_string':
            return '{' + value + '}'

        if isinstance(value, str):
            return value

        if isinstance(value, collections.Sequence):
            value = map(str, value)
            return '{'+', '.join(value)+'}'

        return str(value)


    def getMetadataDict(self):
        return self.meta

    def getMetadataDictAsString(self):
        meta = dict()
        for key, value in self.meta.items():
            meta[key] = self.convertValueToString(key, value)
        return meta

    def getMetadataItem(self, key, default=None):
        key = self.formatKey(key)
        value = self.meta.get(key, None)
        if value is None:
            return default
        else:
            return value

class GDALColorTable():

    def __init__(self):
        self._colorEntries = [None]*257

    def setSwigColorTable(self, swigColorTable):
        assert isinstance(swigColorTable, gdal.ColorTable)
        for i in range(swigColorTable.GetCount()):
            self.setColorEntry(i, swigColorTable.GetColorEntry(i))

    def getSwigColorTable(self):
        swigColorTable = gdal.ColorTable()
        for i in range(self.getCount()):
            swigColorTable.SetColorEntry(i, self.getColorEntry(i))
        return swigColorTable

    def getColorEntry(self, i):
        assert i >= 0 and i <= 255
        assert self._colorEntries[i] is not None
        return self._colorEntries[i]

    def setColorEntry(self, i, entry):
        assert i >= 0 and i <= 255
        assert isinstance(entry, tuple)
        assert len(entry) == 3 or len(entry) == 4 # (r, g, b) or (r, g, b, , alpha)
        self._colorEntries[i] = entry
        # fill up undefiened entries up to i
        for k in range(i):
            if self._colorEntries[k] is None:
                self._colorEntries[k] = (0,0,0)

    def getCount(self):
        return self._colorEntries.index(None)

    def getRGBFlatList(self):
        rgb = list()
        for rgba in self._colorEntries:
            if rgba is None:
                break
            rgb.extend(rgba[:-1])
        return rgb

class GDALMeta():

    def __init__(self, filename=None):
        self.domain = dict()
        self.filename = filename
        self.colorTable = GDALColorTable()
        self.categoryNames = None
        if filename is not None:
            self.readMeta(filename)

    def readMeta(self, filename):
        self.filename = filename
        ds = gdal.Open(filename)

        if ds is None:
            raise Exception('Can not open file: '+filename)

        # read data source meta
        self.driver = ds.GetDriver().ShortName
        if ds.GetMetadataDomainList() is not None:
            for domainName in ds.GetMetadataDomainList():
                domain = GDALMetaDomain(domainName)
                self.domain[domainName] = domain
                domain.setMetadataDictAsString(ds.GetMetadata(domainName))

        # read band specific meta
        bandNames = list()
        for i in range(1, ds.RasterCount + 1):
            rb = ds.GetRasterBand(i)
            bandName = rb.GetDescription()
            if bandName == '':
                bandName = 'Band ' + str(i)
            bandNames.append(bandName)
        self.setMetadataItem('band names', bandNames)

        # Treat a single band image with color table and category names like an ENVI Classification image.
        # Number of classes must be infered from the number of categories, because color tables from GTiff always
        # contain 256 entries. If the category names are undefined, the image is not a valid classification image!
        if ds.RasterCount == 1:
            rb = ds.GetRasterBand(1)
            if rb.GetCategoryNames() is not None:
                self.colorTable.setSwigColorTable(rb.GetColorTable())
                self.categoryNames = rb.GetCategoryNames()

                classNames = self.categoryNames
                classes = len(classNames)
                classLookup = self.colorTable.getRGBFlatList()[0:3*classes+1] # must trim color vector because color table might contain fill values for all 256 categories (problem occurs for GTiff only)

                self.setMetadataItem('file type', 'ENVI Classification')
                self.setMetadataItem('classes', classes)
                self.setMetadataItem('class names', classNames)
                self.setMetadataItem('class lookup', classLookup)

        self.ProjectionRef = ds.GetProjectionRef()
        self.GeoTransform = ds.GetGeoTransform()
        self.RasterXSize = ds.RasterXSize
        self.RasterYSize = ds.RasterYSize
        self.RasterCount = ds.RasterCount
        self.pixelXSize = self.GeoTransform[1]
        self.pixelYSize = self.GeoTransform[5]
        self.xmin = self.GeoTransform[0]-self.GeoTransform[2]
        self.ymin = self.GeoTransform[3]-self.GeoTransform[4]
        self.xmax = self.xmin+self.RasterXSize*self.pixelXSize
        self.ymax = self.ymin+self.RasterXSize*self.pixelYSize
        self.boundingBox  = [self.xmin, self.ymin, self.xmax, self.ymax]
        self.boundingBox2 = [self.xmin, self.ymax, self.xmax, self.ymin]

    def writeMeta(self, filename):

        ds = gdal.Open(filename, gdal.GA_Update)
        if ds is None:
            raise Exception('Unable to open '+filename)

        # write color table and category names only for single band images
        if ds.RasterCount == 1:
            rb = ds.GetRasterBand(1)
            if self.colorTable.getCount() > 0:
                rb.SetColorTable(self.colorTable.getSwigColorTable())
            if self.categoryNames is not None:
                rb.SetCategoryNames(self.categoryNames)

        # set metadata domains
        for domainName, domain in self.domain.items():
            meta = domain.getMetadataDictAsString()
            ds.SetMetadata(meta, domainName)

        # prepare band specific information
        noDataValue = self.getNoDataValue()
        bandNames = self.getBandNames()
        for i in range(1, ds.RasterCount+1):
            rb = ds.GetRasterBand(i)
            if noDataValue is not None:
                rb.SetNoDataValue(noDataValue)
            if bandNames is not None:
                bandName = bandNames[i-1]
                rb.SetDescription(bandName)
                self.setMetadataItem('band_'+str(i), bandName, domainName='') # this will also overwrite the "band names" value in the ENVI domain


        # driver specific manipulations
        if self.driver == 'ENVI':
            # workaround to eliminate duplicated keys inside ENVI header files produced by GDAL
            # Inside the resulting header file the duplicate that appeared last is used
            hdrfile = ds.GetFileList()[-1]
            ds.FlushCache()
            ds = None
            hdr = hub.envi.readHeader(hdrfile)
            # GDAL skips some metadata when writing the HDR file, don't know why
            for key in ['file type','class names']:
                hdr[key] = self.getMetadataItem(key)
            hub.envi.writeHeader(hdrfile, hdr)
        else:
            ds.FlushCache()
            ds = None
        if self.driver == 'GTiff':
            # Create an additional ENVI header to let ENVI know about important metadata like e.g. wavelength and band names.
            hdrfile = self.filename+'.hdr'
            hdr = self.getMetadataDict()
            hdr['file type'] = 'TIFF'
            hdr['samples'] = self.RasterXSize
            hdr['lines'] = self.RasterYSize
            hdr['bands'] = self.RasterCount
            hub.envi.writeHeader(hdrfile, hdr)

        # create


    def getMetadataDomain(self, domainName='ENVI'):

        if domainName in self.domain:
            domain = self.domain[domainName]
        else:
            domain = GDALMetaDomain(domainName)
            self.domain[domainName] = domain

        assert isinstance(domain, GDALMetaDomain)
        return domain

    def setMetadataDict(self, value, domainName='ENVI', update=True):
        domain = self.getMetadataDomain(domainName)
        domain.setMetadataDict(value, update)

    def getMetadataDict(self, domainName='ENVI'):
        domain = self.getMetadataDomain(domainName)
        return domain.getMetadataDict()

    def getMetadataDomainList(self):
        return self.domain.keys()

    def setMetadataItem(self, key, value, domainName='ENVI'):
        domain = self.getMetadataDomain(domainName)
        domain.setMetadataItem(key, value)

    def delMetadataItem(self, key, domainName='ENVI'):
        domain = self.getMetadataDomain(domainName)
        domain.delMetadataItem(key)

    def copyMetadataItem(self, key, gdalMeta, domainName='ENVI'):

        value = gdalMeta.getMetadataItem(key, default=None, domainName=domainName)
        self.setMetadataItem(key, value, domainName=domainName)

    def getMetadataItem(self, key, default=None, domainName='ENVI'):

        domain = self.getMetadataDomain(domainName)
        return domain.getMetadataItem(key, default)

    def setNoDataValue(self, value):

        domain = self.getMetadataDomain(domainName='ENVI')
        domain.setMetadataItem('data ignore value', value)
        return self

    def getNoDataValue(self, default=None):

        domain = self.getMetadataDomain(domainName='ENVI')
        if domain.getMetadataItem('file type', default='').lower() == 'envi classification':
            noDataValue = 0
        else:
            noDataValue = domain.getMetadataItem('data ignore value', default=default)

        if noDataValue is not None:
            noDataValue = float(noDataValue)

        return noDataValue

    def setBandNames(self, values):

        if values is None: return
        self.getMetadataDomain(domainName='ENVI').setMetadataItem('band names', values)

    def getBandNames(self):
        bandNames = self.getMetadataDomain(domainName='ENVI').getMetadataItem('band names', default=None)
        if bandNames is None:
            bandNames = ['Band '+str(i) for i in range(1, self.RasterCount+1)]
        return bandNames

    def getAcquisitionDate(self):
        date = Date.fromText(self.getMetadataItem('acqdate'))
        return date

if __name__ == '__main__':

    infilename = r'c:\work\data\Hymap_Berlin-A_Classification-GroundTruth'
    outfilename = r'c:\work\data\iotest'

    # read/write image
    # - ENVI to GTiff
    cube = readCube(infilename).astype(numpy.uint8)
    writeCube(cube, outfilename+'.tif', srsfilename=infilename, format='GTiff')
    meta = GDALMeta(infilename)

    # - delete all ENVI Classification meta
    meta.delMetadataItem('classes')
    meta.delMetadataItem('class names')
    meta.delMetadataItem('class lookup')
    meta.delMetadataItem('file type')

    # - add GDAL color table and category meta
    meta.categoryNames = ['undef', 'c1', 'c2', 'c3', 'c4', 'c5']
    meta.colorTable.setColorEntry(0, (0, 0, 0))
    meta.colorTable.setColorEntry(1, (255, 0, 0))
    meta.colorTable.setColorEntry(2, (0, 255, 0))
    meta.colorTable.setColorEntry(3, (0, 0, 255))
    meta.colorTable.setColorEntry(4, (0, 255, 0))
    meta.colorTable.setColorEntry(5, (255, 0, 0))

    meta.writeMeta(outfilename+'.tif')

    # - GTiff back to ENVI
    writeCube(cube, outfilename+'.img', srsfilename=infilename, format='ENVI')
    meta = GDALMeta(outfilename+'.tif')
    meta.writeMeta(outfilename+'.img')


