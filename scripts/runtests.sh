#!/bin/bash
QT_QPA_PLATFORM=offscreen
export QT_QPA_PLATFORM
CI=True
export CI

find . -name "*.pyc" -exec rm -f {} \;
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# python3 scripts/setuprepository.py

python3 -m coverage run --rcfile=.coveragec   enmapboxtesting/test_applications.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_crosshair.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_cursorlocationsvalues.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_datasources.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_dependencycheck.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_docksanddatasources.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapbox.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapboxplugin.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_enmapboxprocessingprovider.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_hiddenqgislayers.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_mapcanvas.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_mimedata.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_options.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_settings.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_speclibs.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_spectralprofilesources.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_template.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_testdata_dependency.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_testing.py
python3 -m coverage run --rcfile=.coveragec --append  enmapboxtesting/test_utils.py
python3 -m coverage run --rcfile=.coveragec --append  hubdc/test/test_algorithm.py
python3 -m coverage run --rcfile=.coveragec --append  hubdc/test/test_core.py
python3 -m coverage report