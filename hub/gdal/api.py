__author__ = 'janzandr'
import gdal, numpy, osgeo, hub.file, hub.envi
from gdalconst import *
from hub.collections import Bunch

def geoInfo(file):
    result = Bunch()
    dataset = gdal.Open(file, GA_ReadOnly)
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


class GDALBandmeta():

    def __init__(self, rb=None):
        self.setDescription(None)
        self.setNoDataValue(None)
        self.setCategoryNames(None)
        self.setColorInterpretation(None)
        self.setColorTable(None)
        self.setMetadataDict(Bunch())
        if rb is not None: self.readMeta(rb)

    def readMeta(self, rb):
        self.description = rb.GetDescription()
        self.noDataValue = rb.GetNoDataValue()
        self.categoryNames = rb.GetRasterCategoryNames()
        self.colorInterpretation = rb.GetRasterColorInterpretation()
        self.colorTable = [rb.GetColorTable().GetColorEntry(i) for i in range(len(self.categoryNames))] if self.categoryNames is not None else None
        self.metadata = Bunch(rb.GetMetadata_Dict())

    def setDescription(self, value): self.description = value
    def getDescription(self): return self.description

    def setNoDataValue(self, value): self.noDataValue = value
    def getNoDataValue(self): return self.noDataValue

    def setCategoryNames(self, value): self.categoryNames = value
    def getCategoryNames(self): return self.categoryNames

    def setColorInterpretation(self, value): self.colorInterpretation = value
    def getColorInterpretation(self): return self.colorInterpretation

    def setColorTable(self, value): self.colorTable = value
    def getColorTable(self): return self.colorTable

    def setMetadataDict(self, value): self.metadata = value
    def getMetadataDict(self): return self.metadata

    def setMetadataItem(self, key, value): self.metadata[key] = str(value)
    def getMetadataItem(self, key): return self.metadata[key]

class GDALMeta():

    def __init__(self, filename):
        if filename is not None: self.readMeta(filename)

    def __getitem__(self, i):
        return self.rb[i]

    def readMeta(self, filename):
        ds = gdal.Open(filename)

        if ds is None:
            Exception('Can not open file: '+filename)

        # read data source meta
        self.driver = ds.GetDriver().ShortName
        self.domain = Bunch()
        if ds.GetMetadataDomainList() is not None:
            for domain in ds.GetMetadataDomainList():
                self.domain[domain if domain != '' else 'DEFAULT'] = Bunch(ds.GetMetadata(domain))
                if domain == 'ENVI':
                    # convert arrays given as strings into lists
                    for k,v in self.domain.ENVI.items():
                        if k in ['coordinate_system_string']: continue
                        isArray = v[0] == '{' and v[-1] == '}'
                        if isArray:
                            v = v[1:-1].split(',')
                            v = [vi.strip(" '") for vi in v]
                        else:
                            v = v.strip(' ')
                        self.domain.ENVI[k] = v
                        #if v[0] == '{' and v[-1] == '}': v = '['+v[1:-1]+']'
                        #self.domain.ENVI[k] = yaml.load(v)

        # read band meta
        self.rb = list()
        for band in range(1,ds.RasterCount+1):
            self.rb.append(GDALBandmeta(ds.GetRasterBand(band)))

        #
        self.Projection = ds.GetProjection()
        self.RasterXSize = ds.RasterXSize
        self.RasterYSize = ds.RasterYSize
        self.RasterCount = ds.RasterCount
        self.GeoTransform = ds.GetGeoTransform()
        self.pixelXSize = self.GeoTransform[1]
        self.pixelYSize = self.GeoTransform[5]
        self.xmin = self.GeoTransform[0]-self.GeoTransform[2]
        self.ymin = self.GeoTransform[3]-self.GeoTransform[4]
        self.xmax = self.xmin+self.RasterXSize*self.pixelXSize
        self.ymax = self.ymin+self.RasterXSize*self.pixelYSize
        self.boundingBox  = [self.xmin, self.ymin, self.xmax, self.ymax]
        self.boundingBox2 = [self.xmin, self.ymax, self.xmax, self.ymin]

    def writeMeta(self, filename):

        ds = gdal.Open(filename, GA_Update)
        if ds is None:
            print 'Unable to open '+filename
            raise

        for domain, bunch in self.domain.items():
            # convert values to string
            bunch = {key: '['+', '.join(map(str, value))+']' if hasattr(value,'__iter__') else str(value) for key,value in bunch.items()}
            # for ENVI domain replace [] with {} if needed
            if domain == 'ENVI':
                for key, value in bunch.items():
                    if value[0] == '[' and value[-1] == ']':
                        bunch[key] = '{'+value[1:-1]+'}'

            ds.SetMetadata(bunch, domain if domain != 'DEFAULT' else '')

        for band in range(1,ds.RasterCount+1):
            rb = ds.GetRasterBand(band)
            rb.SetDescription(self.rb[band-1].getDescription())
            rb.SetMetadata(self.rb[band-1].metadata)
            if self.rb[band-1].noDataValue is not None:   rb.SetNoDataValue(float(self.rb[band-1].noDataValue))
            if self.rb[band-1].categoryNames is not None: rb.SetCategoryNames(self.rb[band-1].categoryNames)
            rb.SetColorInterpretation(self.rb[band-1].colorInterpretation)
            ct = gdal.ColorTable()
            if self.rb[band-1].colorTable is not None:
                for i,rgb in zip(range(len(self.rb[band-1].colorTable)),self.rb[band-1].colorTable):
                    ct.SetColorEntry(i, rgb)
                rb.SetColorTable(ct)

        # Workaround to eliminate duplicated keys inside ENVI header files produced bei GDAL
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

    def setMetadataDict(self, value, domain='ENVI'):
        self.domain[domain] = value


    def getMetadataDict(self, domain='ENVI'):
        if self.domain.has_key(domain):
            result = self.domain[domain]
        else:
            result = dict()

        return result

    def createDomain(self, domain):
        if not self.domain.has_key(domain): self.domain[domain] = Bunch()

    def setMetadataItem(self, key, value, domain='ENVI', mapToBands=False):
        key = key.lower().replace(' ','_')
        self.createDomain(domain)
        self.domain[domain][key] = value
        if mapToBands:
            for rb, ivalue in zip(self.rb, value):
                rb.setMetadataItem(key, ivalue)

    def copyMetadataItem(self, key, gdalMeta, domain='ENVI', mapToBands=False):
        value = gdalMeta.getMetadataItem(key, default=None, domain=domain, fromBands=mapToBands)
        self.setMetadataItem(key, value, domain=domain, mapToBands=mapToBands)

    def getMetadataItem(self, key, default=None, domain='ENVI', fromBands=False):
        #key = key.lower().replace(' ','_')
        if fromBands:
            result = list()
            for rb in self.rb:
                result.append(rb.getMetadataItem(key))
        else:
            if domain == 'ENVI': # GDAL casts ENVI keys to all lower letters when writing to disk :-(, need to consider that here
                key = key.replace(' ', '_')
                try:
                    if not self.domain.ENVI.has_key(key):
                        key = key.lower()
                except:
                    pass
                result = self.domain.ENVI.get(key, self.domain.ENVI.get(key.lower(), default))
            else:
                result = self.domain[domain].get(key, default)
        return result

    def setNoDataValue(self, value):
        self.createDomain('ENVI')
        self.domain.ENVI.data_ignore_value = value
        for rb in self.rb:
            rb.setNoDataValue(value)

    def getNoDataValue(self, default=None):
        if self.getMetadataItem('file_type', default='').lower() == 'envi classification':
            noDataValue = 0
        else:
            noDataValue = self.getMetadataItem('data_ignore_value', default)

        return float(noDataValue) if noDataValue is not None else None


    def setBandNames(self, values):

        if values is None:
            return

        for rb, value in zip(self.rb, values):
            rb.setDescription(value)
        self.createDomain('ENVI')
        self.domain.ENVI.band_names = values


if __name__ == '__main__':
    #meta = GDALMeta(r'D:\work\EnMap-Box\EnMAP-Box_1.4\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Image')

    meta = GDALMeta(r'D:\work\EnMap-Box\EnMAP-Box_1.4\EnMAP-Box\enmapProject\lib\hubAPI\resource\testData\image\Hymap_Berlin-A_Classification-GroundTruth')

    # set data source metas
    meta.setMetadataDict({'key1':'hello 1', 'key2':'hello 2'}) # this goes to the ENVI domain per default
    meta.setMetadataItem('key3', 'hello 3') # this goes to the ENVI domain per default
    meta.setMetadataItem('key4', 'hello 4', 'myDomain')
    print meta.getMetadataDict() # this comes from ENVI domain per default
    print meta.getMetadataDict('myDomain')

    # set band metas
    meta[0].setMetadataDict({'key1':'hello 1', 'key2':'hello 2'})
    meta[0].setMetadataItem('key3', 'hello 3')
    print meta[0].getMetadataDict()

#    meta[0].setMetadataItem('key1', 'hello 1')
#    meta[0].metadata.key2 = 'hello 2'
#    print meta[0].getMetadataDict()
    #hub.file.remove(r'T:\ar\copy.hdr')
#    meta.writeMeta(r't:\ar\copy')
    '''

    meta = readMeta(r't:\ar\copy')



    print(type(meta))
    print 'Is correct type?:', isinstance(meta, GDALMeta)
    print
    for k,v in meta.ds.domain.ENVI.items(): print k+':',v

    filename = r'H:\EuropeanDataCube\testCaseAR\cubes\32\32UNB\band2.vrt'
    cube = readCube(filename)
    print(cube.shape)
    writeCube(cube,r't:\testCube.img', filename, nodatavalue=-9999)
    print('...done')
    '''
