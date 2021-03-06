#!/bin/bash
QT_QPA_PLATFORM=offscreen
export QT_QPA_PLATFORM
CI=True
export CI

find . -name "*.pyc" -exec rm -f {} \;
export PYTHONPATH="${PYTHONPATH}:$(pwd):/usr/share/qgis/python/plugins"
# python3 scripts/setup_repository.py

python3 -m coverage run --rcfile=.coveragec   tests/src/coreapps/test_enmapboxapplications.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_imagecube.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_metadataeditorapp.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_reclassifyapp.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_vrtbuilderapp.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_478.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_711.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_724.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_747.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_enpt_enmapboxapp.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_ensomap.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_lmuvegetationapps.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_applications.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_crosshair.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_cursorlocationsvalues.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_datasources.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_datasourcesV2.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_dependencycheck.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_docksanddatasources.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapbox.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapboxplugin.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapboxprocessingprovider.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_hiddenqgislayers.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_mapcanvas.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_mimedata.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_options.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_repo.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_settings.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_speclibs.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_splashscreen.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_template.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_testdata_dependency.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_testing.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_utils.py
python3 -m coverage run --rcfile=.coveragec --append  tests/src/test_vectorlayertools.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_AppendEnviHeaderToGTiffRasterAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ApplyMaskAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ClassificationPerformanceSimpleAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ClassificationPerformanceStratifiedAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ClassificationToFractionAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ClassifierPerformanceAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ClassifierPermutationFeatureImportanceAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ConvolutionFilterAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_CreateDefaultPalettedRasterRendererAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_CreateGridAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_CreateMaskAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_CreateRgbImageFromClassProbabilityAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_FeatureClusteringHierarchicalAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_FitClassifierAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_GeolocateRasterAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportDesisL1BAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportDesisL1CAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportDesisL2AAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportEnmapL1BAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportEnmapL1CAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportEnmapL2AAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportLandsatL2Algorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportPrismaL1Algorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportPrismaL2DAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_ImportSentinel2L2AAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_LayerToMaskAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PredictClassificationAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PredictClassProbabilityAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromCategorizedLibraryAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromCategorizedRasterAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromCategorizedVectorAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromCategorizedVectorAndFieldsAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromCodeAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromFilesAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareClassificationDatasetFromTableAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_PrepareRegressionSampleFromCsvAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_RandomPointsInMaskAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_RandomPointsInStratificationAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_RasterizeCategorizedVectorAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_RasterizeVectorAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_RasterMathAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SampleRasterValuesAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SaveRasterAsAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SelectFeaturesFromDatasetAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SpatialFilterFunctionAlgorithmBase.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SpectralResamplingByResponseFunctionConvolutionAlgorithmBase.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SpectralResamplingByResponseFunctionLibraryAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SpectralResamplingBySpectralRasterWavelengthAndFwhmAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SubsampleClassificationSampleAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_SynthMixAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_TranslateClassificationAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/algorithm/test_TranslateRasterAlgorithm.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_extentwalker.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_glossary.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_gridwalker.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_rasterdriver.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_rastermetadataeditor.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_rasterprocessing.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_rasterreader.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_reportwriter.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxprocessing/test/test_utils.py
python3 -m coverage report