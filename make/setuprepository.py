"""
Initial setup of the EnMAP-Box repository.
Run this script after having cloned the EnMAP-Box repostitory
"""

# specify the local path to the cloned QGIS repository
import os, sys
DIR_QGIS_REPO = os.environ.get('DIR_QGIS_REPO', None)



from os.path import dirname as dn
from os.path import join as jn
DIR_ENMAPBOX_REPO = dn(dn(__file__))
DIR_SITEPACKAGES = jn(DIR_ENMAPBOX_REPO, 'site-packages')
DIR_QGISRESOURCES = jn(DIR_ENMAPBOX_REPO, 'qgisresources')
DIR_MAKE = dn(__file__)

if not DIR_ENMAPBOX_REPO in sys.path:
    sys.path.append(DIR_ENMAPBOX_REPO)


# 1. compile all EnMAP-Box resource files (*.qrc) into corresponding python modules (*.py)
from make.compileresourcefiles import compileResourceFiles, compileQGISResourceFiles
compileResourceFiles()

# 2. create the qgisresource folder
if isinstance(DIR_QGIS_REPO, str):
    pathImages = os.path.join(DIR_QGIS_REPO, *['images', 'images.qrc'])
    if not os.path.isfile(pathImages):
        print('Wrong DIR_QGIS_REPO. Unable to find QGIS images.qrc in {}'.format(DIR_QGIS_REPO), file=sys.stderr)
    else:
        compileQGISResourceFiles(DIR_QGIS_REPO)
else:
    print('DIR_QGIS_REPO undefined. Some widgets might appear without icons', file=sys.stderr)

# 3. install the EnMAP-Box test data

import enmapbox.dependencycheck
enmapbox.dependencycheck.installTestData(overwrite_existing=False, ask=False)

print('EnMAP-Box repository setup finished')

exit(0)