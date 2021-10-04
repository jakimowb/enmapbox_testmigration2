.. _Predict classification layer:

****************************
Predict classification layer
****************************

Uses a fitted classifier to predict a classification layer from a raster layer with features. 
Used in the Cookbook Recipes: <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html">Classification</a>, <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html">Graphical Modeler</a> for information on different parameters.

**Parameters**


:guilabel:`Raster layer with features` [raster]
    A raster layer with bands used as features. Classifier features and raster bands are matched by name to allow for classifiers trained on a subset of the raster bands. If raster bands and classifier features are not matching by name, but overall number of bands and features do match, raster bands are used in original order.


:guilabel:`Mask layer` [layer]
    A mask layer.


:guilabel:`Classifier` [file]
    A fitted classifier.

**Outputs**


:guilabel:`Output classification layer` [rasterDestination]
    Raster file destination.

