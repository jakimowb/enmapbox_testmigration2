from processing.core.GeoAlgorithm import GeoAlgorithm


class ExampleAlgorithm(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'Example GeoAlgorithm'
        self.group = 'Example Menu'

    def processAlgorithm(self, progress):
        pass
