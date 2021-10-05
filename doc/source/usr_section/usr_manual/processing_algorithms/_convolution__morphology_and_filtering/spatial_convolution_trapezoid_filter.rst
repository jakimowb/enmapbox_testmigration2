.. _Spatial convolution Trapezoid filter:

************************************
Spatial convolution Trapezoid filter
************************************

2D Trapezoid filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.TrapezoidDisk2DKernel.html">TrapezoidDisk2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import TrapezoidDisk2DKernel
        kernel = TrapezoidDisk2DKernel(radius=3, slope=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

