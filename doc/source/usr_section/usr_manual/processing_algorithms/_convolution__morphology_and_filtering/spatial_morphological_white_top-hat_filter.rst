.. _Spatial morphological White Top-Hat filter:

******************************************
Spatial morphological White Top-Hat filter
******************************************

Spatial morphological White Top-Hat filter. See <a href="https://en.wikipedia.org/wiki/Top-hat_transform">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.white_tophat.html">scipy.ndimage.white_tophat</a> for information on different parameters.

    Default::

        from scipy.ndimage.morphology import white_tophat
        
        function = lambda array: white_tophat(array, size=(3, 3))
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

