.. _Fit GaussianProcessClassifier:

*****************************
Fit GaussianProcessClassifier
*****************************

Fits Gaussian Process Classifier. See `Gaussian Processes <http://scikit-learn.org/stable/modules/gaussian_process.html>`_ for further information.

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
    Scikit-learn python code. See `GaussianProcessClassifier <http://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html>`_ for information on different parameters.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.gaussian_process import GaussianProcessClassifier
        from sklearn.gaussian_process.kernels import RBF
        
        gpc = GaussianProcessClassifier(RBF(), max_iter_predict=1)
        estimator = make_pipeline(StandardScaler(), gpc)
        
**Outputs**


:guilabel:`Output Classifier` [fileDestination]
    Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

    Default: *outEstimator.pkl*

