.. _Append ENVI header to GeoTiff raster layer:

******************************************
Append ENVI header to GeoTiff raster layer
******************************************

Places an ENVI *.hdr header file next to the GeoTiff `raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-raster-layer>`_, to enable full compatibility to the ENVI software. The header file stores `wavelength <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-wavelength>`_, FWHM and `bad band multiplier <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-bad-band-multiplier>`_ information.

**Parameters**


:guilabel:`GeoTiff raster layer` [raster]
    Source GeoTiff `raster layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-raster-layer>`_.

**Command-line usage**

``>qgis_process help enmapbox:AppendEnviHeaderToGeotiffRasterLayer``::

    ----------------
    Arguments
    ----------------
    
    raster: GeoTiff raster layer
    	Argument type:	raster
    	Acceptable values:
    		- Path to a raster layer
    
    ----------------
    Outputs
    ----------------
    
    
    