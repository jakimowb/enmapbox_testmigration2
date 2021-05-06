.. _Translate raster layer:

**********************
Translate raster layer
**********************

Convert raster data between different formats, potentially performing some operations like spatial subsetting, spatial resampling, reprojection, band subsettings, band reordering and data type conversion.

**Parameters**


:guilabel:`Raster layer` [raster]
    Source raster layer.


:guilabel:`Selected bands` [band]
    Bands to subset and rearrange. An empty selection defaults to all bands in native order.


:guilabel:`Grid` [raster]
    The target grid.


:guilabel:`Copy metadata` [boolean]
    Whether to copy metadata from source to destination. Special care is taken of ENVI list items containing band information. The following list items will be properly subsetted according to the selected bands: band names, bbl, data_gain_values, data_offset_values, data_reflectance_gain_values, data_reflectance_offset_values, fwhm, wavelength.

    Default: *False*


:guilabel:`Copy style` [boolean]
    Whether to copy style from source to destination.

    Default: *False*


:guilabel:`Spatial extent` [extent]
    Spatial extent for clipping the destination grid, which is given by the source Raster or the selected Grid. In both cases, the extent is aligned with the actual pixel grid to avoid subpixel shifts.


:guilabel:`Column subset` [range]
    Column subset range in pixels to extract.


:guilabel:`Row subset` [range]
    Rows subset range in pixels to extract.


:guilabel:`Exclude bad bands` [boolean]
    Whether to exclude bad bands (given by BBL metadata item inside ENVI domain). Also see The ENVI Header Format for more details: https://www.l3harrisgeospatial.com/docs/ENVIHeaderFiles.html 

    Default: *False*


:guilabel:`Resample algorithm` [enum]
    Spatial resample algorithm.

    Default: *0*


:guilabel:`Data type` [enum]
    Output data type.


:guilabel:`Output options` [enum]
    Output format and creation options.

    Default: *0*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Output raster file destination.

