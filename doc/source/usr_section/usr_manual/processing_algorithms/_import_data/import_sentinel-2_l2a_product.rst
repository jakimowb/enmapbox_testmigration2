.. _Import Sentinel-2 L2A product:

*****************************
Import Sentinel-2 L2A product
*****************************

Prepare a spectral raster layer from the given product. Wavelength information is set and data is scaled into the 0 to 10000 range.

**Parameters**


:guilabel:`Metadata file` [file]
    The MTD_MSIL2A.xml metadata file associated with the product.
    Instead of executing this algorithm, you may drag&drop the metadata file directly from your system file browser onto the EnMAP-Box map view area.


:guilabel:`Band list` [enum]
    Bands to be stacked together. Defaults to all 10m and 20m bands ordered by center wavelength. Note that the destination pixel size matches the smallest/finest pixel size over all selected bands.

    Default: *[0, 1, 2, 3, 4, 5, 6, 7]*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

