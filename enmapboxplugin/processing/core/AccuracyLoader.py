from enmapboxplugin.processing.AlgorithmLoader import AlgorithmLoader


class AccuracyLoader(AlgorithmLoader):

    def _loadAlgorithms(self):
        from .accuracy.ClassificationAccuracyAssessor import ClassificationAccuracyAssessor
        from .accuracy.RegressionAccuracyAssessor import RegressionAccuracyAssessor
        self._appendAlgorithm(ClassificationAccuracyAssessor())
        self._appendAlgorithm(RegressionAccuracyAssessor())
