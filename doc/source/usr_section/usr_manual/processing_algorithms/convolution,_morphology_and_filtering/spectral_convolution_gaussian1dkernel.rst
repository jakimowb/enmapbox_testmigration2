.. _Spectral Convolution Gaussian1DKernel:

*************************************
Spectral Convolution Gaussian1DKernel
*************************************

Applies Gaussian1DKernel.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Gaussian1DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Gaussian1DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Gaussian1DKernel
        
        kernel = Gaussian1DKernel(stddev=1)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

