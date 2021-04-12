.. _Fit SVC:

*******
Fit SVC
*******

C-Support Vector Classification. 
The implementation is based on libsvm. The fit time scales at least quadratically with the number of samples and may be impractical beyond tens of thousands of samples. 
The multiclass support is handled according to a one-vs-one scheme.

**Parameters**


:guilabel:`Sample` [file]
    Training data sample (*.pkl) file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Code` [string]
    Scikit-learn python code. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html">SVC</a>, <a href="http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html">GridSearchCV</a>, <a href="http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html">StandardScaler</a> for information on different parameters.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.model_selection import GridSearchCV
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC
        svc = SVC(probability=False)
        param_grid = {'kernel': ['rbf'],
                      'gamma': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                      'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
        tunedSVC = GridSearchCV(cv=3, estimator=svc, scoring='f1_macro', param_grid=param_grid)
        classifier = make_pipeline(StandardScaler(), tunedSVC)
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output classifier model destination *.pkl file.

