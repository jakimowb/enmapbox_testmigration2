.. _Fit generic classifier:

**********************
Fit generic classifier
**********************

A generic classifier.

**Parameters**


:guilabel:`Training dataset` [file]
    Training dataset pickle file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Classifier` [string]
    Scikit-learn python code.

    Default::

        from sklearn.dummy import DummyClassifier
        classifier = DummyClassifier()
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output destination pickle file.

