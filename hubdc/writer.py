from osgeo import gdal, gdal_array
from multiprocessing import Process, Queue
from time import sleep
import numpy
from hubdc.model import Create, Dataset, Band

class Writer():
    WRITE_IMAGEARRAY, WRITE_BANDARRAY, CALL_IMAGEMETHOD, CALL_BANDMETHOD, CLOSE_DATASETS, CLOSE_WRITER = range(6)

    @classmethod
    def getDatasets(cls, outputDatasets, filename):
        ds = outputDatasets[filename]
        assert isinstance(ds, Dataset)
        return ds

    @classmethod
    def handleTask(cls, task, args, outputDatasets):
        if task is cls.WRITE_IMAGEARRAY:
            cls.writeImageArray(outputDatasets, *args)
        elif task is cls.WRITE_BANDARRAY:
            cls.writeBandArray(outputDatasets, *args)
        elif task is cls.CALL_IMAGEMETHOD:
            cls.callImageMethode(outputDatasets, *args)
        elif task is cls.CALL_BANDMETHOD:
            cls.callBandMethode(outputDatasets, *args)
        elif task is cls.CLOSE_DATASETS:
            cls.closeDatasets(outputDatasets, *args)
        elif task is cls.CLOSE_WRITER:
            pass
        else:
            raise ValueError(str(task))

    @staticmethod
    def createDataset(outputDatasets, filename, bands, dtype, grid, format, creationOptions):
        outputDatasets[filename] = Create(grid=grid, bands=bands,
                                          eType=gdal_array.NumericTypeCodeToGDALTypeCode(dtype),
                                          filename=filename, format=format, creationOptions=creationOptions)

    @staticmethod
    def closeDatasets(outputDatasets, createEnviHeader):
        for filename, ds in outputDatasets.items():
            outputDataset = outputDatasets.pop(filename)
            outputDataset.flushCache()
            if createEnviHeader:
                outputDataset.writeENVIHeader()
            outputDataset.close()

    @classmethod
    def writeImageArray(cls, outputDatasets, filename, array, subgrid, maingrid, format, creationOptions):

        if filename not in outputDatasets:
            Writer.createDataset(outputDatasets=outputDatasets, filename=filename, bands=len(array), dtype=array.dtype, grid=maingrid, format=format, creationOptions=creationOptions)
        cls.getDatasets(outputDatasets, filename).writeArray(array=array, grid=subgrid)

    @classmethod
    def writeBandArray(cls, outputDatasets, filename, array, index, bands, subgrid, maingrid, format, creationOptions):

        if filename not in outputDatasets:
            Writer.createDataset(outputDatasets=outputDatasets, filename=filename, bands=bands, dtype=array.dtype, grid=maingrid, format=format, creationOptions=creationOptions)
        cls.getDatasets(outputDatasets, filename).band(index=index).writeArray(array=array, grid=subgrid)

    @classmethod
    def callImageMethode(cls, outputDatasets, filename, method, kwargs):
        getattr(*method)(cls.getDatasets(outputDatasets, filename), **kwargs)

    @classmethod
    def callBandMethode(cls, outputDatasets, filename, index, method, kwargs):
        getattr(*method)(cls.getDatasets(outputDatasets, filename).band(index=index), **kwargs)

class WriterProcess(Process):

    def __init__(self):
        Process.__init__(self)
        self.outputDatasets = dict()
        self.queue = Queue()

    def run(self):

        try:
            gdal.SetCacheMax(1)
            while True:

                sleep(0.01) # this should prevent high CPU load during idle time (not sure if this is really needed)
                if self.queue.qsize() == 0:
                    continue
                value = self.queue.get()
                task, args = value[0], value[1:]
                Writer.handleTask(task=task, args=args, outputDatasets=self.outputDatasets)
                if task is Writer.CLOSE_WRITER:
                    break

        except:

            import traceback
            tb = traceback.format_exc()
            print(tb)

class QueueMock():

    def __init__(self):
        self.outputDatasets = dict()

    def put(self, value):
        task, args = value[0], value[1:]
        Writer.handleTask(task=task, args=args, outputDatasets=self.outputDatasets)
