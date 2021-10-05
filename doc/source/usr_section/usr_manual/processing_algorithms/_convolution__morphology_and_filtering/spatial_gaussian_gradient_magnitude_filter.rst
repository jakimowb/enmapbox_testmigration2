.. _Spatial Gaussian Gradient Magnitude filter:

******************************************
Spatial Gaussian Gradient Magnitude filter
******************************************

Spatial Gaussian Gradient Magnitude filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_gradient_magnitude.html">gaussian_gradient_magnitude</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import gaussian_gradient_magnitude
        
        function = lambda array: gaussian_gradient_magnitude(array, sigma=1)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

