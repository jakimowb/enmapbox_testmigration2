from math import ceil
from typing import Dict, Any, List, Tuple

import numpy as np

from enmapboxprocessing.algorithm.randompointsinstratificationalgorithm import RandomPointsInStratificationAlgorithm
from enmapboxprocessing.driver import Driver
from enmapboxprocessing.typing import Category
from typeguard import typechecked
from qgis._core import QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer

from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils


@typechecked
class RandomPointsInMaskAlgorithm(EnMAPProcessingAlgorithm):
    P_MASK = 'mask'
    P_N = 'n'
    P_DISTANCE = 'distance'
    P_SEED = 'seed'
    P_OUTPUT_VECTOR = 'outVector'

    @classmethod
    def displayName(cls) -> str:
        return 'Random points in raster'

    def shortDescription(self) -> str:
        return 'This algorithm creates a new point layer with a given number of random points, ' \
               'all of them in the area where the given mask raster evaluates to true.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self.P_MASK, self.helpParameterRasterMask()),
            (self.P_N, 'Number of points to be drawn.'),
            (self.P_DISTANCE,
             'A minimum distance between points can be specified. A point will not be added if there is an already '
             'generated point within this (Euclidean) distance from the generated location.'),
            (self.P_SEED, 'The seed for the random generator can be provided.'),
            (self.P_OUTPUT_VECTOR, self.helpParameterVectorDestination())
        ]

    def group(self):
        return Group.Test.value + Group.CreateVector.value

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return True, ''

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_MASK, 'Mask')
        self.addParameterInt(self.P_N, 'Number of points', None, False, 1)
        self.addParameterInt(self.P_DISTANCE, 'Minimum distance between points (in meters)', 0, False, 0)
        self.addParameterInt(self.P_SEED, 'Random seed', None, True, 1)
        self.addParameterVectorDestination(self.P_OUTPUT_VECTOR, 'Output points')

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        mask = self.parameterAsRasterLayer(parameters, self.P_MASK, context)
        N = self.parameterAsInts(parameters, self.P_N, context)
        distance = self.parameterAsInt(parameters, self.P_DISTANCE, context)
        seed = self.parameterAsInt(parameters, self.P_SEED, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_VECTOR, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # create explicit binary mask and style as classification
            bandList = [mask.renderer().usesBands()[0]]
            reader = RasterReader(mask)
            array = reader.array(bandList=bandList)
            marray = reader.maskArray(array, bandList=bandList, defaultNoDataValue=0.)
            driver = Driver(
                Utils.tmpFilename(filename, 'mask.tif'), self.GTiffFormat, self.TiledAndCompressedGTiffCreationOptions,
                feedback
            )
            writer = driver.createFromArray(marray, mask.extent(), mask.crs())
            writer.close()
            stratification = QgsRasterLayer(writer.source())
            categories = [Category(1, 'mask', color='#FF0000')]
            renderer = Utils.palettedRasterRendererFromCategories(stratification.dataProvider(), 1, categories)
            stratification.setRenderer(renderer)
            stratification.saveDefaultStyle()

            # draw ponts
            alg =  RandomPointsInStratificationAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_STRATIFICATION: stratification,
                alg.P_N: N,
                alg.P_DISTANCE_GLOBAL: distance,
                alg.P_SEED: seed,
                alg.P_OUTPUT_VECTOR: filename,
            }
            self.runAlg(alg, parameters, None, feedback2, context, True)
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
