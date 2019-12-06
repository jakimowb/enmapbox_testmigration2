
# use this script to run unit tests locally
#
python3 make/setuprepository.py

mkdir test-reports/today
python3 -m nose2 -s enmapboxtesting test_applications | mv nose2-junit.xml test-reports/today/test_applications.xml
python3 -m nose2 -s enmapboxtesting test_crosshair | mv nose2-junit.xml test-reports/today/test_crosshair.xml
python3 -m nose2 -s enmapboxtesting test_cursorlocationsvalues | mv nose2-junit.xml test-reports/today/test_cursorlocationsvalues.xml
python3 -m nose2 -s enmapboxtesting test_datasources | mv nose2-junit.xml test-reports/today/test_datasources.xml
python3 -m nose2 -s enmapboxtesting test_dependencycheck | mv nose2-junit.xml test-reports/today/test_dependencycheck.xml
python3 -m nose2 -s enmapboxtesting test_docksanddatasources | mv nose2-junit.xml test-reports/today/test_docksanddatasources.xml
python3 -m nose2 -s enmapboxtesting test_enmapbox | mv nose2-junit.xml test-reports/today/test_enmapbox.xml
python3 -m nose2 -s enmapboxtesting test_enmapboxplugin | mv nose2-junit.xml test-reports/today/test_enmapboxplugin.xml
python3 -m nose2 -s enmapboxtesting test_hiddenqgislayers | mv nose2-junit.xml test-reports/today/test_hiddenqgislayers.xml
python3 -m nose2 -s enmapboxtesting test_layerproperties | mv nose2-junit.xml test-reports/today/test_layerproperties.xml
python3 -m nose2 -s enmapboxtesting test_mapcanvas | mv nose2-junit.xml test-reports/today/test_mapcanvas.xml
python3 -m nose2 -s enmapboxtesting test_mimedata | mv nose2-junit.xml test-reports/today/test_mimedata.xml
python3 -m nose2 -s enmapboxtesting test_options | mv nose2-junit.xml test-reports/today/test_options.xml
python3 -m nose2 -s enmapboxtesting test_speclibs | mv nose2-junit.xml test-reports/today/test_speclibs.xml
python3 -m nose2 -s enmapboxtesting test_spectralprofilesources | mv nose2-junit.xml test-reports/today/test_spectralprofilesources.xml
python3 -m nose2 -s enmapboxtesting test_testdata_dependency | mv nose2-junit.xml test-reports/today/test_testdata_dependency.xml
python3 -m nose2 -s enmapboxtesting test_testing | mv nose2-junit.xml test-reports/today/test_testing.xml
python3 -m nose2 -s enmapboxtesting test_utils | mv nose2-junit.xml test-reports/today/test_utils.xml