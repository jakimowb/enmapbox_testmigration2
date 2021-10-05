.. _Spatial convolution ring filter:

*******************************
Spatial convolution ring filter
*******************************

2D Ring filter.
The Ring filter kernel is the difference between two Top-Hat kernels of different width. This kernel is useful for, e.g., background estimation.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Ring2DKernel.html">Ring2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Ring2DKernel
        kernel = Ring2DKernel(radius_in=3, width=2)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

