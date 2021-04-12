.. _Subsample classification sample:

*******************************
Subsample classification sample
*******************************

Draw a random subsample.

**Parameters**


:guilabel:`Sample` [file]
    Sample (*.pkl) file.


:guilabel:`Number of samples per category` [string]
    Number of samples to be drawn from each category. Set a single value N to draw N points for each category. Set a list of values N1, N2, ... Ni, ... to draw Ni points for category i.


:guilabel:`With replacement` [boolean]
    Whether to draw samples with replacement.

    Default: *False*


:guilabel:`Proportional` [boolean]
    Whether to interprete number of samples N or Ni as percentage to be drawn from each category.

    Default: *False*


:guilabel:`Random seed` [number]
    The seed for the random generator can be provided.

**Outputs**


:guilabel:`Output sample` [fileDestination]
    Output sample *.pkl file including sampled data.


:guilabel:`Output sample complement` [fileDestination]
    Output sample *.pkl file including all data not sampled (i.e. complement).

