.. _Spatial convolution Top-Hat filter:

**********************************
Spatial convolution Top-Hat filter
**********************************

2D Top-Hat filter.
The Top-Hat filter is an isotropic smoothing filter. It can produce artifacts when applied repeatedly on the same data.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Tophat2DKernel.html">Tophat2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Tophat2DKernel
        kernel = Tophat2DKernel(radius=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

