.. _Raster math:

***********
Raster math
***********

Create a raster layer by evaluating an expression with numpy syntax. Use any basic arithmetic and logical operators supported by numpy arrays. The numpy modul is imported as np.

**Parameters**


:guilabel:`Raster layers` [multilayer]
    List of raster layers that are mapped to variables A, B, C, ... .
    Individual bands are mapped to variables A@1, A@2, ..., B@1, B@2, ... .


:guilabel:`Expression` [string]
    The expression to be evaluated. Must result in a (multiband) 3d numpy array, a (single-band) 2d numpy array or a list of 2d numpy arrays.
    Example 1 - add up two bands: <pre>A@1 + B@1</pre>
    Example 2 - add up two rasters (with same number of bands) band-wise: <pre>A + B</pre>
    Example 3 - use a numpy function to calculate the exponential of all values in a raster: <pre>np.exp(A)</pre>
    Example 4 - build a band stack with all bands from three raster layers:<pre>list(A) + list(B) + list(C)</pre>
    More complex expressions can be splitted into multiple lines for defining temporary variables or import modules. Here the last line is evaluated as the final result.
    Example 5 - use a multiple line code block to calculate a vegetation index:<pre>nir = np.float32(A@4)<br>red = np.float32(A@3)<br>ndvi = (nir - red) / (nir + red)<br>ndvi</pre>


:guilabel:`Grid` [raster]
    The target grid. If not specified, the grid of the first raster layer is used.

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Output raster file destination.

