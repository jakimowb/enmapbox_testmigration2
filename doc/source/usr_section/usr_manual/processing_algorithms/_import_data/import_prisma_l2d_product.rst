.. _Import PRISMA L2D product:

*************************
Import PRISMA L2D product
*************************

Prepare a `spectral raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-spectral-raster-layer>`_ from the given product. `Wavelength <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-wavelength>`_ and FWHM information is set and data is scaled into the 0 to 10000 range.

**Parameters**


:guilabel:`File` [file]
    The HE5 product file.
    Instead of executing this algorithm, you may drag&drop the HE5 file directly from your system file browser onto the EnMAP-Box map view area.

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

**Command-line usage**

``>qgis_process help enmapbox:ImportPrismaL2DProduct``::

    ----------------
    Arguments
    ----------------
    
    file: File
    	Argument type:	file
    	Acceptable values:
    		- Path to a file
    outputPrismaL2DRaster: Output raster layer
    	Argument type:	rasterDestination
    	Acceptable values:
    		- Path for new raster layer
    
    ----------------
    Outputs
    ----------------
    
    outputPrismaL2DRaster: <outputRaster>
    	Output raster layer
    
    