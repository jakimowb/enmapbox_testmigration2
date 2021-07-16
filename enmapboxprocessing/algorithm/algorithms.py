from enmapboxprocessing.algorithm._experimental_customcolor import ExperimentalCustomColor
from enmapboxprocessing.algorithm.classificationperformancesimplealgorithm import \
    ClassificationPerformanceSimpleAlgorithm
from enmapboxprocessing.algorithm.classificationperformancestratifiedalgorithm import \
    ClassificationPerformanceStratifiedAlgorithm
from enmapboxprocessing.algorithm.classificationtofractionalgorithm import ClassificationToFractionAlgorithm
from enmapboxprocessing.algorithm.classifierfeaturerankingpermutationimportancealgorithm import \
    ClassifierFeatureRankingPermutationImportanceAlgorithm
from enmapboxprocessing.algorithm.classifierperformancealgorithm import ClassifierPerformanceAlgorithm
from enmapboxprocessing.algorithm.createdefaultpalettedrasterrendereralgorithm import \
    CreateDefaultPalettedRasterRendererAlgorithm
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
from enmapboxprocessing.algorithm.rastermathalgorithm import RasterMathAlgorithm
from enmapboxprocessing.algorithm.samplerastervaluesalgorithm import SampleRasterValuesAlgorithm
from enmapboxprocessing.algorithm.selectfeaturesfromdatasetalgorithm import SelectFeaturesFromDatasetAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionairydisk2dalgorithm import SpatialConvolutionAiryDisk2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionbox2dalgorithm import SpatialConvolutionBox2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutioncustom2dalgorithm import SpatialConvolutionCustom2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutiongaussian2dalgorithm import SpatialConvolutionGaussian2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionmoffat2dalgorithm import SpatialConvolutionMoffat2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionrickerwavelet2dalgorithm import \
    SpatialConvolutionRickerWavelet2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionring2dalgorithm import SpatialConvolutionRing2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutionsavitskygolay2dalgorithm import \
    SpatialConvolutionSavitskyGolay2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutiontophat2dalgorithm import SpatialConvolutionTophat2DAlgorithm
from enmapboxprocessing.algorithm.spatialconvolutiontrapezoiddisk2dalgorithm import \
    SpatialConvolutionTrapezoidDisk2DAlgorithm
from enmapboxprocessing.algorithm.spectralconvolutionbox1dalgorithm import SpectralConvolutionBox1DAlgorithm
from enmapboxprocessing.algorithm.spectralconvolutiongaussian1dalgorithm import SpectralConvolutionGaussian1DAlgorithm
from enmapboxprocessing.algorithm.spectralconvolutionrickerwavelet1dalgorithm import \
    SpectralConvolutionRickerWavelet1DAlgorithm
from enmapboxprocessing.algorithm.spectralconvolutionsavitskygolay1dalgorithm import \
    SpectralConvolutionSavitskyGolay1DAlgorithm
from enmapboxprocessing.algorithm.spectralconvolutiontrapezoid1dalgorithm import SpectralConvolutionTrapezoid1DAlgorithm
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
        CreateDefaultPalettedRasterRendererAlgorithm(),
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
        RasterMathAlgorithm(),
        SampleRasterValuesAlgorithm(),
        SelectFeaturesFromDatasetAlgorithm(),
        SpatialConvolutionAiryDisk2DAlgorithm(),
        SpatialConvolutionBox2DAlgorithm(),
        SpatialConvolutionCustom2DAlgorithm(),
        SpatialConvolutionGaussian2DAlgorithm(),
        SpatialConvolutionMoffat2DAlgorithm(),
        SpatialConvolutionRickerWavelet2DAlgorithm(),
        SpatialConvolutionRing2DAlgorithm(),
        SpatialConvolutionSavitskyGolay2DAlgorithm(),
        SpatialConvolutionTophat2DAlgorithm(),
        SpatialConvolutionTrapezoidDisk2DAlgorithm(),
        SpectralConvolutionBox1DAlgorithm(),
        SpectralConvolutionGaussian1DAlgorithm(),
        SpectralConvolutionRickerWavelet1DAlgorithm(),
        SpectralConvolutionSavitskyGolay1DAlgorithm(),
        SpectralConvolutionTrapezoid1DAlgorithm(),
        TranslateCategorizedRasterAlgorithm(),
        TranslateRasterAlgorithm(),
        # ExperimentalCustomColor()
    ]

