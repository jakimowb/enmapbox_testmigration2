import os
import numpy, numpy.random
#from osgeo import gdal
#from tempfile import gettempdir
#from os.path import join, exists, basename, dirname
from hubdc.applier import ApplierOperator, ApplierInputRasterArchive
from hubdc.tsapplier import TSApplier, TSApplierOutputRaster, TSApplierTilingScheme, TSApplierTile, TSApplierRegionOfInterest

#outdir = join(gettempdir(), 'hubdc_test')

def test():

    regionOfInterest = TSApplierRegionOfInterest.fromShapefile(filename=r'C:\Work\data\applier_ts\roi.shp')
    tilingScheme = TSApplierTilingScheme.fromShapefile(filename=r'C:\Work\data\applier_ts\tiling_scheme_mgrs.shp', regionOfInterest=regionOfInterest)

    applier = TSApplier(tilingScheme=tilingScheme)
    #applier.controls.setWindowFullSize()
    applier.controls.setNumThreads(nworkerAcrossTiles=2, nworkerWithinTiles=1)
    #applier.controls.setNumWriter(nwriter=1)
    #applier.controls.setResolution(3000,3000)
    filter = lambda filename: os.path.basename(filename).startswith('LC8')
    applier.setInputRasterArchive(key='landsat', value=ApplierInputRasterArchive(folder=r'C:\Work\data\gms\landsat', extensions=['img'], filter=filter))
    #applier.outputRaster.setOutput(key='rgb', value=TSApplierOutputRaster(filename=r'c:\output\ts\rgb_{tilename}.img'))
    #applier.outputRaster.setOutput(key='counts', value=TSApplierOutputRaster(filename=r'c:\output\ts\counts_{tilename}.img'))
    applier.apply(operator=Operator)

class Operator(ApplierOperator):
    def ufunc(self):
        return
        arrays = dict()
        arrays['counts'] = list()
        arrays['r'] = list()
        arrays['g'] = list()
        arrays['b'] = list()

        landsat = self.inputRaster.getGroup(key='landsat')
        for path in landsat.getGroups():
            for row in path.getGroups():
                for sceneID in row.getGroupKeys():
                    scene = row.getGroup(sceneID)
                    if sceneID.startswith('LC8'):
                        rgbBandNumbers = [5, 6, 4]
                    else:
                        rgbBandNumbers = [4, 5, 3]

                    cfmask = scene.getRaster(key='{sceneID}_cfmask'.format(sceneID=sceneID))
                    cfmaskArray = cfmask.getImageArray()
                    invalid = cfmaskArray > 1
                    for key, i in zip(['r','g','b'], rgbBandNumbers):
                        raster = scene.getRaster(key='{sceneID}_sr_band{i}'.format(sceneID=sceneID, i=i))
                        array = numpy.float32(raster.getImageArray())
                        array[invalid] = numpy.nan
                        arrays[key].append(array)
                    arrays['counts'].append(invalid==False)

        r = numpy.nanmean(arrays['r'], axis=0)
        g = numpy.nanmean(arrays['g'], axis=0)
        b = numpy.nanmean(arrays['b'], axis=0)
        rgb = numpy.vstack((r, g, b))
        counts = numpy.sum(arrays['counts'], axis=0)
        #self.outputRaster.getOutput('rgb').setArray(array=rgb)
        #self.outputRaster.getOutput('counts').setArray(array=counts)

if __name__ == '__main__':
#    print(outdir)
    test()

