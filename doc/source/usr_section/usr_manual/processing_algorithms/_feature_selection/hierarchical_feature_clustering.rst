.. _Hierarchical feature clustering:

*******************************
Hierarchical feature clustering
*******************************

Evaluate feature multicollinearity by performing hierarchical/agglomerative clustering with Ward linkage using squared Spearman rank-order correlation as distance between features. The result report includes i) pairwise squared Spearman rank-order correlation matrix, ii) clustering dendrogram, iii) inter-cluster correlation distribution, iv) intra-cluster correlation distribution, and v) a clustering hierarchy table detailing selected cluster representatives for each cluster size n.
For further analysis, all relevant results are also stored as a JSON sidecar file next to the report.

**Parameters**


:guilabel:`Dataset` [file]
    Dataset pickle file with feature data X to be evaluated.


:guilabel:`Do not report plots` [boolean]
    Skip the creation of plots, which can take a lot of time for large features sets.

    Default: *False*

**Outputs**


:guilabel:`Output report` [fileDestination]
    Output report file destination.

