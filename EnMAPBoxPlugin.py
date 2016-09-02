import inspect
import os
import sys



#from qgis.gui import *
#from qgis.core import *
import qgis.gui
from PyQt4.QtCore import *
from PyQt4.QtGui import *


cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
jp = os.path.join
root = jp(cmd_folder, 'enmapbox')

if True:
    to_add = []
    to_add.append(cmd_folder)
    dir_libs = jp(cmd_folder, 'site-packages')
    for p in os.listdir(dir_libs):
        path = jp(dir_libs,p)
        if os.path.isdir(path):
            to_add.append(path)
            pass
    #to_add.append(jp(root, *['apps']))
    #to_add.append(jp(root, *['gui']))
    #to_add.append(jp(root, *['hub']))

    for folder in to_add:
        assert os.path.isdir(folder)
        if folder not in sys.path:
            sys.path.append(folder)




from enmapbox.enmapbox import EnMAPBox

#for p in sorted(sys.path):
#    print(p)

#import enmapbox.apps
#import enmapbox.apps.core
#import enmapbox.processing


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
            try:
                from processing.core.Processing import Processing
                from enmapbox.apps.core import EnMAPBoxProvider


                p = EnMAPBoxProvider()
                print(p.getIcon())
                self.processingProviders.append(EnMAPBoxProvider())

                #todo: add other providers here

                #add providers to processing framework
                for provider in self.processingProviders:
                    Processing.addProvider(provider)

            except Exception, e:
                import six
                import traceback
                tb = traceback.format_exc()
                six.print_('ERROR occurred while loading EnMAPBoxProvider for processing frame work:', file=sys.stderr)
                six.print_(str(e))
                six.print_(tb)
            print('Processing Framework done')

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
    if True:
        if sys.platform == 'darwin':
            PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        else:
            PATH_QGS = os.environ['QGIS_PREFIX_PATH']
        assert os.path.exists(PATH_QGS)
        qgsApp = qgis.core.QgsApplication([], True)
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
