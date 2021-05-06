.. _Rasterize vector layer:

**********************
Rasterize vector layer
**********************

Converts vector geometries (points, lines and polygons) into a raster grid.

**Parameters**


:guilabel:`Vector layer` [vector]
    A vector layer to be rasterized.


:guilabel:`Grid` [raster]
    The target grid.


:guilabel:`Init value` [number]
    Pre-initialization value for the output raster layer.

    Default: *0*


:guilabel:`Burn value` [number]
    Fixed value to burn into each pixel, which is touched (point, line) or where the center is covered (polygon) by a geometry.

    Default: *1*


:guilabel:`Burn attribute` [field]
    Numeric vector field to use as burn values.


:guilabel:`Burn feature ID` [boolean]
    Whether to use the feature ID as burn values. Initial value is set to -1. Data type is set to Int32.

    Default: *False*


:guilabel:`Aggregation algorithm` [enum]
    If selected, burn at a x10 finer resolution and aggregate values back to target resolution. For example, use Mode aggregation for categorical attributes to burn the category with highest pixel coverage (i.e. majority voting). For continuous attributes use Average to calculate a weighted average.

    Default: *0*


:guilabel:`Add value` [boolean]
    Whether to add up existing values instead of replacing them.

    Default: *False*


:guilabel:`All touched` [boolean]
    Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.

    Default: *False*


:guilabel:`Data type` [enum]
    Output data type.

    Default: *5*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Output raster file destination.

