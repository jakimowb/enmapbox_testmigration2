__version__ = '3.2'

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
ISSUE_TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
CREATE_ISSUE = 'https://bitbucket.org/hu-geomatics/enmap-box/issues/new'
DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib']
DOCUMENTATION = 'https://enmap-box.readthedocs.io/'

import sys, os
from qgis.core import Qgis, QgsApplication

# mockup to make QGIS resources available for uic.loadUiType

import sys
if not 'images' in list(sys.modules.keys()):

    import enmapbox.images

    sys.modules['images'] = enmapbox.images

def messageLog(msg, level=Qgis.Info):
    """
    Writes a log message to the QGIS EnMAP-Box Log
    :param msg: log message string
    :param level: Qgis.MessageLevel=[Qgis.Info |  Qgis.Warning| Qgis.Critical| Qgis.Success | Qgis.NONE]
    """

    if not isinstance(msg, str):
        msg = str(msg)
    QgsApplication.instance().messageLog().logMessage(msg, 'EnMAP-Box', level)



#provide important classes in Top-Level Namespace
from enmapbox.gui.enmapboxgui import EnMAPBox
EnMAPBox = EnMAPBox

from enmapbox.gui.applications import EnMAPBoxApplication
EnMAPBoxApplication = EnMAPBoxApplication