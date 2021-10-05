.. _Spectral convolution Box filter:

*******************************
Spectral convolution Box filter
*******************************

1D Box filter.
The Box filter or running mean is a smoothing filter. It is not isotropic and can produce artifacts, when applied repeatedly to the same data.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Box1DKernel.html">Box1DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Box1DKernel
        kernel = Box1DKernel(width=5)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

