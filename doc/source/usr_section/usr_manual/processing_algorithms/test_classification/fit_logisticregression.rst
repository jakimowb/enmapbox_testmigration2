.. _Fit LogisticRegression:

**********************
Fit LogisticRegression
**********************

Logistic Regression (aka logit, MaxEnt) classifier.
In the multiclass case, the training algorithm uses the one-vs-rest (OvR) scheme if the ‘multi_class’ option is set to ‘ovr’, and uses the cross-entropy loss if the ‘multi_class’ option is set to ‘multinomial’.

**Parameters**


:guilabel:`Training dataset` [file]
    Training dataset pickle file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Classifier` [string]
    Scikit-learn python code. See <a href="https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html">LogisticRegression</a> for information on different parameters.

    Default::

        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        logisticRegression = LogisticRegression()
        classifier = make_pipeline(StandardScaler(), logisticRegression)
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output destination pickle file.

