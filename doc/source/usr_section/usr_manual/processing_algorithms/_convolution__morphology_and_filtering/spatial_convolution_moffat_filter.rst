.. _Spatial convolution Moffat filter:

*********************************
Spatial convolution Moffat filter
*********************************

2D Moffat filter.
This kernel is a typical model for a seeing limited PSF.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.Moffat2DKernel.html">Moffat2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import Moffat2DKernel
        kernel = Moffat2DKernel(gamma=2, alpha=2)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

