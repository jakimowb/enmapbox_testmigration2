from enmapboxplugin.processing.AlgorithmLoader import AlgorithmLoader


class EstimatorLoader(AlgorithmLoader):

    def _loadAlgorithms(self):

        self._loadEstimatorTools()
        self._loadClassifier()
        self._loadRegressor()

    def _loadEstimatorTools(self):
        from .estimator.EstimatorPredictor import EstimatorPredictor
        from .estimator.EstimatorProbabilityPredictor import EstimatorProbabilityPredictor
        from .estimator.EstimatorReportViewer import EstimatorReportViewer
        self._appendAlgorithm(EstimatorPredictor())
        self._appendAlgorithm(EstimatorProbabilityPredictor())
        self._appendAlgorithm(EstimatorReportViewer())

    def _loadClassifier(self):
        from .classifier.RandomForestClassifierFitter import RandomForestClassifierFitter
        self._appendAlgorithm(RandomForestClassifierFitter())

    def _loadRegressor(self):
        from .regressor.RandomForestRegressorFitter import RandomForestRegressorFitter
        self._appendAlgorithm(RandomForestRegressorFitter())
