.. _Spatial Convolution Tophat2DKernel:

**********************************
Spatial Convolution Tophat2DKernel
**********************************

Applies Tophat2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Tophat2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Tophat2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Tophat2DKernel
        
        kernel = Tophat2DKernel(radius=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

