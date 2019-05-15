.. _Spectral Convolution MexicanHat1DKernel:

***************************************
Spectral Convolution MexicanHat1DKernel
***************************************

Applies MexicanHat1DKernel.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.MexicanHat1DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.MexicanHat1DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import MexicanHat1DKernel
        
        kernel = MexicanHat1DKernel(width=10)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

