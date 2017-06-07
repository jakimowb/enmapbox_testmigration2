from __future__ import print_function
import sys
from osgeo import gdal
from timeit import default_timer as now
from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc.applier.ApplierInput import ApplierInput
from hubdc.applier.ApplierOutput import ApplierOutput
from hubdc.applier.ApplierOperator import ApplierOperator
from hubdc.applier.ApplierControls import ApplierControls
from hubdc.applier.Writer import Writer
from hubdc.applier.WriterProcess import WriterProcess
from hubdc.applier.QueueMock import QueueMock

_megaByte = 2**20

class Applier(object):

    AUTOGRID_EXTENT_UNION, AUTOGRID_EXTENT_INTERSECT = range(2)
    AUTOGRID_RESOLUTION_MIN, AUTOGRID_RESOLUTION_MAX, AUTOGRID_RESOLUTION_AVERAGE = range(3)

    def __init__(self):
        self.inputs = dict()
        self.outputs = dict()
        self.controls = ApplierControls()
        self._grid = None

    @property
    def grid(self):
        assert isinstance(self._grid, PixelGrid)
        return self._grid

    def setInput(self, key, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000*2**20, multithread=True):
        self.inputs[key] = ApplierInput(filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def getInput(self, key):
        return self.inputs[key].filename

    def setInputList(self, key, filenames, noData=None, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0., warpMemoryLimit=1000*2**20, multithread=True):
        for i, filename in enumerate(filenames):
            self.setInput(key=(key, i), filename=filename, noData=noData, resampleAlg=resampleAlg, errorThreshold=errorThreshold, warpMemoryLimit=warpMemoryLimit, multithread=multithread)

    def setOutput(self, key, filename, format='GTiff', creationOptions=[]):
        self.outputs[key] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputList(self, key, filenames, format='GTiff', creationOptions=[]):
        for i, filename in enumerate(filenames):
            self.setOutput(key=(key, i), filename=filename, format=format, creationOptions=creationOptions)

    def apply(self, operator, description=' ', *ufuncArgs, **ufuncKwargs):

        import inspect
        if inspect.isclass(operator):
            self.ufuncClass = operator
            self.ufuncFunction = None
        elif callable(operator):
            self.ufuncClass = ApplierOperator
            self.ufuncFunction = operator
        else:
            raise ValueError('operator must be a class or callable')

        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        runT0 = now()
        print('start{description}\n..<init>'.format(description=description), end='..'); sys.stdout.flush()

        self._runCreateGrid()
        self._runInitWriters()
        self._runInitPool()
        results = self._runProcessSubgrids()
        self._runClose()

        print('100%')
        s = (now()-runT0); m = s/60; h = m/60
        print('done{description}in {s} sec | {m}  min | {h} hours'.format(description=description, s=int(s), m=round(m, 2), h=round(h, 2))); sys.stdout.flush()
        return results

    def _runCreateGrid(self):

        if self.controls.referenceGrid is not None:
            self._grid = self.controls.referenceGrid
        else:
            self._grid = self.controls.makeAutoGrid(inputs=self.inputs)

    def _runInitWriters(self):
        self.writers = list()
        self.queues = list()
        self.queueMock = QueueMock()
        if self.controls.multiwriting:
            for w in range(self.controls.nwriter):
                w = WriterProcess()
                w.start()
                self.writers.append(w)
                self.queues.append(w.queue)
        self.queueByFilename = self._getQueueByFilenameDict()

    def _runInitPool(self):
        if self.controls.multiprocessing:
            writers, self.writers = self.writers, None  # writers arn't pickable, need to detache them before passing self to Pool initializer
            self.pool = Pool(processes=self.controls.nworker, initializer=pickableWorkerInitialize, initargs=(self,))
            self.writers = writers  # put writers back
        else:
            Worker.initialize(applier=self)

    def _runProcessSubgrids(self):

        subgrids = self.grid.subgrids(windowxsize=self.controls.windowxsize,
                                      windowysize=self.controls.windowysize)
        if self.controls.multiprocessing:
            applyResults = list()
        else:
            results = list()

        for i, subgrid in enumerate(subgrids):
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'subgrid': subgrid}

            if self.controls.multiprocessing:
                applyResults.append(self.pool.apply_async(func=pickableWorkerProcessSubgrid, kwds=kwargs))
            else:
                results.append(Worker.processSubgrid(**kwargs))

        if self.controls.multiprocessing:
            results = [applyResult.get() for applyResult in applyResults]

        return results

    def _getQueueByFilenameDict(self):

        def lessFilledQueue():
            lfq = self.queues[0]
            for q in self.queues:
                if lfq.qsize() > q.qsize():
                    lfq = q
            return lfq

        queueByFilename = dict()
        for output in self.outputs.values():
            if self.controls.multiwriting:
                queueByFilename[output.filename] = lessFilledQueue()
            else:
                queueByFilename[output.filename] = self.queueMock
        return queueByFilename

    def _runClose(self):
        if self.controls.multiprocessing:
            self.pool.close()
            self.pool.join()

        for writer in self.writers:
            writer.queue.put([Writer.CLOSE_DATASETS, self.controls.createEnviHeader])
            writer.queue.put([Writer.CLOSE_WRITER, None])
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

        gdal.SetCacheMax(applier.controls.cacheMax)
        gdal.SetConfigOption('GDAL_SWATH_SIZE', str(applier.controls.swathSize))
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', str(applier.controls.disableReadDirOnOpen))
        gdal.SetConfigOption('GDAL_MAX_DATASET_POOL_SIZE', str(applier.controls.maxDatasetPoolSize))

        assert isinstance(applier, Applier)
        cls.inputDatasets = dict()
        cls.inputOptions = dict()
        cls.inputFilenames = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()

        # prepare datasets of current main grid without opening
        for i, (key, applierInput) in enumerate(applier.inputs.items()):
            assert isinstance(applierInput, ApplierInput)
            cls.inputDatasets[key] = None
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
                                          ufuncFunction=applier.ufuncFunction, ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        print(int(float(i)/n*100), end='%..'); sys.stdout.flush()
        return cls.operator.apply(subgrid=subgrid, iblock=i, nblock=n)

def pickableWorkerProcessSubgrid(**kwargs):
    return Worker.processSubgrid(**kwargs)

def pickableWorkerInitialize(*args):
    return Worker.initialize(*args)

