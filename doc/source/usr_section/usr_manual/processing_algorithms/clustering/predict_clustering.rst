.. _Predict Clustering:

******************
Predict Clustering
******************

Applies a clusterer to a raster.

Used in the Cookbook Recipes: 
`Clustering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/clustering.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Select raster file which should be clustered.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Clusterer` [file]
    Select path to a clusterer file (.pkl).

**Outputs**


:guilabel:`Clustering` [rasterDestination]
    Specify output path for classification raster.

