.. _Random points from mask raster layer:

************************************
Random points from mask raster layer
************************************

This algorithm creates a new point layer with a given number of random points, all of them in the area where the given mask evaluates to true.

**Parameters**


:guilabel:`Mask raster layer` [raster]
    A mask raster layer to draw locations from.


:guilabel:`Number of points` [number]
    Number of points to be drawn.


:guilabel:`Minimum distance between points (in meters)` [number]
    A minimum distance between points can be specified. A point will not be added if there is an already generated point within this (Euclidean) distance from the generated location.

    Default: *0*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output point layer` [vectorDestination]
    Output vector file destination.

