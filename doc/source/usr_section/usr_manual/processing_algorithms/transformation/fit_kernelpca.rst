.. _Fit KernelPCA:

*************
Fit KernelPCA
*************

Fits a Kernel PCA (Principal Component Analysis).

**Parameters**


:guilabel:`Raster` [raster]
    Specify input raster.


:guilabel:`Mask` [layer]
    Specified vector or raster is interpreted as a boolean mask.
    
    In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.
    
    In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.


:guilabel:`Code` [string]
    Scikit-learn python code. See `KernelPCA <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html>`_ for information on different parameters.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import KernelPCA
        
        kernelPCA = KernelPCA(n_components=3, fit_inverse_transform=True)
        estimator = make_pipeline(StandardScaler(), kernelPCA)
        
**Outputs**


:guilabel:`Output Transformer` [fileDestination]
    Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

