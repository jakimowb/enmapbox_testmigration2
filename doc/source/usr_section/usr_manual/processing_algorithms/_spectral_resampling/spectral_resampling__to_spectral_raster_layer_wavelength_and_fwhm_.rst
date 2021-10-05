.. _Spectral resampling (to spectral raster layer wavelength and FWHM):

******************************************************************
Spectral resampling (to spectral raster layer wavelength and FWHM)
******************************************************************

Spectrally resample a spectral raster layer by applying spectral response function convolution, with spectral response function derived from wavelength and FWHM information stored inside a spectral raster layer.

**Parameters**


:guilabel:`Spectral raster layer` [raster]
    A spectral raster layer to be resampled.


:guilabel:`Spectral raster layer with wavelength and FWHM` [raster]
    A spectral raster layer with center wavelength and FWHM information defining the destination sensor.


:guilabel:`Save spectral response function` [boolean]
    Whether to save the spectral response function library as *.srf.gpkg sidecar file.

    Default: *False*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

