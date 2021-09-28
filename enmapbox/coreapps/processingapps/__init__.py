from os.path import join, dirname

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from enmapbox.gui.applications import EnMAPBoxApplication
from enmapboxprocessing.algorithm.rastermathalgorithm.rastermathalgorithm import RasterMathAlgorithm


def enmapboxApplicationFactory(enmapBox):
    return [ProcessingApps(enmapBox)]


class ProcessingApps(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'ProcessingApps'
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(join(dirname(__file__), 'numpy.png'))

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Raster math')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def startGUI(self, *args):
        self.enmapbox.showProcessingAlgorithmDialog(RasterMathAlgorithm(), parent=self.enmapbox.ui)
