from enmapboxplugin.processing.AlgorithmLoader import AlgorithmLoader


class EstimatorLoader(AlgorithmLoader):

    def _loadAlgorithms(self):

        self._loadEstimatorCaller()
        self._loadClassifier()
        self._loadRegressor()
        self._loadTransformer()

    def _loadEstimatorCaller(self):
        from .estimator.EstimatorPredictor import EstimatorPredictor
        from .estimator.EstimatorProbabilityPredictor import EstimatorProbabilityPredictor
        from .estimator.EstimatorTransformCaller import EstimatorTransformCaller
        from .estimator.EstimatorReportViewer import EstimatorReportViewer
        self._appendAlgorithm(EstimatorPredictor())
        self._appendAlgorithm(EstimatorProbabilityPredictor())
        self._appendAlgorithm(EstimatorTransformCaller())
        self._appendAlgorithm(EstimatorReportViewer())

    def _loadClassifier(self):
        from .classifier.RandomForestClassifierFitter import RandomForestClassifierFitter
        self._appendAlgorithm(RandomForestClassifierFitter())

    def _loadRegressor(self):
        from .regressor.RandomForestRegressorFitter import RandomForestRegressorFitter
        self._appendAlgorithm(RandomForestRegressorFitter())

    def _loadTransformer(self):
        from .transformer.PCA import PCAFitter
        self._appendAlgorithm(PCAFitter())
