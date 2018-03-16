__version__ = '20180212T1035'

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'

DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib','spectral']

import sys, os
from qgis.core import *

def messageLog(msg, level=Qgis.Warning):
    """
    Writes a log message to the QGIS log related to the EnMAP-Box
    :param msg: log message string
    :param level: QgsMessageLog::MessageLevel with MessageLevel =[INFO |  ALL | WARNING | CRITICAL | NONE]
    """

    if not isinstance(msg, str):
        msg = str(msg)
    QgsApplication.instance().messageLog().logMessage(msg, 'EnMAP-Box', level)

