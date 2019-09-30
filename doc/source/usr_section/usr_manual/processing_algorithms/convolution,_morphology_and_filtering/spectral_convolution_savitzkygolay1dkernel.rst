.. _Spectral Convolution SavitzkyGolay1DKernel:

******************************************
Spectral Convolution SavitzkyGolay1DKernel
******************************************

Applies `Savitzki Golay Filter <https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter>`_.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.signal.savgol_coeffs <http://scipy.github.io/devdocs/generated/scipy.signal.savgol_coeffs.html#scipy.signal.savgol_coeffs>`_ for information on different parameters.

    Default::

        from astropy.convolution import Kernel1D
        from scipy.signal import savgol_coeffs
        
        kernel = Kernel1D(array=savgol_coeffs(window_length=11, polyorder=3, deriv=0))
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

