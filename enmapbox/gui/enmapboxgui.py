import qgis.core
import qgis.gui
from qgis import utils as qgsUtils
from PyQt4.QtGui import *

from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import loadUI, settings, DIR_TESTDATA, MimeDataHelper

SETTINGS = settings()
HIDE_SPLASHSCREEN = SETTINGS.value('EMB_SPLASHSCREEN', True)

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
        self.setVisible(False)


        #self.showMaximized()
        self.setAcceptDrops(True)
        import enmapbox
        self.setWindowTitle('EnMAP-Box 3 ({})'.format(enmapbox.__version__))

        self.isInitialized = False
        #add & register panels
        area = None

        import enmapbox.gui.dockmanager
        import enmapbox.gui.datasourcemanager



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
            from enmapbox.gui.processingmanager import ProcessingAlgorithmsPanelUI
            self.processingPanel = addPanel(ProcessingAlgorithmsPanelUI(self))

        #add entries to menu panels
        for dock in self.findChildren(QDockWidget):
            self.menuPanels.addAction(dock.toggleViewAction())


        #tabbify dock widgets
        self.tabifyDockWidget(self.processingPanel, self.dockPanel)
        self.tabifyDockWidget(self.processingPanel, self.dataSourcePanel)

    def setIsInitialized(self):
        self.isInitialized = True

    def menusWithTitle(self, title):
        return [m for m in self.findChildren(QMenu) if str(m.title()) == title]

def getIcon():
    return QIcon(':/enmapbox/icons/enmapbox.png')


class EnMAPBoxSplashScreen(QSplashScreen):

    def __init__(self, parent=None):
        pm = QPixmap(':/enmapbox/splashscreen.png')
        super(EnMAPBoxSplashScreen, self).__init__(pm, Qt.WindowStaysOnTopHint)

    def showMessage(self, text, alignment=None, color=None):
        if alignment is None:
            alignment = Qt.AlignLeft | Qt.AlignBottom
        if color is None:
            color = QColor('white')
        super(EnMAPBoxSplashScreen, self).showMessage(text, alignment, color)
        QApplication.processEvents()


class EnMAPBoxQgisInterface(QgisInterface):
    """
    Implementation of QgisInterface
    """

    def __init__(self, enmapBox):
        assert isinstance(enmapBox, EnMAPBox)
        super(EnMAPBoxQgisInterface, self).__init__()
        self.enmapBox = enmapBox
        self.layers = dict()
        self.virtualMapCanvas = QgsMapCanvas()
        self.virtualMapCanvas.setCrsTransformEnabled(True)


    def mainWindow(self):
        return self.enmapBox.ui

    def messageBar(self):
        return self.enmapBox.ui.messageBar

    def mapCanvas(self):
        assert isinstance(self.virtualMapCanvas, QgsMapCanvas)
        self.virtualMapCanvas.setLayerSet([])

        for ds in self.enmapBox.dataSourceManager.mSources:
            if isinstance(ds, DataSourceSpatial):
                uri = ds.uri()
                if uri not in self.layers.keys():
                    lyr = ds.createUnregisteredMapLayer()
                    QgsMapLayerRegistry.instance().addMapLayer(lyr, addToLegend=False)
                    self.layers[uri] = lyr

        if len(self.layers.values()) > 0:
            lyr = self.layers.values()[0]
            self.virtualMapCanvas.mapSettings().setDestinationCrs(lyr.crs())
            self.virtualMapCanvas.setExtent(lyr.extent())
            self.virtualMapCanvas.setLayerSet([QgsMapCanvasLayer(l) for l in self.layers.values()])

        logger.debug('layers shown in (temporary) QgsInterface::mapCanvas() {}'.format(len(self.virtualMapCanvas.layers())))
        return self.virtualMapCanvas

    def firstRightStandardMenu(self):
        return self.enmapBox.ui.menuApplications

    def registerMainWindowAction(self, action, defaultShortcut):
        self.enmapBox.ui.addAction(action)
        pass

    def vectorMenu(self):
        s = ""

    def addDockWidget(self, area, dockwidget):
        self.enmapBox.ui.addDockWidget(area, dockwidget)

    def openMessageLog(self):
        logger.debug('TODO: implement openMessageLog')

        pass

    def refreshLayerSymbology(self, layerId):
        pass


    def legendInterface(self):
        """DockManager implements legend interface"""
        return self.enmapBox.dockManager


    ###
    ###
    ###
    ###
    ###
    ###
    ###
    ###
    @pyqtSlot('QStringList')
    def addLayers(self, layers):
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        # LOGGER.debug('addLayers called on qgis_interface')
        # LOGGER.debug('Number of layers being added: %s' % len(layers))
        # LOGGER.debug('Layer Count Before: %s' % len(self.canvas.layers()))
        current_layers = self.canvas.layers()
        final_layers = []
        for layer in current_layers:
            final_layers.append(QgsMapCanvasLayer(layer))
        for layer in layers:
            final_layers.append(QgsMapCanvasLayer(layer))

        self.canvas.setLayerSet(final_layers)
        # LOGGER.debug('Layer Count After: %s' % len(self.canvas.layers()))

    @pyqtSlot('QgsMapLayer')
    def addLayer(self, layer):
        """Handle a layer being added to the registry so it shows up in canvas.

        :param layer: list<QgsMapLayer> list of map layers that were added

        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.

        .. note: The addLayer method was deprecated in QGIS 1.8 so you should
                 not need this method much.
        """
        pass

    @pyqtSlot()
    def removeAllLayers(self):

        """Remove layers from the canvas before they get deleted."""
        self.virtualMapCanvas.setLayerSet([])

    def newProject(self):
        """Create new project."""
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zoom to the map full extent."""
        pass

    def zoomToPrevious(self):
        """Zoom to previous view extent."""
        pass

    def zoomToNext(self):
        """Zoom to next view extent."""
        pass

    def zoomToActiveLayer(self):
        """Zoom to extent of active layer."""
        pass

    def addVectorLayer(self, path, base_name, provider_key):
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        pass

    def addRasterLayer(self, path, base_name):
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        pass

    def activeLayer(self):
        """Get pointer to the active layer (layer selected in the legend)."""
        # noinspection PyArgumentList
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for item in layers:
            return layers[item]

    def addToolBarIcon(self, action):
        """Add an icon to the plugins toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def removeToolBarIcon(self, action):
        """Remove an action (icon) from the plugin toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def addToolBar(self, name):
        """Add toolbar with specified name.

        :param name: Name for the toolbar.
        :type name: str
        """
        pass



class EnMAPBox(QObject):

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        splash = EnMAPBoxSplashScreen(self)

        if not HIDE_SPLASHSCREEN:
            splash.show()
        QApplication.processEvents()

        assert EnMAPBox._instance is None
        super(EnMAPBox, self).__init__()

        EnMAPBox._instance = self

        splash.showMessage('Load Interfaces')
        self.ifaceSimulation = EnMAPBoxQgisInterface(self)
        self.iface = iface

        # init QGIS Processing Framework, if necessary
        if qgsUtils.iface is None:
            # there is not running QGIS Instance. This means the entire QGIS processing framework was not
            # initialized at all.
            qgsUtils.iface = self.ifaceSimulation

        # register loggers etc.
        msgLog = QgsMessageLog.instance()
        msgLog.messageReceived.connect(self.onLogMessage)

        assert isinstance(qgsUtils.iface, QgisInterface)
        splash.showMessage('Load UI')
        self.ui = EnMAPBoxUI()

        #define managers (the center of all actions and all evil)
        import enmapbox.gui
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager

        self.dataSourceManager = DataSourceManager()

        self.dockManager = DockManager()
        self.dockManager.connectDataSourceManager(self.dataSourceManager)
        #self.enmapBox = enmapbox
        self.dataSourceManager.sigDataSourceRemoved.connect(self.dockManager.removeDataSource)
        self.dockManager.connectDockArea(self.ui.dockArea)

        splash.showMessage('Load Processing Algorithms Manager')
        self.processingAlgManager = ProcessingAlgorithmsManager(self)

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
        self.ui.actionAddWebView.triggered.connect(lambda: self.dockManager.createDock('WEBVIEW'))
        self.ui.actionAddMimeView.triggered.connect(lambda : self.dockManager.createDock('MIME'))

        #activate map tools
        self.ui.actionZoomIn.triggered.connect(lambda : self.dockManager.activateMapTool('ZOOM_IN'))
        self.ui.actionZoomOut.triggered.connect(lambda: self.dockManager.activateMapTool('ZOOM_OUT'))
        self.ui.actionMoveCenter.triggered.connect(lambda: self.dockManager.activateMapTool('MOVE_CENTER'))
        self.ui.actionPan.triggered.connect(lambda: self.dockManager.activateMapTool('PAN'))
        self.ui.actionZoomFullExtent.triggered.connect(lambda: self.dockManager.activateMapTool('ZOOM_FULL'))
        self.ui.actionZoomPixelScale.triggered.connect(lambda: self.dockManager.activateMapTool('ZOOM_PIXEL_SCALE'))
        self.ui.actionIdentify.triggered.connect(lambda : self.dockManager.activateMapTool('CURSORLOCATIONVALUE'))
        self.ui.actionSettings.triggered.connect(self.saveProject)
        self.ui.actionExit.triggered.connect(self.exit)



        # from now on other routines expect the EnMAP-Box to act like QGIS
        if enmapbox.gui.LOAD_PROCESSING_FRAMEWORK:
            # connect managers with widgets
            splash.showMessage('Connect Processing Algorithm Manager')
            self.ui.processingPanel.connectProcessingAlgManager(self.processingAlgManager)

            def initQPFW():
                logger.debug('initialize own QGIS Processing framework')
                from processing.core.Processing import Processing
                Processing.initialize()

                from enmapboxplugin.processing.EnMAPBoxAlgorithmProvider import EnMAPBoxAlgorithmProvider

                Processing.addProvider(EnMAPBoxAlgorithmProvider())


            initQPFW()
            s = ""
            try:
                initQPFW()
                self.ui.menuProcessing.setEnabled(True)
                self.ui.menuProcessing.setVisible(True)
                logger.debug('QGIS Processing framework initialized')
            except:
                self.ui.menuProcessing.setEnabled(False)
                self.ui.menuProcessing.setVisible(False)
                logger.warning('Failed to initialize QGIS Processing framework')
            s = ""

        #load EnMAP-Box applications
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)
        defaultDir = os.path.join(DIR_ENMAPBOX, *['apps'])

        self.applicationRegistry.addApplicationPackageRootFolder(defaultDir)
        otherAppDirs = settings().value('EMB_')



        self.ui.setVisible(True)
        splash.finish(self.ui)


    def exit(self):
        self.ui.close()
        self.deleteLater()

    LUT_MESSAGELOGLEVEL = {
                QgsMessageLog.INFO:'INFO',
                QgsMessageLog.CRITICAL:'INFO',
                QgsMessageLog.WARNING:'WARNING'}
    LUT_MSGLOG2MSGBAR ={QgsMessageLog.INFO:QgsMessageBar.INFO,
                        QgsMessageLog.CRITICAL:QgsMessageBar.WARNING,
                        QgsMessageLog.WARNING:QgsMessageBar.WARNING,
                        }

    def onLogMessage(self, message, tag, level):
        m = message.split('\n')
        if '' in message.split('\n'):
            m = m[0:m.index('')]
        m = '\n'.join(m)
        #todo: add other prefixes of interest

        if not re.search('enmapbox', m):
            return

        if level in [QgsMessageLog.CRITICAL, QgsMessageLog.WARNING]:
            widget = self.ui.messageBar.createMessage(tag, message)
            button = QPushButton(widget)
            button.setText("Show")
            from enmapbox.gui.utils import showMessage
            button.pressed.connect(lambda: showMessage(message, '{}'.format(tag), level))
            widget.layout().addWidget(button)
            self.ui.messageBar.pushWidget(widget,
                              EnMAPBox.LUT_MSGLOG2MSGBAR.get(level, QgsMessageBar.INFO),
                              SETTINGS.value('EMB_MESSAGE_TIMEOUT', 0))

        #print on normal console
        print('{}({}): {}'.format(tag, level, message))

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

    def openExampleData(self, mapWindows=0):
        import enmapbox.testdata
        from enmapbox.gui.utils import file_search
        dir = os.path.dirname(enmapbox.testdata.__file__)
        files = file_search(dir, re.compile('.*(bsq|img|shp)$', re.I), recursive=True)

        for file in files:
            self.addSource(file)
        for n in range(mapWindows):
            dock = self.createDock('MAP')
            lyrs = [src.createUnregisteredMapLayer()
                    for src in self.dataSourceManager.sources(sourceTypes=['RASTER','VECTOR'])]
            dock.addLayers(lyrs)


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
        raise NotImplementedError()


    def restoreProject(self):
        raise NotImplementedError()

    sigCurrentLocationChanged = pyqtSignal(SpatialPoint)
    def currentLocation(self):
        """
        Returns the SpatialPoint of the map location last clicked by identify
        :return: SpatialPoint
        """

    sigCurrentSpectraChanged = pyqtSignal(list)
    def currentSpectra(self):
        """
        Returns the spectra currently selected using the profile tool.
        :return: [list-of-spectra]
        """

        raise NotImplementedError('EnMAPBox.currentSpectra')

    def dataSources(self, sourceType):
        """
        Returns a list of URIs to the data sources of type "sourceType" opened in the EnMAP-Box
        :param sourceType: ['ALL', 'RASTER''VECTOR', 'MODEL'],
                            see enmapbox.gui.datasourcemanager.DataSourceManager.SOURCE_TYPES
        :return: [list-of-datasource-URIs]
        """
        return self.dataSourceManager.getUriList(sourceType)


    def createDock(self, *args, **kwds):
        return self.dockManager.createDock(*args, **kwds)


    def removeDock(self, *args, **kwds):
        self.dockManager.removeDock(*args, **kwds)

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, qgis.gui.QgisInterface)

    def addSource(self, source, name=None):
        return self.dataSourceManager.addSource(source, name=name)

    def menu(self, title):
        for menu in self.ui.menuBar().findChildren(QMenu):
            if str(menu.title()) == title:
                return menu
        return None

    def menusWithTitle(self, title):
        return self.ui.menusWithTitle(title)

    def getURIList(self, *args, **kwds):
        return self.dataSourceManager.getURIList(*args, **kwds)

    @staticmethod
    def getIcon():
        return getIcon()

    def run(self):
        self.ui.show()
        pass


