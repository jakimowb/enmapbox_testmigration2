### Interfaces to use algorithms in algorithms.py within
### QGIS Processing Framework

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster
class MyAppGeoAlgorithm(GeoAlgorithm):

        def defineCharacteristics(self):
            self.name = 'NDVI (using GDAL)'
            self.group = 'My Example App'

            self.addParameter(ParameterRaster('infile', 'Spectral Image'))
            self.addOutput(OutputRaster('outfile', 'NDVI'))

        def processAlgorithm(self, progress):
            from .algorithms import ndvi
            #map processing framework parameters to that of you algorithm
            infile = self.getParameterValue('infile')
            outfile = self.getOutputValue('outfile')
            ndvi(infile, outfile, progress=progress)

        def help(self):
            return True, 'Calculates the NDVI using GDAL'


