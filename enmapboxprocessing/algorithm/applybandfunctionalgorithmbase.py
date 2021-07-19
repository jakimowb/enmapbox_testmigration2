import inspect
from typing import Dict, Any, List, Tuple

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, Qgis)

from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class ApplyBandFunctionAlgorithmBase(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_FUNCTION, _FUNCTION = 'function', 'Function'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRaster', 'Output raster layer'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, f'Raster layer to be processed band-wise.'),
            (self._FUNCTION, self.helpParameterCode()),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def displayName(self) -> str:
        raise NotImplementedError()

    def shortDescription(self) -> str:
        raise NotImplementedError()

    def code(self):
        raise NotImplementedError()

    def helpParameterCode(self) -> str:
        raise NotImplementedError()

    def group(self):
        raise NotImplementedError()

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterString(self.P_FUNCTION, self._FUNCTION, self.defaultCodeAsString(), True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def defaultCodeAsString(self):
        lines = [line for line in inspect.getsource(self.code).split('\n')
                 if not line.startswith('def') and line != ''][:-1]
        lines = '\n'.join([line[8:] for line in lines[1:]])
        return lines

    def parameterAsFunction(self, parameters: Dict[str, Any], name, context: QgsProcessingContext):
        namespace = dict()
        code = self.parameterAsString(parameters, name, context)
        exec(code, namespace)
        function = namespace['function']
        return function

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        function = self.parameterAsFunction(parameters, self.P_FUNCTION, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            feedback.pushInfo('Apply function')
            rasterReader = RasterReader(raster)
            writer = Driver(filename, format, options, feedback).createLike(rasterReader, Qgis.Float32)
            noDataValue = float(np.finfo(np.float32).min)
            for i in range(rasterReader.bandCount()):
                feedback.setProgress(i / rasterReader.bandCount() * 100)
                bandList = [i + 1]
                array = np.float32(rasterReader.array(bandList=bandList))
                mask = rasterReader.maskArray(array, bandList=bandList)
                outarray = function(array[0])[None]
                outarray[np.logical_not(mask)] = noDataValue
                writer.writeArray(outarray, bandList=bandList)

            writer.setMetadata(rasterReader.metadata())
            writer.setNoDataValue(noDataValue)
            for i in range(rasterReader.bandCount()):
                writer.setBandName(rasterReader.bandName(i + 1), i + 1)

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
