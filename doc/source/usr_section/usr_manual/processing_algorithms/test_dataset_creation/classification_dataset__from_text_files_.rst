.. _Classification dataset (from text files):

****************************************
Classification dataset (from text files)
****************************************

Store tabulated data from text files into a pickle file.
The format matches the output of the <a href="https://force-eo.readthedocs.io/en/latest/components/higher-level/smp/index.html">FORCE Higher Level Sampling Submodule</a>.

**Parameters**


:guilabel:`File with features` [file]
    Text file with tabulated feature data X (no headers). Each row represents the feature vector of a sample.


:guilabel:`File with class values` [file]
    Text file with tabulated target data y (no headers). Each row represents the class value of a sample.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.

