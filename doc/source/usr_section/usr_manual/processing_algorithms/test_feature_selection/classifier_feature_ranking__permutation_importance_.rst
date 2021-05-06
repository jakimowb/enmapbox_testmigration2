.. _Classifier feature ranking (permutation importance):

***************************************************
Classifier feature ranking (permutation importance)
***************************************************

Permutation feature importance is a model inspection technique that is especially useful for non-linear or opaque estimators. The permutation feature importance is defined to be the decrease in a model score when a single feature value is randomly shuffled. This procedure breaks the relationship between the feature and the target, thus the drop in the model score is indicative of how much the model depends on the feature. This technique benefits from being model agnostic and can be calculated many times with different permutations of the feature.
See Permutation feature importance for further information.

**Parameters**


:guilabel:`Classifier` [file]
    Classifier pickle file. In case of an unfitted classifier, also specify a training dataset.


:guilabel:`Training dataset` [file]
    Training dataset pickle file used for (re-)fitting the classifier. Can be skipped in case of a fitted classifier.


:guilabel:`Test dataset` [file]
    Test dataset pickle file used for performance evaluation. If skipped, the training dataset is used.


:guilabel:`Evaluation metric` [enum]
    An evaluation metric to use. See Metrics and scoring: quantifying the quality of predictions for further information.

    Default: *7*


:guilabel:`Number of repetitions` [number]
    Number of times to permute a feature.

    Default: *10*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report file destination.

