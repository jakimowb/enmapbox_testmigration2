.. _Spectral convolution Gaussian filter:

************************************
Spectral convolution Gaussian filter
************************************

1D Gaussian filter.
The Gaussian filter is a filter with great smoothing properties. It is isotropic and does not produce artifacts.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Gaussian1DKernel.html">Gaussian1DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Gaussian1DKernel
        kernel = Gaussian1DKernel(stddev=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

