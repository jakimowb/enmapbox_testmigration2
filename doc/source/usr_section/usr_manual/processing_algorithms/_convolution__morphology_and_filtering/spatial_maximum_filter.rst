.. _Spatial Maximum filter:

**********************
Spatial Maximum filter
**********************

Spatial Maximum filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.maximum_filter.html">maximum_filter</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import maximum_filter
        
        function = lambda array: maximum_filter(array, size=3)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

