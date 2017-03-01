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



class EnMAPBox():

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        assert EnMAPBox._instance is None
        EnMAPBox._instance = self
        self.iface = iface

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


    def onDataSourceTreeViewCustomContextMenu(self, point):
        tv = self.ui.dataSourceTreeView
        assert isinstance(tv, QTreeView)
        index = tv.indexAt(point)


        model = tv.model()
        if index.isValid():
            treeItem = model.data(index, 'TreeItem')
            itemData = model.data(index, Qt.UserRole)

            if itemData or len(treeItem.actions) > 0:
                menu = QMenu()
                #append dynamic parts reactive to opened docks etc
                if isinstance(itemData, DataSource):
                    if isinstance(itemData, DataSourceSpatial):
                        mapDocks = [d for d in self.DOCKS if isinstance(d, MapDock)]
                        mapDocks = sorted(mapDocks, key=lambda d:d.name())
                        if len(mapDocks) > 0:
                            subMenu = QMenu()
                            subMenu.setTitle('Add to Map...')
                            for mapDock in mapDocks:
                                action = QAction('"{}"'.format(mapDock.name()), menu)
                                action.triggered.connect(lambda : mapDock.addLayer(itemData.getMapLayer()))
                                subMenu.addAction(action)
                            menu.addMenu(subMenu)
                        action = QAction('Add to new map', menu)
                        action.triggered.connect(lambda : self.createDock('MAP', initSrc=itemData))
                        menu.addAction(action)
                    action = QAction('Remove', menu)
                    action.triggered.connect(lambda : self.dataSourceManager.removeSource(itemData))
                else:
                    action = QAction('Copy', menu)
                    action.triggered.connect(lambda: QApplication.clipboard().setText(str(itemData)))
                #append item specific menue
                if len(treeItem.actions) > 0:
                    for action in treeItem.actions:
                        #action.setParent(menu)
                        menu.addAction(action)

                menu.exec_(tv.viewport().mapToGlobal(point))



