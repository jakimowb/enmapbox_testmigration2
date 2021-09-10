.. _Create default paletted raster renderer:

***************************************
Create default paletted raster renderer
***************************************

Create a paletted raster renderer from given categories and set it as the default style of the given raster layer.
This will create/overwrite the QML sidecar file of the given raster layer.

**Parameters**


:guilabel:`Raster layer` [raster]
    The raster layer for which to create the QML sidecar file.


:guilabel:`Band` [band]
    The renderer band.


:guilabel:`Categories` [string]
    Comma separated list of tuples with category value, name and color information. E.g.
    (1, 'Urban', '#FF0000'), (2, 'Forest', '#00FF00'), (3, 'Water', '#0000FF')

