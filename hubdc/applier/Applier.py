from __future__ import print_function
import sys
from osgeo import gdal
from timeit import default_timer as now
from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc import Open
from hubdc.applier.ApplierInput import ApplierInput
from hubdc.applier.ApplierOutput import ApplierOutput
from hubdc.applier.WriterProcess import WriterProcess

_megaByte = 2**20
DEFAULT_GDAL_CACHEMAX = 1000 * _megaByte
DEFAULT_GDAL_DISABLE_READDIR_ON_OPEN = True
DEFAULT_GDAL_MAX_DATASET_POOL_SIZE = 1000
DEFAULT_GDAL_SWATH_SIZE = 1000 * _megaByte

class Applier(object):

    def __init__(self, grid, nworker=0, nwriter=1,
                 windowxsize=256, windowysize=256, createEnviHeader=False):

        assert isinstance(grid, PixelGrid)
        self.grid = grid
        self.windowxsize = windowxsize
        self.windowysize = windowysize
        self.createEnviHeader = createEnviHeader
        self.inputs = dict()
        self.outputs = dict()
        self.nwriter = nwriter
        self.nworker = nworker
        self.multiprocessing = nworker > 0

    def setInput(self, key, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=100*2**20, multithread=False):
        self.inputs[key] = ApplierInput(filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setInputs(self, key, filenames, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=100*2**20, multithread=False):
        for i, filename in enumerate(filenames):
            self.setInput(key=(key, i), filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setOutput(self, key, filename, format='GTiff', creationOptions=[]):
        self.outputs[key] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputs(self, key, filenames, format='GTiff', creationOptions=[]):
        for i, filename in enumerate(filenames):
            self.setOutput(key=(key, i), filename=filename, format=format, creationOptions=creationOptions)

    def run(self, ufuncClass, description=' ', *ufuncArgs, **ufuncKwargs):

        self.ufuncClass = ufuncClass
        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        runT0 = now()
        print('start{description}\n..<init>'.format(description=description), end='..'); sys.stdout.flush()
        self._runInitWriters()
        self._runInitPool()
        self._runProcessSubgrids()
        self._runClose()

        print('100%')
        s = (now()-runT0); m = s/60; h = m/60
        print('done{description}in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s), m=round(m, 2), h=round(h, 2))); sys.stdout.flush()

    def _runInitWriters(self):
        self.writers = list()
        self.queues = list()
        for w in range(self.nwriter):
            w = WriterProcess()
            w.start()
            self.writers.append(w)
            self.queues.append(w.queue)
        self.queueByFilename = self._getQueueByFilenameDict()

    def _runInitPool(self):
        if self.multiprocessing:
            writers, self.writers = self.writers, None  # writers arn't pickable, need to detache them before passing self to Pool initializer
            self.pool = Pool(processes=self.nworker, initializer=Worker.initialize, initargs=(self,))
            self.writers = writers  # put writers back
        else:
            Worker.initialize(applier=self)

    def _runProcessSubgrids(self):

        subgrids = self.grid.subgrids(windowxsize=self.windowxsize, windowysize=self.windowysize)
        applyResults = list()
        for i, subgrid in enumerate(subgrids):
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'subgrid': subgrid}

            if self.multiprocessing:
                applyResults.append(self.pool.apply_async(func=pickableWorkerProcessSubgrid, kwds=kwargs))
            else:
                Worker.processSubgrid(**kwargs)

        results = [applyResult.get() for applyResult in applyResults]

    def _getQueueByFilenameDict(self):

        def lessFilledQueue():
            lfq = self.queues[0]
            for q in self.queues:
                if lfq.qsize() > q.qsize():
                    lfq = q
            return lfq

        queueByFilename = dict()
        for output in self.outputs.values():
            queueByFilename[output.filename] = lessFilledQueue()
        return queueByFilename

    def _runClose(self):
        if self.multiprocessing:
            self.pool.close()
            self.pool.join()

        for writer in self.writers:
            writer.queue.put([WriterProcess.CLOSE_DATASETS, self.createEnviHeader])
            writer.queue.put([WriterProcess.CLOSE_WRITER, None])
            writer.join()


class Worker(object):

    queues = list()
    inputDatasets = dict()
    inputOptions = dict()
    outputFilenames = dict()
    outputOptions = dict()
    operator = None

    def __init__(self):
        raise Exception('singleton class')

    @classmethod
    def initialize(cls, applier):

        gdal.SetCacheMax(DEFAULT_GDAL_CACHEMAX)
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', str(DEFAULT_GDAL_DISABLE_READDIR_ON_OPEN))
        gdal.SetConfigOption('GDAL_MAX_DATASET_POOL_SIZE', str(DEFAULT_GDAL_MAX_DATASET_POOL_SIZE))
        gdal.SetConfigOption('GDAL_SWATH_SIZE', str(DEFAULT_GDAL_SWATH_SIZE))

        assert isinstance(applier, Applier)
        cls.inputDatasets = dict()
        cls.inputOptions = dict()
        cls.inputFilenames = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()

        # open datasets of current main grid
        for i, (key, applierInput) in enumerate(applier.inputs.items()):
            assert isinstance(applierInput, ApplierInput)
            cls.inputDatasets[key] = None #Open(applierInput.filename)
            cls.inputFilenames[key] = applierInput.filename
            cls.inputOptions[key] = applierInput.options

        for key, applierOutput in applier.outputs.items():
            assert isinstance(applierOutput, ApplierOutput)
            cls.outputFilenames[key] = applierOutput.filename
            cls.outputOptions[key] = applierOutput.options

        # create operator
        cls.operator = applier.ufuncClass(maingrid=applier.grid,
                                          inputDatasets=cls.inputDatasets, inputFilenames=cls.inputFilenames, inputOptions=cls.inputOptions,
                                          outputFilenames=cls.outputFilenames, outputOptions=cls.outputOptions,
                                          queueByFilename=applier.queueByFilename,
                                          ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        print(int(float(i)/n*100), end='%..'); sys.stdout.flush()
        cls.operator.run(subgrid=subgrid, iblock=i, nblock=n)

def pickableWorkerProcessSubgrid(**kwargs):
    Worker.processSubgrid(**kwargs)