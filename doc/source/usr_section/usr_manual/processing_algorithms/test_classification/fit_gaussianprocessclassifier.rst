.. _Fit GaussianProcessClassifier:

*****************************
Fit GaussianProcessClassifier
*****************************

Gaussian process classification (GPC) based on Laplace approximation.
The implementation is based on Algorithm 3.1, 3.2, and 5.1 of Gaussian Processes for Machine Learning (GPML) by Rasmussen and Williams. 
Internally, the Laplace approximation is used for approximating the non-Gaussian posterior by a Gaussian. Currently, the implementation is restricted to using the logistic link function. For multi-class classification, several binary one-versus rest classifiers are fitted. Note that this class thus does not implement a true multi-class Laplace approximation.
See <a href="http://scikit-learn.org/stable/modules/gaussian_process.html">Gaussian Processes</a> for further information.

**Parameters**


:guilabel:`Sample` [file]
    Training data sample (*.pkl) file used for fitting the classifier. If not specified, an unfitted classifier is created.


:guilabel:`Code` [string]
    Scikit-learn python code. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html">GaussianProcessClassifier</a> for information on different parameters.

    Default::

        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.gaussian_process import GaussianProcessClassifier
        from sklearn.gaussian_process.kernels import RBF
        gpc = GaussianProcessClassifier(RBF(), max_iter_predict=1)
        classifier = make_pipeline(StandardScaler(), gpc)
**Outputs**


:guilabel:`Output classifier` [fileDestination]
    Output classifier model destination *.pkl file.

