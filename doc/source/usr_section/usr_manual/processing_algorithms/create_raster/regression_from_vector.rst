.. _Regression from Vector:

**********************
Regression from Vector
**********************

Creates a regression from a vector field with target values.

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`Vector` [vector]
    Specify input vector.


:guilabel:`Regression value attribute` [field]
    Vector field specifying the regression values.


:guilabel:`No Data Value` [string]
    Specify output no data value.


:guilabel:`Minimal overall coverage` [number]
    Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.


:guilabel:`Oversampling factor` [number]
    Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.
    
    Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

    Default: *1*

**Outputs**


:guilabel:`Output Regression` [rasterDestination]
    Specify output path for regression raster.

