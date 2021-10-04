.. _Raster math:

***********
Raster math
***********

Perform mathematical calculations on raster layer and vector layer data. Use any <a href="https://numpy.org/doc/stable/reference/">NumPy</a>-based arithmetic, or even arbitrary Python code.
See the <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_manual/applications.html#rastermath">RasterMath tutorial</a> for detailed usage instructions.

**Parameters**


:guilabel:`Code` [string]
    The mathematical calculation to be performed on the selected input arrays.
    Select inputs in the available data sources section or use the raster layer R1, ..., R10 and vector layer V1, ..., V10.
    In the code snippets section you can find some prepdefined code snippets ready to use.
    See the <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_manual/applications.html#rastermath">RasterMath tutorial</a> for detailed usage instructions.


:guilabel:`Grid` [raster]
    The destination grid. If not specified, the grid of the first raster layer is used.


:guilabel:`Block overlap` [number]
    The number of columns and rows to read from the neighbouring blocks. Needs to be specified only when performing spatial operations, to avoid artifacts at block borders.


:guilabel:`Monolithic processing` [boolean]
    Whether to read all data for the full extent at once, instead of block-wise processing. This may be useful for some spatially unbound operations, like segmentation or region growing, when calculating global statistics, or if RAM is not an issue at all.

    Default: *False*


:guilabel:`Raster layers ` [multilayer]
    Additional list of raster layers mapped to a list variable RS.


:guilabel:`Raster layer mapped to R1` [raster]

:guilabel:`Raster layer mapped to R2` [raster]

:guilabel:`Raster layer mapped to R3` [raster]

:guilabel:`Raster layer mapped to R4` [raster]

:guilabel:`Raster layer mapped to R5` [raster]

:guilabel:`Raster layer mapped to R6` [raster]

:guilabel:`Raster layer mapped to R7` [raster]

:guilabel:`Raster layer mapped to R8` [raster]

:guilabel:`Raster layer mapped to R9` [raster]

:guilabel:`Raster layer mapped to R10` [raster]

:guilabel:`Vector layer mapped to V1` [vector]

:guilabel:`Vector layer mapped to V2` [vector]

:guilabel:`Vector layer mapped to V3` [vector]

:guilabel:`Vector layer mapped to V4` [vector]

:guilabel:`Vector layer mapped to V5` [vector]

:guilabel:`Vector layer mapped to V6` [vector]

:guilabel:`Vector layer mapped to V7` [vector]

:guilabel:`Vector layer mapped to V8` [vector]

:guilabel:`Vector layer mapped to V9` [vector]

:guilabel:`Vector layer mapped to V10` [vector]
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination for writing the default output variable. Additional outputs are written into the same directory. See the <a href="https://enmap-box.readthedocs.io/en/latest/usr_section/usr_manual/applications.html#rastermath">RasterMath tutorial</a> for detailed usage instructions.

