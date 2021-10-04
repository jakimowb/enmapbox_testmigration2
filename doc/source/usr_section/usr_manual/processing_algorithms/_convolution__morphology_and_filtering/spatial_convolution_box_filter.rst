.. _Spatial convolution Box filter:

******************************
Spatial convolution Box filter
******************************

2D Box filter.
The Box filter or running mean is a smoothing filter. It is not isotropic and can produce artifact, when applied repeatedly to the same data.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Box2DKernel.html">Box2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Box2DKernel
        kernel = Box2DKernel(width=5)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

