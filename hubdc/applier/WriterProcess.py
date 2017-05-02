from osgeo import gdal
from multiprocessing import Process, Queue
from time import sleep
from hubdc import CreateFromArray
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.ApplierOutput import ApplierOutput

class WriterProcess(Process):

    CREATE_DATASET, WRITE_ARRAY, FLUSH_CACHE, SET_META, SET_NODATA, CLOSE_DATASETS = range(6)


    def __init__(self, grid, outputs):
        Process.__init__(self)
        assert isinstance(grid, PixelGrid)
        assert isinstance(outputs, dict)
        self.grid = grid
        self.outputs = outputs
        self.outputDatasets = dict()
        self.queue = Queue()

    def run(self):

        while True:

            sleep(0.250) # this should prevent high CPU load during idle time (not sure if this is really needed)

            value = self.queue.get()
            task, args = value[0], value[1:]
            if value[0] == self.CREATE_DATASET:
                self._createDataset(*args)
            elif value[0] == self.WRITE_ARRAY:
                self._writeArray(*args)
            elif value[0] == self.FLUSH_CACHE:
                self._flushCache(*args)
            elif value[0] == self.SET_META:
                self._setMetadataItem(*args)
            elif value[0] == self.SET_NODATA:
                self._setNoDataValue(*args)
            elif value[0] == self.CLOSE_DATASETS:
                self._closeDatasets()
                break
            else:
                raise ValueError(str(value))

    def _createDataset(self, name, array):
        self.outputDatasets[name] = CreateFromArray(pixelGrid=self.grid, array=array,
                                                   dstName=self.outputs[name].filename,
                                                   format=self.outputs[name].format,
                                                   creationOptions=self.outputs[name].creationOptions)

    def _closeDatasets(self):
        for name, outputDataset in self.outputDatasets.items():
            outputDataset.writeENVIHeader()
            outputDataset.close()

    def _writeArray(self, name, array, grid):
        self.outputDatasets[name].writeArray(array=array, pixelGrid=grid)
        self._flushCache(name)

    def _flushCache(self, name):
        self.outputDatasets[name].flushCache()

    def _setMetadataItem(self, name, key, value, domain):
        self.outputDatasets[name].setMetadataItem(key=key, value=value, domain=domain)
        if key=='band names' and domain=='ENVI':
            for dsBand, bandName in zip(self.outputDatasets[name], value):
                dsBand.setDescription(bandName)

    def _setNoDataValue(self, name, value):
        for dsBand in self.outputDatasets[name]:
            dsBand.setNoDataValue(value)

    def closeDatasets(self):
        self.queue.put([self.CLOSE_DATASETS])
        self.join()
        self.terminate()
