.. _Fit Normalizer:

**************
Fit Normalizer
**************

Fits a Normalizer (normalizes samples individually to unit norm). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Code` [string]
    Scikit-learn python code. See `Normalizer <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Normalizer.html>`_ for information on different parameters.

    Default::

        from sklearn.preprocessing import Normalizer
        
        estimator = Normalizer()
        
**Outputs**


:guilabel:`Output Transformer` [fileDestination]
    Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

