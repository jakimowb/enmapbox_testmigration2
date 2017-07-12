from processing.core.Processing import Processing
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster


def classFactory(iface):
    return TestPlugin(iface)


class TestPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.provider = TestAlgorithmProvider()
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)


class TestAlgorithmProvider(AlgorithmProvider):

    def getName(self):
        return 'TestAlgorithmProvider'

    def getDescription(self):
        return 'TestAlgorithmProvider'

    def _loadAlgorithms(self):
        self.algs.append(NDVIWithGDAL())


class NDVIWithGDAL(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'NDVI (using GDAL)'
        self.group = 'TestGeoAlgorithms'

        self.addParameter(ParameterRaster('infile', 'Spectral Image'))
        self.addOutput(OutputRaster('outfile', 'NDVI'))

    def processAlgorithm(self, progress):
        from .ndviWithGDAL import ndviWithGDAL
        infile = self.getParameterValue('infile')
        outfile = self.getOutputValue('outfile')
        ndviWithGDAL(infile=infile, outfile=outfile, progress=progress)

    def help(self):
        return True, 'Calculates the NDVI using GDAL'
