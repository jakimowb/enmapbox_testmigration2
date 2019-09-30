.. _Spatial  Percentile Filter:

**************************
Spatial  Percentile Filter
**************************

Applies percentile filter to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.percentile_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.percentile_filter.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import percentile_filter
        
        function = lambda array: percentile_filter(array, percentile=50, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

