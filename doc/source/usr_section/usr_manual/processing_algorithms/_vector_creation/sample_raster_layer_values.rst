.. _Sample raster layer values:

**************************
Sample raster layer values
**************************

Creates a new point layer with the same attributes of the input layer and the raster values corresponding to the pixels covered by polygons or point location. 
The resulting point vector contains 1) all input attributes from the Locations vector,  2) attributes SAMPLE_{i}, one for each input raster band, 3) two attributes PIXEL_X, PIXEL_Y for storing the raster pixel locations (zero-based),and 4), in case of polygon locations, an attribute COVER for storing the pixel coverage (%).
Note that we assume non-overlapping feature geometries! In case of overlapping geometries, split the Locations layer into non-overlapping subsets, perform the sampling for each subset individually, and finally concatenate the results.

**Parameters**


:guilabel:`Raster layer` [raster]
    A raster layer to sample data from.


:guilabel:`Vector layer` [vector]
    A vector layer defining the locations to sample.


:guilabel:`Pixel coverage (%)` [range]
    Samples with polygon pixel coverage outside the given range are excluded. This parameter has no effect in case of point locations.

    Default: *[50, 100]*

**Outputs**


:guilabel:`Output point layer` [vectorDestination]
    Output vector file destination.

