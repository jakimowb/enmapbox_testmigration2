.. _Raster math:

***********
Raster math
***********

Create a raster layer by evaluating an expression with numpy syntax. Use any basic arithmetic and logical operators supported by numpy arrays. 

**Parameters**


:guilabel:`Raster layers` [multilayer]
    List of raster layers that are mapped to variables A, B, C, ... .
    Individual bands are mapped to variables A@1, A@2, ..., B@1, B@2, ... .


:guilabel:`Expression` [string]
    The expression to be evaluated. Must result in a (multiband) 3d numpy array, a (singl-band) 2d numpy array or a list of 2d numpy arrays.


:guilabel:`Grid` [raster]
    The target grid. If not specified, the grid of the first raster layer is used.

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Output raster file destination.

