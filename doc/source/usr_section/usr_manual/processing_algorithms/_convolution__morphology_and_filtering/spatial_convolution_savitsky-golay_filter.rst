.. _Spatial convolution Savitsky-Golay filter:

*****************************************
Spatial convolution Savitsky-Golay filter
*****************************************

2D Savitsky-Golay filter.
See <a href="https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter#Two-dimensional_convolution_coefficients">wikipedia</a> for details.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="https://scipy-cookbook.readthedocs.io/items/SavitzkyGolay.html#Two-dimensional-data-smoothing-and-least-square-gradient-estimate">sgolay2d</a> from the SciPy cookbook for information on different parameters.

    Default::

        from astropy.convolution import Kernel2D
        from enmapboxprocessing.algorithm.spatialconvolutionsavitskygolay2dalgorithm import sgolay2d
        kernel = Kernel2D(array=sgolay2d(window_size=11, order=3, derivative=None))

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

