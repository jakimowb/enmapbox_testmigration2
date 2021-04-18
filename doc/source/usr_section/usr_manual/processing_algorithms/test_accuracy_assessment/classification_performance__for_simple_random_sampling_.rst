.. _Classification performance (for simple random sampling):

*******************************************************
Classification performance (for simple random sampling)
*******************************************************

Estimates map accuracy and area proportions for (simple) random sampling. We use the formulars for the stratified random sampling described in Stehman (2014): https://doi.org/10.1080/01431161.2014.930207. Note that (simple) random sampling is a special case of stratified random sampling, with exactly one stratum. 
Reference and map classes are matched by name.

**Parameters**


:guilabel:`Classification` [raster]
    Source raster layer styled with a paletted/unique values renderer.


:guilabel:`Reference sample` [layer]
    Random reference sample. Source raster or vector layer styled with a paletted/unique values (raster) or categorized symbol (vector) renderer. 

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report destination.

