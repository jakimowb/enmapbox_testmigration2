.. _Spectral Convolution Box1DKernel:

********************************
Spectral Convolution Box1DKernel
********************************

Applies Box1DKernel.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Box1DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Box1DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Box1DKernel
        
        kernel = Box1DKernel(width=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

