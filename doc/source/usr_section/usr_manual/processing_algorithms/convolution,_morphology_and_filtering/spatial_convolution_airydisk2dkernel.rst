.. _Spatial Convolution AiryDisk2DKernel:

************************************
Spatial Convolution AiryDisk2DKernel
************************************

Applies AiryDisk2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.AiryDisk2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.AiryDisk2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import AiryDisk2DKernel
        
        kernel = AiryDisk2DKernel(radius=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

