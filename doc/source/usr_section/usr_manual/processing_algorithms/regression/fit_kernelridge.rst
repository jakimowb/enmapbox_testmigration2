.. _Fit KernelRidge:

***************
Fit KernelRidge
***************

Fits a KernelRidge Regression. Click `here <http://scikit-learn.org/stable/modules/kernel_ridge.html>`_ for additional information.

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
    Scikit-learn python code. See `KernelRidge <http://scikit-learn.org/stable/modules/generated/sklearn.kernel_ridge.KernelRidge.html>`_ for information on different parameters. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.model_selection import GridSearchCV
        from sklearn.preprocessing import StandardScaler
        from sklearn.kernel_ridge import KernelRidge
        
        krr = KernelRidge()
        param_grid = {'kernel': ['rbf'],
                      'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                      'alpha': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        tunedKRR = GridSearchCV(cv=3, estimator=krr, scoring='neg_mean_absolute_error', param_grid=param_grid)
        scaledAndTunedKRR = make_pipeline(StandardScaler(), tunedKRR)
        estimator = scaledAndTunedKRR
        
**Outputs**


:guilabel:`Output Regressor` [fileDestination]
    Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

