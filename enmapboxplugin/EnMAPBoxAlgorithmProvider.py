from processing.core.AlgorithmProvider import AlgorithmProvider

class EnMAPBoxAlgorithmProvider(AlgorithmProvider):

    def getName(self):
        return 'EnMAP-Box'

    def getDescription(self):
        return 'EnMAP-Box'

    def getIcon(self):
        return AlgorithmProvider.getIcon(self)

    def _loadAlgorithms(self):
        """Here we fill the list of algorithms in self.algs.

        This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.

        In this case, since the list is always the same, we assign from
        the pre-made list. This assignment has to be done in this method
        even if the list does not change, since the self.algs list is
        cleared before calling this method.
        """
        from GeoAlgorithms.HymapBerlinA import HymapBerlinA
        from GeoAlgorithms.HymapBerlinB import HymapBerlinB

        self.algs = [HymapBerlinA(), HymapBerlinB()]
