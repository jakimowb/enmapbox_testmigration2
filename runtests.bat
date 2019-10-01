
::mkdir test-reports
set CI=True
@echo off
call :sub >test-report.txt
exit /b

:sub

python -m make/setuprepository
:: python -m nose2 --verbose discover enmapboxtesting "test_*.py"
python -m nose2 -s enmapboxtesting test_applications
python -m nose2 -s enmapboxtesting test_crosshair
python -m nose2 -s enmapboxtesting test_cursorlocationsvalues
python -m nose2 -s enmapboxtesting test_datasources
python -m nose2 -s enmapboxtesting test_docksanddatasources
python -m nose2 -s enmapboxtesting test_enmapbox
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