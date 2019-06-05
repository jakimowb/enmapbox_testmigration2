.. _Spatial  Maximum Filter:

***********************
Spatial  Maximum Filter
***********************

Applies maximum filter to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.maximum <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.maximum.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import maximum_filter
        
        function = lambda array: maximum_filter(array, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

