from enmapbox import __version__
from processing.core.AlgorithmProvider import AlgorithmProvider


class EnMAPBoxAlgorithmProvider(AlgorithmProvider):

    def getName(self):
        return 'EnMAP-Box'

    def getDescription(self):
        return 'EnMAP-Box ' + __version__

    def getIcon(self):
        return AlgorithmProvider.getIcon(self)

    def _loadAlgorithms(self):
        from .core.TestdataLoader import TestdataLoader
        from .core.EstimatorLoader import EstimatorLoader
        from .core.AccuracyLoader import AccuracyLoader
        TestdataLoader(provider=self)
        EstimatorLoader(provider=self)
        AccuracyLoader(provider=self)
