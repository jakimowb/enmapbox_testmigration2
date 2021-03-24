from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.colorizeclassprobabilityalgorithm import ColorizeClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm
from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.algorithm.randompointsinstratificationalgorithm import RandomPointsInStratificationAlgorithm
from enmapboxprocessing.algorithm.randompointsinmaskalgorithm import RandomPointsInMaskAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm


def algorithms():
    return [
        ClassificationPerformanceSimpleAlgorithm(),
        ClassificationPerformanceStratifiedAlgorithm(),
        ClassificationToFractionAlgorithm(),
        ColorizeClassProbabilityAlgorithm(),
        CreateGridAlgorithm(),
        FitGaussianProcessClassifierAlgorithm(),
        FitLinearSvcAlgorithm(),
        FitRandomForestClassifierAlgorithm(),
        FitSvcAlgorithm(),
        PredictClassificationAlgorithm(),
        PredictClassPropabilityAlgorithm(),
        RandomPointsInMaskAlgorithm(),
        RandomPointsInStratificationAlgorithm(),
        VectorToClassificationAlgorithm(),
        RasterizeVectorAlgorithm(),
        SampleRasterValuesAlgorithm(),
        TranslateClassificationAlgorithm(),
        TranslateRasterAlgorithm(),
    ]
