.. _Spatial Convolution Ring2DKernel:

********************************
Spatial Convolution Ring2DKernel
********************************

Applies Ring2DKernel to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

