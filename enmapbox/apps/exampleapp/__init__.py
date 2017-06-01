import os

from PyQt4.QtGui import QIcon
from enmapbox.gui.applications import EnMAPBoxApplication
APP_DIR = os.path.dirname(__file__)

class MyEnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(MyEnMAPBoxApp, self).__init__(enmapBox,parent=parent)
        self.name = 'My EnMAPBox App'
        self.version = 'Version 42'
        self.licence = 'BSD-3'
        s = ""

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
        a.triggered.connect(lambda : self.startExampleGUI())

        #add a submenu
        subMenu = menu.addMenu('Submenu')
        #add QAction to run another process
        a = subMenu.addAction('Start Process')
        a.triggered.connect(lambda : self.startExampleProcess('My App Action triggered'))

        return menu

    def geoAlgorithms(self):
        from ExampleApp import MyAppGeoAlgorithm

        return [MyAppGeoAlgorithm()]

    def startExampleGUI(self):
        from ExampleApp import MyAppUserInterface
        ui = MyAppUserInterface(self.enmapbox.ui)
        ui.setModal(False) #True = will block all other widget
        ui.show()

    def startExampleProcess(self, text):
        print('print something:')
        print(text)
        print('exampleProcess done')

