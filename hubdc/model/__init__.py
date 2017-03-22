from osgeo import gdal
from .Dataset import Dataset
from .DatasetList import DatasetList

def Open(filename):
    return Dataset(gdal.Open(filename))

def OpenDSL(filenames):
    return DatasetList([Open(filename) for filename in filenames])

