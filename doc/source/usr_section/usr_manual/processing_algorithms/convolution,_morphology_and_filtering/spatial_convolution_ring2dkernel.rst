.. _Spatial Convolution Ring2DKernel:

********************************
Spatial Convolution Ring2DKernel
********************************

Applies Ring2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Ring2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Ring2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Ring2DKernel
        
        kernel = Ring2DKernel(radius_in=3, width=2)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

