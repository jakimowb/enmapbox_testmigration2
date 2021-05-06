.. _Predict classification layer:

****************************
Predict classification layer
****************************

Uses a fitted classifier to predict a classification layer from a raster layer with features. 
Used in the Cookbook Recipes: <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html">Classification</a>, <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html">Graphical Modeler</a> for information on different parameters.

**Parameters**


:guilabel:`Raster layer with features` [raster]
    A raster layer with bands used as features. Classifier features and raster bands are matched by name.


:guilabel:`Mask layer` [layer]
    A mask layer.


:guilabel:`Classifier` [file]
    A fitted classifier.

**Outputs**


:guilabel:`Output classification layer` [rasterDestination]
    Output raster file destination.

