from __future__ import print_function
from osgeo import gdal
from timeit import default_timer as now
from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc import Open
from hubdc.applier.ApplierInput import ApplierInput
from hubdc.applier.ApplierOutput import ApplierOutput
from hubdc.applier.WriterProcess import WriterProcess

class Applier(object):

    def __init__(self, grid, nworker=1, nwriter=1,
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

    def setInput(self, key, filename, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.):
        self.inputs[key] = ApplierInput(filename=filename, resampleAlg=resampleAlg, errorThreshold=errorThreshold)

    def setInputs(self, key, filenames, resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.):
        for i, filename in enumerate(filenames):
            self.setInput(key=(key, i), filename=filename, resampleAlg=resampleAlg, errorThreshold=errorThreshold)

    def setOutput(self, key, filename, format='GTiff', creationOptions=[]):
        self.outputs[key] = ApplierOutput(filename=filename, format=format, creationOptions=creationOptions)

    def setOutputs(self, key, filenames, format='GTiff', creationOptions=[]):
        for i, filename in enumerate(filenames):
            self.setOutput(key=(key, i), filename=filename, format=format, creationOptions=creationOptions)

    def run(self, ufuncClass, *ufuncArgs, **ufuncKwargs):

        self.ufuncClass = ufuncClass
        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        self.runT0 = now()
        print('start..<init>', end='...')
        self._runInitWriters()
        self._runInitPool()
        self._runInitOutputs()
        self._runProcessSubgrids()
        self._runClose()

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
        if self.nworker == 1:
            Worker.initialize(applier=self)
        else:
            writers, self.writers = self.writers, None # writers arn't pickable, need to detache them before passing self to Pool initializer
            self.pool = Pool(processes=self.nworker, initializer=Worker.initialize, initargs=(self,))
            self.writers = writers # put writers back

    def _runInitOutputs(self):
        if self.nworker == 1:
            Worker.initializeOutputs()
        else:
            self.pool.apply(func=pickableWorkerInitializeOutputs)

    def _runProcessSubgrids(self):

        subgrids = self.grid.subgrids(windowxsize=self.windowxsize, windowysize=self.windowysize)
        for i, subgrid in enumerate(subgrids):
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'subgrid': subgrid}
            if self.nworker == 1:
                Worker.processSubgrid(**kwargs)
            else:
                self.pool.apply_async(func=pickableWorkerProcessSubgrid, kwds=kwargs)

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

        if self.nworker!=1:
            self.pool.close()
            self.pool.join()

        for writer in self.writers:
            writer.queue.put([WriterProcess.CLOSE_DATASETS, self.createEnviHeader])
            writer.queue.put([WriterProcess.CLOSE_WRITER, None])

        print('100%')
        s = (now()-self.runT0); m = s/60; h = m/60
        print('done in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))


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

        assert isinstance(applier, Applier)

        cls.inputDatasets = dict()
        cls.inputOptions = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()

        # open datasets of current main grid
        for i, (key, applierInput) in enumerate(applier.inputs.items()):
            assert isinstance(applierInput, ApplierInput)
            cls.inputDatasets[key] = Open(applierInput.filename)
            cls.inputOptions[key] = applierInput.options

        for key, applierOutput in applier.outputs.items():
            assert isinstance(applierOutput, ApplierOutput)
            cls.outputFilenames[key] = applierOutput.filename
            cls.outputOptions[key] = applierOutput.options

        # create operator
        cls.operator = applier.ufuncClass(maingrid=applier.grid,
                                          inputDatasets=cls.inputDatasets, inputOptions=cls.inputOptions,
                                          outputFilenames=cls.outputFilenames, outputOptions=cls.outputOptions,
                                          queueByFilename=applier.queueByFilename,
                                          ufuncArgs=applier.ufuncArgs, ufuncKwargs=applier.ufuncKwargs)

    @ classmethod
    def initializeOutputs(cls):
        minimalSubgrid = cls.operator.maingrid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1)
        cls.operator.run(subgrid=minimalSubgrid, initialization=True)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        print(int(float(i)/n*100), end='%..')
        cls.operator.run(subgrid=subgrid, initialization=False)

def pickableWorkerInitializeOutputs():
    Worker.initializeOutputs()

def pickableWorkerProcessSubgrid(**kwargs):
    Worker.processSubgrid(**kwargs)