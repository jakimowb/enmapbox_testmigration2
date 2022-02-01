from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from classificationstatisticsapp.classificationstatisticsdialog import ClassificationStatisticsDialog
from enmapbox.gui.applications import EnMAPBoxApplication
from typeguard import typechecked


def enmapboxApplicationFactory(enmapBox):
    return [ClassificationStatisticsApp(enmapBox)]


@typechecked
class ClassificationStatisticsApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = ClassificationStatisticsApp.__name__
        self.version = 'dev'
        self.licence = 'GNU GPL-3'

    @classmethod
    def icon(cls):
        return QIcon(':/images/themes/default/histogram.svg')

    def menu(self, appMenu: QMenu):
        appMenu: QMenu = self.enmapbox.menu('Tools')
        a = appMenu.addAction('Classification Statistics')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def startGUI(self):
        w = ClassificationStatisticsDialog(parent=self.enmapbox.ui)
        w.show()
