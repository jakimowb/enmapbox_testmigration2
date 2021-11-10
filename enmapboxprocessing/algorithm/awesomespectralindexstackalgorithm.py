from typing import Dict, Any, List, Tuple

from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsRasterLayer)

from enmapboxprocessing.algorithm.awesomespectralindexalgorithm import AwesomeSpectralIndexAlgorithm
from enmapboxprocessing.algorithm.vrtbandmathalgorithm import VrtBandMathAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class AwesomeSpectralIndexStackAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_TYPE_LIST, _TYPE_LIST = 'typeList', 'Type list'
    O_TYPE_LIST = ['Vegetation', 'Burn', 'Water', 'Snow', 'Drought', 'Urban']
    D_TYPE_LIST = list(range(len(O_TYPE_LIST)))
    Vegetation, Burn, Water, Snow, Drought, Urban = range(len(O_TYPE_LIST))
    P_SCALE, _SCALE = 'scale', 'Scale factor'
    P_OUTPUT_VRT, _OUTPUT_VRT = 'outputVrt', 'Output VRT layer'

    linkAwesomeSpectralIndices = EnMAPProcessingAlgorithm.htmlLink(
        'https://awesome-ee-spectral-indices.readthedocs.io/en/latest/list.html',
        'Awesome Spectral Indices')

    def displayName(self) -> str:
        return 'Awesome Spectral Indices (all)'

    def shortDescription(self) -> str:
        return f'Create stack of all {self.linkAwesomeSpectralIndices}.\n' \
               f'Note that all spectral indices from that list are considered broad-band spectral indices. ' \
               f'Narrow-band spectral indices are coerced to the closest broad-band spectrum.'

    def helpParameters(self) -> List[Tuple[str, str]]:

        return [
            (self._RASTER, 'Input spectral raster layer.'),
            (self._TYPE_LIST, 'If selected, the list of indices is restricted to the selected types. '
                              'The default is to use all indices.'),
            (self._SCALE, 'Spectral reflectance scale factor. '
                          'Some indices (e.g. EVI) require data to be scaled into the 0 to 1 range. '
                          'If your data is scaled differently, specify an appropriate scale factor.'
                          'E.g. for Int16 data scaled into the 0 to 10000 range, use a value of 10000.\n'
                          'If not specified, '
                          'the scale factor is estimated from the first raster band, '
                          'by using the following heuristic: '
                          'a) if the mean value is between 1 and 100, use a scale factor of 100, '
                          'b) if the mean value is between 100 and 10000, use a scale factor of 10000, '
                          "c) else, don't scale the data."),
            (self._OUTPUT_VRT, 'VRT file destination.'),
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterEnum(self.P_TYPE_LIST, self._TYPE_LIST, self.O_TYPE_LIST, True, self.D_TYPE_LIST, False)
        self.addParameterFloat(self.P_SCALE, self._SCALE, 1., True)
        self.addParameterVrtDestination(self.P_OUTPUT_VRT, self._OUTPUT_VRT)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        type_names = [self.O_TYPE_LIST[i].lower() for i in self.parameterAsEnums(parameters, self.P_TYPE_LIST, context)]
        scale = self.parameterAsFloat(parameters, self.P_SCALE, context)
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_VRT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # create all indices
            indices = AwesomeSpectralIndexAlgorithm.loadIndices()['SpectralIndices']
            filenames = list()
            n = len(indices)
            for i, short_name in enumerate(sorted(indices), 1):
                feedback.setProgress(i / n * 100)
                type_name = indices[short_name]['type']
                if type_name not in type_names:
                    continue

                alg = AwesomeSpectralIndexAlgorithm()
                parameters = {
                    alg.P_RASTER: raster,
                    alg.P_INDEX: short_name,
                    alg.P_SCALE: scale,
                    alg.P_OUTPUT_VRT: Utils.tmpFilename(filename, short_name + '.vrt')
                }
                result = self.runAlg(alg, parameters, None, feedback2, context, True)
                filenames.append(result[alg.P_OUTPUT_VRT])

            # create stack
            ds = gdal.BuildVRT(filename, filenames, separate=True)
            writer = RasterWriter(ds)
            domain = AwesomeSpectralIndexAlgorithm.Domain
            for bandNo, ifilename in enumerate(filenames, 1):
                reader = RasterReader(ifilename)
                metadata = reader.metadataDomain(domain, 1)
                bandName = reader.bandName(1)
                writer.setBandName(bandName, bandNo)
                writer.setMetadataDomain(metadata, domain, bandNo)
            writer = None
            ds = None

            result = {self.P_OUTPUT_VRT: filename}

            self.toc(feedback, result)

        return result
