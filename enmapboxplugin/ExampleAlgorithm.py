from enmapboxplugin.EnMAPBoxGeoAlgorithm import EnMAPBoxGeoAlgorithm
from enmapbox.testdata import HymapBerlinA
from processing.core.outputs import OutputRaster

class ExampleAlgorithm(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Example GeoAlgorithm'
        self.group = 'Example Menu'

    def processAlgorithm(self, progress):
        pass