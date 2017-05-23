from osgeo import gdal, ogr
from hubdc import Applier, ApplierOperator, ApplierInput, ApplierOutput
from hubdc.gis.mgrs import getMGRSPixelGridsByNames
from hubdc.gis.wrs2 import getWRS2NamesInsidePixelGrid
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser

LANDSAT_ANCHOR = (15, 15)

def script():

    applier = Applier(nworker=5, nwriter=4, windowxsize=256, windowysize=256)

    for mgrsFootprint, grid in getMGRSPixelGridsByNames(names=['32UQC', '33UTT'], res=300, anchor=LANDSAT_ANCHOR, buffer=300):

        wrs2Footprints = getWRS2NamesInsidePixelGrid(grid=grid)
        cfmask, nir, red = LandsatArchiveParser.getFilenames(archive=r'C:\Work\data\gms\landsat', footprints=wrs2Footprints, names=['cfmask', 'nir', 'red'])

        # sum up cfmask
        print('Apply CFMASK {mgrsFootprint} ({wrs2Footprints})'.format(mgrsFootprint=mgrsFootprint, wrs2Footprints=', '.join(wrs2Footprints)))
        applier.setInputs('in', filenames=cfmask)
        applier.setOutput('out', filename=r'c:\output\cfmask{mgrsFootprint}.img'.format(mgrsFootprint=mgrsFootprint), format='GTiff')
        applier.run(grid=grid, ufuncClass=ClearObservations)

        # sum up nir
        print('Apply NIR {mgrsFootprint} ({wrs2Footprints})'.format(mgrsFootprint=mgrsFootprint, wrs2Footprints=', '.join(wrs2Footprints)))
        applier.setInputs('in', filenames=nir)
        applier.setOutput('out', filename=r'c:\output\nir{mgrsFootprint}.img'.format(mgrsFootprint=mgrsFootprint), format='GTiff')
        applier.run(grid=grid, ufuncClass=ClearObservations)

        print('---')

    applier.close()

class ClearObservations(ApplierOperator):

    def ufunc(self):
        import numpy
        ysize, xsize = self.grid.getDimensions()
        sum = numpy.zeros(shape=(1, ysize, xsize), dtype=numpy.float32)
        for band in self.getArrayIterator(name='in'): sum += band
        self.setData('out', array=sum)

if __name__ == '__main__':

    from timeit import default_timer
    t0 = default_timer()
    script()
    s = (default_timer() - t0)
    m = s / 60
    h = m / 60
    print('done in {s} sec | {m}  min | {h} hours'.format(s=int(s), m=round(m, 2), h=round(h, 2)))
