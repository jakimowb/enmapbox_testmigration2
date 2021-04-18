.. _Spatial Resampling (Fraction):

*****************************
Spatial Resampling (Fraction)
*****************************

Resamples a Fraction into a target grid.

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`ClassFraction` [raster]
    Specify input raster.


:guilabel:`Minimal overall coverage` [number]
    Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

    Default: *0.5*

**Outputs**


:guilabel:`Output Fraction` [rasterDestination]
    Specify output path for fraction raster.

