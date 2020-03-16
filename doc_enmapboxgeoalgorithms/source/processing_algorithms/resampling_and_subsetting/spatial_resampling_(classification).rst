.. _Spatial Resampling (Classification):

***********************************
Spatial Resampling (Classification)
***********************************

Resamples a Classification into a target grid.

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`Classification` [raster]
    Specify input raster.


:guilabel:`Minimal overall coverage` [number]
    Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

    Default: *0.5*


:guilabel:`Minimal dominant coverage` [number]
    Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

    Default: *0.5*

**Outputs**


:guilabel:`Output Classification` [rasterDestination]
    Specify output path for classification raster.

