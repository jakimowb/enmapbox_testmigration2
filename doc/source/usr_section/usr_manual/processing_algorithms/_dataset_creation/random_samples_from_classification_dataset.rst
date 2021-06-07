.. _Random samples from classification dataset:

******************************************
Random samples from classification dataset
******************************************

Split a dataset by randomly drawing samples.

**Parameters**


:guilabel:`Classification dataset` [file]
    Classification dataset pickle file with feature data X and target data y to draw from.


:guilabel:`Number of samples per category` [string]
    Number of samples to draw from each category. Set a single value N to draw N points for each category. Set a list of values N1, N2, ... Ni, ... to draw Ni points for category i.


:guilabel:`Draw with replacement` [boolean]
    Whether to draw samples with replacement.

    Default: *False*


:guilabel:`Draw proportional` [boolean]
    Whether to interprete number of samples N or Ni as percentage to be drawn from each category.

    Default: *False*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.Stores sampled data.


:guilabel:`Output dataset complement` [fileDestination]
    Output destination pickle file.Stores remaining data that was not sampled.

