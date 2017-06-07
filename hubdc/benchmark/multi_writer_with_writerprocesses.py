from os.path import join
import gdal, numpy
from hubdc import Create
from multiprocessing import Pool, Process, Queue

class WriterProcess(Process):

    def __init__(self, outfile, grid, format, creationOptions, bands):
        Process.__init__(self)
        self.outfile = outfile
        self.grid = grid
        self.bands = bands
        self.format = format
        self.creationOptions = creationOptions
        self.queue = Queue()

    def run(self):

        outDS = Create(pixelGrid=self.grid, bands=self.bands, eType=gdal.GDT_Int16, dstName=self.outfile,
                       format=self.format, creationOptions=self.creationOptions)

        while True:
            value = self.queue.get()

            if value is not None:
                array, grid = value
                outDS.writeArray(array=array, pixelGrid=grid)
                outDS.flushCache()
            else:
                outDS.close()
                break

    def close(self):
        self.queue.put(None)

def script(grid, files, bands, processes, outdir, format, creationOptions, windowxsize, windowysize):

    # start writer processes
    writers = list()
    for i in range(files):
        outfile = join(outdir, '{i}.tif'.format(i=i))
        writer = WriterProcess(outfile=outfile, grid=grid, format=format, creationOptions=creationOptions, bands=bands)
        writer.start()
        writers.append(writer)

    # apply tile-based processing
    queues = [writer.queue for writer in writers]
    pool = Pool(processes=processes, initializer=initializer, initargs=(queues,))
    for windowgrid in grid.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        pool.apply_async(func=ufunc, args=(windowgrid, files, bands))
    pool.close()
    pool.join()

    # close writer processes
    for writer in writers:
        writer.close()

def initializer(queues_):
    global queues
    queues = queues_

def ufunc(grid, files, bands):

    # generate result arrays
    ysize, xsize = grid.getDimensions()
    arrays = list()
    for i in range(files):
        array = numpy.random.rand(bands, ysize, xsize)*42
        arrays.append(array.astype(numpy.int16))

    # send arrays to writers
    for queue, array in zip(queues, arrays):
        queue.put((array, grid))
