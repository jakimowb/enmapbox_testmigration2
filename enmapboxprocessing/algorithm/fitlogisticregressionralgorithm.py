from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from typeguard import typechecked


@typechecked
class FitRandomForestClassifierAlgorithm(FitClassifierAlgorithmBase):

    def displayName(self) -> str:
        return 'Fit RandomForestClassifier'

    def shortDescription(self) -> str:
        return 'A random forest classifier.' \
               '\nA random forest is a meta estimator that fits a number of decision tree classifiers on various ' \
               'sub-samples of the dataset and uses averaging to improve the predictive accuracy and control ' \
               'over-fitting. The sub-sample size is controlled with the max_samples parameter if bootstrap=True ' \
               '(default), otherwise the whole dataset is used to build each tree.'

    def helpParameterCode(self) -> str:
        return 'Scikit-learn python code. ' \
               'See <a href="' \
               'http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html' \
               '">RandomForestClassifier</a> for information on different parameters.'

    def code(cls):
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        logisticRegression = LogisticRegression()
        classifier = make_pipeline(StandardScaler(), logisticRegression)
        return classifier
