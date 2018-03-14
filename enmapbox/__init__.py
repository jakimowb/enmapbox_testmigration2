__version__ = '20180212T1035'

HOMEPAGE = 'https://bitbucket.org/hu-geomatics/enmap-box'
REPOSITORY = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
TRACKER = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'

DEPENDENCIES = ['numpy','scipy','osgeo', 'PyQt5', 'sklearn','pyqtgraph','matplotlib','spectral']

import sys, os

def messageLog(msg, level=None):
    """
    Writes a log message to the QGIS log related to the EnMAP-Box
    :param msg: log message string
    :param level: QgsMessageLog::MessageLevel with MessageLevel =[INFO |  ALL | WARNING | CRITICAL | NONE]
    """
    from qgis.core import QgsMessageLog
    if level is None:
        level = QgsMessageLog.WARNING
    QgsMessageLog.instance().logMessage(msg, 'EnMAP-Box', level)

