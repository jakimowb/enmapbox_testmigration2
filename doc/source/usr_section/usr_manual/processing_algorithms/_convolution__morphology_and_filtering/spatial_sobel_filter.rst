.. _Spatial Sobel filter:

********************
Spatial Sobel filter
********************

Spatial Sobel filter. See <a href="https://en.wikipedia.org/wiki/Sobel_operator">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.sobel.html">sobel</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import sobel
        
        function = lambda array: sobel(array, axis=0)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

