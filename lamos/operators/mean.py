from __future__ import division

import numpy
from hub.timing import tic, toc
from lamos.processing.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint


class MeanApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        invalidValues = inputs.timeseries_cfmask != 0
        validCounts = numpy.sum(numpy.logical_not(invalidValues), dtype=numpy.int16, axis=0, keepdims=True)
        invalidPixels = validCounts == 0
        outputs.mean_valid = validCounts
        for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
            inband = inputs.__dict__['timeseries_'+ name].astype(numpy.float32)
            inband[invalidValues] = numpy.NaN
            outband = numpy.nanmean(inband, axis=0, dtype=numpy.float32, keepdims=True)
            outband[invalidPixels] = -9999
            outputs.__dict__['mean_'+ name] = outband.astype(numpy.int16)


    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
            outmetas.__dict__['mean_' + name].setNoDataValue(-9999)


    def __init__(self, infolder, inextension, outfolder, footprints=None, compressed=False):

        Applier.__init__(self, footprints=footprints)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                         productName='timeseries', imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'], extension=inextension))
        self.appendOutput(ApplierOutput(folder=outfolder,
                                           productName='mean', imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'valid'], extension='.img'))


def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    outfolder = r'C:\Work\data\gms\productsMean'

    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    applier = MeanApplier(infolder=infolder,
                          outfolder=outfolder,
                          inextension='.vrt',
                          footprints=mgrsFootprints,
                          compressed=False)
    applier.controls.setWindowXsize(100)
    applier.controls.setWindowYsize(100)
    applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
