from rios.imageio import NumpyTypeToGDALType
from osgeo import gdal
from hubdc.model.Band import Band


class Dataset():

    @staticmethod
    def fromArray(array, referenceGrid):
        driver = gdal.GetDriverByName('MEM')
        bands, ysize, xsize = array.shape
        gdalDataset = driver.Create('', xsize, ysize, bands, NumpyTypeToGDALType(array.dtype))
        assert isinstance(gdalDataset, gdal.Dataset)
        gdalDataset.SetProjection(referenceGrid.projection)
        gdalDataset.SetGeoTransform(referenceGrid.makeGeoTransform())
        for i, band in enumerate(array):
            rb = gdalDataset.GetRasterBand(i + 1)
            assert isinstance(rb, gdal.Band)
            rb.WriteArray(band)
        return Dataset(gdalDataset=gdalDataset)

    def __init__(self, gdalDataset):
        assert isinstance(gdalDataset, gdal.Dataset)
        self.gdalDataset = gdalDataset

    def __call__(self, bandNumber):
        return self.getBand(bandNumber)

    def getBand(self, bandNumber):
        return Band(self.gdalDataset.GetRasterBand(bandNumber))

    def setNoDataValue(self, value):
        for band in (self.getBand(i+1) for i in range(self.gdalDataset.RasterCount)):
            band.setNoDataValue(value)