.. _Spectral Convolution Trapezoid1DKernel:

**************************************
Spectral Convolution Trapezoid1DKernel
**************************************

Applies Trapezoid1DKernel.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Trapezoid1DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Trapezoid1DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Trapezoid1DKernel
        
        kernel = Trapezoid1DKernel(width=5, slope=1)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

