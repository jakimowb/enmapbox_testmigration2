.. _Spatial  Minimum Filter:

***********************
Spatial  Minimum Filter
***********************

Applies minimum filter to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.minimum <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.minimum.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import minimum_filter
        
        function = lambda array: minimum_filter(array, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

