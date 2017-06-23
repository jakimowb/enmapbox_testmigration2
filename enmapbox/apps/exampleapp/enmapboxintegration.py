import os
from PyQt4.QtGui import QIcon, QMenu, QAction
from enmapbox.gui.applications import EnMAPBoxApplication

from .gui import MyAppUserInterface
class MyEnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(MyEnMAPBoxApp, self).__init__(enmapBox,parent=parent)
        self.name = 'My EnMAPBox App'
        self.version = 'Version 0.42'
        self.licence = 'BSD-3'
        #todo: more requirements?

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return:
        """
        menu = QMenu(self.name, appMenu)
        menu.setIcon(self.icon())

        #add QAction that starts your GUI
        a = menu.addAction('Show My GUI')
        a.triggered.connect(lambda : self.startGUI())

        #add a submenu
        subMenu = menu.addMenu('Submenu')
        #add QAction to run another process
        a = subMenu.addAction('Start Process')
        a.triggered.connect(lambda : self.startExampleProcess('My App Action triggered'))

        return menu

    def startGUI(self):

        from exampleapp.gui import MyAppUserInterface
        ui = MyAppUserInterface(self.enmapbox)
        ui.show()


    def geoAlgorithms(self):
        from processingframework import MyAppGeoAlgorithm
        return [MyAppGeoAlgorithm()]

