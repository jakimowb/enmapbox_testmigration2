from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from decorrelationstretchapp.decorrelationstretchdialog import DecorrelationStretchDialog
from enmapbox.gui.applications import EnMAPBoxApplication
from typeguard import typechecked


def enmapboxApplicationFactory(enmapBox):
    return [DecorrelationStretchApp(enmapBox)]


@typechecked
class DecorrelationStretchApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = DecorrelationStretchApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    @classmethod
    def icon(cls):
        return QIcon(':/images/themes/default/propertyicons/symbology.svg')

    @classmethod
    def title(cls):
        return 'Decorrelation Stretch Renderer'

    def menu(self, appMenu: QMenu):
        appMenu: QMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction(self.title())
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def startGUI(self):
        w = DecorrelationStretchDialog(parent=self.enmapbox.ui)
        w.show()