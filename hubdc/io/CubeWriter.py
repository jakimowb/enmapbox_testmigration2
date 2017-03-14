from os.path import exists, dirname
from os import makedirs
from osgeo import gdal
from hubdc.model.Dataset import Dataset


class CubeWriter(object):

    def __init__(self, driverName='GTiff', creationOptions=None):

        self.driverName = driverName
        self.creationOptions = creationOptions
        self.filenames = list()
        self.datasets = list()

    def __iter__(self):
        for dataset, filename in zip(self.datasets, self.filenames):
            assert isinstance(dataset, Dataset)
            yield dataset, filename

    def addDataset(self, filename, dataset):
        assert isinstance(dataset, Dataset)
        self.filenames.append(filename)
        self.datasets.append(dataset)

    def write(self):

        for dataset, filename in self.__iter__():
            if not exists(dirname(filename)):
                makedirs(dirname(filename))
            strict = 1
            outDataset = gdal.GetDriverByName(self.driverName).CreateCopy(filename, dataset.gdalDataset, strict, options=self.creationOptions)
            del outDataset
