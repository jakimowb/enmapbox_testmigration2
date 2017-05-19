from __future__ import print_function
import sys
sys.path.append(r'S:\source\hub-datacube')
sys.path.append(r'S:\source\site-packages')

from osgeo import gdal, ogr
from hubdc import Applier, ApplierOperator, ApplierInput, ApplierOutput
from hubdc.gis.mgrs import getMGRSPixelGridsByShape
from hubdc.gis.wrs2 import getWRS2NamesInsidePixelGrid, getWRS2FootprintsGeometry
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser
from multiprocessing.pool import ThreadPool

LANDSAT_ANCHOR = (15, 15)

def runROI():

    napplier = 1
    nworker = 1
    nwriter = 1

    if napplier > 0:
        pool = ThreadPool(processes=napplier)

    landsatArchive = r'H:\EuropeanDataCube\landsat'
    #landsatArchive = r'C:\Work\data\gms\landsat'


    roi = getWRS2FootprintsGeometry(footprints=LandsatArchiveParser.getFootprints(archive=landsatArchive))
    i=0

    for mgrsFootprint, grid in getMGRSPixelGridsByShape(shape=roi, res=30, anchor=LANDSAT_ANCHOR, buffer=30, trim=True):
        if mgrsFootprint != '33UUU': continue
        if napplier==0:
            runFootprint(mgrsFootprint, grid, landsatArchive, nworker, nwriter)
        else:
            pool.apply_async(func=runFootprint, args=(mgrsFootprint, grid, landsatArchive, nworker, nwriter))

        i+=1
        #if i==5: break

    if napplier > 0:
        pool.close()
        pool.join()


def runFootprint(mgrsFootprint, grid, landsatArchive, nworker, nwriter):

    wrs2Footprints = getWRS2NamesInsidePixelGrid(grid=grid)
    cfmask, sr1, sr2, sr3, sr4, sr5, sr6 = LandsatArchiveParser.getFilenames(archive=landsatArchive, footprints=wrs2Footprints, names=['cfmask', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'])
    ysize, xsize = grid.getDimensions()
    nscenes = len(cfmask)
    #if nscenes < 1500: return

    #print('Apply {mgrsFootprint} ({nscenes} Scenes)(WRS2 {wrs2Footprints})'.format(mgrsFootprint=mgrsFootprint, nscenes=len(cfmask), wrs2Footprints=', '.join(wrs2Footprints)))
    descr = ' {mgrsFootprint}[{xsize}x{ysize}], {nscenes} Scenes in WRS2 [{wrs2Footprints}]'.format(xsize=xsize, ysize=ysize, mgrsFootprint=mgrsFootprint, nscenes=len(cfmask), wrs2Footprints=', '.join(wrs2Footprints))

    applier = Applier(grid=grid, nworker=nworker, nwriter=nwriter, windowxsize=25600, windowysize=25600)
    applier.setInputs('cfmask', filenames=cfmask)
    #applier.setInputs('sr1', filenames=sr1)
    #applier.setInputs('sr2', filenames=sr2)
    #applier.setInputs('sr3', filenames=sr3)
    #applier.setInputs('sr4', filenames=sr4)
    #applier.setInputs('sr5', filenames=sr5)
    #applier.setInputs('sr6', filenames=sr6)



    applier.setOutput('dataAvailability', filename=r'h:\ar_temp\dataAvailability{mgrsFootprint}.img'.format(mgrsFootprint=mgrsFootprint), format='GTiff')
    applier.run(ufuncClass=ClearObservations, description=descr)
    #print('---')

class ClearObservations(ApplierOperator):

    def ufunc(self):


        import numpy
        ysize, xsize = self.grid.getDimensions()
        dataAvailability = numpy.zeros(shape=(1, ysize, xsize), dtype=numpy.uint16)

        for cfmask in self.getDatas(name='cfmask'):
            cfmask = None
            #dataAvailability += cfmask < 2


        #for srKey in ['sr'+str(i+1) for i in range(6)]:
        #    for sr in self.getDatas(name=srKey):
        #        sr = None

        #self.setData('dataAvailability', array=dataAvailability)

if __name__ == '__main__':

    from timeit import default_timer
    t0 = default_timer()
    runROI()
    s = (default_timer() - t0); m = s / 60; h = m / 60
    print('done ROI Processing in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))
