.. _Classification layer accuracy and area report (for simple random sampling):

**************************************************************************
Classification layer accuracy and area report (for simple random sampling)
**************************************************************************

Estimates map accuracy and area proportions for (simple) random sampling. We use the formulars for the stratified random sampling described in Stehman (2014): https://doi.org/10.1080/01431161.2014.930207. Note that (simple) random sampling is a special case of stratified random sampling, with exactly one stratum. 
Observed and predicted categories are matched by name.

**Parameters**


:guilabel:`Predicted classification layer` [raster]
    A classification layer that is to be assessed.


:guilabel:`Observed categorized layer` [layer]
    A categorized layer representing a (ground truth) observation sample, that was aquired using a (simple) random sampling approach.

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report file destination.

