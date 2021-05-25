.. _Classification dataset (from categorized raster layer and feature raster):

*************************************************************************
Classification dataset (from categorized raster layer and feature raster)
*************************************************************************

Sample data for pixels that match the given categories and store the result as a pickle file. 
If the layer is not categorized, or the band with class values is selected manually, categories are derived from sampled data itself. To be more precise: i) category values are derived from unique raster band values (after excluding no data or zero data pixel), ii) category names are set equal to the category values, and iii) category colors are picked randomly.

**Parameters**


:guilabel:`Categorized raster layer` [raster]
    Categorized raster layer specifying sample locations and target data y. If required, the layer is reprojected and resampled internally to match the feature raster grid.
    


:guilabel:`Raster layer with features` [raster]
    Raster layer used for sampling feature data X.


:guilabel:`Band with class values` [band]
    Band with class values. If not selected, the band defined by the renderer is used. If that is also not specified, the first band is used.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.

