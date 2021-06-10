from typing import Dict, Any, List, Tuple

import numpy as np
from osgeo import gdal
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer, QgsProcessing,
                        QgsProcessingException)

from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class RasterMathAlgorithm(EnMAPProcessingAlgorithm):
    P_RASTER_LIST, _RASTER_LIST = 'rasterList', 'Raster layers'
    P_EXPRESSION, _EXPRESSION = 'expression', 'Expression'
    P_GRID, _GRID = 'grid', 'Grid'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRaster', 'Output raster layer'

    def displayName(self) -> str:
        return 'Raster math'

    def shortDescription(self) -> str:
        return 'Create a raster layer by evaluating an expression with numpy syntax. ' \
               'Use any basic arithmetic and logical operators supported by numpy arrays. ' \
               'The numpy modul is imported as np.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._RASTER_LIST, 'List of raster layers that are mapped to variables A, B, C, ... .\n'
                                'Individual bands are mapped to variables A@1, A@2, ..., B@1, B@2, ... .'),
            (self._EXPRESSION, 'The expression to be evaluated. '
                               'Must result in a (multiband) 3d numpy array, a (single-band) 2d numpy array or a list of 2d numpy arrays.\n'
                               'Example 1 - add up two bands: <pre>A@1 + B@1</pre>\n'
                               'Example 2 - add up two rasters (with same number of bands) band-wise: <pre>A + B</pre>\n'
                               'Example 3 - use a numpy function to calculate the exponential of all values in a raster: <pre>np.exp(A)</pre>\n'
                               'Example 4 - build a band stack with all bands from three raster layers:'
                               '<pre>list(A) + list(B) + list(C)</pre>\n'
                               'More complex expressions can be splitted into multiple lines for defining temporary variables or import modules. '
                               'Here the last line is evaluated as the final result.\n'
                               'Example 5 - use a multiple line code block to calculate a vegetation index:'
                               '<pre>nir = np.float32(A@4)<br>red = np.float32(A@3)<br>ndvi = (nir - red) / (nir + red)<br>ndvi</pre>'),
            (self._GRID, 'The target grid. If not specified, the grid of the first raster layer is used.'),
            (self._OUTPUT_RASTER, self.RasterFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.RasterCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterMultipleLayers(self.P_RASTER_LIST, self._RASTER_LIST, QgsProcessing.TypeRaster)
        self.addParameterString(self.P_EXPRESSION, self._EXPRESSION, None, True)
        self.addParameterRasterLayer(self.P_GRID, self._GRID, optional=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        rasters = self.parameterAsLayerList(parameters, self.P_RASTER_LIST, context)
        expression = self.parameterAsString(parameters, self.P_EXPRESSION, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        if grid is None:
            grid = rasters[0]
        format, options = self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
        maximumMemoryUsage = gdal.GetCacheMax()

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # load data into variables
            namespace = dict()
            raster: QgsRasterLayer
            expression2 = expression
            tmp = expression
            for letter, raster in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', rasters):
                # resample to target grid
                alg = TranslateRasterAlgorithm()
                parameters = {
                    alg.P_RASTER: raster,
                    alg.P_GRID: grid,
                    alg.P_RESAMPLE_ALG: self.NearestNeighbourResampleAlg,
                    alg.P_CREATION_PROFILE: self.VrtProfile,
                    alg.P_OUTPUT_RASTER: '/vsimem/RasterMathAlgorithm.vrt'
                }
                result = self.runAlg(alg, parameters, None, feedback2, context, True)
                # read band data
                reader = RasterReader(result[alg.P_OUTPUT_RASTER])
                for band in reversed(range(1, raster.bandCount() + 1)):
                    aliasName = f'{letter}@{band}'
                    if aliasName in tmp:
                        name = f'{letter}_{band}'
                        tmp = tmp.replace(aliasName, '')
                        expression2 = expression2.replace(aliasName, name)
                        namespace[name] = reader.array(bandList=[band])[0]
                # read raster data
                if letter in tmp:
                    namespace[letter] = np.array(reader.array())

            namespace['np'] = np

            lines = expression2.split('\n')
            lines[-1] = '_result = ' + lines[-1]

            code = '\n'.join(lines)

            # execute all lines but the last
            exec(code, namespace)
            array = namespace['_result']
            if not isinstance(array, (list, np.ndarray)):
                raise QgsProcessingException('expression result is not valid')

            if isinstance(array, np.ndarray) and array.ndim == 2:
                array = array[None]

            driver = Driver(filename, format, options, feedback)
            driver.createFromArray(array, grid.extent(), grid.crs())

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)

        return result
