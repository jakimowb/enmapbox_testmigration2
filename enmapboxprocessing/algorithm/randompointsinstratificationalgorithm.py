from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np
import processing

from enmapboxprocessing.driver import Driver
from typeguard import typechecked
from qgis._core import QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils


@typechecked
class RandomPointsInStratificationAlgorithm(EnMAPProcessingAlgorithm):
    P_STRATIFICATION = 'stratification'
    P_N = 'n'
    P_DISTANCE_GLOBAL = 'distanceGlobal'
    P_DISTANCE_STRATUM = 'distanceStatum'
    P_SEED = 'seed'
    P_OUTPUT_VECTOR = 'outVector'

    @classmethod
    def displayName(cls) -> str:
        return 'Random points in (categorized) raster'

    def shortDescription(self) -> str:
        return 'This algorithm creates a new point layer with a given number of random points, ' \
               'all of them within the categories of the given raster.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_STRATIFICATION, self.helpParameterRasterClassification()),
            (self.P_N, 'Number of points to be drawn from each category. '
                       'Set a single value N to draw N points for each category. '
                       'Set a comma separated list of values N1, N2, ... Ni, ... to draw Ni points for category i.'),
            (self.P_DISTANCE_GLOBAL,
             'A minimum distance between points can be specified. A point will not be added if there is an already '
             'generated point within this (Euclidean) distance from the generated location.'),
            (self.P_DISTANCE_STRATUM,
             'A minimum distance between points in a category can be specified. '
             'A point will not be added for a category if there is an already generated point in that category within '
             'this (Euclidean) distance from the generated location.'),
            (self.P_SEED, 'The seed for the random generator can be provided.'),
            (self.P_OUTPUT_VECTOR, self.helpParameterVectorDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateVector.value

    def checkN(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        stratification = self.parameterAsRasterLayer(parameters, self.P_STRATIFICATION, context)
        categories = Utils.categoriesFromPalettedRasterRenderer(stratification.renderer())
        n = self.parameterAsInts(parameters, self.P_N, context)
        if n is None:
            return False, 'Not a valid integer or list of integers: Number of points per category'
        if len(n) > 1 and len(categories) != len(n):
            return False, f'Number of categories ({len(categories)}) not matching length of list: ' \
                          f'Number of points per category'
        return True, ''

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        valid, message = self.checkParameterRasterClassification(parameters, self.P_STRATIFICATION, context)
        if not valid:
            return valid, message
        valid, message = self.checkN(parameters, context)
        if not valid:
            return valid, message
        return True, ''

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_STRATIFICATION, 'Categories')
        self.addParameterString(self.P_N, 'Number of points per category')
        self.addParameterInt(self.P_DISTANCE_GLOBAL, 'Minimum distance between points (in meters)', 0, False, 0)
        self.addParameterInt(
            self.P_DISTANCE_STRATUM, 'Minimum distance between points inside category (in meters)', 0, False, 0)
        self.addParameterInt(self.P_SEED, 'Random seed', None, True, 1)
        self.addParameterVectorDestination(self.P_OUTPUT_VECTOR, 'Output points')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        stratification = self.parameterAsRasterLayer(parameters, self.P_STRATIFICATION, context)
        N = self.parameterAsInts(parameters, self.P_N, context)
        distanceGlobal = self.parameterAsInt(parameters, self.P_DISTANCE_GLOBAL, context)
        distanceStratum = self.parameterAsInt(parameters, self.P_DISTANCE_STRATUM, context)
        seed = self.parameterAsInt(parameters, self.P_SEED, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_VECTOR, context)
        categories = Utils.categoriesFromPalettedRasterRenderer(stratification.renderer())
        if len(N) == 1:
            N = N * len(categories)

        if seed is not None:
            np.random.seed(seed)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            xres = stratification.rasterUnitsPerPixelX()
            yres = stratification.rasterUnitsPerPixelY()
            kernelGlobal = self.makeKernel(xres, yres, distanceGlobal)
            kernelStratum = self.makeKernel(xres, yres, distanceStratum)
            kernelGlobalY1, kernelGlobalX1 = [-(v - 1) // 2 for v in kernelGlobal.shape]
            kernelGlobalY2, kernelGlobalX2 = [(v + 1) // 2 for v in kernelGlobal.shape]
            kernelStratumY1, kernelStratumX1 = [-(v - 1) // 2 for v in kernelStratum.shape]
            kernelStratumY2, kernelStratumX2 = [(v + 1) // 2 for v in kernelStratum.shape]

            # create a binary mask for each strata (add extra border for convinient kernel masking)
            xsize = stratification.width()
            ysize = stratification.height()
            yborder1, xborder1 = [(v - 1) // 2 for v in kernelGlobal.shape]
            yborder2, xborder2 = [(v - 1) // 2 for v in kernelStratum.shape]
            yborder, xborder = max(yborder1, yborder2), max(xborder1, xborder2)
            noData = min(-9999, np.min([c.value for c in categories]) - 1)
            arrayStrata = np.full((ysize + 2 * yborder, xsize + 2 * xborder), noData)
            arrayStrata[yborder: yborder + ysize, xborder: xborder + xsize] = \
            RasterReader(stratification).array(bandList=[stratification.renderer().band()])[0]
            ysize2, xsize2 = arrayStrata.shape

            masks = list()
            for category in categories:
                mask = (arrayStrata == category.value).astype(np.uint8)
                masks.append(mask)
            arrayStrata[:] = noData

            # draw points
            # - for each strata
            for mask, n, category in zip(masks, N, categories):
                for i in range(n):
                    # - draw single pixel
                    indices = np.where(mask.flat)[0]
                    if len(indices) == 0:
                        feedback.pushInfo(
                            f"Could only draw {i + 1} points ({n} requested) for category '{category.name}'."
                        )
                        break  # no pixel left
                    if len(indices) == 1:
                        index = indices[0]
                    else:
                        index = indices[np.random.randint(0, len(indices) - 1, 1)[0]]
                    x = index % xsize2
                    y = index // xsize2

                    # save point
                    arrayStrata[y, x] = category.value

                    # apply mask kernel
                    mask[y + kernelStratumY1:y + kernelStratumY2,
                    x + kernelStratumX1:x + kernelStratumX2] *= kernelStratum
                    for m in masks:
                        m[y + kernelGlobalY1:y + kernelGlobalY2, x + kernelGlobalX1:x + kernelGlobalX2] *= kernelGlobal

            # cut off border and store as raster
            arrayStrata = [arrayStrata[yborder: yborder + ysize, xborder: xborder + xsize]]
            driver = Driver(Utils.tmpFilename(
                filename, 'sample.tif'), self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions
            )
            writer = driver.createFromArray(arrayStrata, stratification.extent(), stratification.crs())
            writer.setNoDataValue(noData)
            writer.close()

            # store as point vector
            # create sample locations with cover > 0%
            parameters = {
                'FIELD_NAME': 'CATEGORY',
                'INPUT_RASTER': writer.source(),
                'OUTPUT': filename,
                'RASTER_BAND': 1
            }
            processing.run('native:pixelstopoints', parameters, None, feedback2, context, True)
            result = {self.P_OUTPUT_VECTOR: filename}
            self.toc(feedback, result)
        return result


    @classmethod
    def makeKernel(cls, xres: float, yres: float, radius: float) -> np.ndarray:
        nx = ceil((radius - xres / 2) / xres) * 2 + 1
        ny = ceil((radius - yres / 2) / yres) * 2 + 1
        kernel = np.ones((ny, nx), dtype=np.uint8)

        for yi, y in enumerate(np.linspace(- (ny // 2) * yres, (ny // 2) * yres, ny)):
            for xi, x in enumerate(np.linspace(- (nx // 2) * xres, (nx // 2) * xres, nx)):
                kernel[yi, xi] = (x ** 2 + y ** 2) ** 0.5 > radius

        return kernel.astype(np.uint8)
