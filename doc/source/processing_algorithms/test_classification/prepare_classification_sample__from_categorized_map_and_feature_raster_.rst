.. _Prepare classification sample (from categorized map and feature raster):

***********************************************************************
Prepare classification sample (from categorized map and feature raster)
***********************************************************************

Sample all labeled pixels and store the result as a binary Pickle (*.pkl) file.

**Parameters**


:guilabel:`Categorized map layer` [layer]
    Locations with categorical labels. Source raster or vector layer styled with a paletted/unique values (raster) or categorized symbol (vector) renderer. The layer is resampled, reprojected and rasterized internally to match the raster grid, if required.
    


:guilabel:`Raster layer with features` [raster]
    Raster used for sampling feature values.

**Outputs**


:guilabel:`Output classification sample` [fileDestination]
    Output sample destination *.pkl file.

