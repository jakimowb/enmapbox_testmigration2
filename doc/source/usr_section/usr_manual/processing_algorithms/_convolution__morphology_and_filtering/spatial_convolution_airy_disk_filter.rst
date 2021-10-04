.. _Spatial convolution Airy Disk filter:

************************************
Spatial convolution Airy Disk filter
************************************

2D Airy Disk filter.
This kernel models the diffraction pattern of a circular aperture. This kernel is normalized to a peak value of 1

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be filtered.


:guilabel:`Kernel` [string]
    Python code. See <a href="http://docs.astropy.org/en/stable/api/astropy.convolution.AiryDisk2DKernel.html">AiryDisk2DKernel</a> for information on different parameters.

    Default::

        from astropy.convolution import AiryDisk2DKernel
        kernel = AiryDisk2DKernel(radius=1)

:guilabel:`Normalize kernel` [boolean]
    Whether to normalize the kernel to have a sum of one.

    Default: *False*


:guilabel:`Interpolate no data pixel` [boolean]
    Whether to interpolate no data pixel. Will result in renormalization of the kernel at each position ignoring pixels with no data values.

    Default: *True*

**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

