.. _Colorize Class Scores:

*********************
Colorize Class Scores
*********************

Converts multiband class scores (e.g. class cover fractions or probabilies) into a RGB visualization concidering all classes at ones. The RGB color is the weighted mean of class colors given by the style, and weights are given by class scores. Note that scores must range between 0 and 1, and outlieres are trimmed beforehand! 
For example, pure pixels with score of 1 (e.g. class cover fraction equal 100%) appear in its pure class color. A two class mixture pixel with 50% of class red (255, 0, 0) and 50% of class green (0, 255, 0) appears in a dull yellow (127, 127, 0).

**Parameters**


:guilabel:`Score` [raster]
    Source raster layer with bands matching categories given by style.


:guilabel:`Style` [layer]
    Source raster or vector layer styled with a paletted/unique values (raster) or categorized symbol (vector) renderer.

**Outputs**


:guilabel:`Output RGB raster` [rasterDestination]
    Output raster destination.

