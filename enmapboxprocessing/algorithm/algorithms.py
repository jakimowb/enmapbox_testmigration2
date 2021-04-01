from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.classifierpermutationfeatureimportancealgorithm import \
    ClassifierPermutationFeatureImportanceAlgorithm
from enmapboxprocessing.algorithm.colorizeclassprobabilityalgorithm import ColorizeClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.algorithm.hierarchicalfeatureclusteringalgorithm import HierarchicalFeatureClusteringAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationsamplefromcsv import PrepareClassificationSampleFromCsv
from enmapboxprocessing.algorithm.prepareclassificationsamplefrommapandraster import \
    PrepareClassificationSampleFromMapAndRaster
from enmapboxprocessing.algorithm.prepareclassificationsamplefromtable import PrepareClassificationSampleFromTable
from enmapboxprocessing.algorithm.prepareclassificationsamplefromvectorandfields import \
    PrepareClassificationSampleFromVectorAndFields
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
        ClassifierPerformanceAlgorithm(),
        ClassifierPermutationFeatureImportanceAlgorithm(),
        ColorizeClassProbabilityAlgorithm(),
        CreateGridAlgorithm(),
        FitGaussianProcessClassifierAlgorithm(),
        FitLinearSvcAlgorithm(),
        FitRandomForestClassifierAlgorithm(),
        FitSvcAlgorithm(),
        HierarchicalFeatureClusteringAlgorithm(),
        PredictClassificationAlgorithm(),
        PredictClassPropabilityAlgorithm(),
        PrepareClassificationSampleFromCsv(),
        PrepareClassificationSampleFromMapAndRaster(),
        PrepareClassificationSampleFromTable(),
        PrepareClassificationSampleFromVectorAndFields(),
        RandomPointsInMaskAlgorithm(),
        RandomPointsInStratificationAlgorithm(),
        VectorToClassificationAlgorithm(),
        RasterizeVectorAlgorithm(),
        SampleRasterValuesAlgorithm(),
        TranslateClassificationAlgorithm(),
        TranslateRasterAlgorithm(),
    ]
