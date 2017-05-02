from rios.imageio import NumpyTypeToGDALType
from osgeo import gdal
import numpy
from hubdc.model.Band import Band
from hubdc.model.PixelGrid import PixelGrid
from os import makedirs
from os.path import exists, dirname

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

    def readAsArray(self, dtype=None, scale=None, **kwargs):
        array = self.gdalDataset.ReadAsArray(**kwargs)
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

    def setNoDataValue(self, value):
        for band in self:
            band.setNoDataValue(value)

    def getMetadataDomainList(self):
        domains = self.gdalDataset.GetMetadataDomainList()
        return domains if domains is not None else []

    def setMetadataItem(self, key, value, domain=''):
        gdalString = GDALStringFormatter.valueToGDALString(value)
        self.gdalDataset.SetMetadataItem(key, gdalString, domain)

    def getMetadataItem(self, key, domain='', type=str):
        gdalString = self.gdalDataset.GetMetadataItem(key, domain)
        return GDALStringFormatter.gdalStringToValue(gdalString, type=type)

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
        if self.getFormat() == 'GTiff':
            self.writeENVIHeaderForGTiff()

    def writeENVIHeaderForGTiff(self):

        envi = self.getMetadataDomain(domain='ENVI')

        envi['file type'] = 'TIFF'
        envi['samples'] = self.gdalDataset.RasterXSize
        envi['lines'] = self.gdalDataset.RasterYSize
        envi['bands'] = self.gdalDataset.RasterCount

        keys = ['description', 'samples', 'lines', 'bands', 'header offset', 'file type', 'data type',
                'interleave', 'data ignore value',
                'sensor type', 'byte order', 'map info', 'projection info', 'coordinate system string',
                'acquisition time',
                'wavelength units', 'wavelength', 'band names']

        values = [envi.pop(key, None) for key in keys]


        filename = self.gdalDataset.GetFileList()[0]
        with open(filename+'.hdr', 'w') as f:
            f.write('ENVI\n')
            for key, value in zip(keys+envi.keys(), values+envi.values()):
                if value is not None:
                    f.write('{key} = {value}\n'.format(key=key, value=value))


    def warp(self, dstPixelGrid, dstName='', format='MEM', creationOptions=[], **kwargs):

        assert isinstance(dstPixelGrid, PixelGrid)

        xRes, yRes, dstSRS = (getattr(dstPixelGrid, key) for key in ('xRes', 'yRes', 'projection'))
        outputBounds = tuple(getattr(dstPixelGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax'))

        if format != 'MEM' and not exists(dirname(dstName)):
            makedirs(dirname(dstName))

        warpOptions = gdal.WarpOptions(format=format, outputBounds=outputBounds, xRes=xRes, yRes=yRes, dstSRS=dstSRS, creationOptions=creationOptions, **kwargs)
        gdalDataset = gdal.Warp(destNameOrDestDS=dstName, srcDSOrSrcDSTab=self.gdalDataset, options=warpOptions)
        return Dataset(gdalDataset=gdalDataset)

    def translate(self, dstPixelGrid=None, dstName='', format='MEM', creationOptions=[], **kwargs):

        if dstPixelGrid is None:
            dstPixelGrid = self.pixelGrid

        assert isinstance(dstPixelGrid, PixelGrid)
        assert self.pixelGrid.equalProjection(dstPixelGrid)

        if format!='MEM' and not exists(dirname(dstName)):
            makedirs(dirname(dstName))

        ulx, uly, lrx, lry, xRes, yRes = tuple(getattr(dstPixelGrid, key) for key in ('xMin', 'yMax', 'xMax', 'yMin', 'xRes', 'yRes'))
        translateOptions = gdal.TranslateOptions(format=format, projWin=[ulx, uly, lrx, lry], xRes=xRes, yRes=yRes,  creationOptions=creationOptions, **kwargs)
        gdalDataset = gdal.Translate(destName=dstName, srcDS=self.gdalDataset, options=translateOptions)
        return Dataset(gdalDataset=gdalDataset)

    @property
    def shape(self):
        return self.gdalDataset.RasterCount, self.gdalDataset.RasterYSize, self.gdalDataset.RasterXSize

class GDALStringFormatter(object):

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
            return cls._gdalStringToList(gdalString, type)

    @classmethod
    def _listToGDALString(cls, values):
        return '{'+','.join([str(v) for v in values])+'}'

    @classmethod
    def _gdalStringToList(cls, gdalString, type):
        values = [type(v) for v in gdalString[1:-1].split(',')]
        return values
