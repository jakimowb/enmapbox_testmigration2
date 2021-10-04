.. _SynthMix:

********
SynthMix
********

Create synthetically mixed regression datasets, one for each category. Results are stored as <category.name>.pkl files inside the destination folder.

**Parameters**


:guilabel:`Classification dataset` [file]
    A classification dataset with spectral endmembers used for synthetical mixing.


:guilabel:`Number of mixtures per class` [number]
    Number of mixtures per class


:guilabel:`Include original endmembers` [boolean]
    Whether to include the original library spectra into the dataset.

    Default: *True*


:guilabel:`Mixing complexity likelihoods` [string]
    A list of likelihoods for using 2, 3, 4, ... endmember mixing models. Trailing 0 likelihoods can be skipped. The default values of 0.5, 0.5,results in 50% 2-endmember and 50% 3-endmember models.

    Default: *0.5, 0.5*


:guilabel:`Allow within-class mixtures` [boolean]
    Whether to allow mixtures with profiles belonging to the same class.

    Default: *True*


:guilabel:`Class likelihoods` [string]
    A list of likelihoods for drawing profiles from each class. If not specified, class likelihoods are proportional to the class size.

**Outputs**


:guilabel:`Output folder` [folderDestination]
    Folder destination.

