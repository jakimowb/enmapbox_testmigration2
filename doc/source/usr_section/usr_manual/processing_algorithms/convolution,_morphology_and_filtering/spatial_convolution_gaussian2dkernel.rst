.. _Spatial Convolution Gaussian2DKernel:

************************************
Spatial Convolution Gaussian2DKernel
************************************

Applies Gaussian2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Gaussian2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Gaussian2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Gaussian2DKernel
        
        kernel = Gaussian2DKernel(x_stddev=1, y_stddev=1)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

