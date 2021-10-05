.. _Spatial Percentile filter:

*************************
Spatial Percentile filter
*************************

Spatial Percentile filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.percentile_filter.html">percentile_filter</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import percentile_filter
        
        function = lambda array: percentile_filter(array, percentile=50, size=3)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

