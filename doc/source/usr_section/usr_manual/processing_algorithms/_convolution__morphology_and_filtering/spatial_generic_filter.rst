.. _Spatial generic filter:

**********************
Spatial generic filter
**********************

Spatial generic (user-defined) filter.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generic_filter.html">generic_filter</a> for information on different parameters.

    Default::

        from scipy.ndimage.filters import generic_filter
        import numpy as np
        
        def filter_function(invalues):
            # do whatever you want to create the output value, e.g. np.nansum
            outvalue = np.nansum(invalues)  # replace this line with your code!
            return outvalue
        
        function = lambda array: generic_filter(array, function=filter_function, size=3)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

