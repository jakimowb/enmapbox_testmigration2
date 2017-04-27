from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Dataset import Dataset
from hubdc.model import Open
from .ApplierInput import ApplierInput
from .ApplierOutput import ApplierOutput
from .WriterProcess import WriterProcess

class ApplierIOTypeError(Exception):
    pass

class Applier(object):

    def __init__(self, ufuncClass, grid=None, nworker=1, nwriter=1,
                 windowxsize=256, windowysize=256):

        self.grid = grid
        self.ufuncClass = ufuncClass
        self.ufuncArgs = None
        self.ufuncKwargs = None
        self.inputs = dict()
        self.inputDatasets = None
        self.outputs = dict()
        self.queues = None
        self.nworker = nworker
        self.nwriter = nwriter
        self.windowxsize = windowxsize
        self.windowysize = windowysize

    def __setitem__(self, key, value):
        if isinstance(value, ApplierInput):

            if isinstance(value.filename, list):
                for i, filename in enumerate(value.filename):
                    self.inputs[(key, i)] = ApplierInput(filename=filename, **value.options)
            else:
                self.inputs[key] = value

        elif isinstance(value, ApplierOutput):

            if isinstance(value.filename, list):
                for i, filename in enumerate(value.filename):
                    self.outputs[(key, i)] = ApplierOutput(filename=filename, format=value.format, creationOptions=value.creationOptions)
            else:
                self.outputs[key] = value

        else:
            raise Exception('wrong _applier i/o type')

    def __getitem__(self, key):
        if key in self.inputs:
            return self.inputs[key]
        elif key in self.outputs:
            return self.outputs[key]
        else:
            raise KeyError()

    def run(self, *ufuncArgs, **ufuncKwargs):

        self.ufuncArgs = ufuncArgs
        self.ufuncKwargs = ufuncKwargs

        # init writer processes
        nwriter = min(self.nwriter, len(self.outputs))
        writers = list()

        for iwriter in range(nwriter):
            outputs = {key:output for ioutput, (key, output) in enumerate(self.outputs.items()) if ioutput % nwriter == iwriter}
            writer = WriterProcess(grid=self.grid, outputs=outputs)
            writer.start()
            writers.append(writer)

        # associate outputs to writer queues (distribute evenly)
        queues = dict()
        for i, key in enumerate(self.outputs.keys()):
            queues[key] = writers[i % nwriter].queue

        # run operator in initialization mode, which creates the output datasets and calls umeta()
        #workerInitializer(self, queues)
        #workerFunc(windowgrid=self.grid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1), initialization=True)

        if self.nworker==1: # single-processing

            workerInitializer(self, queues)

            # run operator in initialization mode, which creates the output datasets and calls umeta()
            workerFunc(windowgrid=self.grid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1), initialization=True)

            # run operator for the whole grid
            for windowgrid in self.grid.iterSubgrids(windowxsize=self.windowxsize, windowysize=self.windowysize):
                workerFunc(windowgrid=windowgrid)

        else: # multi-processing

            pool = Pool(processes=self.nworker, initializer=workerInitializer, initargs=(self, queues))

            # run operator in initialization mode, which creates the output datasets and calls umeta()
            # NOTE: this only runs inside a single worker
            pool.apply(func=workerFunc, kwds={'windowgrid':self.grid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1),
                                              'initialization':True})

            # run operator for the whole grid
            for windowgrid in self.grid.iterSubgrids(windowxsize=self.windowxsize, windowysize=self.windowysize):
                pool.apply_async(func=workerFunc, kwds={'windowgrid':windowgrid})
            pool.close()
            pool.join()

        # close writer processes
        for writer in writers:
            writer.close()


def workerInitializer(applier_, queues):

    global applier
    applier = applier_
    assert isinstance(applier_, Applier)
    applier.queues = queues

    # open input datasets
    applier.inputDatasets = dict()
    applier.inputOptions = dict()
    for key, input in applier.inputs.items():
        assert isinstance(input, ApplierInput)
        if isinstance(input.filename, (list, tuple)):
            applier.inputDatasets[key] = [Open(filename) for filename in input.filename]
        else:
            applier.inputDatasets[key] = Open(input.filename)

def workerFunc(windowgrid, initialization=False):

    global applier
    assert isinstance(applier, Applier)
    assert isinstance(windowgrid, PixelGrid)

    # call operator ufunc
    operator = applier.ufuncClass(applier=applier, grid=windowgrid, initialization=initialization)
    operator.ufunc(*applier.ufuncArgs, **applier.ufuncKwargs)

    if initialization:
        operator.umeta(*applier.ufuncArgs, **applier.ufuncKwargs)
