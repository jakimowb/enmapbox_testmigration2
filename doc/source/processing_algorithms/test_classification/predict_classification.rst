.. _Predict classification:

**********************
Predict classification
**********************

Applies a classifier to a raster to predict class labels. 
Used in the Cookbook Recipes: <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html">Classification</a>, <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html">Graphical Modeler</a> for information on different parameters.

**Parameters**


:guilabel:`Raster` [raster]
    Source raster layer.


:guilabel:`Mask` [layer]
    Source raster or vector layer interpreted as binary mask. In case of a raster, all no data (zero, if missing), inf and nan pixel evaluate to false, all other to true. In case of a vector, all pixel with pixel center not covered by a feature geometry evaluate to false,all other to true. Note that only the first raster band used by the renderer is considered.


:guilabel:`Classifier` [file]
    Source classifier file (*.pkl).

**Outputs**


:guilabel:`Output classification` [rasterDestination]
    Output raster destination.

