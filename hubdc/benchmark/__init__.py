from timeit import default_timer as timer
from hubdc import PixelGrid

if __name__ == '__main__':

    files = 1
    xsize = ysize = 3333
    bands = 200
    processes = 5
    grid = PixelGrid(projection='EPSG:3035', xRes=1, yRes=1, xMin=0, xMax=xsize, yMin=0, yMax=ysize)

    subimagexsize = 512
    subimageysize = 512

    windowxsize = 256
    windowysize = 256

    format = 'GTiff'
    creationOptions = ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256',
                       'SPARSE_OK=TRUE', 'NUM_THREADS=ALL_CPUS', 'BIGTIFF=YES']

    #format = 'ENVI'
    #creationOptions = ['INTERLEAVE=BSQ']


    from hubdc.benchmark import single_writer_with_callback, multi_writer_with_lock, multi_writer_with_subimages, multi_writer_with_writerprocesses, multi_writer_with_bandwriterprocesses, multi_writer_with_openclose

    if 0:
        start = timer()
        outdir = r'c:\output\a'
        single_writer_with_callback.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize)
        end = timer()
        print(end - start)

    if 0:
        start = timer()
        outdir = r'c:\output\b'
        multi_writer_with_lock.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize)
        end = timer()
        print(end - start)

    if 0:
        start = timer()
        outdir = r'c:\output\c'
        multi_writer_with_subimages.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize,
                                           subimagexsize=subimagexsize, subimageysize=subimageysize)
        end = timer()
        print(end - start)

    if 1:
        start = timer()
        outdir = r'c:\output\d'
        multi_writer_with_writerprocesses.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize)
        end = timer()
        print(end - start)

    if 0:
        start = timer()
        outdir = r'c:\output\e'
        multi_writer_with_bandwriterprocesses.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize)
        end = timer()
        print(end - start)

    if 0:
        start = timer()
        outdir = r'c:\output\f'
        multi_writer_with_openclose.script(grid=grid, files=files, bands=bands, processes=processes, outdir=outdir,
                                           format=format, creationOptions=creationOptions,
                                           windowxsize=windowxsize, windowysize=windowysize)
        end = timer()
        print(end - start)
