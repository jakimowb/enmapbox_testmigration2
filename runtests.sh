
# use this script to run unit tests locally
#
python runfirst.py

mkdir test-reports/today
python -m nose2 -s enmapboxtesting test_applications ; mv nose2-junit.xml test-reports/today/test_applications.xml
python -m nose2 -s enmapboxtesting test_crosshair ; mv nose2-junit.xml test-reports/today/test_crosshair.xml
python -m nose2 -s enmapboxtesting test_cursorlocationsvalues ; mv nose2-junit.xml test-reports/today/test_cursorlocationsvalues.xml
python -m nose2 -s enmapboxtesting test_datasources ; mv nose2-junit.xml test-reports/today/test_datasources.xml
python -m nose2 -s enmapboxtesting test_docksanddatasources ; mv nose2-junit.xml test-reports/today/test_docksanddatasources.xml
python -m nose2 -s enmapboxtesting test_enmapbox ; mv nose2-junit.xml test-reports/today/test_enmapbox.xml
python -m nose2 -s enmapboxtesting test_enmapboxplugin ; mv nose2-junit.xml test-reports/today/test_enmapboxplugin.xml
python -m nose2 -s enmapboxtesting test_layerproperties ; mv nose2-junit.xml test-reports/today/test_layerproperties.xml
python -m nose2 -s enmapboxtesting test_mapcanvas ; mv nose2-junit.xml test-reports/today/test_mapcanvas.xml
python -m nose2 -s enmapboxtesting test_mimedata ; mv nose2-junit.xml test-reports/today/test_mimedata.xml
python -m nose2 -s enmapboxtesting test_options ; mv nose2-junit.xml test-reports/today/test_options.xml
python -m nose2 -s enmapboxtesting test_speclibs ; mv nose2-junit.xml test-reports/today/test_speclibs.xml
python -m nose2 -s enmapboxtesting test_spectralprofilesources ; mv nose2-junit.xml test-reports/today/test_spectralprofilesources.xml
python -m nose2 -s enmapboxtesting test_testdata_dependency ; mv nose2-junit.xml test-reports/today/test_testdata_dependency.xml
python -m nose2 -s enmapboxtesting test_testing ; mv nose2-junit.xml test-reports/today/test_testing.xml
python -m nose2 -s enmapboxtesting test_utils ; mv nose2-junit.xml test-reports/today/test_utils.xml