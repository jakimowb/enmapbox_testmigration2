.. _Spectral convolution Trapezoid filter:

*************************************
Spectral convolution Trapezoid filter
*************************************

1D Trapezoid filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Trapezoid1DKernel.html">Trapezoid1DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Trapezoid1DKernel
        kernel = Trapezoid1DKernel(width=3, slope=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

