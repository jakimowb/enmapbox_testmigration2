from osgeo import gdal
from hubdc import Applier, ApplierOperator, ApplierInput, ApplierOutput
from hubdc.gis.mgrs import getMGRSPixelGrids
from hubdc.gis.wrs2 import getWRS2NamesInsidePixelGrid
from hubdc.landsat.LandsatArchiveParser import LandsatArchiveParser

LANDSAT_ANCHOR = (15, 15)

def script():

    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']
    for mgrsFootprint, grid in zip(mgrsFootprints, getMGRSPixelGrids(names=mgrsFootprints, res=3000, anchor=LANDSAT_ANCHOR, buffer=300)):

        wrs2Footprints = getWRS2NamesInsidePixelGrid(grid=grid)
        cfmask, red, nir = LandsatArchiveParser.getFilenames(archive=r'C:\Work\data\gms\landsat',
                                                             footprints=wrs2Footprints,
                                                             names=['cfmask', 'red', 'nir'])

        print('Apply {mgrsFootprint} ({wrs2Footprints})'.format(mgrsFootprint=mgrsFootprint, wrs2Footprints=', '.join(wrs2Footprints)))
        applier = Applier(grid=grid, ufuncClass=NDVICompositor, nworker=1, nwriter=1, windowxsize=256, windowysize=256)
        applier['cfmask'] = ApplierInput(cfmask)
        applier['red'] = ApplierInput(red)
        applier['nir'] = ApplierInput(nir)
        applier['ndvi'] = ApplierOutput(r'c:\output\ndvi{mgrsFootprint}.img'.format(mgrsFootprint=mgrsFootprint), format='ENVI')
        applier.run()
        print('---')

def getGermanyROI():
    shapeFile = 


class NDVICompositor(ApplierOperator):

    def ufunc(self):
        from numpy import float32, full, nan

        normalizedDifference = lambda a, b: (a-b)/(a+b)

        ysize, xsize = self.grid.getDimensions()
        ndvi = full((1, ysize, xsize), fill_value=nan, dtype=float32)

        for cfmask, red, nir in zip(self.getDatas('cfmask'),
                                    self.getDatas('red', dtype=float32),
                                    self.getDatas('nir', dtype=float32)):
            valid = cfmask == 0
            ndvi[valid] = normalizedDifference(nir[valid], red[valid])

        self.setData('ndvi', array=ndvi)

if __name__ == '__main__':
    script()
