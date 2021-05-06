.. _Spatial Convolution TrapezoidDisk2DKernel:

*****************************************
Spatial Convolution TrapezoidDisk2DKernel
*****************************************

Applies TrapezoidDisk2DKernel to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

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

