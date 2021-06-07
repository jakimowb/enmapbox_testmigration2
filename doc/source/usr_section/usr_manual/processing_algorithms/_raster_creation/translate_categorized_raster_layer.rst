.. _Translate categorized raster layer:

**********************************
Translate categorized raster layer
**********************************

Translates categorized raster layer into target grid.
Resampling is done via a two-step majority voting approach. First, the categorized raster layer is resampled at x10 finer resolution, and subsequently aggregated back to the target resolution using majority voting. This approach leads to pixel-wise class decisions that are accurate to the percent.

**Parameters**


:guilabel:`Categorized raster layer` [raster]
    A categorized raster layer to be resampled.


:guilabel:`Grid` [raster]
    The target grid.


:guilabel:`Majority voting` [boolean]
    Whether to use majority voting. Turn off to use simple nearest neighbour resampling, which is much faster, but may result in highly inaccurate decisions.

    Default: *True*

**Outputs**


:guilabel:`Output categorized raster layer` [rasterDestination]
    Output raster file destination.

