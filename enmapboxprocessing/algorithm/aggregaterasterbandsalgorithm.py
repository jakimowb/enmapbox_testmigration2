from collections import OrderedDict
from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer,
                        Qgis, QgsProcessingException, QgsMapLayer)

from enmapboxprocessing.algorithm.layertomaskalgorithm import LayerToMaskAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.typing import ClassifierDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class AggregateRasterBandsAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER, _RASTER = 'raster', 'Raster layer'
    P_FUNCTION, _FUNCTION = 'function', 'Aggregation function'
    FUNCTIONS = OrderedDict(
        mean=np.mean,
        std=np.std,
        min=np.min,
        p5=lambda array, axis: np.percentile(array, 5, axis),
        p25=lambda array, axis: np.percentile(array, 55, axis),
        median=np.median,
        p75=lambda array, axis: np.percentile(array, 75, axis),
        p95=lambda array, axis: np.percentile(array, 95, axis),
        max=np.max,
        sum=np.sum,
        product=np.product,
        range=np.ptp,  # The name of the function comes from the acronym for ‘peak to peak’.
        iqr=lambda array, axis: np.subtract(*np.percentile(array, [75, 25], axis)),
        any=np.any,
        all=np.all
    )
    (
        MeanFunction, StdFunction, MinFunction, P5Function, P25Function, MedianFunction, P75Function, P95Function,
        MaxFunction, SumFunction, ProductFunction, RangeFunction, IqrFunction, AnyFunction, AllFunction
    ) = range(len(FUNCTIONS))
    O_FUNCTION = FUNCTIONS.keys()
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRaster', 'Output raster layer'

    def displayName(self) -> str:
        return 'Aggregate raster layer bands'

    def shortDescription(self) -> str:
        return 'Aggregate raster layer bands.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER, 'A raster layer with bands to be aggregated.'),
            (self._FUNCTION, 'Functions to be used. Number of selected functions equals number of output bands.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_RASTER, self._RASTER)
        self.addParameterEnum(self.P_FUNCTION, self._FUNCTION, self.O_FUNCTION, True, [self.MeanFunction])
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        raster = self.parameterAsRasterLayer(parameters, self.P_RASTER, context)
        functions = self.parameterAsEnums(parameters, self.P_FUNCTION, context)
        format, options = self.GTiffFormat, self.DefaultGTiffCreationOptions
        filename = self.parameterAsOutputLayer(parameters, self.P_OUTPUT_RASTER, context)
        maximumMemoryUsage = gdal.GetCacheMax()

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            reader = RasterReader(raster)
            writer = Driver(filename, format, options, feedback).createLike(reader, Qgis.Float32, len(functions))
            noDataValue = Utils.defaultNoDataValue(np.float32)
            lineMemoryUsage = reader.lineMemoryUsage(reader.bandCount() + len(functions), 4)
            blockSizeY = min(raster.height(), ceil(maximumMemoryUsage / lineMemoryUsage))
            blockSizeX = raster.width()
            for block in reader.walkGrid(blockSizeX, blockSizeY, feedback):
                array = np.array(reader.arrayFromBlock(block), dtype=np.float32)
                invalid = ~np.all(reader.maskArray(array), axis=0)
                for bandNo, fi in enumerate(functions, 1):
                    funcName, func = list(self.FUNCTIONS.items())[fi]
                    outarray = func(array, axis=0)
                    outarray = np.array(outarray, dtype=np.float32)
                    outarray[invalid] = noDataValue
                    writer.writeArray2d(outarray, bandNo, xOffset=block.xOffset, yOffset=block.yOffset)

            for bandNo, fi in enumerate(functions, 1):
                funcName, func = list(self.FUNCTIONS.items())[fi]
                writer.setBandName(funcName, bandNo)

            writer.setNoDataValue(noDataValue)

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
