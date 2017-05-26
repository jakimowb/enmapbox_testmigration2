from __future__ import print_function
import sys

from osgeo import gdal, ogr
from hubdc import Applier, ApplierOperator, ApplierInput, ApplierOutput
from hubdc.gis.mgrs import getMGRSPixelGridsByShape
from hubdc.gis.wrs2 import getWRS2NamesInsidePixelGrid, getWRS2FootprintsGeometry
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser
from multiprocessing.pool import ThreadPool

LANDSAT_ANCHOR = (15, 15)

#done 33UUT[3335x3335], 2147 Scenes in WRS2 [194023, 194024, 192024, 193023, 193024]in 13483 sec | 224.73  min | 3.75 hours
#done ROI Processing in 19766 sec | 329.43  min | 5.49 hours

def runROI():

    napplier = 0
    nworker = 0
    nwriter = 1

    if napplier > 0:
        pool = ThreadPool(processes=napplier)

    landsatArchive = r'H:\EuropeanDataCube\landsat'
#    landsatArchive = r'C:\Work\data\gms\landsat'


    roi = getWRS2FootprintsGeometry(footprints=LandsatArchiveParser.getFootprints(archive=landsatArchive))
    i=0

    for mgrsFootprint, grid in getMGRSPixelGridsByShape(shape=roi, res=30, anchor=LANDSAT_ANCHOR, buffer=30, trim=True):
        if mgrsFootprint != '33UUT': continue
        if napplier==0:
            runFootprint(mgrsFootprint, grid, landsatArchive, nworker, nwriter)
        else:
            pool.apply_async(func=runFootprint, args=(mgrsFootprint, grid, landsatArchive, nworker, nwriter))

        i+=1
        #if i==1: break

    if napplier > 0:
        pool.close()
        pool.join()


def runFootprint(mgrsFootprint, grid, landsatArchive, nworker, nwriter):

    wrs2Footprints = getWRS2NamesInsidePixelGrid(grid=grid)
    cfmask, sr1, sr2, sr3, sr4, sr5, sr6 = LandsatArchiveParser.getFilenames(archive=landsatArchive, footprints=wrs2Footprints, names=['cfmask', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'])

    for f in sr1:

        f2 = f.replace('landsat', 'landsatTestAR')
        print(f2)
        import os
        if not os.path.exists(f2):
            os.makedirs(os.path.dirname(f2))
            co = ['COMPRESS=LZW', 'INTERLEAVE=BAND', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256', 'SPARSE_OK=TRUE', 'NUM_THREADS=ALL_CPUS', 'BIGTIFF=YES']

            gdal.Translate(destName=f.replace('landsat', 'landsatTestAR'), srcDS=f,
                       options=gdal.TranslateOptions(format='GTiff', creationOptions=co))


class ClearObservations(ApplierOperator):

    def ufunc(self):

        import numpy
        ysize, xsize = self.grid.getDimensions()
        dataAvailability = numpy.zeros(shape=(1, ysize, xsize), dtype=numpy.int16)

        #for cfmask in self.getArrayIterator(name='cfmask'):
        #    dataAvailability += cfmask < 2

        #for srKey in ['sr'+str(i+1) for i in range(6)]:
        i=0
        for sr in self.getArrayIterator(name='sr1'):
            i += 1
            print(i)
            dataAvailability += sr != -9999

        self.setData('dataAvailability', array=dataAvailability)

if __name__ == '__main__':

    from timeit import default_timer
    t0 = default_timer()
    runROI()
    s = (default_timer() - t0); m = s / 60; h = m / 60
    print('done ROI Processing in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))
