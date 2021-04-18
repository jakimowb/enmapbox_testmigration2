.. _Translate classification:

************************
Translate classification
************************

Translates classification into target grid.
Resampling is done by class majority voting at x10 oversampled resolution, using 100 classified subpixel to be accurate to the percent.

**Parameters**


:guilabel:`Classification` [raster]
    Source raster layer styled with a paletted/unique values renderer.


:guilabel:`Grid` [raster]
    Source raster layer defining the destination extent, resolution and coordinate reference system.


:guilabel:`Majority voting` [boolean]
    Whether to use majority voting. Turn off to use simple nearest neighbour resampling, which is much faster, but may result in highly inaccurate decisions.

    Default: *True*

**Outputs**


:guilabel:`Output raster` [rasterDestination]
    Output raster destination.

