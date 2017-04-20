from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Dataset import Dataset
from hubdc import CreateFromArray

class ApplierOperator(object):

    def __init__(self, grid, inputs):
        assert isinstance(grid, PixelGrid)
        self.grid = grid
        self.inputs = inputs
        self.outputs = dict()

    def getDataset(self, name):
        dataset = self.inputs[name]
        assert isinstance(dataset, Dataset)
        return dataset

    def setDataset(self, name, array):
        array = array if array.ndim == 3 else array[None]
        outDS = CreateFromArray(pixelGrid=self.grid, array=array)
        self.outputs[name] = outDS
        return outDS

    def getImage(self, name, bandIndex=None, dtype=None):
        if bandIndex is None:
            return self.getDataset(name).readAsArray(dtype=dtype)
        else:
            return self.getDataset(name).getBand(bandNumber=bandIndex+1).readAsArray(dtype=dtype)

    def setImage(self, name, array):
        self.setDataset(name=name, array=array)

    def setMetadataItem(self, name, key, value, domain):
        dataset = self.getDataset(name=name)
        dataset.setMetadataItem(key=key, value=value, domain=domain)

    def ufunc(self):
        raise NotImplementedError()