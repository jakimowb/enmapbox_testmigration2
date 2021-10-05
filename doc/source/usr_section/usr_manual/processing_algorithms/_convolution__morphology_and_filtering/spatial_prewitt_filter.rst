.. _Spatial Prewitt filter:

**********************
Spatial Prewitt filter
**********************

Spatial Prewitt filter. See <a href="https://en.wikipedia.org/wiki/Prewitt_operator">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.prewitt.html">prewitt</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import prewitt
        
        function = lambda array: prewitt(array, axis=0)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

