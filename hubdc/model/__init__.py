from os import makedirs
from os.path import dirname, exists
from osgeo import gdal, gdal_array
import numpy
from .Dataset import Dataset
from .DatasetList import DatasetList

def Open(filename, eAccess=gdal.GA_ReadOnly):
    return Dataset(gdal.Open(filename, eAccess))

def OpenDSL(filenames):
    return DatasetList([Open(filename) for filename in filenames])

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
    assert isinstance(array, numpy.ndarray)
    assert array.ndim == 3
    bands = len(array)
    eType = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
    dataset = Create(pixelGrid, bands=bands, eType=eType, dstName=dstName, format=format, creationOptions=creationOptions)
    dataset.writeArray(array=array, pixelGrid=pixelGrid)
    return dataset