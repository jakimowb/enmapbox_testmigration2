from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc

class NDVIApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

        print('tile done ', info.yblock + 1, '/', info.ytotalblocks)

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


class TCApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):


        print('tile done ', info.yblock + 1, '/', info.ytotalblocks)

        coeffBrightness = {'TM':       [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303],
                           'ETM':      [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303],
                           'OLI_TIRS': [0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303]}

        coeffGreenness  = {'TM':       [-0.1603, -0.2819, -0.4934, 0.7940, 0.0002, 0.1446],
                           'ETM':      [-0.1603, -0.2819, -0.4934, 0.7940, 0.0002, 0.1446],
                           'OLI_TIRS': [-0.1603, -0.2819, -0.4934, 0.7940, 0.0002, 0.1446]}

        coeffWetness    = {'TM':       [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109],
                           'ETM':      [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109],
                           'OLI_TIRS': [0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109]}

        # cast inputs to float
        for name in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
            inputs.__dict__['timeseries_'+ name] = inputs.__dict__['timeseries_'+ name].astype(numpy.float32)

        # create sensor-specific coefficient array
        sensors = inmetas.timeseries_cfmask.getMetadataItem('sensor')
        coeffB = numpy.array([coeffBrightness[sensor] for sensor in sensors]).T
        coeffG = numpy.array([coeffGreenness[sensor] for sensor in sensors]).T
        coeffW = numpy.array([coeffWetness[sensor] for sensor in sensors]).T

        # calculate tc components
        b = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
        g = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
        w = numpy.zeros_like(inputs.timeseries_cfmask, dtype=numpy.float32)
        for i, name in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
            b += coeffB[i].reshape(-1,1,1) * inputs.__dict__['timeseries_' + name]
            g += coeffG[i].reshape(-1,1,1) * inputs.__dict__['timeseries_' + name]
            w += coeffW[i].reshape(-1,1,1) * inputs.__dict__['timeseries_' + name]

        # mask out invalid pixel
        cfmask = inputs.timeseries_cfmask
        invalid = cfmask != 0
        noDataValue = -30000
        b[invalid] = noDataValue
        g[invalid] = noDataValue
        w[invalid] = noDataValue

        # return results
        outputs.tasseled_cap_brightness = b.astype(numpy.int16)
        outputs.tasseled_cap_greeness = g.astype(numpy.int16)
        outputs.tasseled_cap_wetness = w.astype(numpy.int16)



    @staticmethod
    def userFunctionMeta(inmetas, outmetas, otherArgs):

        outmetas.tasseled_cap_brightness = inmetas.timeseries_cfmask
        outmetas.tasseled_cap_greeness = inmetas.timeseries_cfmask
        outmetas.tasseled_cap_wetness = inmetas.timeseries_cfmask
        noDataValue = -30000
        outmetas.tasseled_cap_brightness.setNoDataValue(noDataValue)
        outmetas.tasseled_cap_greeness.setNoDataValue(noDataValue)
        outmetas.tasseled_cap_wetness.setNoDataValue(noDataValue)


    def __init__(self, infolder, inextension, outfolder, footprints=None, compressed=False):

        Applier.__init__(self, footprints=footprints, compressed=compressed)
        self.appendInput(ApplierInput(archive=MGRSArchive(folder=infolder),
                                         productName='timeseries', imageNames=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask'], extension=inextension))
        self.appendOutput(ApplierOutput(folder=outfolder,
                                           productName='tasseled_cap', imageNames=['brightness', 'greeness', 'wetness'], extension='.img'))

def test_ar():

    applier = NDVIApplier(infolder=r'c:\work\data\gms\landsatTimeseriesMGRS',
                          inextension='.vrt', # use '.img' if timeseries is written as ENVI Files
                          outfolder=r'c:\work\data\gms\products',
                          compressed=True)
    applier.controls.setWindowXsize(100)
    applier.controls.setWindowYsize(100)
    archive = applier.apply()
    archive.info()

def test():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\gis\MGRS_100km_1MIL_Files'

    #mgrsFootprints = ['36SVG']
    #mgrsFootprints = ['37SEB', '36SVG', '38TMK', '38SMK', '37SEA']
    mgrsFootprints = None

    applier = TCApplier(infolder=r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_landsatTimeseriesMGRS',
                          outfolder=r'\\141.20.140.91\SAN_RSDBrazil\LandsatData\Landsat_Turkey\02_OutputData\LandsatX\ar_products',
                          inextension='.img',
                          footprints=mgrsFootprints,
                          compressed=False)
    applier.controls.setWindowXsize(256*100)
    applier.controls.setWindowYsize(256)
    archive = applier.apply()


if __name__ == '__main__':

    tic()
    test()
    toc()
