import inspect
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

jp = os.path.join

from enmapbox.enmapbox import EnMAPBox

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

        #2. other stuff

        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)


        self.initProcessingAlgs()

        pass

    def initProcessingAlgs(self):
        pass



    def unload(self):
        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

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
