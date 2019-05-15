.. _Spatial  Median Filter:

**********************
Spatial  Median Filter
**********************

Applies median filter to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.median <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import median_filter
        
        function = lambda array: median_filter(array, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

