
import inspect, sys, os, shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from gui.enmapbox import EnMAPBox

class EnMAPBoxPlugin:

    def __init__(self, iface):
        self.iface = iface


    def initGui(self):

        #initialize stuff, register GUI buttons etc.
        #self.menu = self.tr(u'&EnMAP-Box')

        path_icon = os.path.join(cmd_folder, *['gui','icons','enmapbox_icon.png'])

        self.enmapbox = EnMAPBox(self.iface)
        self.action = QAction(QIcon(path_icon), u'EnMAP-Box', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        # action.setEnabled(enabled_flag)

        # add to toolbar:
        self.iface.addToolBarIcon(self.action)

        self.initProcessingAlgs()

        pass

    def initProcessingAlgs(self):
        pass



    def unload(self):

        self.iface.unregisterMainWindowAction(self.action)

    def openGUI(self):
        pass


    def tr(self, message):
        return QCoreApplication.translate('EnMAPBoxPlugin', message)


if __name__ == '__main__':

    import zipfile

    #start a QGIS instance

    #load the plugin
    print('Done')
