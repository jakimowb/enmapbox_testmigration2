.. _Spatial Morphological Laplace:

*****************************
Spatial Morphological Laplace
*****************************

Applies morphological_laplace filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Image_Processing>`_ for more information on laplace filtering.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.morphological_laplace <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphological_laplace.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.morphology import morphological_laplace
        function = lambda array: morphological_laplace(array, size=(3,3))
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

