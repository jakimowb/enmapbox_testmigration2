from __future__ import print_function
import gdal, numpy, osgeo, hub.file, hub.envi
import collections
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

def writeCube(cube, filename, srsfilename=None, nodatavalue=None):

    hub.file.mkfiledir(filename)

    if srsfilename == None:
        # create file without SRS (spatial reference system)
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format='ENVI')
    else:
        # use SRS (spatial reference system) from another image
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format='ENVI', prototype=gdal.Open(srsfilename))

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

    def setMetadataDict(self, meta, update=True):

        if update is False:
            self.meta = dict()
        for key, value in meta.items():
            self.setMetadataItem(key, value)

    def setMetadataDictAsString(self, meta, update=True):

        if update is False:
            self.meta = dict()
        for key, value in meta.items():
            self.setMetadataItemAsString(key, value)

    def setMetadataItem(self, key, value):

        key = self.formatKey(key)
        self.meta[key] = value

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
        return self.meta.get(key, default)

class GDALMeta():

    def __init__(self, filename=None):
        self.domain = dict()
        self.filename = filename
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

        for domainName, domain in self.domain.items():
            meta = domain.getMetadataDictAsString()
            ds.SetMetadata(meta, domainName)


        # Workaround to eliminate duplicated keys inside ENVI header files produced by GDAL
        # Inside the resulting header file the duplicate that appeared last is used
        if ds.GetDriver().ShortName == 'ENVI':
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

    def getMetadataDomain(self, domainName):

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

    def copyMetadataItem(self, key, gdalMeta, domainName='ENVI'):

        value = gdalMeta.getMetadataItem(key, default=None, domainName=domainName)
        self.setMetadataItem(key, value, domainName=domainName)

    def getMetadataItem(self, key, default=None, domainName='ENVI'):

        domain = self.getMetadataDomain(domainName)
        return domain.getMetadataItem(key, default)

    def setNoDataValue(self, value):

        domain = self.getMetadataDomain(domainName='ENVI')
        domain.setMetadataItem('data ignore value', value)

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

        if values is None:
            return

        self.getMetadataDomain(domainName='ENVI').setMetadataItem('band names', values)


if __name__ == '__main__':
    #meta = GDALMeta(r'D:\work\EnMap-Box\EnMAP-Box_1.4\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Image')

    infilename = r'c:\work\data\Hymap_Berlin-A_Classification-GroundTruth'
    outfilename = r'c:\work\data\iotest'

    # read/write cube
    cube = readCube(infilename)
    writeCube(readCube(infilename), outfilename)

    # copy metadata

    meta = GDALMeta(infilename)

    # set data source metas
    meta.setMetadataDict({'key1':'hello 1', 'key2':'hello 2'}) # this goes to the ENVI domain per default
    meta.setMetadataItem('key3', 'hello 3') # this goes to the ENVI domain per default
    meta.setMetadataItem('key4', 'hello 4', 'myDomain')
    print(meta.getMetadataDict()) # this comes from ENVI domain per default
    print(meta.getMetadataDict('myDomain'))

    meta.writeMeta(outfilename)
