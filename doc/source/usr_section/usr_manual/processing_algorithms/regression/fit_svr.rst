.. _Fit SVR:

*******
Fit SVR
*******

Fits a Support Vector Regression.

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
    Scikit-learn python code. See `SVR <http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html>`_ for information on different parameters. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.model_selection import GridSearchCV
        from sklearn.multioutput import MultiOutputRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVR
        
        svr = SVR()
        param_grid = {'epsilon' : [0.], 'kernel' : ['rbf'],
                      'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                      'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        tunedSVR = GridSearchCV(cv=3, estimator=svr, scoring='neg_mean_absolute_error', param_grid=param_grid)
        scaledAndTunedSVR = make_pipeline(StandardScaler(), tunedSVR)
        estimator = MultiOutputRegressor(scaledAndTunedSVR)
        
**Outputs**


:guilabel:`Output Regressor` [fileDestination]
    Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

    Default: *outEstimator.pkl*

