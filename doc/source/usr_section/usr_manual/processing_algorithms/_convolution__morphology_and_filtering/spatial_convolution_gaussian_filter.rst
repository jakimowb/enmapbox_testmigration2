.. _Spatial convolution Gaussian filter:

***********************************
Spatial convolution Gaussian filter
***********************************

2D Gaussian filter.
The Gaussian filter is a filter with great smoothing properties. It is isotropic and does not produce artifacts.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Gaussian2DKernel.html">Gaussian2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Gaussian2DKernel
        kernel = Gaussian2DKernel(x_stddev=1, y_stddev=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

