from enmapboxprocessing.algorithm.classificationperformancealgorithm import ClassificationPerformanceAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.colorizeclassprobabilityalgorithm import ColorizeClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.rasterizeclassificationalgorithm import RasterizeClassificationAlgorithm
from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.algorithm.randompointsinstratificationalgorithm import RandomPointsInStratificationAlgorithm
from enmapboxprocessing.algorithm.randompointsinmaskalgorithm import RandomPointsInMaskAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm


def algorithms():
    return [
        ClassificationPerformanceAlgorithm(),
        ClassificationToFractionAlgorithm(),
        ColorizeClassProbabilityAlgorithm(),
        CreateGridAlgorithm(),
        FitRandomForestClassifierAlgorithm(),
        PredictClassificationAlgorithm(),
        PredictClassPropabilityAlgorithm(),
        RandomPointsInMaskAlgorithm(),
        RandomPointsInStratificationAlgorithm(),
        RasterizeClassificationAlgorithm(),
        RasterizeVectorAlgorithm(),
        SampleRasterValuesAlgorithm(),
        TranslateClassificationAlgorithm(),
        TranslateRasterAlgorithm(),
    ]
