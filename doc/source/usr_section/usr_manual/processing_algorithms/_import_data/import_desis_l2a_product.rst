.. _Import DESIS L2A product:

************************
Import DESIS L2A product
************************

Prepare a spectral raster layer from the given product. Wavelength and FWHM information is set and data is scaled into the 0 to 10000 range.
Note that the DESIS L2D spectral data file is band interleaved by pixel and compressed, which is very disadvantageous for visualization in QGIS / EnMAP-Box. For faster exploration concider saving the resulting VRT raster layer as GTiff format via the "Translate raster layer" algorithm.

**Parameters**


:guilabel:`Metadata file` [file]
    The metadata XML file associated with the product.
    Instead of executing this algorithm, you may drag&drop the metadata XML file directly from your system file browser onto the EnMAP-Box map view area.

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

