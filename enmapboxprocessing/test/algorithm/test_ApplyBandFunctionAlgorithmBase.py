from enmapboxprocessing.algorithm.applybandfunctionalgorithmbase import ApplyBandFunctionAlgorithmBase
from enmapboxprocessing.algorithm.spatialmorphologicalbinaryclosingalgorithm import \
    SpatialMorphologicalBinaryClosingAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalbinarydilationalgorithm import \
    SpatialMorphologicalBinaryDilationAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalbinaryerosionalgorithm import \
    SpatialMorphologicalBinaryErosionAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalbinaryfillholesalgorithm import \
    SpatialMorphologicalBinaryFillHolesAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalbinaryopeningalgorithm import \
    SpatialMorphologicalBinaryOpeningAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalbinarypropagationalgorithm import \
    SpatialMorphologicalBinaryPropagationAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalblacktophatalgorithm import \
    SpatialMorphologicalBlackTophatAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalgradientalgorithm import SpatialMorphologicalGradientAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalgreydilationalgorithm import \
    SpatialMorphologicalGreyDilationAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalgreyerosionalgorithm import \
    SpatialMorphologicalGreyErosionAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalgreyopeningalgorithm import \
    SpatialMorphologicalGreyOpeningAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicallaplacealgorithm import SpatialMorphologicalLaplaceAlgorithm
from enmapboxprocessing.algorithm.spatialmorphologicalwhitetophatalgorithm import \
    SpatialMorphologicalWhiteTophatAlgorithm
from enmapboxprocessing.test.algorithm.testcase import TestCase
from enmapboxtestdata import hires

writeToDisk = True
c = ['', 'c:'][int(writeToDisk)]


class ApplyBandFunctionAlgorithm(ApplyBandFunctionAlgorithmBase):

    def displayName(self) -> str:
        return ''

    def shortDescription(self) -> str:
        return ''

    def helpParameterCode(self) -> str:
        return ''

    def group(self):
        return ''

    def code(self):
        def function(array):
            return array

        return function


class TestApplyBandFunctionAlgorithm(TestCase):

    def test(self):
        alg = ApplyBandFunctionAlgorithm()
        parameters = {
            alg.P_RASTER: hires,
            alg.P_FUNCTION: alg.defaultCodeAsString(),
            alg.P_OUTPUT_RASTER: 'c:/vsimem/result.tif',
        }
        self.runalg(alg, parameters)

    def test_bandFunctions(self):
        algs = [
            SpatialMorphologicalBinaryClosingAlgorithm(),
            SpatialMorphologicalBinaryDilationAlgorithm(),
            SpatialMorphologicalBinaryErosionAlgorithm(),
            SpatialMorphologicalBinaryFillHolesAlgorithm(),
            SpatialMorphologicalBinaryOpeningAlgorithm(),
            SpatialMorphologicalBinaryPropagationAlgorithm(),
            SpatialMorphologicalBlackTophatAlgorithm(),
            SpatialMorphologicalGradientAlgorithm(),
            SpatialMorphologicalGreyDilationAlgorithm(),
            SpatialMorphologicalGreyErosionAlgorithm(),
            SpatialMorphologicalGreyOpeningAlgorithm(),
            SpatialMorphologicalLaplaceAlgorithm(),
            SpatialMorphologicalWhiteTophatAlgorithm()
        ]
        for alg in algs:
            print(alg.displayName())
            alg.initAlgorithm()
            alg.shortHelpString()
            parameters = {
                alg.P_RASTER: hires,
                alg.P_FUNCTION: alg.defaultCodeAsString(),
                alg.P_OUTPUT_RASTER: 'c:/vsimem/result.tif',
            }
            self.runalg(alg, parameters)
