.. _Random Points from Classification:

*********************************
Random Points from Classification
*********************************

Randomly samples a user defined amount of points/pixels from a classification raster and returns them as a vector dataset.

**Parameters**


:guilabel:`Classification` [raster]
    Specify input raster.


:guilabel:`Number of Points per Class` [string]
    List of number of points, given as integers or fractions between 0 and 1, to sample from each class. If a scalar is specified, the value is broadcasted to all classes. 
    
    
    
    

    Default: *100*

**Outputs**


:guilabel:`Output Vector` [vectorDestination]
    Specify output path for the vector.

