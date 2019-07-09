.. _Spatial  Gaussian Gradient Magnitude:

************************************
Spatial  Gaussian Gradient Magnitude
************************************

Applies gaussian_gradient_magnitude filter to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.gaussian_gradient_magnitude <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_gradient_magnitude.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import gaussian_gradient_magnitude
        
        function = lambda array: gaussian_gradient_magnitude(array, sigma=1)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

