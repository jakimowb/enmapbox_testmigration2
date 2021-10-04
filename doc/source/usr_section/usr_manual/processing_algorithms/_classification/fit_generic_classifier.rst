.. _Fit generic classifier:

**********************
Fit generic classifier
**********************

A generic classifier.

**Parameters**


:guilabel:`Classifier` [string]
    Scikit-learn python code.

    Default::

        from sklearn.dummy import DummyClassifier
        
        classifier = DummyClassifier()

:guilabel:`Training dataset` [file]
    Training dataset pickle file used for fitting the classifier. If not specified, an unfitted classifier is created.

**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Destination pickle file.

