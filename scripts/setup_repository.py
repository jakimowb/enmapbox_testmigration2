"""
Initial setup of the EnMAP-Box repository.
Run this script after you have cloned the EnMAP-Box repository
"""
import sys, getopt

def setup_enmapbox_repository():
    # specify the local path to the cloned QGIS repository
    import os, sys, pathlib, site

    DIR_REPO = pathlib.Path(__file__).parents[1].resolve()
    DIR_SITEPACKAGES = DIR_REPO / 'site-packages'
    DIR_QGISRESOURCES = DIR_REPO / 'qgisresources'

    site.addsitedir(DIR_REPO)

    from scripts.compile_resourcefiles import compileEnMAPBoxResources
    from scripts.install_testdata import install_qgisresources, install_enmapboxtestdata

    # 1. compile EnMAP-Box resource files (*.qrc) into corresponding python modules (*.py)
    print('Compile EnMAP-Box resource files...')
    compileEnMAPBoxResources()

    # 2. install the EnMAP-Box test data
    print('Install EnMAP-Box Test Data')
    install_enmapboxtestdata()

    print('Install QGIS resource files')
    install_qgisresources()
    print('EnMAP-Box repository setup finished')


if __name__ == "__main__":
    print('setup repository')
    setup_enmapbox_repository()
