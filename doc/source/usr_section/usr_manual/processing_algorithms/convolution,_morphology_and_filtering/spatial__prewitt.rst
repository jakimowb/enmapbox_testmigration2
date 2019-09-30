.. _Spatial  Prewitt:

****************
Spatial  Prewitt
****************

Applies prewitt filter to image. See `Wikipedia <https://en.wikipedia.org/wiki/Prewitt_operator>`_ for further information on prewitt operators.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.prewitt <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.prewitt.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import prewitt
        
        function = lambda array: prewitt(array, axis=0)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

