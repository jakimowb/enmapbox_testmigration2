.. _Fit RandomForestClassifier:

**************************
Fit RandomForestClassifier
**************************

A random forest classifier.
A random forest is a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting. The sub-sample size is controlled with the max_samples parameter if bootstrap=True (default), otherwise the whole dataset is used to build each tree.

**Parameters**


:guilabel:`Sample` [file]
    Training data sample (*.pkl) file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Code` [string]
    Scikit-learn python code. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html">RandomForestClassifier</a> for information on different parameters.

    Default::

        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators=100, bootstrap=True, oob_score=True, max_samples=None)
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output classifier model destination *.pkl file.

