from osgeo import gdal
from hubdc.model.Dataset import Dataset
from hubdc.model.PixelGrid import PixelGrid

class DatasetList():

    def __init__(self, datasets=None):
        self.datasets = []
        if datasets is not None:
            for dataset in datasets:
                self.append(dataset)

    def __iter__(self):
        for dataset in self.datasets:
            assert isinstance(dataset, Dataset)
            yield dataset

    def __len__(self):
        return len(self.datasets)

    def append(self, dataset):
        assert isinstance(dataset, Dataset)
        self.datasets.append(dataset)

    def readAsArray(self):
        for dataset in self:
            yield dataset.readAsArray()
