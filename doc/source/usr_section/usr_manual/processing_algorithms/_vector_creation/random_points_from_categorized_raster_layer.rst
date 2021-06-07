.. _Random points from categorized raster layer:

*******************************************
Random points from categorized raster layer
*******************************************

This algorithm creates a new point layer with a given number of random points, all of them within the categories of the given categorized raster layer.

**Parameters**


:guilabel:`Categorized raster layer` [raster]
    A categorized raster layer to draw points from.


:guilabel:`Number of points per category` [string]
    Number of points to draw from each category. Set a single value N to draw N points for each category. Set a list of values N1, N2, ... Ni, ... to draw Ni points for category i.


:guilabel:`Minimum distance between points (in meters)` [number]
    A minimum (Euclidean) distance between points can be specified.

    Default: *0*


:guilabel:`Minimum distance between points inside category (in meters)` [number]
    A minimum (Euclidean) distance between points in a category can be specified.

    Default: *0*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output point layer` [vectorDestination]
    Output vector file destination.

