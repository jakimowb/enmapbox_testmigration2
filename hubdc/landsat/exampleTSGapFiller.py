from osgeo import gdal
from hubdc import PixelGrid, Applier, ApplierInput, ApplierOutput
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser
from hubdc.landsat.TSGapFiller import TSGapFiller

from datetime import date

def script_rabe_local():

    # define grid
    grid = PixelGrid.fromFile(r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_cfmask.img')
    grid.xRes = grid.yRes = 3000

    # parse landsat archive for filenames
    cfmask, blue, red, nir = LandsatArchiveParser.getFilenames(archive=r'C:\Work\data\gms\landsat',
                                                               footprints=['194024'],
                                                               names=['cfmask', 'blue', 'red', 'nir'])

    # setup and run _applier
    applier = Applier(grid=grid, ufuncClass=TSGapFiller, nworker=2, nwriter=2, windowxsize=256, windowysize=256)
    applier['cfmask'] = ApplierInput(cfmask)
    applier['blue'] = ApplierInput(blue)
    applier['red'] = ApplierInput(red)
    applier['nir'] = ApplierInput(nir)

    sigmas = [3, 5, 7]
    filteredTSFilenames = [r'c:\output\filteredTS{s}.img'.format(s=s) for s in sigmas]
    filteredDAFilenames = [r'c:\output\filteredDA{s}.img'.format(s=s) for s in sigmas]

    applier['filteredTS'] = ApplierOutput(filteredTSFilenames, format='ENVI', creationOptions=[])
    applier['filteredDA'] = ApplierOutput(filteredDAFilenames, format='ENVI', creationOptions=[])

    applier.run(start=date(2015, 1, 1), end=date(2015, 12, 31),
                workTempRes=1, outTempRes=10,
                sigmas=sigmas, kernelCutOff=0.9)

def script_brazil_server():

    # define grid
    grid = PixelGrid.fromFile(r'G:\_EnMAP\Rohdaten\Brazil\Raster\LANDSAT\ESPA\PESA\224\071\LC82240712013103LGN01\LC82240712013103LGN01_cfmask.img')
    grid.xRes = grid.yRes = 3000

    # parse landsat archive for filenames
    cfmask, blue, red, nir = LandsatArchiveParser.getFilenames(archive=r'G:\_EnMAP\Rohdaten\Brazil\Raster\LANDSAT\ESPA\PESA',
                                                               footprints=['224071'],
                                                               names=['cfmask', 'blue', 'red', 'nir'])

    # setup and run _applier
    applier = Applier(grid=grid, ufuncClass=TSGapFiller, nworker=1, nwriter=10, windowxsize=256, windowysize=256)
    applier['cfmask'] = ApplierInput(cfmask)
    applier['blue'] = ApplierInput(blue)
    applier['red'] = ApplierInput(red)
    applier['nir'] = ApplierInput(nir)

    sigmas = [31]
    filteredTSFilenames = [r'G:\_EnMAP\temp\temp_ar\brazil\filteredTS{s}.img'.format(s=s) for s in sigmas]
    filteredDAFilenames = [r'G:\_EnMAP\temp\temp_ar\brazil\filteredDA{s}.img'.format(s=s) for s in sigmas]

    format = 'GTiff'
    creationOptions=['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'SPARSE_OK=TRUE', 'NUM_THREADS=ALL_CPUS', 'BIGTIFF=YES']
    #format = 'ENVI'
    #creationOptions = []
    applier['filteredTS'] = ApplierOutput(filteredTSFilenames, format=format, creationOptions=creationOptions)
    applier['filteredDA'] = ApplierOutput(filteredDAFilenames, format=format, creationOptions=creationOptions)

    applier.run(start=date(2013, 1, 1), end=date(2015, 12, 31),
                workTempRes=1, outTempRes=1,
                sigmas=sigmas, kernelCutOff=0.9)

if __name__ == '__main__':
    #script_rabe_local()
    script_brazil_server()
