from __future__ import division

from hub.timing import tic, toc
from lamos.processing.types import Applier, ApplierInput, MGRSArchive, MGRSFootprint


class DummyReadApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):
        # do nothing
        return


    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):
        # do nothing
        return

    def __init__(self, infolder, inextension, footprints=None):

        Applier.__init__(self, footprints=footprints, overwrite=True)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                         productName='timeseries', imageNames=['cfmask'], extension=inextension))
                                         #productName='timeseries', imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'], extension=inextension))



def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']
    mgrsFootprints = ['33UTT']

    #2.74 min
    applier = DummyReadApplier(infolder=infolder, inextension='.vrt', footprints=mgrsFootprints)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()



if __name__ == '__main__':

    tic()
    test()
    toc()
