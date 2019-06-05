.. _Spatial Convolution HighPass2DKernel:

************************************
Spatial Convolution HighPass2DKernel
************************************

Applies a 3x3 High-Pass kernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code.

    Default::

        from astropy.convolution import Kernel2D
        
        kernel = Kernel2D(array=
          [[-1, -1, -1],
           [-1,  8, -1],
           [-1, -1, -1]])
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

