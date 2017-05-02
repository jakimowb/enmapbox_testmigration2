'''
Writing image data using Pool.apply_async.
'''

from os.path import join, dirname, basename
import gdal, numpy
from hubdc import Create, OpenDSL

def script(grid, files, bands, processes, outdir,
           format, creationOptions,
           windowxsize, windowysize, subimagexsize, subimageysize):

    outfiles = [join(outdir, '{i}.tif'.format(i=i)) for i in range(files)]

    # Run tile-based processing using a pool of worker.
    # Each worker writes all its job outputs (small windows, e.g. 128x128) into a subimage (e.g. 1024x1024)
    from multiprocessing import Pool
    pool = Pool(processes=processes)

    subimageOutfiles = list()
    for i, grid2 in enumerate(grid.iterSubgrids(windowxsize=subimagexsize, windowysize=subimageysize)):
        outfiles2 = [join(dirname(outfile), str(i), basename(outfile)) for outfile in outfiles]
        subimageOutfiles.append(outfiles2)
        pool.apply_async(func=script2,
                         args=(grid2, outfiles2, format, creationOptions,
                               windowxsize, windowysize,
                               files, bands))

    pool.close()
    pool.join()

    # create final VRTs
    for filenames, outfile in zip(zip(*subimageOutfiles), outfiles):
        dsl = OpenDSL(filenames)
        dsl.buildVRT(dstPixelGrid=grid, dstName=outfile+'.vrt')

def script2(grid2, outfiles2, format, creationOptions, windowxsize, windowysize, nfiles, nbands):

    # create subimages
    outDSList = list()
    for outfile in outfiles2:
        outDS = Create(pixelGrid=grid2, bands=nbands, eType=gdal.GDT_Int16, dstName=outfile, format=format,
                       creationOptions=creationOptions)
        outDSList.append(outDS)

    # tile-based processing
    for windowgrid in grid2.iterSubgrids(windowxsize=windowxsize, windowysize=windowysize):
        arrays = ufunc(windowgrid, nfiles, nbands)
        for outDS, array in zip(outDSList, arrays):
            outDS.writeArray(array=array, pixelGrid=windowgrid)

    # flush cache
    for outDS in outDSList:
        outDS.flashCache()

def ufunc(windowgrid, nfiles, nbands):
    # generate result arrays
    ysize, xsize = windowgrid.getDimensions()
    arrays = list()
    for i in range(nfiles):
        array = numpy.random.rand(nbands, ysize, xsize) * 42
        arrays.append(array.astype(numpy.int16))
    return arrays
