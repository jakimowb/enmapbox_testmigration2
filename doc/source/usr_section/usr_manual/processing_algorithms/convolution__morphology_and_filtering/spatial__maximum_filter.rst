.. _Spatial  Maximum Filter:

***********************
Spatial  Maximum Filter
***********************

Applies maximum filter to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.maximum <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.maximum.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import maximum_filter
        
        function = lambda array: maximum_filter(array, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

