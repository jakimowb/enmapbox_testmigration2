'''
Writing image data using Pool.apply_async with a lock.
'''

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
        outDS.flushCache()
#        outDS.gdalDataset = None
        outfiles.append(outfile)
#    exit()
    from multiprocessing import Pool, Lock
    lock = Lock()
    pool = Pool(processes=processes, initializer=initializer, initargs=(outfiles, lock))

    for subgrid in grid.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        pool.apply_async(func=ufunc, args=(subgrid, files, bands))

    pool.close()
    pool.join()

def initializer(outfiles, sharedLock):
    global outDSList
    global lock
    outDSList = list()
    for outfile in outfiles:
        outDS = Open(outfile, eAccess=gdal.GA_Update)
        outDSList.append(outDS)
    lock = sharedLock

def ufunc(grid, files, bands):
    ysize, xsize = grid.getDimensions()
    arrays = list()
    for i in range(files):
        array = numpy.random.rand(bands, ysize, xsize)*42
        arrays.append(array.astype(numpy.int16))

    lock.acquire()
    for outDS, array in zip(outDSList, arrays):
        outDS.writeArray(array=array, pixelGrid=grid, flushCache=True)
        outDS.flushCache()
    lock.release()
