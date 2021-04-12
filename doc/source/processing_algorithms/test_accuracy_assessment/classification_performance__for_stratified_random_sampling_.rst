.. _Classification performance (for stratified random sampling):

***********************************************************
Classification performance (for stratified random sampling)
***********************************************************

Estimates map accuracy and area proportions for stratified random sampling as described in Stehman (2014): https://doi.org/10.1080/01431161.2014.930207. 
Reference and map classes are matched by name.

**Parameters**


:guilabel:`Classification` [raster]
    Source raster layer styled with a paletted/unique values renderer.


:guilabel:`Reference sample` [layer]
    Stratified random reference sample. Source raster or vector layer styled with a paletted/unique values (raster) or categorized symbol (vector) renderer. 


:guilabel:`Sample strata` [layer]
    Sample strata. Source raster layer styled with a paletted/unique values renderer..


:guilabel:`Use map strata as sample strata` [boolean]
    Whether to use map classes as sample strata, if sample strata are not selected.

    Default: *True*

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report destination.

