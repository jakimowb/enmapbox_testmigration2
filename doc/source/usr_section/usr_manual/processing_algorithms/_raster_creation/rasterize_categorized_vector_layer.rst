.. _Rasterize categorized vector layer:

**********************************
Rasterize categorized vector layer
**********************************

Rasterize a categorized vector layer into a categorized raster layer. Output category names and colors are given by the source layer.
Resampling is done via a two-step majority voting approach. First, the categorized raster layer is resampled at x10 finer resolution, and subsequently aggregated back to the target resolution using majority voting. This approach leads to pixel-wise class decisions that are accurate to the percent.

**Parameters**


:guilabel:`Categorized vector layer` [vector]
    A categorized vector layer to be rasterized.


:guilabel:`Grid` [raster]
    The target grid.


:guilabel:`Minimum pixel coverage` [number]
    Exclude all pixel where (polygon) coverage is smaller than given threshold.

    Default: *0*


:guilabel:`Majority voting` [boolean]
    Whether to use majority voting. Turn off to use simple nearest neighbour resampling, which is much faster, but may result in highly inaccurate decisions.

    Default: *True*

**Outputs**


:guilabel:`Output categorized raster layer` [rasterDestination]
    Output raster file destination.

