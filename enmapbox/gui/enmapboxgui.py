#from __future__ import absolute_import

import site

import qgis.core
import qgis.gui

from PyQt4.QtGui import *

from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import loadUI, SETTINGS, DIR_TESTDATA, MimeDataHelper



class CentralFrame(QFrame):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    def __init__(self, *args, **kwds):
        super(CentralFrame, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        logger.debug('CentralFrame dragEnterEvent')
        pass
        #self.sigDragEnterEvent.emit(event)

    def dragMoveEvent(self, event):
        pass
        #self.sigDragMoveEvent.emit(event)

    def dragLeaveEvent(self, event):
        pass
        #self.sigDragLeaveEvent(event)

    def dropEvent(self, event):
        logger.debug('CentralFrame dropEvent')
        pass
        #self.sigDropEvent.emit(event)


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

        if enmapbox.gui.LOAD_PROCESSING_FRAMEWORK:
            self.processingPanel = addPanel(enmapbox.gui.processingmanager.ProcessingAlgorithmsPanelUI(self))

        #add entries to menu panels
        for dock in self.findChildren(QDockWidget):
            if len(dock.actions()) > 0:
                s = ""
            self.menuPanels.addAction(dock.toggleViewAction())


def getIcon():
    return QIcon(':/enmapbox/icons/enmapbox.png')


class EnMAPBoxQgisInterface(QgisInterface):

    def __init__(self, enmapBox):
        assert isinstance(enmapBox, EnMAPBox)
        super(EnMAPBoxQgisInterface, self).__init__()
        self.enmapBox = enmapBox
        self.virtualMapCanvas = QgsMapCanvas()
        self.virtualMapCanvas.setCrsTransformEnabled(True)
    def mainWindow(self):
        return self.enmapBox.ui

    def messageBar(self):
        return self.enmapBox.ui.messageBar

    def mapCanvas(self):
        assert isinstance(self.virtualMapCanvas, QgsMapCanvas)
        self.virtualMapCanvas.setLayerSet([])
        lyrs = []
        for ds in self.enmapBox.dataSourceManager.sources:
            if isinstance(ds, DataSourceSpatial):
                lyrs.append(ds.createRegisteredMapLayer())
        if len(lyrs) > 0:
            self.virtualMapCanvas.mapSettings().setDestinationCrs(lyrs[0].crs())
        lyrs = [QgsMapCanvasLayer(l) for l in lyrs]

        self.virtualMapCanvas.setLayerSet(lyrs)
        self.virtualMapCanvas.setExtent(self.virtualMapCanvas.fullExtent())
        logger.debug('layers shown in (temporary) QgsInterface::mapCanvas() {}'.format(len(self.virtualMapCanvas.layers())))
        return self.virtualMapCanvas

    def openMessageLog(self):
        logger.debug('TODO: implement openMessageLog')
        pass

    def refreshLayerSymbology(selflayerId):
        pass


    def legendInterface(self):
        return self.enmapBox.dockManager

class EnMAPBox(QObject):

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):


        assert EnMAPBox._instance is None
        super(EnMAPBox, self).__init__()
        EnMAPBox._instance = self

        self.ifaceSimulation = EnMAPBoxQgisInterface(self)
        self.iface = iface

        # init QGIS Processing Framework if necessary
        from qgis import utils as qgsUtils
        if qgsUtils.iface is None:
            # there is not running QGIS Instance. This means the entire QGIS processing framework was not
            # initialized at all.
            qgsUtils.iface = self.ifaceSimulation


        self.ui = EnMAPBoxUI()



        #define managers (the center of all actions and all evil)
        import enmapbox.gui
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager

        self.dataSourceManager = DataSourceManager(self)
        self.dockManager = DockManager(self)
        self.processingAlgManager = ProcessingAlgorithmsManager(self)

        #connect managers with widgets
        if enmapbox.gui.LOAD_PROCESSING_FRAMEWORK:
            self.ui.processingPanel.connectProcessingAlgManager(self.processingAlgManager)

        self.ui.dataSourcePanel.connectDataSourceManager(self.dataSourceManager)
        self.ui.dockPanel.connectDockManager(self.dockManager)

        self.ui.centralFrame.sigDragEnterEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragMoveEvent.connect(
            lambda event : self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragLeaveEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDropEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))

        #link action to managers
        self.ui.actionAddDataSource.triggered.connect(self.onAddDataSource)
        self.ui.actionAddMapView.triggered.connect(lambda : self.dockManager.createDock('MAP'))
        self.ui.actionAddTextView.triggered.connect(lambda: self.dockManager.createDock('TEXT'))
        self.ui.actionAddMimeView.triggered.connect(lambda : self.dockManager.createDock('MIME'))

        self.ui.actionIdentify.triggered.connect(lambda : self.dockManager.createDock('CURSORLOCATIONVALUE'))
        self.ui.actionSettings.triggered.connect(self.saveProject)



        self.ui.actionExit.triggered.connect(self.exit)



        # from now on other routines expect the EnMAP-Box to act like QGIS
        if enmapbox.gui.LOAD_PROCESSING_FRAMEWORK:
            try:
                logger.debug('initialize own QGIS Processing framework')
                from processing.core.Processing import Processing
                Processing.initialize()

                from enmapboxplugin.processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider
                Processing.addProvider(EnMAPBoxAlgorithmProvider())

                logger.debug('QGIS Processing framework initialized')
            except:
                logger.warning('Failed to initialize QGIS Processing framework')
            s = ""


    def exit(self):
        self.ui.close()
        self.deleteLater()


    def onDataDropped(self, droppedData):
        assert isinstance(droppedData, list)
        mapDock = None
        from enmapbox.gui.datasources import DataSourceSpatial
        for dataItem in droppedData:
            if isinstance(dataItem, DataSourceSpatial):
                dataSrc = self.dataSourceManager.addSource(dataItem)
                if mapDock is None:
                    mapDock = self.createDock('MAP')
                mapDock.addLayers(dataSrc.createRegisteredMapLayer())
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
        return self.dockManager.createDock(*args, **kwds)

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


