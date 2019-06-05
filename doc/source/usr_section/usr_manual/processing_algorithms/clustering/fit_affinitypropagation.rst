.. _Fit AffinityPropagation:

***********************
Fit AffinityPropagation
***********************

Fits a Affinity Propagation clusterer (input data will be scaled).

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Code` [string]
    Scikit-learn python code. For information on different parameters have a look at `AffinityPropagation <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html>`_. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on scaling

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import AffinityPropagation
        
        clusterer = AffinityPropagation()
        estimator = make_pipeline(StandardScaler(), clusterer)
        
**Outputs**


:guilabel:`Output Clusterer` [fileDestination]
    Specifiy output path for the clusterer (.pkl). This file can be used for applying the clusterer to an image using 'Clustering -> Predict Clustering'.

