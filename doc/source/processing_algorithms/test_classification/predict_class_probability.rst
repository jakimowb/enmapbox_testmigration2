.. _Predict class probability:

*************************
Predict class probability
*************************

Applies a classifier to a raster to predict class probability.

**Parameters**


:guilabel:`Raster` [raster]
    Source raster layer.


:guilabel:`Classifier` [file]
    Source classifier file (*.pkl).


:guilabel:`Mask` [layer]
    Source raster or vector layer interpreted as binary mask. In case of a raster, all no data (zero, if missing), inf and nan pixel evaluate to false, all other to true. In case of a vector, all pixel with pixel center not covered by a feature geometry evaluate to false,all other to true. Note that only the first raster band used by the renderer is considered.

**Outputs**


:guilabel:`Output class probability` [rasterDestination]
    Output raster destination.

