.. _Spatial  Prewitt:

****************
Spatial  Prewitt
****************

Applies prewitt filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Prewitt_operator>`_ for further information on prewitt operators.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.prewitt <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.prewitt.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import prewitt
        
        function = lambda array: prewitt(array, axis=0)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

