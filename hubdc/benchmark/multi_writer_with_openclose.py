from os.path import join
import gdal, numpy
from hubdc import Create, Open

def script(grid, files, bands, processes, outdir,
           format, creationOptions,
           windowxsize, windowysize):

    outfiles = list()
    for i in range(files):
        outfile = join(outdir, '{i}.tif'.format(i=i))
        outDS = Create(pixelGrid=grid, bands=bands, eType=gdal.GDT_Int16, dstName=outfile, format=format,
                       creationOptions=creationOptions)
        outDS.close()
        outfiles.append(outfile)
    from multiprocessing import Pool, Lock
    lock = Lock()
    pool = Pool(processes=processes, initializer=initializer, initargs=(outfiles, lock))

    for subgrid in grid.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        pool.apply_async(func=ufunc, args=(subgrid, files, bands))

    pool.close()
    pool.join()

def initializer(outfiles_, lock_):
    global outfiles
    global lock
    outfiles = outfiles_
    lock = lock_

def ufunc(grid, files, bands):
    ysize, xsize = grid.getDimensions()
    arrays = list()
    for i in range(files):
        array = numpy.random.rand(bands, ysize, xsize)*42
        arrays.append(array.astype(numpy.int16))

#    lock.acquire()
    for outfile, array in zip(outfiles, arrays):
        outDS = Open(outfile, eAccess=gdal.GA_Update)
        outDS.writeArray(array=array, pixelGrid=grid, flushCache=True)
        outDS.close()
#    lock.release()
