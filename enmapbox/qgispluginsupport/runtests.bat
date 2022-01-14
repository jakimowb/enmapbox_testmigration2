
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
%PYTHON% -m coverage run --rcfile=.coveragec   tests/test_cursorlocationsvalues.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_qps.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_models.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_plotstyling.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_qgisissues.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_utils.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_layerconfigwidgets.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_crosshair.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_example.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_plotting.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io_asd.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_processing.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_core.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io_rastersources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io_envi.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io_DEPR.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_io_geopackage.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_gui.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/speclib/test_speclib_profilesources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_layerproperties.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_testing.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_classificationscheme.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_init.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_searchfiledialog.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_simplewidget.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_maptools.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_resources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_subdatasets.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_vectorlayertools.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/test_qgsfunctions.py
%PYTHON% -m coverage report