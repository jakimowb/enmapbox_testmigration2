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
        return [dataset.readAsArray() for dataset in self]

    def translate(self, dstPixelGrid=None, dstName=None, format='MEM', creationOptions=[], **kwargs):
        dstNames = dstName
        if dstNames is None or dstNames == '':
            dstNames = ['']*len(self)

        translated = DatasetList([dataset.translate(dstPixelGrid=dstPixelGrid, dstName=dstName, format=format, creationOptions=creationOptions, **kwargs)
                           for dataset, dstName in zip(self, dstNames)])

        return translated

    def buildVRT(self, dstPixelGrid, dstName, **kwargs):
        assert isinstance(dstPixelGrid, PixelGrid)
        options = gdal.BuildVRTOptions(resolution='user',
                                       outputBounds=tuple(getattr(dstPixelGrid, key) for key in ('xMin', 'yMin', 'xMax', 'yMax')),
                                       xRes=dstPixelGrid.xRes, yRes=dstPixelGrid.yRes, **kwargs)
        gdalDS = gdal.BuildVRT(destName=dstName, srcDSOrSrcDSTab=[ds.gdalDataset for ds in self])
        return Dataset(gdalDS)
