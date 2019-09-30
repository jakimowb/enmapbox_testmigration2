.. _Fit PLSRegression:

*****************
Fit PLSRegression
*****************

Fits a Partial Least Squares Regression.

See the following Cookbook Recipes on how to use regressors: 
`Regression <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/regression.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Regression` [raster]
    Specify input raster.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Code` [string]
    Scikit-learn python code. See `PLSRegression <https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.PLSRegression.html>`_ for information on different parameters.

    Default::

        from sklearn.cross_decomposition import PLSRegression
        estimator = PLSRegression(n_components=3, scale=True)
        
**Outputs**


:guilabel:`Output Regressor` [fileDestination]
    Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

    Default: *outEstimator.pkl*

