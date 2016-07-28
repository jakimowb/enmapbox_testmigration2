from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc

'''
class ShapefileImporterApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        nir = inputs.timeseries_nir.astype(numpy.float32)
        red = inputs.timeseries_red.astype(numpy.float32)
        ndvi = (nir-red)/(nir+red)

        # scale output to int range
        ndvi = (ndvi * 10000).astype(numpy.int16)

        # mask out invalid pixel
        cfmask = inputs.timeseries_cfmask
        invalid = cfmask != 0
        ndvi[invalid] = -10000

        outputs.vi_ndvi = ndvi


    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        outmetas.vi_ndvi = inmetas.timeseries_cfmask
        outmetas.vi_ndvi.setNoDataValue(-10000)


    def __init__(self, infolder, inextension, outfolder, footprints=None, compressed=False):

        Applier.__init__(self, footprints=footprints, compressed=compressed)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                         productName='timeseries', imageNames=['nir', 'red', 'cfmask'], extension=inextension))
        self.appendOutput(ApplierOutput(folder=outfolder,
                                           productName='vi', imageNames=['ndvi'], extension='.img'))
'''

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'

    inshapefile = r'C:\Work\data\gms\lucas\eu27_lucas_2012_subset1.shp'
    outfolder = r'C:\Work\data\gms\lucasMGRS'
    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    import hub.ogr.util, os, hub.gdal.util
    for mgrsFootprint in [MGRSFootprint.fromShp(name) for name in mgrsFootprints]:
        outfile = os.path.join(outfolder, '32UPC', 'lucas.shp')
        clipdst = '-clipdst '+str(mgrsFootprint.ul[0])+' '+str(mgrsFootprint.ul[1])+' '+str(mgrsFootprint.lr[0])+' '+str(mgrsFootprint.lr[1])+' '
        t_srs = '-t_srs EPSG:326' + mgrsFootprint.utm + ' '
        options = clipdst+t_srs
        hub.ogr.util.ogr2ogr(outfile=outfile, infile=inshapefile, options=options)

        outfile2 = outfile.replace('.shp', '_lc4.img')
        a = '-a LC4_ID '
        a_nodata = '-a_nodata 0 '
        init = '-init 0 '
        tr = '-tr 30 30 '
        ot = '-ot Byte '
        of = '-of ENVI '
        options = a+a_nodata+tr+ot+of
        hub.gdal.util.gdal_rasterize(outfile=outfile2, infile=outfile, options=options)

        break

    '''applier = NDVIApplier(infolder=infolder,
                          outfolder=outfolder,
                          inextension='.img',
                          footprints=mgrsFootprints,
                          compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()'''


if __name__ == '__main__':

    tic()
    test()
    toc()
