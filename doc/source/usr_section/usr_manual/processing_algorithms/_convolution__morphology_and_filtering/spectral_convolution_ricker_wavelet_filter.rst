.. _Spectral convolution Ricker Wavelet filter:

******************************************
Spectral convolution Ricker Wavelet filter
******************************************

1D Ricker Wavelet filter kernel (sometimes known as a Mexican Hat kernel).
The Ricker Wavelet, or inverted Gaussian-Laplace filter, is a bandpass filter. It smooths the data and removes slowly varying or constant structures (e.g. background). It is useful for peak or multi-scale detection.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.RickerWavelet1DKernel.html">RickerWavelet1DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import RickerWavelet1DKernel
        kernel = RickerWavelet1DKernel(width=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

