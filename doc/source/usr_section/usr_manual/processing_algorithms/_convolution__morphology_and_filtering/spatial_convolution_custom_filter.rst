.. _Spatial convolution custom filter:

*********************************
Spatial convolution custom filter
*********************************

Create a spatial 2D filter kernel from list or array.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.CustomKernel.html">CustomKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import CustomKernel
        array = [[1, 1, 1],
                 [1, 1, 1],
                 [1, 1, 1]]
        kernel = CustomKernel(array)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

