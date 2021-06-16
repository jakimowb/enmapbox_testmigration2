.. _Classification layer accuracy and area report (for stratified random sampling):

******************************************************************************
Classification layer accuracy and area report (for stratified random sampling)
******************************************************************************

Estimates map accuracy and area proportions for stratified random sampling as described in Stehman (2014): https://doi.org/10.1080/01431161.2014.930207. 
Observed and predicted categories are matched by name.

**Parameters**


:guilabel:`Predicted classification layer` [raster]
    A classification layer that is to be assessed.


:guilabel:`Observed categorized layer` [layer]
    A categorized layer representing a (ground truth) observation sample, that was aquired using a stratified random sampling approach.


:guilabel:`Stratification layer` [layer]
    A stratification layer that was used for drawing the observation sample. If not defined, the classification layer is used as stratification layer.

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report file destination.

