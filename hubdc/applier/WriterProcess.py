from osgeo import gdal
from multiprocessing import Process, Queue
from time import sleep
from hubdc import CreateFromArray
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.ApplierOutput import ApplierOutput

class WriterProcess(Process):

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
            if value is None:
                self._close()
                break
            else:
                self._write(value)

    def _close(self):
        for outputDataset in self.outputDatasets.values():
            outputDataset.close()

    def _write(self, value):
        key, array, grid = value
        if key not in self.outputDatasets:
            output = self.outputs[key]
            self.outputDatasets[key] = CreateFromArray(pixelGrid=self.grid, array=array,
                                                       dstName=output.filename,
                                                       format=output.format,
                                                       creationOptions=output.creationOptions)
        self.outputDatasets[key].writeArray(array=array, pixelGrid=grid)
        self.outputDatasets[key].flushCache()


    def close(self):
        self.queue.put(None)
