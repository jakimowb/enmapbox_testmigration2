.. _Spatial morphological Gradient filter:

*************************************
Spatial morphological Gradient filter
*************************************

Spatial morphological Gradient filter. See <a href="https://en.wikipedia.org/wiki/Morphological_gradient">Wikipedia</a> for general information.

**Parameters**


:guilabel:`Raster layer` [raster]
    Raster layer to be processed band-wise.


:guilabel:`Function` [string]
    Python code. See <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphological_gradient.html">binary_closing</a>, <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html">generate_binary_structure</a>, <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html">iterate_structure</a> for information on different parameters.

    Default::

        from scipy.ndimage.morphology import morphological_gradient, generate_binary_structure, iterate_structure
        
        structure = generate_binary_structure(rank=2, connectivity=1)
        structure = iterate_structure(structure=structure, iterations=1)
        function = lambda array: morphological_gradient(array, structure=structure)
**Outputs**


:guilabel:`Output raster layer` [rasterDestination]
    Raster file destination.

