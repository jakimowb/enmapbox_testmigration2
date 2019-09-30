.. _Classification from Vector:

**************************
Classification from Vector
**************************

Creates a classification from a vector field with class ids.

Used in the Cookbook Recipes: 
`Classification <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html>`_
, `Graphical Modeler <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html>`_

**Parameters**


:guilabel:`Pixel Grid` [raster]
    Specify input raster.


:guilabel:`Vector` [vector]
    Specify input vector.


:guilabel:`Class id attribute` [field]
    Vector field specifying the class ids.


:guilabel:`Minimal overall coverage` [number]
    Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.


:guilabel:`Minimal dominant coverage` [number]
    Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.


:guilabel:`Oversampling factor` [number]
    Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.
    
    Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

    Default: *1*

**Outputs**


:guilabel:`Output Classification` [rasterDestination]
    Specify output path for classification raster.

