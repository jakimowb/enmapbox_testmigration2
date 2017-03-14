from osgeo import gdal
from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Dataset import Dataset

class Cube(object):

    def __init__(self, referenceGrid):

        assert isinstance(referenceGrid, PixelGrid)
        self.referenceGrid = referenceGrid
        self.datasets = list()
        self.keys = list()

    def __getitem__(self, key):
        return self.getArray(key)

    def __setitem__(self, key, array):
        ds = Dataset.fromArray(array=array, referenceGrid=self.referenceGrid)
        self.addDataset(dataset=ds, key=key)

    def __call__(self, key):
        return self.getDataset(key)

    def addDataset(self, dataset, key=None):

        assert isinstance(dataset, Dataset)
        referenceGrid = PixelGrid.fromDataset(dataset)
        assert self.referenceGrid.equalProjection(referenceGrid), 'projection mismatch'
        assert self.referenceGrid.makeGeoTransform() == referenceGrid.makeGeoTransform(), 'geo transform mismatch'
        self.datasets.append(dataset)
        self.keys.append(key)

    def getDataset(self, key):
        ds = self.datasets[self.keys.index(key)]
        assert isinstance(ds, Dataset)
        return ds

    def getArray(self, key):
        array = self.getDataset(key).gdalDataset.ReadAsArray()
        if array.ndim == 2:
            array = array.reshape(1, *array.shape)
        return array
