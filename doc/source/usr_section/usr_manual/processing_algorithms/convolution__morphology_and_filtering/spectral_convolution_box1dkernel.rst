.. _Spectral Convolution Box1DKernel:

********************************
Spectral Convolution Box1DKernel
********************************

Applies Box1DKernel.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `astropy.convolution.Box1DKernel <http://docs.astropy.org/en/stable/api/astropy.convolution.Box1DKernel.html>`_ for information on different parameters.

    Default::

        from astropy.convolution import Box1DKernel
        
        kernel = Box1DKernel(width=5)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

