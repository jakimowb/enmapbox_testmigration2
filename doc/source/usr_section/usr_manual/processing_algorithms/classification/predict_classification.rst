Predict Classification
----------------------

Applies a classifier to a raster.

Raster
    Select raster file which should be classified.

Mask
    Specified vector or raster is interpreted as a boolean mask.

    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Classifier
    Select path to a classifier file (.pkl).

Output Classification
    Specify output path for classification raster.
