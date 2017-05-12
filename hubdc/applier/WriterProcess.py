from osgeo import gdal
import os
from multiprocessing import Process, Queue
from time import sleep
from hubdc import CreateFromArray
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.ApplierOutput import ApplierOutput

class WriterProcess(Process):

    CREATE_DATASET, WRITE_ARRAY, FLUSH_CACHE, SET_META, SET_NODATA, CLOSE_DATASETS, CLOSE_WRITER = range(7)

    def __init__(self):
        Process.__init__(self)
        self.outputDatasets = dict()
        self.queue = Queue()

    def run(self):

        gdal.SetCacheMax(1)
        while True:

            #sleep(0.01) # this should prevent high CPU load during idle time (not sure if this is really needed)

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
                self._closeDatasets(*args)
            elif value[0] == self.CLOSE_WRITER:
                os._exit(0)
            else:
                raise ValueError(str(value))

    def _createDataset(self, filename, array, grid, format, creationOptions):

        self.outputDatasets[filename] = CreateFromArray(pixelGrid=grid, array=array,
                                                    dstName=filename,
                                                    format=format,
                                                    creationOptions=creationOptions)

    def _closeDatasets(self, createEnviHeader):
        sleep(0.25)
        for filename, ds in self.outputDatasets.items():
            outputDataset = self.outputDatasets.pop(filename)
            if createEnviHeader:
                outputDataset.writeENVIHeader()
            outputDataset.flushCache()
            outputDataset.close()

    def _writeArray(self, filename, array, grid):
        self.outputDatasets[filename].writeArray(array=array, pixelGrid=grid)
        self.outputDatasets[filename].flushCache()

    def _setMetadataItem(self, filename, key, value, domain):
        self.outputDatasets[filename].setMetadataItem(key=key, value=value, domain=domain)
        if key=='band names' and domain=='ENVI':
            for dsBand, bandName in zip(self.outputDatasets[filename], value):
                dsBand.setDescription(bandName)

    def _setNoDataValue(self, filename, value):
        for dsBand in self.outputDatasets[filename]:
            dsBand.setNoDataValue(value)

    def _closeWriter(self, createEnviHeader):
        pass
        #for filename in self.outputDatasets.keys():
        #    self.queue.put([self.CLOSE_DATASETS, filename, createEnviHeader])
        #self.queue.put([self.CLOSE_WRITER, None])
