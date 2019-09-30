.. _Spatial  Gaussian Gradient Magnitude:

************************************
Spatial  Gaussian Gradient Magnitude
************************************

Applies gaussian_gradient_magnitude filter to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

