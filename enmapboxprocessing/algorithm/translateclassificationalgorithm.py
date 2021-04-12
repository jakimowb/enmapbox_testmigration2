from typing import Dict, Any, List, Tuple

from processing.core.Processing import Processing
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsRasterLayer)

from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class TranslateClassificationAlgorithm(EnMAPProcessingAlgorithm):
    P_CLASSIFICATION, _CLASSIFICATION = 'classification', 'Classification'
    P_GRID, _GRID = 'grid', 'Grid'
    P_MAJORITY_VOTING, _MAJORITY_VOTING = 'majorityVoting', 'Majority voting'
    P_OUTPUT_RASTER, _OUTPUT_RASTER = 'outputRaster', 'Output raster'

    def displayName(self):
        return 'Translate classification'

    def shortDescription(self):
        return 'Translates classification into target grid.' \
               '\nResampling is done by class majority voting at x10 oversampled resolution, using 100 classified ' \
               'subpixel to be accurate to the percent.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._CLASSIFICATION, self.helpParameterRasterClassification()),
            (self._GRID, self.helpParameterGrid()),
            (self._MAJORITY_VOTING, 'Whether to use majority voting. '
                                    'Turn off to use simple nearest neighbour resampling, which is much faster, '
                                    'but may result in highly inaccurate decisions.'),
            (self._OUTPUT_RASTER, self.helpParameterRasterDestination())
        ]

    def checkParameterValues(self, parameters: Dict[str, Any], context: QgsProcessingContext) -> Tuple[bool, str]:
        return self.checkParameterRasterClassification(parameters, self.P_CLASSIFICATION, context)

    def group(self):
        return Group.Test.value + Group.CreateRaster.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterRasterLayer(self.P_CLASSIFICATION, self._CLASSIFICATION)
        self.addParameterRasterLayer(self.P_GRID, self._GRID)
        self.addParameterBoolean(self.P_MAJORITY_VOTING, self._MAJORITY_VOTING, True, False, advanced=True)
        self.addParameterRasterDestination(self.P_OUTPUT_RASTER, self._OUTPUT_RASTER)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        classification = self.parameterAsRasterLayer(parameters, self.P_CLASSIFICATION, context)
        grid = self.parameterAsRasterLayer(parameters, self.P_GRID, context)
        majorityVoting = self.parameterAsBoolean(parameters, self.P_MAJORITY_VOTING, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_RASTER, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            isGridMatching = all([grid.crs() == classification.crs(),
                                  grid.extent() == classification.extent(),
                                  grid.width() == classification.width(),
                                  grid.height() == classification.height()])
            if isGridMatching or majorityVoting is False:
                # use simple nn-resampling
                alg = TranslateRasterAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_RASTER: classification,
                    alg.P_GRID: grid,
                    alg.P_RESAMPLE_ALG: self.NearestNeighbourResampleAlg,
                    alg.P_COPY_STYLE: True,
                    alg.P_CREATION_PROFILE: self.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: filename
                }
                Processing.runAlgorithm(alg, parameters, None, feedback2, context)
            else:
                # create oversampling grid
                alg = CreateGridAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_CRS: grid.crs(),
                    alg.P_EXTENT: grid.extent(),
                    alg.P_UNIT: alg.PixelUnits,
                    alg.P_WIDTH: grid.width() * 10,
                    alg.P_HEIGHT: grid.height() * 10,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'grid.x10.vrt')
                }
                result = Processing.runAlgorithm(alg, parameters, None, feedback2, context)
                oversamplingGrid = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])

                # translate into oversampling grid
                alg = TranslateRasterAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_RASTER: classification,
                    alg.P_GRID: oversamplingGrid,
                    alg.P_RESAMPLE_ALG: alg.NearestNeighbourResampleAlg,
                    alg.P_COPY_STYLE: True,
                    alg.P_CREATION_PROFILE: alg.VrtProfile,
                    alg.P_OUTPUT_RASTER: Utils.tmpFilename(filename, 'classification.x10.vrt')
                }
                result = Processing.runAlgorithm(alg, parameters, None, feedback2, context)
                oversamplingClassification = QgsRasterLayer(result[alg.P_OUTPUT_RASTER])

                # final majority voting
                alg = TranslateRasterAlgorithm()
                alg.initAlgorithm()
                parameters = {
                    alg.P_RASTER: oversamplingClassification,
                    alg.P_GRID: grid,
                    alg.P_RESAMPLE_ALG: alg.ModeResampleAlg,
                    alg.P_COPY_STYLE: True,
                    alg.P_CREATION_PROFILE: self.TiledAndCompressedGTiffProfile,
                    alg.P_OUTPUT_RASTER: filename
                }
                Processing.runAlgorithm(alg, parameters, None, feedback2, context)

            result = {self.P_OUTPUT_RASTER: filename}
            self.toc(feedback, result)
        return result
