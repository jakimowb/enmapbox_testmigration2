.. _Vector to classification:

************************
Vector to classification
************************

Converts a categorized vector into a classification by evaluating renderer categories. Output class ids run from 1 to number of categories, in the order of the given categories. Class names and colors are given by the category legend and symbol color. 
Rasterization is done by class majority voting at x10 oversampled resolution, using 100 classified subpixel to be accurate to the percent.

**Parameters**


:guilabel:`Vector` [vector]
    Source vector layer styled with a categorized symbol renderer.


:guilabel:`Grid` [raster]
    Source raster layer defining the destination extent, resolution and coordinate reference system.


:guilabel:`Minimum pixel coverage` [number]
    Exclude all pixel where (polygon) coverage is smaller than given threshold.

    Default: *0*


:guilabel:`Majority voting` [boolean]
    Whether to use majority voting. Turn off to use simple vector burning, which is much faster.

    Default: *True*

**Outputs**


:guilabel:`Output classification` [rasterDestination]
    Output raster destination.

