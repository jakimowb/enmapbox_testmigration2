.. _Spatial  Minimum Filter:

***********************
Spatial  Minimum Filter
***********************

Applies minimum filter to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.minimum <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.minimum.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import minimum_filter
        
        function = lambda array: minimum_filter(array, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

