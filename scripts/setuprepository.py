"""
Initial setup of the EnMAP-Box repository.
Run this script after you have cloned the EnMAP-Box repository
"""
import sys, getopt
def setup_enmapbox_repository():
    # specify the local path to the cloned QGIS repository
    import os, sys, pathlib

    DIR_REPO = pathlib.Path(__file__).parents[1].resolve()
    DIR_SITEPACKAGES = DIR_REPO / 'site-packages'
    DIR_QGISRESOURCES = DIR_REPO / 'qgisresources'

    # 1. compile EnMAP-Box resource files (*.qrc) into corresponding python modules (*.py)
    from scripts.compileresourcefiles import compileEnMAPBoxResources
    compileEnMAPBoxResources()


    # 2. create the qgisresource folder which contains
    from enmapbox.externals.qps.resources import compileQGISResourceFiles
    compileQGISResourceFiles(None, DIR_QGISRESOURCES)

    # 3. install the EnMAP-Box test data
    import enmapbox.dependencycheck
    enmapbox.dependencycheck.installTestData(overwrite_existing=False, ask=False)

    print('EnMAP-Box repository setup finished')



if __name__ == "__main__":

    try:
        print(sys.argv)
        opts, options = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError as err:
        print(err)

    setup_enmapbox_repository()
    exit(0)