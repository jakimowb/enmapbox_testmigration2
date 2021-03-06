from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from classificationworkflowapp.classificationworkflowgui import ClassificationWorkflowGui
from enmapbox.gui.applications import EnMAPBoxApplication

def enmapboxApplicationFactory(enmapBox):
    return [ClassificationWorkflowApp(enmapBox)]

class ClassificationWorkflowApp(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        super().__init__(enmapBox, parent=parent)

        self.name = 'ClassificationWorkflowApp'
        self.version = '2.0'
        self.licence = 'GNU GPL-3'

    def icon(self):
        return QIcon(None)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Classification Workflow')
        assert isinstance(a, QAction)
        a.setIcon(self.icon())
        a.triggered.connect(self.startGUI)
        return appMenu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ClassificationWorkflowGui(parent=self.enmapbox.ui)
        w.show()

