from multiprocessing import Pool
from hubdc.model.PixelGrid import PixelGrid
from hubdc.model.Dataset import Dataset
from hubdc.model import Open
from .ApplierInput import ApplierInput
from .ApplierOutput import ApplierOutput
from .ApplierOperator import ApplierOperator
from .WriterProcess import WriterProcess

class ApplierIOTypeError(Exception):
    pass

class Applier(object):

    def __init__(self, ufuncClass, grid=None, nworker=1, nwriter=1,
                 windowxsize=256, windowysize=256):

        self.grid = grid
        self.ufuncClass = ufuncClass
        self.inputs = dict()
        self.outputs = dict()
        self.nworker = nworker
        self.nwriter = nwriter
        self.windowxsize = windowxsize
        self.windowysize = windowysize

    def __setitem__(self, key, value):
        if isinstance(value, ApplierInput):
            self.inputs[key] = value
        elif isinstance(value, ApplierOutput):
            self.outputs[key] = value
        else:
            raise ApplierIOTypeError()

    def __getitem__(self, key):
        if key in self.inputs:
            return self.inputs[key]
        elif key in self.outputs:
            return self.outputs[key]
        else:
            raise KeyError()

    def run(self):

        # init writer processes
        nwriter = min(self.nwriter, len(self.outputs))
        writers = list()
        for i in range(nwriter):
            outputs = {key:output for i, (key, output) in enumerate(self.outputs.items()) if i % nwriter == 0}
            writer = WriterProcess(grid=self.grid, outputs=outputs)
            writer.start()
            writers.append(writer)

        # associate outputs to writer queues (distribute evenly)
        queues = dict()
        for i, key in enumerate(self.outputs.keys()):
            queues[key] = writers[i % nwriter].queue

        # run tile-based processing
        pool = Pool(processes=self.nworker, initializer=workerInitializer, initargs=(self.inputs, self.outputs, queues))
        for windowgrid in self.grid.iterSubgrids(windowxsize=self.windowxsize, windowysize=self.windowysize):
            pool.apply_async(func=workerFunc, kwds={'applier':self, 'windowgrid':windowgrid})
        pool.close()
        pool.join()

        # close writer processes
        for writer in writers:
            writer.close()

def workerInitializer(inputs_, outputs_, queues_):

    global inputs, outputs, queues, inputDatasets
    inputs = inputs_
    outputs = outputs_
    queues = queues_

    # open input datasets
    inputDatasets = dict()
    for key, input in inputs.items():
        assert isinstance(input, ApplierInput)
        inputDatasets[key] = Open(input.filename)

def workerFunc(applier, windowgrid):

    global inputs, outputs, inputDatasets, queues
    assert isinstance(applier, Applier)
    assert isinstance(windowgrid, PixelGrid)

    # warp/translate inputs into GDAL MEM
    inputDatasetsWarped = dict()
    for key in inputDatasets:
        input = inputs[key]
        inputDataset = inputDatasets[key]
        assert isinstance(input, ApplierInput)
        assert isinstance(inputDataset, Dataset)

        # TODO: also support translate, which will be much faster in cases where warp is not needed
        inputDatasetsWarped[key] = inputDataset.warp(dstPixelGrid=windowgrid, dstName='', format='MEM', **input.warpKwargs)

        inputDatasetsWarped[key].copyMetadata(inputDataset)

    # call operator ufunc
    operator = applier.ufuncClass(grid=windowgrid, inputs=inputDatasetsWarped)
    operator.ufunc()

    # send output arrays to writer queues
    for key, outputDataset in operator.outputs.items():
        assert isinstance(outputDataset, Dataset)
        array = outputDataset.readAsArray()
        queues[key].put((key, array, windowgrid))
