.. _Predict Classification:

**********************
Predict Classification
**********************

Applies a classifier to a raster.

Used in the Cookbook Recipes
    - `Classification <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html#predict-classification>`_ (section: predict-classification)

**Parameters**


:guilabel:`Raster` [raster]
    Select raster file which should be classified.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Classifier` [file]
    Select path to a classifier file (.pkl).

**Outputs**


:guilabel:`Output Classification` [rasterDestination]
    Specify output path for classification raster.

