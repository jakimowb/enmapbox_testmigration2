.. _Spatial  Laplace:

****************
Spatial  Laplace
****************

Applies laplace filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Image_Processing>`_ for more information on laplace filtering.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.laplace <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.laplace.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import laplace
        
        function = lambda array: laplace(array)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

