import os, sys, pathlib
from enmapbox import DIR_REPO, DIR_UNITTESTS
from enmapbox.gui.utils import file_search
DIR_REPO = pathlib.Path(DIR_REPO)
DIR_TESTS = DIR_UNITTESTS


PATH_RUNTESTS_BAT = DIR_REPO / 'runtests.bat'
PATH_RUNTESTS_SH = DIR_REPO / 'runtests.sh'

jUnitXML = r'nose2-junit.xml'

PREFACE_BAT = \
"""
:: use this script to run unit tests locally
::
set CI=True
python make/setuprepository.py
"""

PREFACE_SH = \
"""
# use this script to run unit tests locally
#
python make/setuprepository.py
"""

dirOut = 'test-reports/today'
linesBat = [PREFACE_BAT]
linesSh = [PREFACE_SH]
linesBat.append('mkdir {}'.format(dirOut.replace('/', '\\')))
linesSh.append('mkdir {}'.format(dirOut))


bnDirTests = os.path.basename(DIR_TESTS)
for file in file_search(DIR_TESTS, 'test_*.py'):

    bn = os.path.basename(file)
    bn = os.path.splitext(bn)[0]
    lineBat = 'python -m nose2 -s {3} {0} & move {1} {2}/{0}.xml'.format(bn, jUnitXML, dirOut, bnDirTests)
    lineSh = 'python -m nose2 -s {3} {0} | mv {1} {2}/{0}.xml'.format(bn, jUnitXML, dirOut, bnDirTests)
    linesBat.append(lineBat)
    linesSh.append(lineSh)


with open(PATH_RUNTESTS_BAT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(linesBat))

with open(PATH_RUNTESTS_SH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(linesSh))

