import inspect
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis.gui

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
jp = os.path.join
root = jp(cmd_folder, 'enmapbox')

if False:
    to_add = [root]
    #to_add.append(jp(root, *['apps']))
    to_add.append(jp(root, *['gui']))
    #to_add.append(jp(root, *['hub']))

    for folder in reversed(to_add):
        assert os.path.isdir(folder)
        if folder not in sys.path:
            sys.path.insert(0, folder)




from enmapbox.enmapbox import EnMAPBox



class EnMAPBoxPlugin:
    _enmapBoxInstance = None

    def enmapBoxInstance(self):
        return self._enmapBoxInstance
    # initialize and unload all the stuff that comes under the umbrella of the EnMAP-Box:
    # main gui, maybe smaller GUIs and QGIS extensions, processing routines....

    def __init__(self, iface):
        self.iface = iface


        #open QGIS python console. this is required to allow for print() statements in the source code.
        if isinstance(self.iface, qgis.gui.QgisInterface):
            import console
            console.show_console()

    def has_processing_framework(self):
        try:
            from processing.core.Processing import Processing
            return True
        except:
            return False


    def initGui(self):
        # add toolbar actions
        self.toolbarActions = []

        #1. EnMAP-Box main window
        for p in sys.path:
            print(p)

        self.enmapbox = EnMAPBox(self.iface)
        EnMAPBoxPlugin._enmapBoxInstance = self.enmapbox

        action = QAction(EnMAPBox.getIcon(), u'EnMAP-Box', self.iface)
        action.triggered.connect(self.enmapbox.run)
        self.toolbarActions.append(action)

        #2. tbd...
        for action in self.toolbarActions:
            self.iface.addToolBarIcon(action)


        # init processing provider

        self.processingProviders = []
        if self.has_processing_framework():
            # add example app
            from processing.core.Processing import Processing
            from enmapbox.apps.exampleapp.ExampleAlgorithmProvider import ExampleAlgorithmProvider
            self.processingProviders.append(ExampleAlgorithmProvider())

            for provider in self.processingProviders:
                Processing.addProvider(provider)




    def unload(self):
        for action in self.toolbarActions:
            print(action)
            self.iface.removeToolBarIcon(action)

        if self.has_processing_framework():
            from processing.core.Processing import Processing
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
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
    else:
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)
    qgsApp = QgsApplication([], True)
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

    import enmapbox.enmapbox

    w = QMainWindow()
    w.setWindowTitle('QgsMapCanvas Example')
    w.show()
    EB = enmapbox.enmapbox.EnMAPBox(w)
    EB.run()
    qgsApp.exec_()
    qgsApp.exitQgis()

    # qgsApp.exitQgis()
    # app.exec_()
    pass

    #load the plugin
    print('Done')
