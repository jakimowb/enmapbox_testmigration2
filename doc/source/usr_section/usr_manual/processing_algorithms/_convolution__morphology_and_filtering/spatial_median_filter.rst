.. _Spatial Median filter:

*********************
Spatial Median filter
*********************

Spatial Median filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html">median_filter</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import median_filter
        
        function = lambda array: median_filter(array, size=3)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

