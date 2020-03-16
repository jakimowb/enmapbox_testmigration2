.. _Raster from Vector:

******************
Raster from Vector
******************

Converts vector to raster (using `gdal rasterize <http://gdal.org/python/osgeo.gdal-module.html#RasterizeOptions>`_).

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`Vector` [vector]
    Specify input vector.


:guilabel:`Init Value` [number]
    Pre-initialization value for the output raster before burning. Note that this value is not marked as the nodata value in the output raster.

    Default: *0*


:guilabel:`Burn Value` [number]
    Fixed value to burn into each pixel, which is covered by a feature (point, line or polygon).

    Default: *1*


:guilabel:`Burn Attribute` [field]
    Specify numeric vector field to use as burn values.


:guilabel:`All touched` [boolean]
    Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.

    Default: *False*


:guilabel:`Filter SQL` [string]
    Create SQL based feature selection, so that only selected features will be used for burning.
    
    Example: Level_2 = 'Roof' will only burn geometries where the Level_2 attribute value is equal to 'Roof', others will be ignored. This allows you to subset the vector dataset on-the-fly.

    Default: **


:guilabel:`Data Type` [enum]
    Specify output datatype.

    Default: *7*


:guilabel:`No Data Value` [string]
    Specify output no data value.

**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

