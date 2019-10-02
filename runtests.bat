
:: use this script to run unit tests locally
::
set CI=True
python make/setuprepository.py

mkdir test-reports\today
python -m nose2 -s enmapboxtesting test_applications & move nose2-junit.xml test-reports/today/test_applications.xml
python -m nose2 -s enmapboxtesting test_crosshair & move nose2-junit.xml test-reports/today/test_crosshair.xml
python -m nose2 -s enmapboxtesting test_cursorlocationsvalues & move nose2-junit.xml test-reports/today/test_cursorlocationsvalues.xml
python -m nose2 -s enmapboxtesting test_datasources & move nose2-junit.xml test-reports/today/test_datasources.xml
python -m nose2 -s enmapboxtesting test_docksanddatasources & move nose2-junit.xml test-reports/today/test_docksanddatasources.xml
python -m nose2 -s enmapboxtesting test_enmapbox & move nose2-junit.xml test-reports/today/test_enmapbox.xml
python -m nose2 -s enmapboxtesting test_enmapboxplugin & move nose2-junit.xml test-reports/today/test_enmapboxplugin.xml
python -m nose2 -s enmapboxtesting test_layerproperties & move nose2-junit.xml test-reports/today/test_layerproperties.xml
python -m nose2 -s enmapboxtesting test_mapcanvas & move nose2-junit.xml test-reports/today/test_mapcanvas.xml
python -m nose2 -s enmapboxtesting test_mimedata & move nose2-junit.xml test-reports/today/test_mimedata.xml
python -m nose2 -s enmapboxtesting test_options & move nose2-junit.xml test-reports/today/test_options.xml
python -m nose2 -s enmapboxtesting test_speclibs & move nose2-junit.xml test-reports/today/test_speclibs.xml
python -m nose2 -s enmapboxtesting test_spectralprofilesources & move nose2-junit.xml test-reports/today/test_spectralprofilesources.xml
python -m nose2 -s enmapboxtesting test_testdata_dependency & move nose2-junit.xml test-reports/today/test_testdata_dependency.xml
python -m nose2 -s enmapboxtesting test_testing & move nose2-junit.xml test-reports/today/test_testing.xml
python -m nose2 -s enmapboxtesting test_utils & move nose2-junit.xml test-reports/today/test_utils.xml