.. _Spatial Convolution Box2DKernel:

*******************************
Spatial Convolution Box2DKernel
*******************************

Applies Box2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Box2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Box2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Box2DKernel
        
        kernel = Box2DKernel(width=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

