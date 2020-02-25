import os, sys, pathlib
from enmapbox import DIR_REPO, DIR_UNITTESTS
from enmapbox.gui.utils import file_search
DIR_REPO = pathlib.Path(DIR_REPO)
DIR_TESTS = DIR_UNITTESTS


PATH_RUNTESTS_BAT = DIR_REPO / 'runtests.bat'
PATH_RUNTESTS_SH = DIR_REPO / 'runtests.sh'

PREFACE_BAT = \
"""
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

start %PYTHON% make/setuprepository.py
"""

PREFACE_SH = \
"""#!/bin/bash
QT_QPA_PLATFORM=offscreen
export QT_QPA_PLATFORM
CI=True
export CI

find . -name "*.pyc" -exec rm -f {} \;
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 runfirst.py
"""


#dirOut = 'test-reports/today'
linesBat = [PREFACE_BAT]
linesSh = [PREFACE_SH]
#linesBat.append('mkdir {}'.format(dirOut.replace('/', '\\')))
#linesSh.append('mkdir {}'.format(dirOut))


bnDirTests = os.path.basename(DIR_TESTS)
for i, file in enumerate(file_search(DIR_TESTS, 'test_*.py')):
    file = pathlib.Path(file)
    do_append = '' if i == 0 else '--append'
    pathTest = str(pathlib.Path(*file.parts[-2:]).as_posix())
    lineBat = '%PYTHON% -m coverage run --rcfile=.coveragec {}  {}'.format(do_append, pathTest)
    lineSh = 'python3 -m coverage run --rcfile=.coveragec {}  {}'.format(do_append, pathTest)
    linesBat.append(lineBat)
    linesSh.append(lineSh)

linesBat.append('%PYTHON% -m coverage report')
linesSh.append('python3 -m coverage report')

with open(PATH_RUNTESTS_BAT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(linesBat))

with open(PATH_RUNTESTS_SH, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(linesSh))

