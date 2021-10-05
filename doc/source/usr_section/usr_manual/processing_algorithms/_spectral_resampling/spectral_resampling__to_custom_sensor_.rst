.. _Spectral resampling (to custom sensor):

**************************************
Spectral resampling (to custom sensor)
**************************************

Spectrally resample a spectral raster layer by applying spectral response function convolution.

**Parameters**


:guilabel:`Spectral raster layer` [raster]
    A spectral raster layer to be resampled.


:guilabel:`Spectral response function` [string]
    Python code specifying the spectral response function.

    Default::

        from collections import OrderedDict
        
        # Place response function definition here. Should look something like this:
        responses = OrderedDict()
        
        # Option 1: Use band name as dict-key,
        #           together with fully defined list of (<wavelength>, <response>) tuples as dict-value.
        #           Define <response> as values between 0 and 1 for each whole nanometer <wavelength>.
        responses['Blue'] = [(443, 0.001), (444, 0.002), ..., (509, 1.0), ..., (518, 0.002), (519, 0.001)]
        responses['Green'] = [(519, 0.001), (520, 0.002), ..., (550, 1.0), ..., (597, 0.003), (598, 0.001)]
        ...
        # Option 2: Use band center wavelength as dict-key,
        #           together with band full width at half maximum (FWHM) as dict-value.
        #           The response function is modelled as an RBF around the center wavelength with a width of FWHM / 2.355.
        #           See https://en.wikipedia.org/wiki/Full_width_at_half_maximum for details.
        responses[460] = 5.8
        ...
        responses[2409] = 9.1
        

:guilabel:`Save spectral response function` [boolean]
    Whether to save the spectral response function library as *.srf.gpkg sidecar file.

    Default: *False*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.
