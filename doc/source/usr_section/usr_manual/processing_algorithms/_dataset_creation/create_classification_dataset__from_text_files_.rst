.. _Create classification dataset (from text files):

***********************************************
Create classification dataset (from text files)
***********************************************

Create a classification dataset from tabulated text files and store the result as a pickle file. 
The format matches that of the <a href="https://force-eo.readthedocs.io/en/latest/components/higher-level/smp/index.html">FORCE Higher Level Sampling Submodule</a>.
Example files (force_features.csv and force_labels.csv) can be found in the EnMAP-Box testdata folder).

**Parameters**


:guilabel:`File with features` [file]
    Text file with tabulated feature data X (no headers). Each row represents the feature vector of a sample.


:guilabel:`File with class values` [file]
    Text file with tabulated target data y (no headers). Each row represents the class value of a sample.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Destination pickle file.

