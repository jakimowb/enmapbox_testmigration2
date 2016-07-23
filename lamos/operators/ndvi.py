from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc

class NDVIApplier(Applier):

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

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    outfolder = r'C:\Work\data\gms\products'

    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    applier = NDVIApplier(infolder=infolder,
                          outfolder=outfolder,
                          inextension='.img',
                          footprints=mgrsFootprints,
                          compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
