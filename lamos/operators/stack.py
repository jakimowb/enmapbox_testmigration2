from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc
from hub.gdal.util import stack_bands
from hub.gdal.api import GDALMeta
import enmapbox.processing
from enmapbox.processing.estimators import Classifiers
from enmapbox.processing.env import PrintProgress
import gdal
import os

class StackApplier(Applier):

    def __init__(self, outfolder, outproduct, outimage, footprints=None):

        Applier.__init__(self, footprints=footprints)


        self.appendOutput(ApplierOutput(folder=outfolder,
                                        productName=outproduct,
                                        imageNames=[outimage],
                                        extension='.vrt'))

    def appendFeatures(self, infolder, inproduct, inimage, inextension, inbands=None):
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                      productName=inproduct,
                                      imageNames=[inimage],
                                      extension=inextension,
                                      bands=inbands))

    def applyToFootprint(self, footprint):

        print(footprint.name)

        # create VRT stack
        outfile = self.outputs[0].getFilenameAssociations(footprint).__dict__.values()[0]
        if os.path.exists(outfile):
            return

        infiles = list()
        inbands = list()
        band_names = list()
        for input in self.inputs:
            filename = input.getFilenameAssociations(footprint).__dict__.values()[0]
            if input.bands is None:
                ds = gdal.Open(filename)
                bands = range(0, ds.RasterCount)
                ds = None
            else:
                bands = input.bands

            for band in bands:
                infiles.append(filename)
                inbands.append(band+1)

            meta = GDALMeta(filename)
            basename = os.path.splitext(os.path.basename(filename))[0]
            band_names.extend([name+'_'+basename for i, name in enumerate(meta.getMetadataItem('band_names')) if i in bands])


        stack_bands(outfile, infiles, inbands)

        outmeta = GDALMeta(outfile)
        outmeta.setMetadataItem('band_names', band_names)
        outmeta.writeMeta(outfile)

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'

    infolder = r'C:\Work\data\gms\productsMGRS'
    outfolder = r'C:\Work\data\gms\stackMGRS'

    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']

    stacker = StackApplier(outfolder=outfolder, outproduct='stack', outimage='stack', footprints=mgrsFootprints)
    stacker.appendFeatures(infolder=infolder, inproduct='composite', inimage='2000-01-01_to_2000-12-31_61y', inextension='.img', inbands=None)
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi', 'nbr']:
        stacker.appendFeatures(infolder=infolder, inproduct='statistics', inimage=key+'_2000-01-01_to_2000-12-31_61y', inextension='.img', inbands=None)
    stacker.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
