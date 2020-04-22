.. _Fit LinearSVC:

*************
Fit LinearSVC
*************

Fits a linear Support Vector Classification. Input data will be scaled and grid search is used for model selection.

See the following Cookbook Recipes on how to use classifiers: 
`Classification <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/classification.html>`_
, `Graphical Modeler <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_cookbook/graphical_modeler.html>`_

**Parameters**


:guilabel:`Raster` [raster]
    Raster with training data features.


:guilabel:`Labels` [raster]
    Classification with training data labels.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Code` [string]
    Scikit-learn python code. For information on different parameters have a look at `LinearSVC <http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html>`_. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.model_selection import GridSearchCV
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import LinearSVC
        
        svc = LinearSVC()
        param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        tunedSVC = GridSearchCV(cv=3, estimator=svc, scoring='f1_macro', param_grid=param_grid)
        estimator = make_pipeline(StandardScaler(), tunedSVC)
        
**Outputs**


:guilabel:`Output Classifier` [fileDestination]
    Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

    Default: *outEstimator.pkl*

