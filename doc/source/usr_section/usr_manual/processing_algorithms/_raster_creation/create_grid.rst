.. _Create grid:

***********
Create grid
***********

Create an empty raster that can be used as a grid.

**Parameters**


:guilabel:`CRS` [crs]
    Target coordinate reference system.


:guilabel:`Extent` [extent]
    Target extent.


:guilabel:`Size units` [enum]
    Units to use when defining target raster size/resolution.


:guilabel:`Width / horizontal resolution` [number]
    Target width if size units is "Pixels", or horizontal resolution if size units is "Georeferenced units".

    Default: *0*


:guilabel:`Height / vertical resolution` [number]
    Target height if size units is "Pixels", or vertical resolution if size units is "Georeferenced units".

    Default: *0*

**Outputs**


:guilabel:`Output grid` [rasterDestination]
    Output raster file destination.

