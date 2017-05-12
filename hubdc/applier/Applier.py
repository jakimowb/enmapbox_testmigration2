from __future__ import print_function
from osgeo import gdal
from timeit import default_timer as now
from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc import Open, Dataset
from .ApplierInput import ApplierInput
from .ApplierOutput import ApplierOutput
from .WriterProcess import WriterProcess

class ApplierIOTypeError(Exception):
    pass

class Applier(object):

    def __init__(self, nworker=1, nwriter=1,
                 windowxsize=256, windowysize=256, createEnviHeader=False):

        self.windowxsize = windowxsize
        self.windowysize = windowysize
        self.createEnviHeader = createEnviHeader
        self._initWriters(nwriter)
        self._initWorker(nworker)
        self._runFinish()

    def _initWriters(self, nwriter):
        self.writers = list()
        self.queues = list()
        for w in range(nwriter):
            w = WriterProcess()
            w.start()
            self.writers.append(w)
            self.queues.append(w.queue)

    def _initWorker(self, nworker):
        self.nworker = nworker
        if nworker==1:
            Worker.initialize(self.queues)
        else:
            self.pool = Pool(processes=nworker, initializer=Worker.initialize, initargs=(self.queues,))

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

    def run(self, grid, ufuncClass, *ufuncArgs, **ufuncKwargs):

        assert isinstance(grid, PixelGrid)
        self.grid = grid
        self.ufuncClass = ufuncClass
        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        runT0 = now()
        print('start..<init>', end='...')
        self._runInit()
        self._runSubgrids()
        print('100%')
        self._runFinish()
        s = (now()-runT0); m = s/60; h = m/60
        print('done in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))



    def _runInit(self):

        kwargs={'maingrid' : self.grid,
              'ufuncClass' : self.ufuncClass,
              'ufuncArgs' : self.ufuncArgs,
              'ufuncKwargs' : self.ufuncKwargs,
              'applierInputs' : self.inputs,
              'applierOutputs' : self.outputs,
              'queueIndexByFilename': self._getQueueIndexByFilenameDict()}

        if self.nworker==1:
            #Worker.startNewMaingrid(**kwargs)
            pickableWorkerStartNewMaingrid(**kwargs)
        else:
            self.pool.apply(func=pickableWorkerStartNewMaingrid, kwds=kwargs)

    def _runSubgrids(self):

        subgrids = self.grid.subgrids(windowxsize=self.windowxsize, windowysize=self.windowysize)
        for i, subgrid in enumerate(subgrids):
            kwargs = {'i': i,
                      'n': len(subgrids),
                      'subgrid': subgrid}
            if self.nworker == 1:
                Worker.processSubgrid(**kwargs)
            else:
                self.pool.apply_async(func=pickableWorkerProcessSubgrid, kwds=kwargs)

    def _runFinish(self):
        self.inputs = dict()
        self.outputs = dict()

    def _getQueueIndexByFilenameDict(self):

        def lessFilledQueueIndex():
            lfqi = 0
            for i, q in enumerate(self.queues):
                if self.queues[lfqi].qsize() > q.qsize():
                    lfqi = i
            return lfqi

        queueIndexByFilename = dict()
        for output in self.outputs.values():
            queueIndexByFilename[output.filename] = lessFilledQueueIndex()
        return queueIndexByFilename

    def close(self):

        if self.nworker!=1:
            self.pool.close()

        for writer in self.writers:
            writer.queue.put([WriterProcess.CLOSE_DATASETS, self.createEnviHeader])
            writer.queue.put([WriterProcess.CLOSE_WRITER, None])

def pickableWorkerStartNewMaingrid(**kwargs):
    Worker.startNewMaingrid(**kwargs)

def pickableWorkerProcessSubgrid(**kwargs):
    Worker.processSubgrid(**kwargs)


class InputDatasets:
    pass
    #def append(self, dataset):


#a=InputDatasets()

class Worker(object):

    queues = list()
    inputDatasets = list()

    inputOptions = dict()
    outputFilenames = dict()
    outputOptions = dict()
    currentRunID = ''

    def __init__(self):
        raise Exception('singleton class')

    @classmethod
    def initialize(cls, queues):
        cls.queues = queues

    @classmethod
    def startNewMaingrid(cls, maingrid, ufuncClass, ufuncArgs, ufuncKwargs, applierInputs, applierOutputs, queueIndexByFilename):

        cls.maingrid = maingrid
        cls.ufuncClass = ufuncClass
        cls.ufuncArgs = ufuncArgs
        cls.ufuncKwargs = ufuncKwargs
        cls.queueByFilename = {filename:cls.queues[index] for filename, index in queueIndexByFilename.items()}

        #global a
        # close datasets of last maingrid
        for i in range(len(cls.inputDatasets)):
            #ds = None
            #cls.inputDatasets[key] = cls.inputDatasets.values()[0]
            cls.inputDatasets[i] = None
            #ds = getattr(a, 'ds_{i}'.format(i=i))
            #setattr(cls, 'ds_{i}'.format(i=i), None)
            #delattr(a, 'ds_{i}'.format(i=i))
        #del a
        #a=A()

        cls.inputDatasets = None
        cls.inputDatasets = list()
        cls.inputOptions = dict()
        cls.outputFilenames = dict()
        cls.outputOptions = dict()

        # open datasets of current main grid
        for i, (key, applierInput) in enumerate(applierInputs.items()):
            assert isinstance(applierInput, ApplierInput)
            #print(key)
            if i <= len(cls.inputDatasets)-1:
                cls.inputDatasets[i] = Open(applierInput.filename)
            else:
                cls.inputDatasets.append(Open(applierInput.filename))
            #dataset = Dataset.fromFilename(applierInput.filename)
            #dataset._gdalDataset = gdal.Open(applierInput.filename)
            #dataset._pixelGrid = PixelGrid.fromDataset(dataset=dataset)
            #setattr(cls, 'ds_{i}'.format(i=i), Open(applierInput.filename))
            cls.inputOptions[key] = applierInput.options

        return
        for key, applierOutput in applierOutputs.items():
            assert isinstance(applierOutput, ApplierOutput)
            cls.outputFilenames[key] = applierOutput.filename
            cls.outputOptions[key] = applierOutput.options


        return
        # create operator
        cls.operator = ufuncClass(maingrid=maingrid,
                                  inputDatasets=cls.inputDatasets, inputOptions=cls.inputOptions,
                                  outputFilenames=cls.outputFilenames, outputOptions=cls.outputOptions,
                                  queueByFilename=cls.queueByFilename,
                                  ufuncArgs=cls.ufuncArgs, ufuncKwargs=cls.ufuncKwargs)

        return

        # initialize output datasets
        minimalSubgrid = maingrid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1)
        cls.operator.run(subgrid=minimalSubgrid, initialization=True)

    @classmethod
    def processSubgrid(cls, i, n, subgrid):
        return
        print(int(float(i)/n*100), end='%..')
        cls.operator.run(subgrid=subgrid, initialization=False)
