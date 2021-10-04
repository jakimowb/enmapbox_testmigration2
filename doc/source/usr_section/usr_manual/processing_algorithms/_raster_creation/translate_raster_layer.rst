.. _Translate raster layer:

**********************
Translate raster layer
**********************

Convert raster data between different formats, potentially performing some operations like spatial subsetting, spatial resampling, reprojection, band subsetting, band reordering, data scaling, no data value specification, and data type conversion.

**Parameters**


:guilabel:`Raster layer` [raster]
    Source raster layer.


:guilabel:`Selected bands` [band]
    Bands to subset and rearrange. An empty selection defaults to all bands in native order.


:guilabel:`Grid` [raster]
    The destination grid.


:guilabel:`Copy metadata` [boolean]
    Whether to copy metadata from source to destination. Special care is taken of ENVI list items containing band information. The following list items will be properly subsetted according to the selected bands: band names, bbl, data_gain_values, data_offset_values, data_reflectance_gain_values, data_reflectance_offset_values, fwhm, wavelength.

    Default: *False*


:guilabel:`Copy style` [boolean]
    Whether to copy style from source to destination.

    Default: *False*


:guilabel:`Write ENVI header` [boolean]
    Whether to write an ENVI header *.hdr sidecar file with spectral metadata required for proper visualization in ENVI software.

    Default: *False*


:guilabel:`Spectral raster layer for band subsetting` [raster]
    A spectral raster layer used for specifying a band subset by matching the center wavelength.


:guilabel:`Selected spectral bands` [band]
    Spectral bands used to match source raster bands.An empty selection defaults to all bands in native order.


:guilabel:`Data offset value` [number]
    A data offset value applied to each band.


:guilabel:`Data gain/scale value` [number]
    A data gain/scale value applied to each band.


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


:guilabel:`Source no data value` [number]
    The value to be used instead of the original raster layer no data value.


:guilabel:`No data value` [number]
    The value to be used instead of the default destination no data value.


:guilabel:`Unset source no data value` [boolean]
    Whether to unset (i.e. not use) the source no data value.

    Default: *False*


:guilabel:`Unset no data value` [boolean]
    Whether to unset the destination no data value.

    Default: *False*


:guilabel:`Data type` [enum]
    Output data type.


:guilabel:`Output options` [string]
    Output format and creation options.

    Default: **

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

