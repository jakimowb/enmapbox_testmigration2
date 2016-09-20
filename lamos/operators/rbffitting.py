from __future__ import division
#from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc
import numba

import numpy
import matplotlib.pyplot as plt
from hub.gdal.api import readCube, GDALMeta
from hub.datetime import Date
from astropy.convolution import Gaussian1DKernel, convolve

def test_1dfit():

    # Read profile

    cfmaskFile = r'C:\Work\data\rbffit\cfmask.img'
    swir1File = r'C:\Work\data\rbffit\swir1.img'
    meta = GDALMeta(swir1File)
    cfmask = readCube(cfmaskFile).astype(float)
    invalid = cfmask > 1
    valid = numpy.logical_not(invalid)
    swir1 = readCube(swir1File).astype(float)
    swir1[invalid] = numpy.NaN
    dates = [Date.fromText(bandName) for bandName in meta.getMetadataItem('band_names')]
    indices = [(date-dates[0]).days for date in dates]
    outshape = [indices[-1]+1] + list(swir1.shape[1:])

    swir1_full = numpy.full(outshape, numpy.NaN, dtype=numpy.float32)
    for i, index in enumerate(indices):
        swir1_full[index] = swir1[i]

    x = map(float, range(indices[-1]+1))
    y = swir1_full[:,1,1]
    v = numpy.isfinite(y)

    def conv(stddev):
        kernel = Gaussian1DKernel(stddev=stddev)
        z = convolve(y, kernel, boundary='fill', fill_value=numpy.NaN, normalize_kernel=True)
        m = numpy.isfinite(z)
        z[numpy.logical_not(m)] = 0
        w = convolve(v, kernel.array*0+1., boundary='fill', fill_value=0, normalize_kernel=False)
        print kernel.array.shape[0]/8.
        return z, m, w

    plt.plot(x, y, 'k.')

    # Convolve data
    z = numpy.zeros_like(y)
    m = numpy.zeros_like(y)
    w = numpy.zeros_like(y)
#    for stddev, weight in zip([5, 10, 15, 20, 25, 30, 35, 40, 50, 60],
#                              [100, 100, 100, 30, 10, 5, 1, 1, 1, 1]):
    for stddev, weight in zip([3*8, 5*8, 7*8],
                              [5, 2, 1]):
        zi, mi, wi = conv(stddev)
        z += zi*wi*weight
        #m += mi
        w += wi*weight
        plt.plot(x, zi, 'r-')
        plt.plot(x, wi, 'g-')

    z /= w
    # Plot data before and after convolution

    plt.plot(x, z)
    plt.show()

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'
    infolder = r'C:\Work\data\gms\landsatTimeseriesMGRS'
    outfolder = r'C:\Work\data\gms\products'

    mgrsFootprints = ['32UPC','32UQC','33UTT','33UUT']

    applier = RBFFitApplier(infolder=infolder,
                          outfolder=outfolder,
                          inextension='.img',
                          footprints=mgrsFootprints,
                          compressed=False)
    applier.controls.setWindowXsize(10000)
    applier.controls.setWindowYsize(100)
    applier.apply()


if __name__ == '__main__':

    tic()
    test_1dfit()
    toc()
