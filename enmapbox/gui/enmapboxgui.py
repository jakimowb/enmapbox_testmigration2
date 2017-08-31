# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapboxgui.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import absolute_import
from qgis.core import *
from qgis.gui import  *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis import utils as qgsUtils

class EnMAPBoxQgisInterface(QgisInterface):
    """
    Implementation of QgisInterface
    """
    def __init__(self):
        super(EnMAPBoxQgisInterface, self).__init__()

        self.layers = dict()
        self.virtualMapCanvas = QgsMapCanvas()
        self.virtualMapCanvas.setCrsTransformEnabled(True)
        # self.mLog = QgsApplication.instance().messageLog()
        # self.mLog = QgsApplication.messageLog()

    def enmapBox(self):
        return EnMAPBox.instance()

    def mainWindow(self):
        return self.enmapBox().ui

    def messageBar(self):
        return self.enmapBox().ui.messageBar

    def mapCanvas(self):
        assert isinstance(self.virtualMapCanvas, QgsMapCanvas)
        self.virtualMapCanvas.setLayerSet([])

        for ds in self.enmapBox().dataSourceManager.mSources:
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

        logger.debug(
            'layers shown in (temporary) QgsInterface::mapCanvas() {}'.format(len(self.virtualMapCanvas.layers())))
        return self.virtualMapCanvas

    def firstRightStandardMenu(self):
        return self.enmapBox().ui.menuApplications

    def registerMainWindowAction(self, action, defaultShortcut):
        self.enmapBox().ui.addAction(action)
        pass

    def vectorMenu(self):
        s = ""

    def addDockWidget(self, area, dockwidget):
        self.enmapBox().ui.addDockWidget(area, dockwidget)

    def openMessageLog(self):
        logger.debug('TODO: implement openMessageLog')

        pass

    def refreshLayerSymbology(self, layerId):
        pass

    def legendInterface(self):
        """DockManager implements legend interface"""
        return self.enmapBox().dockManager

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


if qgsUtils.iface is None:
    qgsUtils.iface = EnMAPBoxQgisInterface()

from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *

SETTINGS = settings()
HIDE_SPLASHSCREEN = SETTINGS.value('EMB_SPLASHSCREEN', False)

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


        from enmapbox.gui.processingmanager import ProcessingAlgorithmsPanelUI
        self.processingPanel = addPanel(ProcessingAlgorithmsPanelUI(self))

        area = Qt.BottomDockWidgetArea
        from enmapbox.gui.spectrallibraries import SpectraLibraryViewPanel
        self.specLibViewPanel = addPanel(SpectraLibraryViewPanel(self))
        self.specLibViewPanel.setVisible(False)
        #add entries to menu panels
        for dock in self.findChildren(QDockWidget):
            self.menuPanels.addAction(dock.toggleViewAction())


        #tabbify dock widgets

        #self.tabifyDockWidget(self.dockPanel, self.dataSourcePanel)
        #self.tabifyDockWidget(self.processingPanel, self.dataSourcePanel)

    def setIsInitialized(self):
        self.isInitialized = True

    def menusWithTitle(self, title):
        return [m for m in self.findChildren(QMenu) if str(m.title()) == title]


    def closeEvent(event):
        pass




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



class EnMAPBox(QObject):

    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance


    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface):
        assert EnMAPBox.instance() is None
        #necessary to make the resource file available
        from enmapbox.gui.ui import resources

        super(EnMAPBox, self).__init__()
        splash = EnMAPBoxSplashScreen(self)
        if not HIDE_SPLASHSCREEN:
            splash.show()
        QApplication.processEvents()

        splash.showMessage('Load Interfaces')

        self.iface = iface

        # register loggers etc.
        splash.showMessage('Load UI')
        self.ui = EnMAPBoxUI()
        self.ui.closeEvent = self.closeEvent

        msgLog = QgsMessageLog.instance()
        msgLog.messageReceived.connect(self.onLogMessage)

        assert isinstance(qgsUtils.iface, QgisInterface)

        self.mCurrentSpectra=[] #set of currently selected spectral profiles
        self.mCurrentMapSpectraLoading = 'TOP'
        self.sigCurrentSpectraChanged.connect(self.ui.specLibViewPanel.setCurrentSpectra)

        # define managers (the center of all actions and all evil)
        import enmapbox.gui
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager, installQPFExtensions, removeQPFExtensions

        self.dataSourceManager = DataSourceManager()

        self.dockManager = DockManager()
        self.dockManager.connectDataSourceManager(self.dataSourceManager)

        # self.enmapBox = enmapbox
        self.dataSourceManager.sigDataSourceRemoved.connect(self.dockManager.removeDataSource)
        self.dockManager.connectDockArea(self.ui.dockArea)
        self.dockManager.sigDockAdded.connect(self.onDockAdded)

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

        from enmapbox.gui.mapcanvas import MapDock
        self.ui.actionLoadExampleData.triggered.connect(lambda: self.openExampleData(
            mapWindows=1 if len(self.dockManager.docks(MapDock)) == 0 else 0))

        #activate map tools
        self.ui.actionZoomIn.triggered.connect(lambda : self.activateMapTool('ZOOM_IN'))
        self.ui.actionZoomOut.triggered.connect(lambda: self.activateMapTool('ZOOM_OUT'))
        self.ui.actionMoveCenter.triggered.connect(lambda: self.activateMapTool('MOVE_CENTER'))
        self.ui.actionPan.triggered.connect(lambda: self.activateMapTool('PAN'))
        self.ui.actionZoomFullExtent.triggered.connect(lambda: self.activateMapTool('ZOOM_FULL'))
        self.ui.actionZoomPixelScale.triggered.connect(lambda: self.activateMapTool('ZOOM_PIXEL_SCALE'))
        self.ui.actionIdentify.triggered.connect(lambda : self.activateMapTool('CURSORLOCATIONVALUE'))
        self.ui.actionSettings.triggered.connect(self.saveProject)
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.actionSelectProfiles.triggered.connect(lambda : self.activateMapTool('SPECTRUMREQUEST'))
        self.ui.specLibViewPanel.btnLoadfromMap.clicked.connect(lambda: self.activateMapTool('SPECTRUMREQUEST'))

        # from now on other routines expect the EnMAP-Box to act like QGIS
        if enmapbox.gui.LOAD_PROCESSING_FRAMEWORK:
            # connect managers with widgets
            splash.showMessage('Connect Processing Algorithm Manager')
            self.ui.processingPanel.connectProcessingAlgManager(self.processingAlgManager)

            def initQPFW():
                logger.debug('initialize own QGIS Processing framework')
                from processing.core.Processing import Processing
                Processing.initialize()
                from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider

                if not self.processingAlgManager.enmapBoxProvider():
                    Processing.addProvider(EnMAPBoxAlgorithmProvider())


            try:
                initQPFW()
                installQPFExtensions()
                self.ui.menuProcessing.setEnabled(True)
                self.ui.menuProcessing.setVisible(True)

                logger.debug('QGIS Processing framework initialized')

            except Exception as ex:
                self.ui.menuProcessing.setEnabled(False)
                self.ui.menuProcessing.setVisible(False)
                logger.warning('Failed to initialize QGIS Processing framework')
                logger.warning(str(ex))
            s = ""

        #load EnMAP-Box applications
        self.loadEnMAPBoxApplications()


        self.ui.setVisible(True)
        splash.finish(self.ui)

        #finally, let this be the EnMAP-Box Singleton
        EnMAPBox._instance = self


    def onDockAdded(self, dock):
        assert isinstance(dock, Dock)
        from enmapbox.gui.mapcanvas import MapDock
        if isinstance(dock, MapDock):
            dock.canvas.sigProfileRequest.connect(self.loadCurrentMapSpectra)


    def loadCurrentMapSpectra(self, spatialPoint, mapCanvas):
        assert self.mCurrentMapSpectraLoading in ['TOP', 'ALL']
        assert isinstance(spatialPoint, SpatialPoint)
        from enmapbox.gui.mapcanvas import MapCanvas
        assert isinstance(mapCanvas, QgsMapCanvas)

        currentSpectra = []

        lyrs = [l for l in mapCanvas.layers() if isinstance(l, QgsRasterLayer)]
        for lyr in lyrs:
            assert isinstance(lyr, QgsRasterLayer)
            path = lyr.source()
            from enmapbox.gui.spectrallibraries import SpectralProfile
            p = SpectralProfile.fromRasterSource(path, spatialPoint)
            if isinstance(p, SpectralProfile):
                currentSpectra.append(p)
                if self.mCurrentMapSpectraLoading == 'TOP':
                    break

        #if len(currentSpectra) > 0:
        self.setCurrentSpectra(currentSpectra)


    def activateMapTool(self, mapToolKey):
        return self.dockManager.activateMapTool(mapToolKey)


    def loadEnMAPBoxApplications(self):
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)
        appDirs = []
        appDirs.append(os.path.join(DIR_ENMAPBOX, *['coreapps']))
        appDirs.append(os.path.join(DIR_ENMAPBOX, *['apps']))
        for appDir in re.split('[:;]', settings().value('EMB_APPLICATION_PATH', '')):
            if os.path.isdir(appDir):
                appDirs.append(appDir)
        for appDir in appDirs:
            self.applicationRegistry.addApplicationPackageRootFolder(appDir)

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

        from enmapbox.gui import DEBUG
        if not DEBUG and not re.search('enmapbox', m):
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
        import enmapboxtestdata
        from enmapbox.gui.utils import file_search
        dir = os.path.dirname(enmapboxtestdata.__file__)
        files = file_search(dir, re.compile('.*(bsq|sli|img|shp)$', re.I), recursive=True)

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

    def setCurrentSpectra(self, spectra):
        assert isinstance(spectra, list)
        b = len(self.mCurrentSpectra) == 0
        self.mCurrentSpectra = spectra[:]

        if b and len(self.mCurrentSpectra) > 0:
            self.ui.specLibViewPanel.setVisible(True)
        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra[:])


    def currentSpectra(self):
        """
        Returns the spectra currently selected using the profile tool.
        :return: [list-of-spectra]
        """
        return self.mCurrentSpectra[:]


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
        return self.iface is not None and isinstance(self.iface, QgisInterface)

    def addSources(self, sourceList):
        return [self.addSource(s) for s in sourceList]

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

    def closeEvent(self, event):
        assert isinstance(event, QCloseEvent)
        if True:

            #de-refere the EnMAP-Box Singleton
            EnMAPBox._instance = None
            enmapbox.gui.processingmanager.removeQPFExtensions()
            self.sigClosed.emit()
            event.accept()
        else:
            event.ignore()

    sigClosed = pyqtSignal()
    def close(self):
        print('CLOSE ENMAPBOX')
        enmapbox.gui.processingmanager.removeQPFExtensions()
        self.ui.close()

        #this will trigger the closeEvent

