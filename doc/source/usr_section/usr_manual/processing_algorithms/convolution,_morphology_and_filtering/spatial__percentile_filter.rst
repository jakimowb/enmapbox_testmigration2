.. _Spatial  Percentile Filter:

**************************
Spatial  Percentile Filter
**************************

Applies percentile filter to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.percentile_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.percentile_filter.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import percentile_filter
        
        function = lambda array: percentile_filter(array, percentile=50, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

