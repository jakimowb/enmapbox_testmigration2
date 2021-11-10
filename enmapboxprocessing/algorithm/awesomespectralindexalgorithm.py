from typing import Dict, Any, List, Tuple, Optional

from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsProcessingException, QgsRasterBandStats,
                        QgsRasterLayer)

from enmapboxprocessing.algorithm.vrtbandmathalgorithm import VrtBandMathAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.rasterwriter import RasterWriter
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class AwesomeSpectralIndexAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_INDEX, _INDEX = 'index', 'Index'
    P_SCALE, _SCALE = 'scale', 'Scale factor'
    P_OUTPUT_VRT, _OUTPUT_VRT = 'outputVrt', 'Output VRT layer'
    Domain = 'AwesomeSpectralIndices'

    linkAwesomeSpectralIndices = EnMAPProcessingAlgorithm.htmlLink(
        'https://awesome-ee-spectral-indices.readthedocs.io/en/latest/list.html',
        'Awesome Spectral Indices')

    def displayName(self) -> str:
        return 'Awesome Spectral Indices (single)'

    def shortDescription(self) -> str:
        return f'Create one of the {self.linkAwesomeSpectralIndices}.\n' \
               f'Note that all spectral indices from that list are considered broad-band spectral indices. ' \
               f'Narrow-band spectral indices are coerced to the closest broad-band spectrum.'

    def helpParameters(self) -> List[Tuple[str, str]]:

        return [
            (self._RASTER, 'Input spectral raster layer.'),
            (self._INDEX, 'The short name of the index to be created (e.g. NDVI). '
                          f'See the full list of available {self.linkAwesomeSpectralIndices}.'),
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
        self.addParameterString(self.P_INDEX, self._INDEX, 'NDVI', False)
        self.addParameterFloat(self.P_SCALE, self._SCALE, None, True)
        self.addParameterVrtDestination(self.P_OUTPUT_VRT, self._OUTPUT_VRT)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        name = self.parameterAsString(parameters, self.P_INDEX, context)
        scale = self.parameterAsFloat(parameters, self.P_SCALE, context)
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_VRT, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            reader = RasterReader(raster)
            if not reader.isSpectralRasterLayer():
                raise QgsProcessingException(f'not a spectral raster layer: {self._RASTER}')

            # get index info
            indices = self.loadIndices()
            if not name in indices['SpectralIndices']:
                raise QgsProcessingException(f'unknown index short name: {name}')
            index = indices['SpectralIndices'][name]

            feedback.pushInfo(f'Index found: {index}')

            bandList, code = self.deriveParameters(index, reader, scale, feedback)

            alg = VrtBandMathAlgorithm()
            parameters = {
                alg.P_RASTER: raster,
                alg.P_BAND_LIST: bandList,
                alg.P_BAND_NAME: f'{index["short_name"]} - {index["long_name"]}',
                alg.P_NODATA: -9999,
                alg.P_DATA_TYPE: self.Float32,
                alg.P_CODE: code,
                alg.P_OUTPUT_VRT: filename
            }
            self.runAlg(alg, parameters, None, feedback2, context, True)

            # set metadata
            ds = gdal.Open(filename)
            writer = RasterWriter(ds)
            for key in ['bands', 'contributor', 'date_of_addition']:  # skip that items
                index[key] = None
            writer.setMetadataDomain(index, self.Domain, 1)
            writer = None
            ds = None

            result = {self.P_OUTPUT_VRT: filename}
            self.toc(feedback, result)

        return result

    def deriveParameters(
            self, index: Dict, reader: RasterReader, scale: Optional[float], feedback: QgsProcessingFeedback
    ):
        short_name = index['short_name']
        wavebandMapping = {
            'A': 443, 'B': 492, 'G': 560, 'R': 665, 'RE1': 704, 'RE2': 741, 'RE3': 783, 'RE4': 865, 'N': 833,
            'S1': 1614, 'S2': 2202, 'T1': 10895, 'T2': 12005}
        constantMapping = {
            'L': 1.0,  # Canopy background adjustment
            'g': 2.5,  # Gain factor
            'C1': 6.0,  # Coefficient 1 for the aerosol resistance term
            'C2': 7.5,  # Coefficient 2 for the aerosol resistance term
            'cexp': 1.16,  # Exponent used for OCVI
            'nexp': 2.0,  # Exponent used for GDVI
            'alpha': 0.1,  # Weighting coefficient used for WDRVI
            'gamma': 1.0,  # Weighting coefficient used for ARVI
            'sla': 1.0,  # Soil line slope
            'slb': 0.0  # Soil line intercept
        }

        if scale is None:
            stats: QgsRasterBandStats = reader.provider.bandStatistics(
                1, QgsRasterBandStats.Mean, sampleSize=QgsRasterLayer.SAMPLE_SIZE
            )
            if 1 < stats.mean < 100:
                scale = 100
            elif 100 < stats.mean < 10000:
                scale = 10000
            else:
                scale = 1.
            feedback.pushInfo(f'Derived scale factor from first band: {scale}')

        bandList = list()
        bandNames = list()
        noDataValues = list()
        for name in index['bands']:
            if name in constantMapping:
                continue
            wavelength = wavebandMapping[name]
            bandNo = reader.findWavelength(wavelength)
            bandList.append(bandNo)
            bandNames.append(name)
            noDataValues.append(reader.noDataValue(bandNo))

        # add imports
        code = 'import numpy as np\n\n'

        # add constants
        extraNewLine = False
        for name in index['bands']:
            if name in constantMapping:
                code += f'{name} = {constantMapping[name]}\n'
                extraNewLine = True

        # add ufunc
        if extraNewLine:
            code += '\n'
        code += f'def ufunc(in_ar, out_ar, *args, **kwargs):\n'

        # prepare input band variables; use the same identifier as in the formulas; also cast to Float32
        for i, name in enumerate(bandNames):
            if scale == 1:
                code += f'    {name} = np.float32(in_ar[{i}]) / 1e4\n'
            else:
                code += f'    {name} = np.float32(in_ar[{i}]) / {scale}\n'

        # add formula
        code += f'    {short_name} = {index["formula"]}\n'

        # mask noDataRegion
        for i, noDataValue in enumerate(noDataValues):
            code += f'    {short_name}[in_ar[{i}] == {noDataValue}] = -9999\n'

        # fill out_ar
        code += f'    out_ar[:] = {short_name}\n'

        return bandList, code

    @classmethod
    def loadIndices(cls) -> Dict:
        return Utils.jsonLoad(__file__.replace('.py', '.json'))
