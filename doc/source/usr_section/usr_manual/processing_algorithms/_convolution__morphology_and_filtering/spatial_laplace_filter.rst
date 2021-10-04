.. _Spatial Laplace filter:

**********************
Spatial Laplace filter
**********************

Spatial Laplace filter. See <a href="https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Image_Processing">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.laplace.html">laplace</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import laplace
        
        function = lambda array: laplace(array)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

