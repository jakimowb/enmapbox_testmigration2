.. _Spatial Morphological Binary Fill Holes:

***************************************
Spatial Morphological Binary Fill Holes
***************************************

Applies binary_fill_holes morphology filter to image.

See the following Cookbook Recipes on how to apply filters: 
`Filtering <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/filtering.html>`_
, `Generic Filter <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/generic_filter.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Code` [string]
    Python code. See `scipy.ndimage.binary_fill_holes <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.binary_fill_holes.html>`_ for information on different parameters. At first, the structuring element will be defined (`scipy.ndimage.generate_binary_structure <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html>`_). By default, its dimensions are always equal to 3. The connectivity parameter defines the type of neighborhood. In order create a bigger structuring element, the parameters in `iterate_structure <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html>`_ have to be altered (e.g. iterations=2 will increase the size to 5). Alternatively, a custom numpy array can be used as structural element.

    Default::

        from scipy.ndimage.morphology import binary_fill_holes, generate_binary_structure, iterate_structure
        
        structure = generate_binary_structure(rank=2, connectivity=1)
        structure = iterate_structure(structure=structure, iterations=1)
        function = lambda array: binary_fill_holes(array, structure=structure)
        
**Outputs**


:guilabel:`Output Raster` [rasterDestination]
    Specify output path for raster.

