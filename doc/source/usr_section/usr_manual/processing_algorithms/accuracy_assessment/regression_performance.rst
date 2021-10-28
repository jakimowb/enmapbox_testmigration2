.. _Regression Performance:

**********************
Regression Performance
**********************

Assesses the performance of a regression.

**Parameters**


:guilabel:`Prediction` [raster]
    Specify regression raster to be evaluated.


:guilabel:`Reference` [raster]
    Specify reference regression raster (i.e. ground truth).


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Invert Mask` [boolean]
    Whether or not to invert the selected mask.

    Default: *0*

**Outputs**


:guilabel:`HTML Report` [fileDestination]
    Specify output path for HTML report file (.html).

