from osgeo import gdal, ogr
from hubdc import Applier, ApplierOperator, ApplierInput, ApplierOutput
from hubdc.gis.mgrs import getMGRSPixelGridsByShape
from hubdc.gis.wrs2 import getWRS2NamesInsidePixelGrid, getWRS2FootprintsGeometry
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser
from multiprocessing.pool import ThreadPool

LANDSAT_ANCHOR = (15, 15)

def runROI():

    napplier = 5
    nworker = 2
    nwriter = 1

    pool = ThreadPool(processes=napplier)

    landsatArchive = r'H:\EuropeanDataCube\landsat'
    landsatArchive = r'C:\Work\data\gms\landsat'

    roi = getWRS2FootprintsGeometry(footprints=LandsatArchiveParser.getFootprints(archive=landsatArchive))
    for mgrsFootprint, grid in getMGRSPixelGridsByShape(shape=roi, res=30, anchor=LANDSAT_ANCHOR, buffer=30):
        pool.apply_async(func=runFootprint, args=(mgrsFootprint, grid, landsatArchive, nworker, nwriter))
    pool.close()
    pool.join()


def runFootprint(mgrsFootprint, grid, landsatArchive, nworker, nwriter):

    wrs2Footprints = getWRS2NamesInsidePixelGrid(grid=grid)
    cfmask, sr1, sr2, sr3, sr4, sr5, sr6 = LandsatArchiveParser.getFilenames(archive=landsatArchive, footprints=wrs2Footprints, names=['cfmask', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'])

    print('Apply {mgrsFootprint} ({nscenes} Scenes)(WRS2 {wrs2Footprints})'.format(mgrsFootprint=mgrsFootprint, nscenes=len(cfmask), wrs2Footprints=', '.join(wrs2Footprints)))

    applier = Applier(grid=grid, nworker=nworker, nwriter=nwriter, windowxsize=256, windowysize=256)
    applier.setInputs('cfmask', filenames=cfmask)
    applier.setInputs('sr1', filenames=sr1)
    applier.setInputs('sr2', filenames=sr2)
    applier.setInputs('sr3', filenames=sr3)
    applier.setInputs('sr4', filenames=sr4)
    applier.setInputs('sr5', filenames=sr5)
    applier.setInputs('sr6', filenames=sr6)

    applier.setOutput('dataAvailability', filename=r'c:\ar_temp\dataAvailability{mgrsFootprint}.img'.format(mgrsFootprint=mgrsFootprint), format='GTiff')
    applier.run(ufuncClass=ClearObservations)
    print('---')

class ClearObservations(ApplierOperator):

    def ufunc(self):

        #import time
        #time.sleep(0)
        #return

        import numpy
        ysize, xsize = self.grid.getDimensions()
        dataAvailability = numpy.zeros(shape=(1, ysize, xsize), dtype=numpy.uint16)
        for cfmask in self.getDatas(name='cfmask'):
            dataAvailability += cfmask < 2

        self.setData('dataAvailability', array=dataAvailability)


if __name__ == '__main__':
    from timeit import default_timer
    t0 = default_timer()
    runROI()
    s = (default_timer() - t0); m = s / 60; h = m / 60
    print('done ROI Processing in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))
