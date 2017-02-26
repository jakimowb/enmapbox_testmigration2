from enmapboxplugin.processing.AlgorithmLoader import AlgorithmLoader


class TestdataLoader(AlgorithmLoader):

    def _loadAlgorithms(self):
        from .testdata.HymapBerlinAOpener import HymapBerlinAOpener
        from .testdata.HymapBerlinBOpener import HymapBerlinBOpener
        self._appendAlgorithm(HymapBerlinAOpener())
        self._appendAlgorithm(HymapBerlinBOpener())
