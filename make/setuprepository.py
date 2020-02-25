"""
Initial setup of the EnMAP-Box repository.
Run this script after you have cloned the EnMAP-Box repository
"""

# specify the local path to the cloned QGIS repository
import os, sys, pathlib

DIR_REPO = pathlib.Path(__file__).parents[1]
DIR_SITEPACKAGES = DIR_REPO / 'site-packages'
DIR_QGISRESOURCES = DIR_REPO / 'qgisresources'

KEY_QGIS_REPO = 'QGIS_REPO'

# 1. compile EnMAP-Box resource files (*.qrc) into corresponding python modules (*.py)
from make.compileresourcefiles import compileEnMAPBoxResources
compileEnMAPBoxResources()


# 2. create the qgisresource folder
from enmapbox.externals.qps.make.make import compileQGISResourceFiles
if KEY_QGIS_REPO in os.environ.keys():

    DIR_QGIS_REPO = pathlib.Path(os.environ.get(KEY_QGIS_REPO))
    os.makedirs(DIR_QGISRESOURCES, exist_ok=True)
    print('Compile QGIS resource files:\nQGIS_REPO={}\nDestination:{}'.format(DIR_QGIS_REPO, DIR_QGISRESOURCES))
    compileQGISResourceFiles(DIR_QGIS_REPO, DIR_QGISRESOURCES)

# 3. install the EnMAP-Box test data
import enmapbox.dependencycheck
enmapbox.dependencycheck.installTestData(overwrite_existing=False, ask=False)

print('EnMAP-Box repository setup finished')

exit(0)