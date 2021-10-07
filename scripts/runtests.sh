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
python3 -m coverage report