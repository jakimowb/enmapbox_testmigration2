.. _Geolocate raster layer:

**********************
Geolocate raster layer
**********************

Geolocate a raster layer using geolocation arrays. See <a href="https://gdal.org/development/rfc/rfc4_geolocate.html">Geolocation Arrays</a> in the GDAL documentation for details on the concept and parameters.

**Parameters**


:guilabel:`Raster layer` [raster]
    A raster layer to be geolocated.


:guilabel:`X locations raster layer` [raster]
    A raster layer containing the x geolocation array.


:guilabel:`Y locations raster layer` [raster]
    A raster layer containing the y geolocation array.


:guilabel:`Grid` [raster]
    The destination grid. If skipped, the grid CRS is set to the CRS of the geolocation arrays, extent and resolution is controlled by gdal.Warp defaults.


:guilabel:`Locations CRS` [crs]
    The coordinate reference system of the geolocation arrays.

    Default: *<QgsCoordinateReferenceSystem: EPSG:4326>*


:guilabel:`No data value` [number]
    Value used to fill no data regions introduced by warping.


:guilabel:`X locations band` [band]
    The x coordinates band.


:guilabel:`Y locations band` [band]
    The y coordinates band.


:guilabel:`Pixel offset` [number]
    Pixel offset into geo-located data of left geolocation pixel.

    Default: *0*


:guilabel:`Line offset` [number]
    Line offset into geo-located data of top geolocation pixel.

    Default: *0*


:guilabel:`Pixel step` [number]
    Each geolocation pixel represents this many geolocated pixels.

    Default: *1*


:guilabel:`Line step` [number]
    Each geolocation pixel represents this many geolocated lines.

    Default: *1*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

