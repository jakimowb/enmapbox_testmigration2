.. _Spatial Convolution HighPass2DKernel:

************************************
Spatial Convolution HighPass2DKernel
************************************

Applies a 3x3 High-Pass kernel to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

