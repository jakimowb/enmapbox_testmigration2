import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QHBoxLayout, QLabel, QPushButton
from enmapbox.gui.applications import EnMAPBoxApplication
from enmapboxapplications.imagemathapp.core import ImageMathApp
VERSION = 'dev'
LICENSE = 'GNU GPL-3'

def enmapboxApplicationFactory(enmapBox):
    return [ImageMathApplication(enmapBox)]

class ImageMathApplication(EnMAPBoxApplication):
    def __init__(self, enmapBox, parent=None):
        EnMAPBoxApplication.__init__(self, enmapBox=enmapBox, parent=parent)

        self.enmapBox = enmapBox
        self.name = 'imageMath'
        self.version = 'dev'
        self.licence = LICENSE


    def icon(self):
        filename = os.path.join(os.path.dirname(__file__), 'imagemathapp', 'icons', 'numpy.png')
        return QIcon(filename)

    def menu(self, appMenu):
        assert isinstance(appMenu, QMenu)
        menu = appMenu.addMenu(self.name)
        menu.setIcon(self.icon())

        action = menu.addAction('Show ExampleApp GUI')
        assert isinstance(action, QAction)
        action.triggered.connect(self.startGUI)
        appMenu.addMenu(menu)

        return menu

    def geoAlgorithms(self):
        return []

    def startGUI(self, *args):
        w = ImageMathApp()
        w.show()

if __name__ == '__main__':
    from enmapbox.gui.utils import initQgisApplication
    from enmapbox.gui.enmapboxgui import EnMAPBox

    qgsApp = initQgisApplication()
    enmapbox = EnMAPBox(None)
    enmapbox.run()
    #enmapbox.openExampleData(mapWindows=2)
    app = ImageMathApplication(enmapBox=enmapbox)

    #enmapbox.addApplication(app)
    app.startGUI()
    qgsApp.exec_()
