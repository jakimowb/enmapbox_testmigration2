'''
Writing image data using Pool.apply_async with callback.
'''

from os.path import join
import gdal, numpy
from hubdc import Create

def script(grid, files, bands, processes, outdir,
           format, creationOptions, windowxsize, windowysize):

    global outDSList
    for i in range(files):
        outfile = join(outdir, '{i}.tif'.format(i=i))
        outDS = Create(pixelGrid=grid, bands=bands, eType=gdal.GDT_Int16, dstName=outfile, format=format,
                       creationOptions=creationOptions)
        outDSList.append(outDS)


    # run tile-based warping
    from multiprocessing import Pool
    pool = Pool(processes=processes)

    for subgrid in grid.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        pool.apply_async(func=ufunc, args=(subgrid, files, bands), callback=callback)

    pool.close()
    pool.join()

    for outDS in outDSList:
        outDS.flushCache()

def ufunc(grid, files, bands):
    #print('start job')
    ysize, xsize = grid.getDimensions()
    arrays = list()
    for i in range(files):
        array = numpy.random.rand(bands, ysize, xsize)*42
        arrays.append(array.astype(numpy.int16))
    return arrays, grid

def callback(args):
    arrays, grid = args
    global globalDict
    for outDS, array in zip(outDSList, arrays):
        outDS.writeArray(array=array, pixelGrid=grid)

outDSList = list()
