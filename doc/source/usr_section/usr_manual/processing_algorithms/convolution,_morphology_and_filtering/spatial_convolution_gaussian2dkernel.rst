.. _Spatial Convolution Gaussian2DKernel:

************************************
Spatial Convolution Gaussian2DKernel
************************************

Applies Gaussian2DKernel to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

