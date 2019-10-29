
# use this script to run unit tests locally

mkdir test-reports/today
python -m nose2 -s enmapboxtesting test_applications
python -m nose2 -s enmapboxtesting test_crosshair
python -m nose2 -s enmapboxtesting test_cursorlocationsvalues
python -m nose2 -s enmapboxtesting test_datasources
python -m nose2 -s enmapboxtesting test_docksanddatasources
python -m nose2 -s enmapboxtesting test_enmapboxplugin
python -m nose2 -s enmapboxtesting test_layerproperties
python -m nose2 -s enmapboxtesting test_mapcanvas
python -m nose2 -s enmapboxtesting test_mimedata
python -m nose2 -s enmapboxtesting test_options
python -m nose2 -s enmapboxtesting test_speclibs
python -m nose2 -s enmapboxtesting test_spectralprofilesources
python -m nose2 -s enmapboxtesting test_testdata_dependency
python -m nose2 -s enmapboxtesting test_testing
python -m nose2 -s enmapboxtesting test_utils