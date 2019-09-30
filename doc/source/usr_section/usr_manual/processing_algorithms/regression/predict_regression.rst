.. _Predict Regression:

******************
Predict Regression
******************

Applies a regressor to an raster.

Used in the Cookbook Recipes: 
`Regression <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/regression.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Select raster file which should be regressed.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Regressor` [file]
    Select path to a regressor file (.pkl).

**Outputs**


:guilabel:`Output Regression` [rasterDestination]
    Specify output path for regression raster.

