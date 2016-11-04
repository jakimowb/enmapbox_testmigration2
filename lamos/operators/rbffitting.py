from __future__ import division
from lamos.processing.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
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

    cfmaskFile = r'C:\Work\data\marcel\TS_RBF_test_stacks_big_intersection\fmask.tif'
    swir1File = r'C:\Work\data\marcel\TS_RBF_test_stacks_big_intersection\swir1.tif'

    meta = GDALMeta(swir1File)
    xoff = 0
    yoff = 0
    cfmask = readCube(cfmaskFile, xoff=xoff, yoff=yoff, xsize=1, ysize=1).astype(float)
    swir1 = readCube(swir1File, xoff=xoff, yoff=yoff, xsize=1, ysize=1).astype(float)
    invalid = cfmask > 1
    valid = numpy.logical_not(invalid)
    swir1[invalid] = numpy.NaN
    #dates = [Date.fromText(bandName) for bandName in meta.getMetadataItem('band_names')]
    dates = [Date.fromLandsatSceneID(bandName) for bandName in meta.getMetadataItem('band_names')]

    indices = [(date-dates[0]).days for date in dates]
    outshape = [indices[-1]+1] + list(swir1.shape[1:])

    swir1_full = numpy.full(outshape, numpy.NaN, dtype=numpy.float32)
    for i, index in enumerate(indices):
        swir1_full[index] = swir1[i]

    x = map(float, range(indices[-1]+1))
    #x = [date.decimalYear for date in dates]

    y = swir1_full[:,0,0]
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
    #for stddev, weight in zip([10],
    #                          [1]):
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

if __name__ == '__main__':

    tic()
    test_1dfit()
    toc()
