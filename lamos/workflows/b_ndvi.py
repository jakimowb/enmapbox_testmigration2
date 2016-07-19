from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive
import numpy

class NDVIApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        nir = inputs.timeseries_nir.astype(numpy.float32)
        red = inputs.timeseries_red.astype(numpy.float32)
        ndvi = (nir-red)/(nir+red)

        cfmask = inputs.timeseries_cfmask
        invalid = cfmask != 0
        ndvi[invalid] = -1

        outputs.vi_ndvi = ndvi


    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        outmetas.vi_ndvi = inmetas.timeseries_cfmask
        outmetas.vi_ndvi.setNoDataValue(-1)


    def __init__(self, infolder, outfolder, compressed=False):

        Applier.__init__(self, compressed=compressed)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                         productName='timeseries', imageNames=['nir', 'red', 'cfmask'], extension='.img'))
        self.appendOutput(ApplierOutput(folder=outfolder,
                                           productName='vi', imageNames=['ndvi'], extension='.img'))


    def apply(self):

        Applier.apply(self)
        return MGRSArchive(self.outputs[0].folder)


def test():

    applier = NDVIApplier(infolder=r'c:\work\data\gms\landsatTimeseriesMGRS',
                          outfolder=r'c:\work\data\gms\products',
                          compressed=True)
    applier.controls.setWindowXsize(100)
    applier.controls.setWindowYsize(100)
    archive = applier.apply()
    archive.info()


if __name__ == '__main__':

    import hub.timing
    hub.timing.tic()
    test()
    hub.timing.toc()
