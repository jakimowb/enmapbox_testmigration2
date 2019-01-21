import os, sys, fnmatch, six, subprocess, re

from qgis.core import *

from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from xml.etree import ElementTree
ROOT = os.path.dirname(os.path.dirname(__file__))
from enmapbox.testing import initQgisApplication

app = initQgisApplication()
from enmapbox import DIR_REPO
from qps.make.make import *
from qps.utils import *
from osgeo import gdal, ogr, osr


if __name__ == '__main__':
    from enmapbox import DIR_UIFILES, DIR_ICONS

    icondir = DIR_ICONS
    pathQrc = jp(DIR_UIFILES, 'resources.qrc')

    if False:
        pathQGISRepo = r'C:\Users\geo_beja\Repositories\QGIS'
        copyQGISRessourceFile(pathQGISRepo)

    if False:
        #convert SVG to PNG and add link them into the resource file
        svg2png(icondir, overwrite=False)
        png2qrc(icondir, pathQrc)
    if False:
        #migrateBJexternals()
        compile_rc_files(DIR_UIFILES)
    if True:
        DIR_ROOT = os.path.join(DIR_REPO, 'enmapbox')
        #compileResourceFiles(DIR_ROOT)
        compileResourceFiles(jp(DIR_REPO, 'resources.qrc'))
    print('Done')

