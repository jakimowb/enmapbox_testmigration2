.. _Spatial morphological Laplace filter:

************************************
Spatial morphological Laplace filter
************************************

Spatial morphological Laplace filter. See <a href="https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Image_Processing">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphological_laplace.html">morphological_laplace</a> for information on different parameters.

    Default::

        from scipy.ndimage.morphology import morphological_laplace
        
        function = lambda array: morphological_laplace(array, size=(3, 3))
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

