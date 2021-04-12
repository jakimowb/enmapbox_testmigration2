.. _Classifier feature ranking (permutation importance):

***************************************************
Classifier feature ranking (permutation importance)
***************************************************

Permutation feature importance is a model inspection technique that is especially useful for non-linear or opaque estimators. The permutation feature importance is defined to be the decrease in a model score when a single feature value is randomly shuffled. This procedure breaks the relationship between the feature and the target, thus the drop in the model score is indicative of how much the model depends on the feature. This technique benefits from being model agnostic and can be calculated many times with different permutations of the feature.
See <a href="https://scikit-learn.org/stable/modules/permutation_importance.html#permutation-importance">Permutation feature importance</a> for further information.

**Parameters**


:guilabel:`Classifier` [file]
    Classifier (*.pkl) file. In case of unfitted classifier, also specify a training sample.


:guilabel:`Train sample` [file]
    Training sample (*.pkl) file used for (re-)fitting the classifier. Can be skipped in case of fitted classifier.


:guilabel:`Test sample` [file]
    Testing sample (*.pkl) file used for performance evaluation. If skipped, the training sample is used.


:guilabel:`Scoring` [enum]
    Scorer to use. See <a href="https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter">The scoring parameter: defining model evaluation rules</a> for further information.

    Default: *7*


:guilabel:`Number of repeats` [number]
    Number of times to permute a feature.

    Default: *10*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report *.html file.

