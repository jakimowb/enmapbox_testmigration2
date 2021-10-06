.. _Categorized layer to class fraction layer:

*****************************************
Categorized layer to class fraction layer
*****************************************

Aggregates a (single-`band <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-band>`_) `categorized layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-categorized-layer>`_ into a (multiband) `class <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-class>`_ fraction raster, by resampling into the given `grid <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-grid>`_. `Output <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-output>`_ band order and naming are given by the renderer `categories <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-categories>`_.

**Parameters**


:guilabel:`Categorized layer` [layer]
    A `categorized layer <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-categorized-layer>`_ with `categories <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-categories>`_ to be aggregated into fractions.


:guilabel:`Grid` [raster]
    The target `grid <https://enmap-box.readthedocs.io/en/latest/general/glossary.html#term-grid>`_.

**Outputs**


:guilabel:`Output class fraction layer` [rasterDestination]
    Raster file destination.

**Command-line usage**

``>qgis_process help enmapbox:CategorizedLayerToClassFractionLayer``::

    ----------------
    Arguments
    ----------------
    
    categorizedLayer: Categorized layer
    	Argument type:	layer
    	Acceptable values:
    		- Path to a vector, raster or mesh layer
    grid: Grid
    	Argument type:	raster
    	Acceptable values:
    		- Path to a raster layer
    outputClassFraction: Output class fraction layer
    	Argument type:	rasterDestination
    	Acceptable values:
    		- Path for new raster layer
    
    ----------------
    Outputs
    ----------------
    
    outputClassFraction: <outputRaster>
    	Output class fraction layer
    
    