import inspect
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
jp = os.path.join

if False:
    to_add = [cmd_folder]

    to_add.append(jp(cmd_folder, *['apps','exampleapp']))
    to_add.append(jp(cmd_folder, *['gui']))
    to_add.append(jp(cmd_folder, *['hub']))

    for folder in reversed(to_add):
        assert os.path.isdir(folder)
        if folder not in sys.path:
            sys.path.insert(0, folder)

from enmapbox.enmapbox import EnMAPBox
from processing.core.Processing import Processing

class EnMAPBoxPlugin:
    # initialize and unload all the stuff that comes under the umbrella of the EnMAP-Box:
    # main gui, maybe smaller GUIs and QGIS extensions, processing routines....

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):


        # add toolbar actions
        self.toolbarActions = []

        #1. EnMAP-Box main window
        self.enmapbox = EnMAPBox(self.iface)
        path_icon = jp(cmd_folder, *['enmapbox','gui','icons','enmapbox.png'])
        action = QAction(QIcon(path_icon), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.enmapbox.run)
        self.toolbarActions.append(action)

        #2. tbd...

        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)


        # init processing provider

        self.processingProviders = []
        #add example app
        from enmapbox.apps.exampleapp.ExampleAlgorithmProvider import ExampleAlgorithmProvider
        self.processingProviders.append(ExampleAlgorithmProvider())

        #2.tbd...

        for provider in self.processingProviders:
            Processing.addProvider(provider)
        pass



    def unload(self):
        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

        for provider in self.processingProviders:
            Processing.removeProvider(provider)

    def openGUI(self):
        pass


    def tr(self, message):
        return QCoreApplication.translate('EnMAPBoxPlugin', message)


if __name__ == '__main__':

    #start a QGIS instance
    from qgis.gui import *
    from qgis.core import *

    PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    app = QgsApplication([], False)
    app.setPrefixPath(PATH_QGS, True)
    app.initQgis()

    w = QMainWindow()
    c = QgsMapCanvas()
    c.setCanvasColor(Qt.black)
    c.enableAntiAliasing(True)

    reg = QgsMapLayerRegistry.instance()
    w.setCentralWidget(c)
    w.show()
    #load the plugin
    print('Done')
