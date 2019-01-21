import os, sys, fnmatch, six, subprocess, re

from qgis.core import *

from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from xml.etree import ElementTree
ROOT = os.path.dirname(os.path.dirname(__file__))
#from enmapbox.testing import initQgisApplication

#app = initQgisApplication()
from enmapbox import DIR_REPO

from osgeo import gdal, ogr, osr

from enmapbox import DIR_REPO

def compileResourceFiles():
    from qps.make.make import compileResourceFile
    from qps.utils import file_search
    qrcFiles = file_search(DIR_REPO, '*.qrc', recursive=True)

    for file in qrcFiles:
        compileResourceFile(file)
    s = ""


if __name__ == '__main__':

    if False:
        pathQGISRepo = r'C:\Users\geo_beja\Repositories\QGIS'
        copyQGISRessourceFile(pathQGISRepo)

    if True:
        compileResourceFiles()
    print('Done')

