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
class AwesomeSpectralIndicesAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_INDICES, _INDICES = 'indices', 'Indices'
    P_SCALE, _SCALE = 'scale', 'Scale factor'

    P_A, _A = 'A', 'Aerosols band'
    P_B, _B = 'B', 'Blue band'
    P_G, _G = 'G', 'Green band'
    P_R, _R = 'R', 'Red band'
    P_RE1, _RE1 = 'RE1', 'Red Edge 1 band'
    P_RE2, _RE2 = 'RE2', 'Red Edge 2 band'
    P_RE3, _RE3 = 'RE3', 'Red Edge 3 band'
    P_RE4, _RE4 = 'RE4', 'Red Edge 4 band'
    P_N, _N = 'N', 'NIR band'
    P_S1, _S1 = 'S1', 'SWIR 1 band'
    P_S2, _S2 = 'S2', 'SWIR 2 band'
    P_T1, _T1 = 'T1', 'Thermal 1 band'
    P_T2, _T2 = 'T2', 'Thermal 2 band'

    P_L, _L = 'L', 'Canopy background adjustment'
    P_g, _g = 'g', 'Gain factor'
    P_C1, _C1 = 'C1', 'Coefficient 1 for the aerosol resistance term'
    P_C2, _C2 = 'C2', 'Coefficient 2 for the aerosol resistance term'
    P_cexp, _cexp = 'cexp', 'Exponent used for OCVI'
    P_nexp, _nexp = 'nexp', 'Exponent used for GDVI'
    P_alpha, _alpha = 'alpha', 'Weighting coefficient used for WDRVI'
    P_gamma, _gamma = 'gamma', 'Weighting coefficient used for ARVI'
    P_sla, _sla = 'sla', 'Soil line slope'
    P_slb, _slb = 'slb', 'Soil line intercept'

    P_OUTPUT_VRT, _OUTPUT_VRT = 'outputVrt', 'Output VRT layer'

    Domain = 'AwesomeSpectralIndices'
    WavebandMapping = {  # (<center wavelength>, <fwhm>)
        'A': (443, 21), 'B': (492, 66), 'G': (560, 36), 'R': (665, 31), 'RE1': (704, 15), 'RE2': (741, 15),
        'RE3': (783, 20), 'RE4': (865, 21), 'N': (833, 106), 'S1': (1614, 91), 'S2': (2202, 175), 'T1': (10895, 590),
        'T2': (12005, 1010)}
    ConstantMapping = {
        'L': 1.0, 'g': 2.5, 'C1': 6.0, 'C2': 7.5, 'cexp': 1.16, 'nexp': 2.0, 'alpha': 0.1, 'gamma': 1.0, 'sla': 1.0,
        'slb': 0.0
    }

    linkAwesomeSpectralIndices = EnMAPProcessingAlgorithm.htmlLink(
        'https://awesome-ee-spectral-indices.readthedocs.io/en/latest/list.html',
        'Awesome Spectral Indices')

    def displayName(self) -> str:
        return 'Create Awesome Spectral Indices'

    def shortDescription(self) -> str:
        linkMaintainer = EnMAPProcessingAlgorithm.htmlLink('https://github.com/davemlz', 'David Montero Loaiza')
        return f'Create a stack of {self.linkAwesomeSpectralIndices} and/or custom indices.\n' \
               f'Credits: the Awesome Spectral Indices project provides a ready-to-use curated list ' \
               f'of Spectral Indices for Remote Sensing applications, maintained by {linkMaintainer}.'

    def helpParameters(self) -> List[Tuple[str, str]]:

        return [
            (self._RASTER, 'A spectral raster layer.'),
            (self._INDICES, 'The list of indices to be created. Usage examples:\n'
                            'Create (predefined) NDVI: <code>NDVI</code>\n'
                            'Create stack of NDVI and EVI: <code>NDVI, EVI</code>\n'
                            'Create custom index: <code>MyNDVI = (N - R) / (N + R)</code>\n'
                            f'See the full list of predefined  {self.linkAwesomeSpectralIndices}.'),
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
            ('Aerosols band (A), ..., Thermal 2 band (T2)',
             'The spectral band mapping from source raster bands to standardized bands used in the formulas.'),
            ('Canopy background adjustment (L), ..., Soil line intercept (slb)',
             'Standardized additional index parameters used in the formulas.'),
            (self._OUTPUT_VRT, 'VRT file destination.'),
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterString(self.P_INDICES, self._INDICES, 'NDVI', False)
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
            if name in self.ConstantMapping:
                continue
            wavelength, fwhm = self.WavebandMapping[name]
            assert 0  # todo check FWHM
            bandNo = reader.findWavelength(wavelength)
            bandList.append(bandNo)
            bandNames.append(name)
            noDataValues.append(reader.noDataValue(bandNo))

        # add imports
        code = 'import numpy as np\n\n'

        # add constants
        extraNewLine = False
        for name in index['bands']:
            if name in self.ConstantMapping:
                code += f'{name} = {self.ConstantMapping[name]}\n'
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
    def findBroadBand(cls, raster: QgsRasterLayer, name: str, strict=False) -> Optional[int]:
        reader = RasterReader(raster)
        wavelength, fwhm = cls.WavebandMapping[name]
        bandNo = reader.findWavelength(wavelength)
        if bandNo is None:
            return None
        if strict:
            if abs(wavelength - reader.wavelength(bandNo)) > (fwhm / 2):
                return None
        return bandNo

    @classmethod
    def loadIndices(cls) -> Dict:
        return Utils.jsonLoad(__file__.replace('.py', '.json'))
