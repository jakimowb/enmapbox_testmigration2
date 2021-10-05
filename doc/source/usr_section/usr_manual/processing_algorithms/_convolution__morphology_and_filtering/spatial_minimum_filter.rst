.. _Spatial Minimum filter:

**********************
Spatial Minimum filter
**********************

Spatial Minimum filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.minimum_filter.html">minimum_filter</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import minimum_filter
        
        function = lambda array: minimum_filter(array, size=3)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

