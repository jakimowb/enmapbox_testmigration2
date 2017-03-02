from __future__ import absolute_import

import site

import qgis.core
import qgis.gui

from PyQt4.QtGui import *

from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import loadUI, SETTINGS, DIR_TESTDATA

class EnMAPBoxUI(QMainWindow, loadUI('enmapbox_gui.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(EnMAPBoxUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowIcon(getIcon())

        self.showMaximized()
        self.setAcceptDrops(True)
        from enmapbox import __version__ as version
        self.setWindowTitle('EnMAP-Box {}'.format(version))


        #add & register panels
        area = None

        import enmapbox.gui.dockmanager
        import enmapbox.gui.datasourcemanager
        import enmapbox.gui.processingmanager
        from processing.gui.ProcessingToolbox import ProcessingToolbox
        def addPanel(panel):
            """
            shortcut to add a created panel and return it
            :param dock:
            :return:
            """
            self.addDockWidget(area, panel)
            return panel

        area = Qt.LeftDockWidgetArea
        self.dataSourcePanel = addPanel(enmapbox.gui.datasourcemanager.DataSourcePanelUI(self))
        self.dockPanel = addPanel(enmapbox.gui.dockmanager.DockPanelUI(self))
        self.processingPanel = addPanel(enmapbox.gui.processingmanager.ProcessingAlgorithmsPanelUI(self))
        #self.processingPanel2 = addPanel()

        #add entries to menu panels
        for dock in self.findChildren(QDockWidget):
            if len(dock.actions()) > 0:
                s = ""
            self.menuView.addAction(dock.toggleViewAction())


def getIcon():
    return QIcon(':/enmapbox/icons/enmapbox.png')


class EnMAPBox(QgisInterface):

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):


        assert EnMAPBox._instance is None
        super(EnMAPBox, self).__init__()
        EnMAPBox._instance = self

        self.iface = iface

        #init QGIS Processing Framework if necessary
        from qgis import utils as qgsUtils
        if qgsUtils.iface is None:
            #there is not running QGIS Instance. This means the entire QGIS processing framework was not
            #initialzed at all.
            qgsUtils.iface = self
            #from now on other routines expect the EnMAP-Box to act like QGIS

            from processing.core.Processing import Processing
            Processing.initialize()
            from enmapboxplugin.processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider
            Processing.addProvider(EnMAPBoxAlgorithmProvider())

        self.ui = EnMAPBoxUI()

        #define managers (the center of all actions and all evil)
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager

        self.dataSourceManager = DataSourceManager(self)
        self.dockManager = DockManager(self)
        self.processingAlgManager= ProcessingAlgorithmsManager(self)

        #connect managers with widgets
        self.ui.processingPanel.connectProcessingAlgManager(self.processingAlgManager)
        self.ui.dataSourcePanel.connectDataSourceManager(self.dataSourceManager)
        self.ui.dockPanel.connectDockManager(self.dockManager)


        #link action to managers
        self.ui.actionAddDataSource.triggered.connect(self.onAddDataSource)
        self.ui.actionAddMapView.triggered.connect(lambda : self.dockManager.createDock('MAP'))
        self.ui.actionAddTextView.triggered.connect(lambda: self.dockManager.createDock('TEXT'))
        self.ui.actionAddMimeView.triggered.connect(lambda : self.dockManager.createDock('MIME'))

        self.ui.actionCursor_Location_Values.triggered.connect(lambda : self.dockManager.createDock('CURSORLOCATIONVALUE'))
        self.ui.actionSave_Settings.triggered.connect(self.saveProject)
        s = ""



    def onAddDataSource(self):
        lastDataSourceDir = SETTINGS.value('lastsourcedir', None)

        if lastDataSourceDir is None:
            lastDataSourceDir = DIR_TESTDATA

        if not os.path.exists(lastDataSourceDir):
            lastDataSourceDir = None

        uris = QFileDialog.getOpenFileNames(self.ui, "Open a data source(s)", lastDataSourceDir)

        for uri in uris:
            self.addSource(uri)

        if len(uris) > 0:
            SETTINGS.setValue('lastsourcedir', os.path.dirname(uris[-1]))

    def saveProject(self):
        proj = QgsProject.instance()
        proj.dumpObjectInfo()
        proj.dumpObjectTree()
        proj.dumpProperties()
        s = ""

    def restoreProject(self):
        s = ""


    def createDock(self, *args, **kwds):
        self.dockManager.createDock(*args, **kwds)

    def removeDock(self, *args, **kwds):
        self.dockManager.removeDock(*args, **kwds)

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)

    def addSource(self, source, name=None):
        return self.dataSourceManager.addSource(source, name=name)



    def getURIList(self, *args, **kwds):
        return self.dataSourceManager.getURIList(*args, **kwds)

    @staticmethod
    def getIcon():
        return getIcon()

    def run(self):
        self.ui.show()
        pass

    """
    QgisInterface compliance
    """
    def mainWindow(self):
        return self.ui

    def mapCanvas(self):
        return QgsMapCanvas()

    def refreshLayerSymbology(selflayerId):
        pass


    def legendInterface(self):
        return self.dockManager