__author__ = 'janzandr'
import gdal, numpy, osgeo, hub.file, yaml, hub.envi
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

def readCube(filename):
    driver = gdal.GetDriverByName('MEM')
    dataset = driver.CreateCopy('', gdal.Open(filename))
    cube = dataset.ReadAsArray(xoff=0, yoff=0, xsize=dataset.RasterXSize, ysize=dataset.RasterYSize)
    return cube

def writeCube(cube, filename, srsfilename=None, nodatavalue=None):
    hub.file.mkfiledir(filename)
    #bands, lines, samples  = cube.shape
    '''
    GDALType = osgeo.gdal_array.NumericTypeCodeToGDALTypeCode(cube.dtype)
    driver = gdal.GetDriverByName('ENVI')
    dataset = driver.Create(filename, samples, lines, bands, GDALType)
    for i in range(bands):
        band = dataset.GetRasterBand(i + 1)
        band.WriteArray(cube[i])
    dataset = None
    '''
    if srsfilename == None:
        datasource = osgeo.gdal_array.SaveArray(cube, filename, format='ENVI')
    else:
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

    def setMetadataItem(self, key, value): self.metadata[key] = value
    def getMetadataItem(self, key): return self.metadata[key]

class GDALMeta():

    def __init__(self, filename):
        if filename is not None: self.readMeta(filename)

    def __getitem__(self, i):
        return self.rb[i]

    def readMeta(self, filename):
        ds = gdal.Open(filename)

        # read data source meta
        self.domain = Bunch()
        for domain in ds.GetMetadataDomainList():
            self.domain[domain if domain != '' else 'DEFAULT'] = Bunch(ds.GetMetadata(domain))

        # read band meta
        self.rb = list()
        for band in range(1,ds.RasterCount+1):
            self.rb.append(GDALBandmeta(ds.GetRasterBand(band)))

        ds = None

    def writeMeta(self, filename):

        ds = gdal.Open(filename, GA_Update)
        print 'write:', filename, ds.GetFileList()

        ds.SetDescription(self.ds.description) # note that this will alter the filename returned by ds.GetFileList(), which is strange


        for domain, bunch in self.ds.domain.items():
            # convert values to string
            bunch = {key:str(value) for key,value in bunch.items()} # this also makes a copy of the bunch!
            # for ENVI domain replace [] with {} if needed
            if domain == 'ENVI':
                for key, value in bunch.items():
                    if value[0] == '[' and value[-1] == ']':
                        bunch[key] = '{'+value[1:-1]+'}'

            ds.SetMetadata(bunch, domain if domain != 'DEFAULT' else '')

        for band in range(1,ds.RasterCount+1):
            rb = ds.GetRasterBand(band)
            rb.SetDescription(self.rb[band-1].description)
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
            hub.envi.writeHeader(hdrfile, hdr)
        else:
            ds.FlushCache()
            ds = None

    def setMetadataDict(self, value, domain='ENVI'): self.domain[domain] = value
    def getMetadataDict(self, domain='ENVI'): return self.domain[domain]

    def setMetadataItem(self, key, value, domain='ENVI'):
        if not self.domain.has_key(domain): self.domain[domain] = Bunch()
        self.domain[domain][key] = value
    def getMetadataItem(self, key, domain): return self.domain[domain][key]

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
