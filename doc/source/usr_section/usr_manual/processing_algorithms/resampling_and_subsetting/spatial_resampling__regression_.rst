.. _Spatial Resampling (Regression):

*******************************
Spatial Resampling (Regression)
*******************************

Resamples a Regression into a target grid.

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`Regression` [raster]
    Specify input raster.


:guilabel:`Minimal overall coverage` [number]
    Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

    Default: *0.5*

**Outputs**


:guilabel:`Output Regression` [rasterDestination]
    Specify output path for regression raster.

