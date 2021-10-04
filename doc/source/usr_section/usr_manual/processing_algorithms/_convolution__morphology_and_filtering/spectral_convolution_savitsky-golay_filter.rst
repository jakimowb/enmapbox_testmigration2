.. _Spectral convolution Savitsky-Golay filter:

******************************************
Spectral convolution Savitsky-Golay filter
******************************************

1D Savitsky-Golay filter.
See <a href="https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter">wikipedia</a> for details.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://scipy.github.io/devdocs/generated/scipy.signal.savgol_coeffs.html#scipy.signal.savgol_coeffs">scipy.signal.savgol_coeffs</a> for information on different parameters.

    Default::

        from astropy.convolution import Kernel1D
        from scipy.signal import savgol_coeffs
        kernel = Kernel1D(array=savgol_coeffs(window_length=11, polyorder=3, deriv=0))

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

