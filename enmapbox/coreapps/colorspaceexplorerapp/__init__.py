from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from colorspaceexplorerapp.colorspaceexplorerdialog import ColorSpaceExplorerDialog
from enmapbox.gui.applications import EnMAPBoxApplication
from typeguard import typechecked


def enmapboxApplicationFactory(enmapBox):
    return [ColorSpaceExplorerApp(enmapBox)]


@typechecked
class ColorSpaceExplorerApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = ColorSpaceExplorerApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    @classmethod
    def icon(cls):
        return QIcon(':/images/themes/default/styleicons/color.svg')

    def menu(self, appMenu: QMenu):
        appMenu: QMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction('Color Space Explorer')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def startGUI(self):
        w = ColorSpaceExplorerDialog(parent=self.enmapbox.ui)
        w.show()
