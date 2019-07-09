.. _Spatial Convolution MexicanHat2DKernel:

**************************************
Spatial Convolution MexicanHat2DKernel
**************************************

Applies MexicanHat2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.MexicanHat2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.MexicanHat2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import MexicanHat2DKernel
        
        kernel = MexicanHat2DKernel(width=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

