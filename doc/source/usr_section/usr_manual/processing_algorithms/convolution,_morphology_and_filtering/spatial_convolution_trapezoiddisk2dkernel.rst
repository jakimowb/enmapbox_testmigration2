.. _Spatial Convolution TrapezoidDisk2DKernel:

*****************************************
Spatial Convolution TrapezoidDisk2DKernel
*****************************************

Applies TrapezoidDisk2DKernel to image.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.TrapezoidDisk2DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.TrapezoidDisk2DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import TrapezoidDisk2DKernel
        
        kernel = TrapezoidDisk2DKernel(radius=3, slope=1)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

