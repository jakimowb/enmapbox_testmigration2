
:: use this script to run unit tests locally
::
@echo off
set CI=True
set PYTHONPATH=%~dp0/..;%PYTHONPATH%
set PYTHONPATH
WHERE python3 >nul 2>&1 && (
    echo Found "python3" command
    set PYTHON=python3
) || (
    echo Did not found "python3" command. use "python" instead
    set PYTHON=python
)

::start %PYTHON% scripts/setup_repository.py

%PYTHON% -m coverage run --rcfile=.coveragec   tests/src/coreapps/test_enmapboxapplications.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_imagecube.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_metadataeditorapp.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_reclassifyapp.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/coreapps/test_vrtbuilderapp.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_478.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_711.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_724.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/issues/test_issue_747.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_enpt_enmapboxapp.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_ensomap.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/otherapps/test_lmuvegetationapps.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_applications.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_crosshair.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_cursorlocationsvalues.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_datasources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_dependencycheck.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_docksanddatasources.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapbox.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapboxplugin.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_enmapboxprocessingprovider.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_hiddenqgislayers.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_mapcanvas.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_mimedata.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_options.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_repo.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_settings.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_speclibs.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_splashscreen.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_template.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_testdata_dependency.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_testing.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_utils.py
%PYTHON% -m coverage run --rcfile=.coveragec --append  tests/src/test_vectorlayertools.py
%PYTHON% -m coverage report