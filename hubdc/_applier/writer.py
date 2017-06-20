from osgeo import gdal, gdal_array
from multiprocessing import Process, Queue
from time import sleep
import numpy
from hubdc.model import Create

class Writer():

    WRITE_ARRAY, SET_META, SET_NODATA, CLOSE_DATASETS, CLOSE_WRITER = range(5)

    @classmethod
    def handleTask(cls, task, args, outputDatasets):
        if task is cls.WRITE_ARRAY:
            cls.writeArray(outputDatasets, *args)
        elif task is cls.SET_META:
            cls.setMetadataItem(outputDatasets, *args)
        elif task is cls.SET_NODATA:
            cls.setNoDataValue(*args)
        elif task is cls.CLOSE_DATASETS:
            cls.closeDatasets(outputDatasets, *args)
        elif task is cls.CLOSE_WRITER:
            pass
        else:
            raise ValueError(str(task))

    @staticmethod
    def createDataset(outputDatasets, filename, array, grid, format, creationOptions):
        if not isinstance(array, numpy.ndarray) or array.ndim != 3:
            raise Exception('array must be a 3-d numpy array')

        outputDatasets[filename] = Create(pixelGrid=grid, bands=len(array),
                                          eType=gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype),
                                          dstName=filename, format=format, creationOptions=creationOptions)

    @staticmethod
    def closeDatasets(outputDatasets, createEnviHeader):
        for filename, ds in outputDatasets.items():
            outputDataset = outputDatasets.pop(filename)
            if createEnviHeader:
                outputDataset.writeENVIHeader()
            outputDataset.flushCache()
            outputDataset.close()

    @staticmethod
    def writeArray(outputDatasets, filename, array, subgrid, maingrid, format, creationOptions):

        if filename not in outputDatasets:
            Writer.createDataset(outputDatasets, filename, array, maingrid, format, creationOptions)

        outputDatasets[filename].writeArray(array=array, pixelGrid=subgrid)
        outputDatasets[filename].flushCache()

    @staticmethod
    def setMetadataItem(outputDatasets, filename, key, value, domain):
        outputDatasets[filename].setMetadataItem(key=key, value=value, domain=domain)
        if key=='band names' and domain=='ENVI':
            for dsBand, bandName in zip(outputDatasets[filename], value):
                dsBand.setDescription(bandName)

    @staticmethod
    def setNoDataValue(outputDatasets, filename, value):
        for dsBand in outputDatasets[filename]:
            dsBand.setNoDataValue(value)

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
