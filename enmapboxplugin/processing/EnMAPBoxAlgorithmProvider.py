from enmapbox import __version__
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm


class EnMAPBoxAlgorithmProvider(AlgorithmProvider):
    def __init__(self):
        super(EnMAPBoxAlgorithmProvider, self).__init__()
        #internal list of GeoAlgorithms. Is used on re-loads and can be manipulated
        self._algs = []

    def getName(self):
        return 'EnMAP-Box'

    def getDescription(self):
        return 'EnMAP-Box ' + __version__

    def getIcon(self):
        from enmapbox.gui.enmapboxgui import getIcon
        return getIcon()

    def loadAlgorithms(self):
        self.algs = []
        self._loadAlgorithms()
        for alg in self.algs:
            alg.provider = self

    def _loadAlgorithms(self):
        #first, load own algorithms
        try:
            from enmapboxgeoalgorithms.algorithms import ALGORITHMS
            self.algs.extend(ALGORITHMS)
        except Exception as ex:
            print('Error: Failed to load enmapboxgeoalgorithms.algorithms')
            print(ex)

        #load other algorthms
        self.algs.extend(self._algs[:])

    def appendAlgorithms(self, geoAlgorithms):
        """Allows to add GeoAlgorithms during runtime"""

        from processing.core.alglist import algList
        pAlgs = algList.algs[self.getName()]

        self._algs.extend(geoAlgorithms[:])

        if len(self.algs) > 0:
            for ga in geoAlgorithms:
                assert isinstance(ga, GeoAlgorithm)
                # todo: remove from previous provider
                ga.provider = self
                pAlgs[ga.commandLineName()] = ga
            algList.providerUpdated.emit(self.getName())

