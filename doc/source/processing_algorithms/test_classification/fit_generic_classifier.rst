.. _Fit generic classifier:

**********************
Fit generic classifier
**********************

A generic classifier.

**Parameters**


:guilabel:`Sample` [file]
    Training data sample (*.pkl) file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Code` [string]
    Scikit-learn python code.

    Default::

        from sklearn.dummy import DummyClassifier
        classifier = DummyClassifier()
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output classifier model destination *.pkl file.

