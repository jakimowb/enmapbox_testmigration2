.. _Spatial Morphological White Tophat:

**********************************
Spatial Morphological White Tophat
**********************************

Applies white_tophat morphology filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Top-hat_transform>`_ for more information on top-hat transformation.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.white_tophat <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.white_tophat.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.morphology import white_tophat
        function = lambda array: white_tophat(array, size=(3,3))
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

