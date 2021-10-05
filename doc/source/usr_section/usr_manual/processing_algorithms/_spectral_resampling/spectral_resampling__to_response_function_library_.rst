.. _Spectral resampling (to response function library):

**************************************************
Spectral resampling (to response function library)
**************************************************

Spectrally resample a spectral raster layer by applying spectral response function convolution, with spectral response function stored inside a spectral library. Each spectral profile defines a destination spectral band.

**Parameters**


:guilabel:`Spectral raster layer` [raster]
    A spectral raster layer to be resampled.


:guilabel:`Spectral response function library` [vector]
    A spectral response function library defining the destination sensor.


:guilabel:`Field with spectral profiles used as features` [field]
    Binary field with spectral profiles used as spectral response functions. If not selected, the default field is used. If that is also not specified, an error is raised.

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

