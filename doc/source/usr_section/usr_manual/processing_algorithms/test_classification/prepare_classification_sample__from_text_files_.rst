.. _Prepare classification sample (from text files):

***********************************************
Prepare classification sample (from text files)
***********************************************

Read sample from two text file with tabulated values and store it as a binary Pickle (*.pkl) file. The format matches the output of the <a href="https://force-eo.readthedocs.io/en/latest/components/higher-level/smp/index.html">FORCE Higher Level Sampling Submodule</a>.

**Parameters**


:guilabel:`Text file with features` [file]
    Text file with plain feature values (no headers). One row represents the feature vector of one sample.


:guilabel:`Text file with labels` [file]
    Text file with plain label values (no headers). One row represents the class label of one sample.

**Outputs**


:guilabel:`Output classification sample` [fileDestination]
    Output sample destination *.pkl file.

