from sklearn.base import RegressorMixin, ClassifierMixin, TransformerMixin, BaseEstimator
from sklearn.utils.validation import check_is_fitted, check_array, check_X_y


class FeatureSubsetter(BaseEstimator, TransformerMixin):
    def __init__(self, indices=None):
        self.indices = indices

    def fit(self, X=None, y=None):
        check_X_y(X, y)
        self.nfeatures_ = len(X[0])
        return self

    def transform(self, X, y=None):
        if len(X[0]) != self.nfeatures_:
            raise ValueError('number of features in transform is different from the number of features in fit')
        X = check_array(X)
        return X[:, self.indices]

def check():
    from sklearn.utils.estimator_checks import check_estimator
    from sklearn.svm import LinearSVC
    from sklearn.decomposition import PCA
    check_estimator(FeatureSubsetter)

if __name__ == '__main__':
    check()