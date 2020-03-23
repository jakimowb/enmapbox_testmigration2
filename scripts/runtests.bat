
:: use this script to run unit tests locally
::
@echo off
set CI=True

WHERE python3 >nul 2>&1 && (
    echo Found "python3" command
    set PYTHON=python3
) || (
    echo Did not found "python3" command. use "python" instead
    set PYTHON=python
)

start %PYTHON% scripts/setuprepository.py

%PYTHON% -m coverage run --rcfile=.coveragec   enmapboxtesting/test_applications.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_crosshair.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_cursorlocationsvalues.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_datasources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_dependencycheck.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_docksanddatasources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapbox.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapboxplugin.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapboxprocessingprovider.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_hiddenqgislayers.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_mapcanvas.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_mimedata.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_options.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_settings.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_speclibs.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_spectralprofilesources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_template.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_testdata_dependency.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_testing.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_utils.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  hubdc/test/test_algorithm.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  hubdc/test/test_core.py
%PYTHON% -m coverage report