
:: use this script to run unit tests locally
::

@echo off
set CI=True
set PYTHONPATH=%~dp0;%PYTHONPATH%
set PYTHONPATH

WHERE python3 >nul 2>&1 && (
    echo Found "python3" command
    set PYTHON=python3
) || (
    echo Did not found "python3" command. use "python" instead
    set PYTHON=python
)

start %PYTHON% runfirst.py

mkdir test-reports
mkdir test-reports\today
pytest -p no:faulthandler -x tests/speclib/test_speclib_core.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_gui.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_gui_processing.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io_asd.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io_ecosys.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io_envi.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io_geopackage.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_io_rastersources.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_plotting.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_profilesources.py
pytest -p no:faulthandler -x tests/speclib/test_speclib_rasterdataprovider.py
pytest -p no:faulthandler -x tests/test_classificationscheme.py
pytest -p no:faulthandler -x tests/test_crosshair.py
pytest -p no:faulthandler -x tests/test_cursorlocationsvalues.py
pytest -p no:faulthandler -x tests/test_example.py
pytest -p no:faulthandler -x tests/test_init.py
pytest -p no:faulthandler -x tests/test_layerconfigwidgets.py
pytest -p no:faulthandler -x tests/test_layerproperties.py
pytest -p no:faulthandler -x tests/test_maptools.py
pytest -p no:faulthandler -x tests/test_models.py
pytest -p no:faulthandler -x tests/test_plotstyling.py
pytest -p no:faulthandler -x tests/test_processing.py
pytest -p no:faulthandler -x tests/test_qgsfunctions.py
pytest -p no:faulthandler -x tests/test_qps.py
pytest -p no:faulthandler -x tests/test_resources.py
pytest -p no:faulthandler -x tests/test_searchfiledialog.py
pytest -p no:faulthandler -x tests/test_simplewidget.py
pytest -p no:faulthandler -x tests/test_subdatasets.py
pytest -p no:faulthandler -x tests/test_testing.py
pytest -p no:faulthandler -x tests/test_utils.py
pytest -p no:faulthandler -x tests/test_vectorlayertools.py