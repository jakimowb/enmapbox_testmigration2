.. _Random points in (categorized) raster:

*************************************
Random points in (categorized) raster
*************************************

This algorithm creates a new point layer with a given number of random points, all of them within the categories of the given raster.

**Parameters**


:guilabel:`Categories` [raster]
    Source raster layer styled with a paletted/unique values renderer.


:guilabel:`Number of points per category` [string]
    Number of points to be drawn from each category. Set a single value N to draw N points for each category. Set a list of values N1, N2, ... Ni, ... to draw Ni points for category i.


:guilabel:`Minimum distance between points (in meters)` [number]
    A minimum (Euclidean) distance between points can be specified.

    Default: *0*


:guilabel:`Minimum distance between points inside category (in meters)` [number]
    A minimum (Euclidean) distance between points in a category can be specified.

    Default: *0*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output points` [vectorDestination]
    Output vector destination.

