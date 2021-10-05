.. _Create mask raster layer:

************************
Create mask raster layer
************************

Create a mask raster layer by applying a user-defined evaluation function band-wise to a source raster layer. 

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code defining the evaluation function. The defined function must return a binary-valued array with same shape as the input array.

    Default::

        import numpy as np
        
        def function(array: np.ndarray, noDataValue: float):
        
            # if source no data value is not defined, use zero as no data value
            if noDataValue is None:
                noDataValue = 0
        
            # mask no data pixel
            marray = np.not_equal(array, noDataValue)
        
            # mask inf and nan pixel
            marray[np.logical_not(np.isfinite(array))] = 0
        
            # include further masking criteria here
            pass
        
            return marray
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

