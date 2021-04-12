from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.classifierfeaturerankingpermutationimportancealgorithm import \
    ClassifierFeatureRankingPermutationImportanceAlgorithm
from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.colorizeclassprobabilityalgorithm import ColorizeClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.featureclusteringhierarchicalalgorithm import FeatureClusteringHierarchicalAlgorithm
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitgenericclassifier import FitGenericClassifier
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitlogisticregressionralgorithm import FitLogisticRegressionAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationsamplefromcsv import PrepareClassificationSampleFromCsv
from enmapboxprocessing.algorithm.prepareclassificationsamplefrommapandraster import \
    PrepareClassificationSampleFromMapAndRaster
from enmapboxprocessing.algorithm.prepareclassificationsamplefromtable import PrepareClassificationSampleFromTable
from enmapboxprocessing.algorithm.prepareclassificationsamplefromvectorandfields import \
    PrepareClassificationSampleFromVectorAndFields
from enmapboxprocessing.algorithm.randompointsinmaskalgorithm import RandomPointsInMaskAlgorithm
from enmapboxprocessing.algorithm.randompointsinstratificationalgorithm import RandomPointsInStratificationAlgorithm
from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.algorithm.selectfeaturesubsetfromsamplealgorithm import SelectFeatureSubsetFromSampleAlgorithm
from enmapboxprocessing.algorithm.subsampleclassificationsamplealgorithm import SubsampleClassificationSampleAlgorithm
from enmapboxprocessing.algorithm.translateclassificationalgorithm import TranslateClassificationAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.algorithm.vectortoclassificationalgorithm import VectorToClassificationAlgorithm


def algorithms():
    return [
        ClassificationPerformanceSimpleAlgorithm(),
        ClassificationPerformanceStratifiedAlgorithm(),
        ClassificationToFractionAlgorithm(),
        ClassifierPerformanceAlgorithm(),
        ClassifierFeatureRankingPermutationImportanceAlgorithm(),
        ColorizeClassProbabilityAlgorithm(),
        CreateGridAlgorithm(),
        FitGaussianProcessClassifierAlgorithm(),
        FitGenericClassifier(),
        FitLinearSvcAlgorithm(),
        FitLogisticRegressionAlgorithm(),
        FitRandomForestClassifierAlgorithm(),
        FitSvcAlgorithm(),
        FeatureClusteringHierarchicalAlgorithm(),
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
        SelectFeatureSubsetFromSampleAlgorithm(),
        SubsampleClassificationSampleAlgorithm(),
        TranslateClassificationAlgorithm(),
        TranslateRasterAlgorithm(),
    ]
