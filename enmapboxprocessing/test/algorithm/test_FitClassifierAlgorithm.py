from sklearn.base import ClassifierMixin

from sklearn.base import ClassifierMixin
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

from enmapboxprocessing.algorithm.fitclassifieralgorithmbase import FitClassifierAlgorithmBase
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitgenericclassifier import FitGenericClassifier
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from enmapboxunittestdata import (classifierDumpPkl)

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class FitTestClassifierAlgorithm(FitClassifierAlgorithmBase):

    def displayName(self) -> str:
        return ''

    def shortDescription(self) -> str:
        return ''

    def helpParameterCode(self) -> str:
        return ''

    def code(self) -> ClassifierMixin:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(n_estimators=10, oob_score=True, random_state=42)
        return classifier


class TestFitClassifierAlgorithm(TestCase):

    def test_fitted(self):
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_DATEST: classifierDumpPkl,
            alg.P_CLASSIFIER: alg.defaultCodeAsString(),
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        self.runalg(alg, parameters)

    def test_unfitted(self):
        alg = FitTestClassifierAlgorithm()
        parameters = {
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        self.runalg(alg, parameters)

    def test_code(self):
        alg = FitGenericClassifier()
        parameters = {
            alg.P_CODE: 'from sklearn.linear_model import LogisticRegression\n'
                        'classifier = LogisticRegression(max_iter=1000)',
            alg.P_OUTPUT_CLASSIFIER: c + '/vsimem/classifier.pkl',
        }
        self.runalg(alg, parameters)

    def test_classifiers(self):
        algs = [
            FitRandomForestClassifierAlgorithm(), FitGaussianProcessClassifierAlgorithm(), FitLinearSvcAlgorithm(),
            FitSvcAlgorithm(),
        ]
        for alg in algs:
            print(alg.displayName())
            alg.initAlgorithm()
            alg.shortHelpString()

