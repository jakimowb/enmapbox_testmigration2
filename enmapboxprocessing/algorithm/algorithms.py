from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.classifierfeaturerankingpermutationimportancealgorithm import \
    ClassifierFeatureRankingPermutationImportanceAlgorithm
from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.creategridalgorithm import CreateGridAlgorithm
from enmapboxprocessing.algorithm.creatergbimagefromclassprobabilityalgorithm import \
    CreateRgbImageFromClassProbabilityAlgorithm
from enmapboxprocessing.algorithm.featureclusteringhierarchicalalgorithm import FeatureClusteringHierarchicalAlgorithm
from enmapboxprocessing.algorithm.fitgaussianprocessclassifier import FitGaussianProcessClassifierAlgorithm
from enmapboxprocessing.algorithm.fitgenericclassifier import FitGenericClassifier
from enmapboxprocessing.algorithm.fitlinearsvcalgorithm import FitLinearSvcAlgorithm
from enmapboxprocessing.algorithm.fitlogisticregressionralgorithm import FitLogisticRegressionAlgorithm
from enmapboxprocessing.algorithm.fitrandomforestclassifieralgorithm import FitRandomForestClassifierAlgorithm
from enmapboxprocessing.algorithm.fitsvcalgorithm import FitSvcAlgorithm
from enmapboxprocessing.algorithm.predictclassificationalgorithm import PredictClassificationAlgorithm
from enmapboxprocessing.algorithm.predictclassprobabilityalgorithm import PredictClassPropabilityAlgorithm
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedlibrary import \
    PrepareClassificationDatasetFromCategorizedLibrary
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedraster import \
    PrepareClassificationDatasetFromCategorizedRaster
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvector import \
    PrepareClassificationDatasetFromCategorizedVector
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedvectorandfields import \
    PrepareClassificationDatasetFromCategorizedVectorAndFields
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromfiles import PrepareClassificationDatasetFromFiles
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromtable import PrepareClassificationDatasetFromTable
from enmapboxprocessing.algorithm.randompointsfromcategorizedrasteralgorithm import \
    RandomPointsFromCategorizedRasterAlgorithm
from enmapboxprocessing.algorithm.randompointsfrommaskrasteralgorithm import RandomPointsFromMaskRasterAlgorithm
from enmapboxprocessing.algorithm.randomsamplesfromclassificationdatasetalgorithm import \
    RandomSamplesFromClassificationDatasetAlgorithm
from enmapboxprocessing.algorithm.rasterizevectoralgorithm import RasterizeVectorAlgorithm
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.algorithm.selectfeaturesfromdatasetalgorithm import SelectFeaturesFromDatasetAlgorithm
from enmapboxprocessing.algorithm.translatecategorizedrasteralgorithm import TranslateCategorizedRasterAlgorithm
from enmapboxprocessing.algorithm.translaterasteralgorithm import TranslateRasterAlgorithm
from enmapboxprocessing.algorithm.rasterizecategorizedvectoralgorithm import RasterizeCategorizedVectorAlgorithm


def algorithms():
    return [
        ClassificationPerformanceSimpleAlgorithm(),
        ClassificationPerformanceStratifiedAlgorithm(),
        ClassificationToFractionAlgorithm(),
        ClassifierPerformanceAlgorithm(),
        ClassifierFeatureRankingPermutationImportanceAlgorithm(),
        CreateGridAlgorithm(),
        CreateRgbImageFromClassProbabilityAlgorithm(),
        FitGaussianProcessClassifierAlgorithm(),
        FitGenericClassifier(),
        FitLinearSvcAlgorithm(),
        FitLogisticRegressionAlgorithm(),
        FitRandomForestClassifierAlgorithm(),
        FitSvcAlgorithm(),
        FeatureClusteringHierarchicalAlgorithm(),
        PredictClassificationAlgorithm(),
        PredictClassPropabilityAlgorithm(),
        PrepareClassificationDatasetFromFiles(),
        PrepareClassificationDatasetFromCategorizedRaster(),
        PrepareClassificationDatasetFromCategorizedVector(),
        PrepareClassificationDatasetFromTable(),
        PrepareClassificationDatasetFromCategorizedVectorAndFields(),
        PrepareClassificationDatasetFromCategorizedLibrary(),
        RandomPointsFromMaskRasterAlgorithm(),
        RandomPointsFromCategorizedRasterAlgorithm(),
        RandomSamplesFromClassificationDatasetAlgorithm(),
        RasterizeCategorizedVectorAlgorithm(),
        RasterizeVectorAlgorithm(),
        SampleRasterValuesAlgorithm(),
        SelectFeaturesFromDatasetAlgorithm(),
        TranslateCategorizedRasterAlgorithm(),
        TranslateRasterAlgorithm()
    ]
