.. _Spatial  Sobel:

**************
Spatial  Sobel
**************

Applies sobel filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Sobel_operator>`_ for further information on sobel operators

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.sobel <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.sobel.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import sobel
        
        function = lambda array: sobel(array, axis=0)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

