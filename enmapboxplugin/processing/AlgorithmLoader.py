from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm


class AlgorithmLoader(object):

    def __init__(self, provider):
        assert isinstance(provider, AlgorithmProvider)
        self.provider = provider
        self._loadAlgorithms()

    def _loadAlgorithms(self):
        raise NotImplementedError

    def _appendAlgorithm(self, algorithm):
        assert isinstance(algorithm, GeoAlgorithm)
        self.provider.algs.append(algorithm)