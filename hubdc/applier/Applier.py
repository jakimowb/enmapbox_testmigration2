from __future__ import print_function
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
        self.ntasks = None

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

        from timeit import default_timer
        runT0 = default_timer()

        print('start', end='..')

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


        # tile-based processing
        self.subgrids = self.grid.subgrids(windowxsize=self.windowxsize, windowysize=self.windowysize)

        if self.nworker==1: # single-processing

            t0 = default_timer()
            print('<open inputs>', end='')
            workerInitializer(self, queues)
            print('({s} sec)'.format(s=int(default_timer()-t0)), end='..')

            print('<init outputs>', end='..')
            # run operator in initialization mode, which creates the output datasets and calls umeta()
            workerFunc(i=None, windowgrid=self.grid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1), initialization=True)

            # run operator for the whole grid
            for i, windowgrid in enumerate(self.subgrids):
                workerFunc(i=i, windowgrid=windowgrid)

        else: # multi-processing

            t0 = default_timer()
            print('<open inputs>', end='')
            pool = Pool(processes=self.nworker, initializer=workerInitializer, initargs=(self, queues))
            print('({s} sec)'.format(s=int(default_timer()-t0)), end='..')

            t0 = default_timer()
            print('<init outputs>', end='')
            # run operator in initialization mode, which creates the output datasets and calls umeta()
            # NOTE: this only runs inside a single worker
            pool.apply(func=workerFunc, kwds={'i':None,
                                              'windowgrid':self.grid.subsetPixelWindow(xoff=0, yoff=0, width=1, height=1),
                                              'initialization':True})
            print('({s} sec)'.format(s=int(default_timer()-t0)), end='..')

            # run operator for the whole grid
            tasks = list()
            for i, windowgrid in enumerate(self.subgrids):
                tasks.append(pool.apply_async(func=workerFunc, kwds={'i':i, 'windowgrid':windowgrid}))

            results = [task.get() for task in tasks]
            pool.close()

        print('100%')

        # close writer processes
        for writer in writers:
            writer.close()

        s = (default_timer()-runT0)
        m = s/60
        h = m/60
        print('done in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))

def workerInitializer(applier_, queues):
    from osgeo import gdal
    gdal.SetCacheMax(1)
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

def workerFunc(i, windowgrid, initialization=False):

    global applier
    assert isinstance(applier, Applier)
    assert isinstance(windowgrid, PixelGrid)

    # report progress
    if i is not None:
        print(int(float(i)/len(applier.subgrids)*100), end='%..')

    # call operator ufunc
    operator = applier.ufuncClass(applier=applier, grid=windowgrid, initialization=initialization)
    operator.ufunc(*applier.ufuncArgs, **applier.ufuncKwargs)

    if initialization:
        operator.umeta(*applier.ufuncArgs, **applier.ufuncKwargs)
