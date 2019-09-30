.. _Spatial Convolution Tophat2DKernel:

**********************************
Spatial Convolution Tophat2DKernel
**********************************

Applies Tophat2DKernel to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

