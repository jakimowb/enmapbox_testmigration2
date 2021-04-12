.. _Create Grid:

***********
Create Grid
***********

Create an empty (VRT) raster that can be used as a pixel grid.

**Parameters**


:guilabel:`CRS` [crs]
    Target coordinate reference system.


:guilabel:`Extent` [extent]
    Target extent.


:guilabel:`Size units` [enum]
    Units to use when defining target raster size/resolution.


:guilabel:`Width / horizontal resolution` [number]
    Target width if size units is 0, or horizontal resolution if size units is 1.

    Default: *0*


:guilabel:`Height / vertical resolution` [number]
    Target height if size units is 0, or vertical resolution if size units is 1.

    Default: *0*

**Outputs**


:guilabel:`Output VRT raster` [rasterDestination]
    Output raster destination.

