from enmapbox import __version__
from processing.core.AlgorithmProvider import AlgorithmProvider
from enmapboxgeoalgorithms.algorithms import ALGORITHMS

class EnMAPBoxAlgorithmProvider(AlgorithmProvider):

    def getName(self):
        return 'EnMAP-Box'

    def getDescription(self):
        return 'EnMAP-Box ' + __version__

    def getIcon(self):
        return AlgorithmProvider.getIcon(self)

    def _loadAlgorithms(self):
        self.algs.extend(ALGORITHMS)