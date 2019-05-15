.. _Build Mask from Raster:

**********************
Build Mask from Raster
**********************

Builds a mask from a raster based on user defined values and value ranges.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Foreground values` [string]
    List of values and ranges that are mapped to True, e.g. [1, 2, 5, range(5, 10)].

    Default: *[]*


:guilabel:`Background values` [string]
    List of values and ranges that are mapped to False, e.g. [-9999, range(-10, 0)].

    Default: *[]*

**Outputs**


:guilabel:`Output Mask` [rasterDestination]
    Specify output path for mask raster.

