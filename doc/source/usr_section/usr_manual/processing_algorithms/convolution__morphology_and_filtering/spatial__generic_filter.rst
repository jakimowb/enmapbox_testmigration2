.. _Spatial  Generic Filter:

***********************
Spatial  Generic Filter
***********************

Applies generic_filter to image using a user-specifiable function. This algorithm can perform operations you might know as moving window or focal statistics from some other GIS systems. Mind that depending on the function this algorithms can take some time to process.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. The function argument can take any callable function that expects a 1D array as input and returns a single value. You should alter the preset in the code window and define your own function. See `scipy.ndimage.generic_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generic_filter.html>`_ for information on different parameters.

    Default::

        from scipy.ndimage.filters import generic_filter
        import numpy as np
        
        def filter_function(invalues):
        
            # do whatever you want to create the output value, e.g. np.nansum
            # outvalue = np.nansum(invalues)
            return outvalue
        
        function = lambda array: generic_filter(array, function=filter_function, size=3)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

