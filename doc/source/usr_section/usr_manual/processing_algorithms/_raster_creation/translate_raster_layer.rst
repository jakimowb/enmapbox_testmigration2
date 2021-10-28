.. _Translate raster layer:

**********************
Translate raster layer
**********************

Convert raster data between different formats, potentially performing some operations like spatial subsetting, spatial resampling, reprojection, `band <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_ subsetting, band reordering, data scaling, `no data value <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-no-data-value>`_ specification, and data type conversion.

**Parameters**


:guilabel:`Raster layer` [raster]
    Source `raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-raster-layer>`_.


:guilabel:`Selected bands` [band]
    Bands to subset and rearrange. An empty selection defaults to all `bands <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_ in native order.


:guilabel:`Grid` [raster]
    The destination `grid <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-grid>`_.


:guilabel:`Copy metadata` [boolean]
    Whether to copy GDAL metadata from source to destination.

    Default: *False*


:guilabel:`Copy style` [boolean]
    Whether to copy style from source to destination.

    Default: *False*


:guilabel:`Write ENVI header` [boolean]
    Whether to write an ENVI header *.hdr sidecar file with spectral metadata required for proper visualization in ENVI software.

    Default: *False*


:guilabel:`Spectral raster layer for band subsetting` [raster]
    A `spectral raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-spectral-raster-layer>`_ used for specifying a `band <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_ subset by matching the `center wavelength <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-center-wavelength>`_.


:guilabel:`Selected spectral bands` [band]
    `Spectral bands <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-spectral-band>`_ used to match source raster `bands <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_.An empty selection defaults to all bands in native order.


:guilabel:`Data offset value` [number]
    A data offset value applied to each `band <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_.


:guilabel:`Data gain/scale value` [number]
    A data gain/scale value applied to each `band <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_.


:guilabel:`Spatial extent` [extent]
    Spatial extent for clipping the destination `grid <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-grid>`_, which is given by the source Raster or the selected Grid. In both cases, the extent is aligned with the actual pixel grid to avoid subpixel shifts.


:guilabel:`Column subset` [range]
    Column subset range in pixels to extract.


:guilabel:`Row subset` [range]
    Rows subset range in pixels to extract.


:guilabel:`Exclude bad bands` [boolean]
    Whether to exclude bad `bands <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_ (given by BBL metadata item inside ENVI domain). Also see The ENVI Header Format for more details: https://www.l3harrisgeospatial.com/docs/ENVIHeaderFiles.html 

    Default: *False*


:guilabel:`Resample algorithm` [enum]
    Spatial resample algorithm.

    Default: *0*


:guilabel:`Source no data value` [number]
    The value to be used instead of the original `raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-raster-layer>`_ `no data value <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-no-data-value>`_.


:guilabel:`No data value` [number]
    The value to be used instead of the default destination `no data value <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-no-data-value>`_.


:guilabel:`Unset source no data value` [boolean]
    Whether to unset (i.e. not use) the source `no data value <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-no-data-value>`_.

    Default: *False*


:guilabel:`Unset no data value` [boolean]
    Whether to unset the destination `no data value <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-no-data-value>`_.

    Default: *False*


:guilabel:`Data type` [enum]
    Output data type.


:guilabel:`Output options` [string]
    Output format and creation options.

    Default: **

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

**Command-line usage**

``>qgis_process help enmapbox:TranslateRasterLayer``::

    ----------------
    Arguments
    ----------------
    
    raster: Raster layer
    	Argument type:	raster
    	Acceptable values:
    		- Path to a raster layer
    bandList: Selected bands
    	Argument type:	band
    	Acceptable values:
    		- Integer value representing an existing raster band number
    grid: Grid
    	Argument type:	raster
    	Acceptable values:
    		- Path to a raster layer
    copyMetadata: Copy metadata
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    copyStyle: Copy style
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    writeEnviHeader: Write ENVI header
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    spectralSubset: Spectral raster layer for band subsetting
    	Argument type:	raster
    	Acceptable values:
    		- Path to a raster layer
    spectralBandList: Selected spectral bands
    	Argument type:	band
    	Acceptable values:
    		- Integer value representing an existing raster band number
    offset: Data offset value
    	Argument type:	number
    	Acceptable values:
    		- A numeric value
    scale: Data gain/scale value
    	Argument type:	number
    	Acceptable values:
    		- A numeric value
    extent: Spatial extent
    	Argument type:	extent
    	Acceptable values:
    		- A comma delimited string of x min, x max, y min, y max. E.g. '4,10,101,105'
    		- Path to a layer. The extent of the layer is used.
    sourceColumns: Column subset
    	Argument type:	range
    	Acceptable values:
    		- Two comma separated numeric values, e.g. '1,10'
    sourceRows: Row subset
    	Argument type:	range
    	Acceptable values:
    		- Two comma separated numeric values, e.g. '1,10'
    excludeBadBands: Exclude bad bands
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    resampleAlg: Resample algorithm
    	Argument type:	enum
    	Available values:
    		- 0: NearestNeighbour
    		- 1: Bilinear
    		- 2: Cubic
    		- 3: CubicSpline
    		- 4: Lanczos
    		- 5: Average
    		- 6: Mode
    		- 7: Min
    		- 8: Q1
    		- 9: Med
    		- 10: Q3
    		- 11: Max
    	Acceptable values:
    		- Number of selected option, e.g. '1'
    		- Comma separated list of options, e.g. '1,3'
    sourceNoData: Source no data value
    	Argument type:	number
    	Acceptable values:
    		- A numeric value
    noData: No data value
    	Argument type:	number
    	Acceptable values:
    		- A numeric value
    unsetSourceNoData: Unset source no data value
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    unsetNoData: Unset no data value
    	Argument type:	boolean
    	Acceptable values:
    		- 1 for true/yes
    		- 0 for false/no
    dataType: Data type
    	Argument type:	enum
    	Available values:
    		- 0: Byte
    		- 1: Int16
    		- 2: UInt16
    		- 3: UInt32
    		- 4: Int32
    		- 5: Float32
    		- 6: Float64
    	Acceptable values:
    		- Number of selected option, e.g. '1'
    		- Comma separated list of options, e.g. '1,3'
    creationProfile: Output options
    	Argument type:	string
    	Acceptable values:
    		- String value
    outputTranslatedRaster: Output raster layer
    	Argument type:	rasterDestination
    	Acceptable values:
    		- Path for new raster layer
    
    ----------------
    Outputs
    ----------------
    
    outputTranslatedRaster: <outputRaster>
    	Output raster layer
    
    