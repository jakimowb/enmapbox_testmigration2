from __future__ import absolute_import
import os
import qgis
from PyQt5.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication
from enmapboxgeoalgorithms import ENMAPBOXGEOALGORITHMS_VERSION
from enmapboxgeoalgorithms.algorithms import ALGORITHMS

def enmapboxApplicationFactory(enmapBox):
    return [App(enmapBox)]

class App(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        EnMAPBoxApplication.__init__(self, enmapBox, parent=parent)
        self.name = 'EnMAP-Box Core GeoAlgorithms'
        self.version = 'Version ' + ENMAPBOXGEOALGORITHMS_VERSION
        self.licence = 'BSD-3'

    def icon(self):
        pathIcon = os.path.join(os.path.dirname(__file__), 'icon.png')
        return QIcon(pathIcon)

    def geoAlgorithms(self):
        return ALGORITHMS

def sandboxWithEnMapBox(loadPF=False):
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=loadPF)
    qgsApp.exec_()
    qgsApp.quit()
