.. _Spectral Convolution Trapezoid1DKernel:

**************************************
Spectral Convolution Trapezoid1DKernel
**************************************

Applies Trapezoid1DKernel.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

