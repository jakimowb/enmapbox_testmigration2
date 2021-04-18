.. _Random points in raster:

***********************
Random points in raster
***********************

This algorithm creates a new point layer with a given number of random points, all of them in the area where the given mask raster evaluates to true.

**Parameters**


:guilabel:`Mask` [raster]
    Source raster interpreted as binary mask. All no data (zero, if missing), inf and nan pixel evaluate to false, all other to true. Note that only the first band used by the renderer is considered.


:guilabel:`Number of points` [number]
    Number of points to be drawn.


:guilabel:`Minimum distance between points (in meters)` [number]
    A minimum distance between points can be specified. A point will not be added if there is an already generated point within this (Euclidean) distance from the generated location.

    Default: *0*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output points` [vectorDestination]
    Output vector destination.

