.. _Create RGB image from class probability/fraction layer:

******************************************************
Create RGB image from class probability/fraction layer
******************************************************

Create an RGB image from a class fraction/probability layer.The RGB pixel color of a single pixel is given by the weighted mean of the given category colors.The weights are given by class fractions/probabilities (i.e. values between 0 and 1).
For example, pure pixels with cover fractions of 1 appear in its pure category color. A mixed-pixel with a 50% fractions in two categories colored in red and green,appears in a dull yellow ( 0.5 x (255, 0, 0) + 0.5 x (0, 255, 0) = (127, 127, 0) ).

**Parameters**


:guilabel:`Class probability/fraction layer` [raster]
    A class fraction layer or class probability layer used as weights for calculating final pixel colors.


:guilabel:`Colors` [string]
    Comma separated list of hex-colors representing (pure) category colors, one color for each band in the given class probability/fraction layer.


:guilabel:`Colors from categorized layer` [layer]
    A categorized layer with (pure) category colors, one category for each band in the given class probability/fraction layer.

**Outputs**


:guilabel:`Output RGB image` [rasterDestination]
    Output raster file destination.

