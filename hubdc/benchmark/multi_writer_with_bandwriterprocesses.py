from os.path import join
import gdal, numpy
from hubdc import Create, Open
from multiprocessing import Pool, Process, Queue, Lock

class BandWriterProcess(Process):

    def __init__(self, lock, outfile, outband, grid, format, creationOptions, bands):
        Process.__init__(self)
        self.lock = lock
        self.outfile = outfile
        self.outband = outband
        self.grid = grid
        self.bands = bands
        self.format = format
        self.creationOptions = creationOptions
        self.queue = Queue()

    def run(self):

        outDS = Open(self.outfile, eAccess=gdal.GA_Update)

        while True:
            value = self.queue.get()

            if value is not None:
                array, grid = value
                outRB = outDS.getBand(self.outband)
                #self.lock.acquire()
                outRB.writeArray(array=array, pixelGrid=grid)
                outRB.gdalBand.FlushCache()
                #self.lock.release()
            else:
                outDS.close()
                break

    def close(self):
        self.queue.put(None)

def script(grid, files, bands, processes, outdir, format, creationOptions, windowxsize, windowysize):

    # start writer processes
    bandwriters = list()
    lock = Lock()
    for i in range(files):
        outfile = join(outdir, '{i}.tif'.format(i=i))
        outDS = Create(pixelGrid=grid, bands=bands, eType=gdal.GDT_Int16, dstName=outfile, format=format,
                       creationOptions=creationOptions)
        outDS.close()
        for outband in range(1, bands+1):
            bandwriter = BandWriterProcess(lock=lock, outfile=outfile, outband=outband, grid=grid, format=format, creationOptions=creationOptions, bands=bands)
            bandwriter.start()
            bandwriters.append(bandwriter)

    # apply tile-based processing
    queues = [w.queue for w in bandwriters]
    pool = Pool(processes=processes, initializer=initializer, initargs=(queues,))
    for windowgrid in grid.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        pool.apply_async(func=ufunc, args=(windowgrid, files, bands))
    pool.close()
    pool.join()

    # close writer processes
    for writer in bandwriters:
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
    i = 0
    for array in arrays:
        for bandarray in array:
            queues[i].put((bandarray, grid))
            i += 1
