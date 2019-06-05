.. _Classification from Fraction:

****************************
Classification from Fraction
****************************

Creates classification from class fraction. Winner class is equal to the class with maximum class fraction.

**Parameters**


:guilabel:`ClassFraction` [raster]
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

