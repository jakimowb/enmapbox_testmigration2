from __future__ import division

import numpy
from hub.timing import tic, toc
from lamos.processing.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint


class TCApplier(Applier):

    @staticmethod
    def userFunction(info, inputs, outputs, inmetas, otherArgs):

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


def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    outfolder = r'C:\Work\data\gms\products'

    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    applier = TCApplier(infolder=infolder,
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
