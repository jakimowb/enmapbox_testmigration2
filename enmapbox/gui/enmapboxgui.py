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
import enmapbox
from qgis import utils as qgsUtils
import qgis.utils
from qgis.PyQt.QtGui import QGuiApplication
from enmapbox.gui.docks import *
from enmapbox.gui.datasources import *
from enmapbox import DEBUG, DIR_ENMAPBOX
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.maptools import *
# if qgis.utils.iface is None:
#    qgis.utils.iface = EnMAPBoxQgisInterface()

SETTINGS = enmapboxSettings()
HIDE_SPLASHSCREEN = SETTINGS.value('EMB_SPLASHSCREEN', False)

class Views(object):
    def __init__(self):
        raise Exception('This class is not for any instantiation')

    MapView= 'MAP'
    SpecLibView = 'SPECLIB'
    TextView = 'TEXT'
    EmptyView = 'EMPTY'






class CentralFrame(QFrame):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    def __init__(self, *args, **kwds):
        super(CentralFrame, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        pass
        # self.sigDragEnterEvent.emit(event)

    def dragMoveEvent(self, event):
        pass
        # self.sigDragMoveEvent.emit(event)

    def dragLeaveEvent(self, event):
        pass
        # self.sigDragLeaveEvent(event)

    def dropEvent(self, event):
        pass
        # self.sigDropEvent.emit(event)


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

        # self.showMaximized()
        self.setAcceptDrops(True)
        import enmapbox
        self.setWindowTitle('EnMAP-Box 3 ({})'.format(enmapbox.__version__))

    def menusWithTitle(self, title):
        return [m for m in self.findChildren(QMenu) if m.title() == title]

    def closeEvent(event):
        pass


def getIcon():
    return QIcon(':/enmapbox/icons/enmapbox.svg')



class EnMAPBoxSplashScreen(QSplashScreen):
    def __init__(self, parent=None):
        pm = QPixmap(':/enmapbox/splashscreen.png')
        super(EnMAPBoxSplashScreen, self).__init__(pm)

    def showMessage(self, text, alignment=None, color=None):
        if alignment is None:
            alignment = Qt.AlignLeft | Qt.AlignBottom
        if color is None:
            color = QColor('white')
        super(EnMAPBoxSplashScreen, self).showMessage(text, alignment, color)
        QApplication.processEvents()

class EnMAPBox(QgisInterface, QObject):

    _instance = None
    @staticmethod
    def instance():
        return EnMAPBox._instance



    sigDataSourceAdded = pyqtSignal(str)
    sigSpectralLibraryAdded = pyqtSignal(str)
    sigRasterSourceAdded = pyqtSignal(str)
    sigVectorSourceAdded = pyqtSignal(str)

    sigDataSourceRemoved = pyqtSignal(str)
    sigSpectralLibraryRemoved = pyqtSignal(str)
    sigRasterSourceRemoved = pyqtSignal(str)
    sigVectorSourceRemoved = pyqtSignal(str)

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface:QgisInterface=None):
        assert EnMAPBox.instance() is None
        # necessary to make the resource file available
        from enmapbox.gui.ui import resources
        resources.qInitResources()
        QObject.__init__(self)
        # super(EnMAPBox, self).__init__()
        QgisInterface.__init__(self)
        splash = EnMAPBoxSplashScreen(self)
        if not HIDE_SPLASHSCREEN:
            splash.show()
        QApplication.processEvents()

        splash.showMessage('Load Interfaces')

        # register loggers etc.
        splash.showMessage('Load UI')
        self.ui = EnMAPBoxUI()
        self.ui.closeEvent = self.closeEvent

        self.initQgisInterface()
        self.iface = iface
        self.mMapLayerStore = QgsMapLayerStore()
        if not isinstance(iface, QgisInterface):
            self.initEnMAPBoxAsIFACE()
        self.initPanels()

        if not DEBUG:
            msgLog = QgsApplication.instance().messageLog()
            msgLog.messageReceived.connect(self.onLogMessage)

        assert isinstance(qgsUtils.iface, QgisInterface)

        self.mCurrentSpectra = []  # set of currently selected spectral profiles
        self.mCurrentMapSpectraLoading = 'TOP'

        self.mCurrentMapLocation = None
        self.mMapToolActivator = None
        self.mMapTools = []
        self.mMapToolBlock = False

        # define managers
        import enmapbox.gui
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsManager

        self.dataSourceManager = DataSourceManager()

        #if qgisAppQgisInterface():
        self.dataSourceManager.sigDataSourceAdded.connect(lambda: self.dataSourceManager.exportSourcesToQGISRegistry(False))


        self.dockManager = DockManager()
        self.dockManager.connectDataSourceManager(self.dataSourceManager)

        # self.enmapBox = enmapboxl
        self.dataSourceManager.sigDataSourceRemoved.connect(self.dockManager.removeDataSource)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.onDataSourceRemoved)
        self.dataSourceManager.sigDataSourceAdded.connect(self.onDataSourceAdded)
        self.dockManager.connectDockArea(self.ui.dockArea)
        self.dockManager.sigDockAdded.connect(self.onDockAdded)
        self.dockManager.sigDockRemoved.connect(self.onDockRemoved)

        splash.showMessage('Load Processing Algorithms Manager')
        self.processingAlgManager = ProcessingAlgorithmsManager(self)
        self.ui.dataSourcePanel.connectDataSourceManager(self.dataSourceManager)
        self.ui.dockPanel.connectDockManager(self.dockManager)

        self.ui.centralFrame.sigDragEnterEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragMoveEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragLeaveEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDropEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))

        self.initActions()



        self.ui.cursorLocationValuePanel.sigLocationRequest.connect(lambda: self.setMapTool(MapTools.CursorLocation))

        self.sigCurrentLocationChanged[SpatialPoint, MapCanvas].connect(
            lambda pt, canvas: self.ui.cursorLocationValuePanel.loadCursorLocation(pt, canvas))

        # from now on other routines expect the EnMAP-Box to act like QGIS
        if enmapbox.LOAD_PROCESSING_FRAMEWORK:
            # connect managers with widgets
            splash.showMessage('Connect Processing Algorithm Manager')
            self.ui.processingPanel.connectProcessingAlgManager(self.processingAlgManager)


            try:
                messageLog('initializes an own QGIS Processing framework')
                self.initQGISProcessingFramework()
                #installQPFExtensions()
                self.ui.menuProcessing.setEnabled(True)
                self.ui.menuProcessing.setVisible(True)
                messageLog('QGIS Processing framework initialized')

            except Exception as ex:
                self.ui.menuProcessing.setEnabled(False)
                self.ui.menuProcessing.setVisible(False)
                messageLog('Failed to initialize QGIS Processing framework')
                messageLog('{}'.format(ex))

        # load EnMAP-Box applications
        self.initEnMAPBoxApplications()

        self.ui.setVisible(True)
        splash.finish(self.ui)

        # finally, let this be the EnMAP-Box Singleton
        EnMAPBox._instance = self

    def mapLayerStore(self)->QgsMapLayerStore:
        """
        Returns the EnMAP-Box internal QgsMapLayerStore
        :return: QgsMapLayerStore
        """
        return self.mMapLayerStore

    def initPanels(self):
        # add & register panels
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
        self.ui.dataSourcePanel = addPanel(enmapbox.gui.datasourcemanager.DataSourcePanelUI(self.ui))
        self.ui.dockPanel = addPanel(enmapbox.gui.dockmanager.DockPanelUI(self.ui))
        from enmapbox.gui.cursorlocationvalue import CursorLocationInfoDock
        self.ui.cursorLocationValuePanel = addPanel(CursorLocationInfoDock(self.ui))

        area = Qt.RightDockWidgetArea
        from enmapbox.gui.processingmanager import ProcessingAlgorithmsPanelUI
        self.ui.processingPanel = addPanel(ProcessingAlgorithmsPanelUI(self.ui))

        area = Qt.BottomDockWidgetArea

        # add entries to menu panels
        for dock in self.ui.findChildren(QDockWidget):
            self.ui.menuPanels.addAction(dock.toggleViewAction())

            # tabbify dock widgets

            # self.tabifyDockWidget(self.dockPanel, self.dataSourcePanel)
            # self.tabifyDockWidget(self.processingPanel, self.dataSourcePanel)


    def initEnMAPBoxAsIFACE(self):
        """
        Sets the EnMAP-Box as global iface, so that the EnMAPBox instance serves as QGIS instance
        """
        self.iface = self
        qgis.utils.iface = self

        if enmapbox.LOAD_PROCESSING_FRAMEWORK:

            import processing
            qgis.utils.iface = self.iface
            processing.Processing.initialize()

            import pkgutil
            prefix = str(processing.__name__ + '.')
            for importer, modname, ispkg in pkgutil.walk_packages(processing.__path__, prefix=prefix):
                try:
                    module = __import__(modname, fromlist="dummy")
                    if hasattr(module, 'iface'):
                        #print(modname)
                        module.iface = self.iface
                except:
                    pass
            s = ""

    def initQGISProcessingFramework(self):

        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        if not self.processingAlgManager.enmapBoxProvider():
            QgsApplication.processingRegistry().addProvider(EnMAPBoxAlgorithmProvider())


    def addApplication(self, app):
        """
        :param app: Can be the path of a directory which contains an EnMAP-Box Application or
                    an instance of an EnMAPBoxApplication
        """
        from enmapbox.gui.applications import EnMAPBoxApplication
        if isinstance(app, EnMAPBoxApplication):
            self.applicationRegistry.addApplication(app)
        elif type(app) in [str]:
            self.applicationRegistry.addApplicationPackageSavely(app)
        else:
            raise Exception('argument "app" has unknown type: {}. '.format(str(app)))


    def initActions(self):
        # link action to managers
        self.ui.actionAddDataSource.triggered.connect(lambda : self.dataSourceManager.addDataSourceByDialog())
        self.ui.actionAddMapView.triggered.connect(lambda: self.dockManager.createDock('MAP'))
        self.ui.actionAddTextView.triggered.connect(lambda: self.dockManager.createDock('TEXT'))
        self.ui.actionAddWebView.triggered.connect(lambda: self.dockManager.createDock('WEBVIEW'))
        self.ui.actionAddMimeView.triggered.connect(lambda: self.dockManager.createDock('MIME'))
        self.ui.actionAddSpeclibView.triggered.connect(lambda: self.dockManager.createDock('SPECLIB'))
        self.ui.actionLoadExampleData.triggered.connect(lambda: self.openExampleData(
            mapWindows=1 if len(self.dockManager.docks(MapDock)) == 0 else 0))
        # activate map tools
        self.ui.actionZoomIn.triggered.connect(lambda: self.setMapTool(MapTools.ZoomIn))
        self.ui.actionZoomOut.triggered.connect(lambda: self.setMapTool(MapTools.ZoomOut))
        self.ui.actionMoveCenter.triggered.connect(lambda: self.setMapTool(MapTools.MoveToCenter))
        self.ui.actionPan.triggered.connect(lambda: self.setMapTool(MapTools.Pan))
        self.ui.actionZoomFullExtent.triggered.connect(lambda: self.setMapTool(MapTools.ZoomFull))
        self.ui.actionZoomPixelScale.triggered.connect(lambda: self.setMapTool(MapTools.ZoomPixelScale))
        self.ui.actionIdentify.triggered.connect(lambda: self.setMapTool(MapTools.CursorLocation))
        self.ui.actionSaveProject.triggered.connect(lambda: self.saveProject(saveAs=False))
        self.ui.actionSaveProjectAs.triggered.connect(lambda: self.saveProject(saveAs=True))
        from enmapbox.gui.mapcanvas import CanvasLinkDialog
        self.ui.actionMapLinking.triggered.connect(lambda : CanvasLinkDialog.showDialog(parent=self.ui, canvases=self.mapCanvases()))
        from enmapbox.gui.about import AboutDialog
        self.ui.actionAbout.triggered.connect(lambda: AboutDialog(parent=self.ui).show())
        from enmapbox.gui.settings import showSettingsDialog
        self.ui.actionProjectSettings.triggered.connect(lambda: showSettingsDialog(self.ui))
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.actionSelectProfiles.triggered.connect(lambda: self.setMapTool(MapTools.SpectralProfile))

        import webbrowser
        self.ui.actionOpenIssueReportPage.triggered.connect(lambda : webbrowser.open(enmapbox.CREATE_ISSUE))
        self.ui.actionOpenProjectPage.triggered.connect(lambda: webbrowser.open(enmapbox.REPOSITORY))
        self.ui.actionOpenOnlineDocumentation.triggered.connect(lambda : webbrowser.open(enmapbox.DOCUMENTATION))

    sigDockAdded = pyqtSignal(Dock)

    def onDockAdded(self, dock):
        assert isinstance(dock, Dock)
        from enmapbox.gui.mapcanvas import MapDock

        if isinstance(dock, SpectralLibraryDock):
            dock.sigLoadFromMapRequest.connect(lambda: self.setMapTool(MapTools.SpectralProfile))
            self.sigCurrentSpectraChanged.connect(dock.speclibWidget.setCurrentSpectra)

        if isinstance(dock, MapDock):
            self.sigMapCanvasAdded.emit(dock.mapCanvas())

        self.sigDockAdded.emit(dock)

    sigCanvasRemoved = pyqtSignal(MapCanvas)
    def onDockRemoved(self, dock):
        if isinstance(dock, MapDock):
            self.sigCanvasRemoved.emit(dock.mapCanvas())


    def setCurrentMapSpectraLoading(self, mode:str):
        """
        Sets the way how SpectralProfiles will be loaded from a map position
        :param mode: str 'TOP' for first raster layer spectrum only, 'ALL' for all raster layers
        """
        assert mode in ['TOP','ALL']
        self.mCurrentMapSpectraLoading = mode

    @pyqtSlot(SpatialPoint, QgsMapCanvas)
    def loadCurrentMapSpectra(self, spatialPoint, mapCanvas):
        assert self.mCurrentMapSpectraLoading in ['TOP', 'ALL']
        assert isinstance(spatialPoint, SpatialPoint)
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

        # if len(currentSpectra) > 0:
        self.setCurrentSpectra(currentSpectra)

    def activateMapTool(self, mapToolKey, *args, **kwds):
        import warnings
        warnings.warn('Please use setMapTool instead', DeprecationWarning)
        self.setMapTool(mapToolKey, *args, **kwds)

    def setMapTool(self, mapToolKey, *args, **kwds):
        # filter map tools
        self.mMapToolActivator = self.sender()

        #disconnect previous map-tools?

        del self.mMapTools[:]

        for canvas in self.mapCanvases():
            mt = None
            if mapToolKey in MapTools.mapToolKeys():
                mt = MapTools.create(mapToolKey, canvas, *args, **kwds)

            if isinstance(mapToolKey, QgsMapTool):
                mt = MapTools.copy(mapToolKey, canvas, *args, **kwds)

            if isinstance(mt, QgsMapTool):
                canvas.setMapTool(mt)
                self.mMapTools.append(mt)

                #if required, link map-tool with specific EnMAP-Box slots
                if type(mt) is CursorLocationMapTool:
                    mt.sigLocationRequest[SpatialPoint, QgsMapCanvas].connect(self.setCurrentLocation)

                if type(mt) is SpectralProfileMapTool:
                    mt.sigLocationRequest[SpatialPoint, QgsMapCanvas].connect(self.loadCurrentMapSpectra)

        return self.mMapTools



    def initEnMAPBoxApplications(self):
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)

        INTERNAL_APPS = jp(DIR_ENMAPBOX, *['coreapps'])
        EXTERNAL_APPS = jp(DIR_ENMAPBOX, *['apps'])

        listingBasename = 'enmapboxapplications.txt'

        if enmapbox.LOAD_INTERNAL_APPS:
            self.applicationRegistry.addApplicationFolder(INTERNAL_APPS, isRootFolder=True)
        p = os.path.join(INTERNAL_APPS, listingBasename)
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        if enmapbox.LOAD_EXTERNAL_APPS:
            self.applicationRegistry.addApplicationFolder(EXTERNAL_APPS, isRootFolder=True)
        p = os.path.join(INTERNAL_APPS, listingBasename)
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        #find root folders
        from enmapbox.gui.settings import enmapboxSettings
        settings = enmapboxSettings()
        for appDir in re.split('[:;]', settings.value('EMB_APPLICATION_PATH', '')):
            if os.path.isdir(appDir):
                self.applicationRegistry.addApplicationFolder(appDir, isRootFolder=True)
            p = os.path.join(INTERNAL_APPS, listingBasename)
            if os.path.isfile(p):
                self.applicationRegistry.addApplicationListing(p)



    def exit(self):
        self.ui.close()
        self.deleteLater()

    def onLogMessage(self, message, tag, level):
        m = message.split('\n')
        if '' in message.split('\n'):
            m = m[0:m.index('')]
        m = '\n'.join(m)


        if not DEBUG and not re.search('(enmapbox|plugins)', m):
            return

        #print('{}({}): {}'.format(tag, level, message))

        if False and level in [Qgis.Critical, Qgis.Warning]:
            widget = self.ui.messageBar.createMessage(tag, message)
            button = QPushButton(widget)
            button.setText("Show")
            from enmapbox.gui.utils import showMessage
            button.pressed.connect(lambda: showMessage(message, '{}'.format(tag), level))
            widget.layout().addWidget(button)
            self.ui.messageBar.pushWidget(widget,level,SETTINGS.value('EMB_MESSAGE_TIMEOUT', 0))

            # print on normal console


    def onDataDropped(self, droppedData):
        assert isinstance(droppedData, list)
        mapDock = None
        from enmapbox.gui.datasources import DataSourceSpatial
        for dataItem in droppedData:
            if isinstance(dataItem, DataSourceSpatial):
                dataSources = self.dataSourceManager.addSource(dataItem)
                if mapDock is None:
                    mapDock = self.createDock('MAP')
                mapDock.addLayers([ds.createRegisteredMapLayer() for ds in dataSources])

            #any other types to handle?


    def openExampleData(self, mapWindows=0):
        """
        Opens the example data
        :param mapWindows: number of new MapDocks to be opened
        """
        from enmapbox.dependencycheck import missingTestdata, installTestdata
        if missingTestdata():
            installTestdata()

        if not missingTestdata():

            import enmapboxtestdata
            from enmapbox.gui.utils import file_search
            dir = os.path.dirname(enmapboxtestdata.__file__)
            files = file_search(dir, re.compile('.*(bsq|sli|img|shp)$', re.I), recursive=True)

            added = self.addSources(files)

            for n in range(mapWindows):
                dock = self.createDock('MAP')
                assert isinstance(dock, MapDock)
                lyrs = []
                for src in self.dataSourceManager.sources(sourceTypes=['RASTER', 'VECTOR']):
                    lyr = src.createUnregisteredMapLayer()
                    lyrs.append(lyr)

                dock.addLayers(lyrs)



    def onDataSourceRemoved(self, dataSource:DataSource):

        self.sigDataSourceRemoved.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceRaster):
            self.sigRasterSourceRemoved.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceVector):
            self.sigVectorSourceRemoved.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceSpectralLibrary):
            self.sigSpectralLibraryRemoved.emit(dataSource.uri())

    def onDataSourceAdded(self, dataSource:DataSource):

        self.sigDataSourceAdded.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceRaster):
            self.sigRasterSourceAdded.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceVector):
            self.sigVectorSourceAdded.emit(dataSource.uri())
        if isinstance(dataSource, DataSourceSpectralLibrary):
            self.sigSpectralLibraryAdded.emit(dataSource.uri())


    sigMapCanvasAdded = pyqtSignal(MapCanvas)

    def saveProject(self, saveAs=False):
        proj = QgsProject.instance()
        path = proj.fileName()
        if saveAs or not os.path.exists(path):
            path = QFileDialog.getSaveFileName(self.ui, \
                                               'Choose a filename to save the QGIS project file',
                                               # directory=os.path.dirname(path)
                                               filter='QGIS files (*.qgs *.QGIS)')
            if len(path) > 0:
                proj.setFileName(path)

        proj.write()

    def restoreProject(self):
        raise NotImplementedError()

    sigCurrentLocationChanged = pyqtSignal([SpatialPoint],
                                           [SpatialPoint, QgsMapCanvas])


    def setCurrentLocation(self, spatialPoint, mapCanvas=None):
        assert isinstance(spatialPoint, SpatialPoint)

        self.mCurrentMapLocation = spatialPoint
        self.sigCurrentLocationChanged[SpatialPoint].emit(self.mCurrentMapLocation)
        if isinstance(mapCanvas, QgsMapCanvas):
            self.sigCurrentLocationChanged[SpatialPoint, QgsMapCanvas].emit(self.mCurrentMapLocation, mapCanvas)

    def currentLocation(self):
        """
        Returns the SpatialPoint of the map location last clicked by identify
        :return: SpatialPoint
        """
        return self.mCurrentMapLocation

    sigCurrentSpectraChanged = pyqtSignal(list)

    def setCurrentSpectra(self, spectra:list):

        b = len(self.mCurrentSpectra) == 0
        self.mCurrentSpectra = spectra[:]
        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra[:])

    def currentSpectra(self)->list:
        """
        Returns the spectra currently selected using the profile tool.

        :return: [list-of-spectra]
        """
        return self.mCurrentSpectra[:]

    def dataSources(self, sourceType='ALL')->list:
        """
        Returns a list of URIs to the data sources of type "sourceType" opened in the EnMAP-Box
        :param sourceType: ['ALL', 'RASTER', 'VECTOR', 'MODEL'],
                            see enmapbox.gui.datasourcemanager.DataSourceManager.SOURCE_TYPES
        :return: [list-of-datasource-URIs (str)]
        """
        return self.dataSourceManager.uriList(sourceType)

    def createDock(self, *args, **kwds)->Dock:
        """
        Create and returns a new Dock
        :param args:
        :param kwds:
        :return:
        """
        return self.dockManager.createDock(*args, **kwds)

    def removeDock(self, *args, **kwds):
        self.dockManager.removeDock(*args, **kwds)

    def isLinkedWithQGIS(self):
        return self.iface is not None and isinstance(self.iface, QgisInterface)

    def addSources(self, sourceList):
        """
        :param sourceList:
        :return: Returns a list of added DataSources or the list of DataSources that were derived from a single data source uri.
        """
        assert isinstance(sourceList, list)
        return self.dataSourceManager.addSources(sourceList)

    def addSource(self, source, name=None):
        """
        Returns a list of added DataSources or the list of DataSources that were derived from a single data source uri.
        :param source:
        :param name:
        :return: [list-of-dataSources]
        """
        return self.dataSourceManager.addSource(source, name=name)


    def removeSources(self, dataSourceList:list=None):
        self.dataSourceManager.removeSources(dataSourceList)

    def removeSource(self, source):
        self.dataSourceManager.removeSource(source)

    def menu(self, title)->QMenu:
        """
        Returns the QMenu with name "title"
        :param title: str
        :return: QMenu
        """
        for menu in self.ui.menuBar().findChildren(QMenu):
            if menu.title() == title:
                return menu
        return None

    def menusWithTitle(self, title):
        return self.ui.menusWithTitle(title)

    def getURIList(self, *args, **kwds):
        return self.dataSourceManager.getURIList(*args, **kwds)

    @staticmethod
    def getIcon():
        """
        Returns the EnMAP-Box icon.
        :return: QIcon
        """
        return getIcon()

    def run(self):
        """
        Shows the EnMAP-Box GUI and centers it to the middle of the primary screen.
        """
        self.ui.show()
        screen = QGuiApplication.primaryScreen()
        rect = screen.geometry()
        assert isinstance(rect, QRect)
        f = 0.8
        newSize = QSize(int(f * rect.width()), int(f * rect.height()))

        geom = QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter,
                                  newSize, QApplication.instance().desktop().availableGeometry())
        self.ui.setGeometry(geom)


    def closeEvent(self, event):
        assert isinstance(event, QCloseEvent)
        if True:

            # de-refere the EnMAP-Box Singleton
            EnMAPBox._instance = None
            self.sigClosed.emit()
            event.accept()
        else:
            event.ignore()

    sigClosed = pyqtSignal()

    def close(self):
        self.ui.close()
        EnMAPBox._instance = None


    """
    Implementation of QGIS Interface 
    """

    def initQgisInterface(self):
        """
        Initializes internal variables required to provide the QgisInterface
        :return:
        """
        self.mQgisInterfaceLayerSet = dict()
        self.mQgisInterfaceMapCanvas = MapCanvas()

    ### SIGNALS from QgisInterface ####

    initializationCompleted = pyqtSignal()
    layerSavedAs = pyqtSignal(QgsMapLayer, str)
    currentLayerChanged = pyqtSignal(QgsMapLayer)


    ### ACTIONS ###
    def actionAbout(self):
        return self.ui.actionAbout

    def actionAddAfsLayer(self):
        return self.ui.actionAddDataSource

    def actionAddAllToOverview(self):
        return self.ui.actionAddDataSource

    def actionAddAmsLayer(self):
        return self.ui.actionAddDataSource

    def actionAddFeature(self):
        return self.ui.actionAddDataSource

    def actionAddOgrLayer(self):
        return self.ui.actionAddDataSource

    # def actionAddPart(self): pass
    def actionAddPgLayer(self):
        return self.ui.actionAddDataSource

    def actionAddRasterLayer(self):
        return self.ui.actionAddDataSource

    # def actionAddRing(self):
    # def actionAddToOverview(self):
    def actionAddWmsLayer(self):
        return self.ui.actionAddDataSource

    def actionAllEdits(self):
        pass

    def actionCancelAllEdits(self):
        pass

    def actionCancelEdits(self):
        pass

    def actionCheckQgisVersion(self):
        pass  # todo: set EnMAP-Box check

    def actionCopyFeatures(self):
        pass

    def actionCopyLayerStyle(self):
        pass

    def actionCustomProjection(slf):
        pass

    def actionCutFeatures(self):
        pass

    def actionDeletePart(self):
        pass

    def actionDeleteRing(self):
        pass

    def actionDeleteSelected(self):
        pass

    def actionDraw(self):
        pass

    def actionDuplicateLayer(self):
        pass

    def actionExit(self):
        return self.ui.actionExit()

    def actionFeatureAction(self):
        pass

    def actionHelpContents(self):
        pass

    def actionHideAllLayers(self):
        pass

    def actionHideSelectedLayers(self):
        pass

    def actionIdentify(self):
        return self.ui.actionIdentify

    def actionAddToOverview(self):
        pass

    def actionAddRing(self):
        pass

    def actionAddPart(self):
        pass

    def actionLayerProperties(self):
        pass

    def actionLayerSaveAs(self):
        pass

    def actionLayerSelectionSaveAs(self):
        pass

    def actionManagePlugins(self):
        pass

    def actionMapTips(self):
        pass

    def actionMeasure(self):
        pass

    def actionMeasureArea(self):
        pass

    def actionMoveFeature(self):
        pass

    def actionNewBookmark(self):
        pass

    def actionNewProject(self):
        pass

    def actionNewVectorLayer(self):
        pass

    def actionNodeTool(self):
        pass

    def actionOpenFieldCalculator(self):
        pass

    def actionOpenProject(self):
        pass

    def actionOpenTable(self):
        pass

    def actionOptions(self):
        pass

    def actionPan(self):
        return self.ui.actionPan

    def actionPanToSelected(self):
        pass

    def actionPasteFeatures(self):
        pass

    def actionPasteLayerStyle(self):
        pass

    def actionPluginListSeparator(self):
        pass

    def actionPrintComposer(self):
        pass

    def actionProjectProperties(self):
        pass

    def actionQgisHomePage(self):
        pass

    def actionRemoveAllFromOverview(self):
        pass

    def actionRemoveLayer(self):
        pass

    def actionRollbackAllEdits(self):
        pass

    def actionRollbackEdits(self):
        pass

    def actionSaveActiveLayerEdits(self):
        pass

    def actionSaveAllEdits(self):
        pass

    def actionSaveEdits(self):
        pass

    def actionSaveMapAsImage(self):
        pass

    def actionSaveProject(self):
        pass

    def actionSaveProjectAs(self):
        pass

    def actionSelect(self):
        pass

    def actionSelectFreehand(self):
        pass

    def actionSelectPolygon(self):
        pass

    def actionSelectRadius(self):
        pass

    def actionSelectRectangle(self):
        pass

    def actionShowAllLayers(self):
        pass

    def actionShowBookmarks(self):
        pass

    def actionShowComposerManager(self):
        pass

    def actionShowPythonDialog(self):
        pass

    def actionShowSelectedLayers(self):
        pass

    def actionSimplifyFeature(self):
        pass

    def actionSplitFeatures(self):
        pass

    def actionSplitParts(self):
        pass

    def actionToggleEditing(self):
        pass

    def actionToggleFullScreen(self):
        pass

    def actionTouch(self):
        pass

    def actionZoomActualSize(self):
        return self.ui.actionZoomPixelScale

    def actionZoomFullExtent(self):
        return self.ui.actionZoomFullExtent

    def actionZoomIn(self):
        return self.ui.actionZoomIn

    def actionZoomLast(self):
        pass

    def actionZoomNext(self):
        pass

    def actionZoomOut(self):
        return self.ui.actionZoomOut

    def actionZoomToLayer(self):
        pass

    def actionZoomToSelected(self):
        pass



    def activeComposers(self):
        pass

    ###
    ### addXYZ() routines
    ####
    def addDatabaseToolBarIcon(self, QAction):
        pass

    def addDatabaseToolBarWidget(self, QWidget):
        pass


    def addDockWidget(self, area, dockWidget, orientation=None):
        'Add a dock widget to the main window'
        self.ui.addDockWidget(area, dockWidget, orientation=orientation)

    def addLayerMenu(self):
        pass

    def mainWindow(self):
        return self.ui

    def messageBar(self):
        return self.ui.messageBar

    def iconSize(self, dockedToolbar=False):
        #return self.ui.actionAddDataSource.icon().availableSizes()[0]
        return QSize(16,16)

    def mapCanvases(self):
        """
        Returns all MapCanvas(QgsMapCanvas) objects known to the EnMAP-Box
        :return: [list-of-MapCanvases]
        """
        from enmapbox.gui.mapcanvas import MapDock
        return [d.mCanvas for d in self.dockManager.docks() if isinstance(d, MapDock)]

    def mapCanvas(self, virtual=False)->MapCanvas:
        """
        Returns a virtual QgsMapCanvas that contains all QgsMapLayers visible in the EnMAP-Box DataSource Manager
        :return: QgsMapCanvas
        """


        if virtual:
            assert isinstance(self.mQgisInterfaceMapCanvas, QgsMapCanvas)
            self.mQgisInterfaceMapCanvas.setLayers([])

            layers = []
            for ds in self.dataSourceManager.sources():
                if isinstance(ds, DataSourceSpatial):
                    layers.append(ds.createUnregisteredMapLayer())
            self.mQgisInterfaceMapCanvas.setLayers(layers)
            if len(layers) > 0:
                self.mQgisInterfaceMapCanvas.mapSettings().setDestinationCrs(layers[0].crs())
                self.mQgisInterfaceMapCanvas.setExtent(layers[0].extent())

            return self.mQgisInterfaceMapCanvas
        mapDocks = self.dockManager.docks(dockType='MAP')
        if len(mapDocks) > 0:
            return mapDocks[0].mapCanvas()
        else:
            return None


    def firstRightStandardMenu(self)->QMenu:
        return self.ui.menuApplications

    def registerMainWindowAction(self, action, defaultShortcut):
        self.ui.addAction(action)

    def vectorMenu(self):
        return QMenu()

    def addDockWidget(self, area, dockwidget):
        self.ui.addDockWidget(area, dockwidget)

    def loadExampleData(self):
        """
        Loads the EnMAP-Box example data
        """
        self.ui.actionLoadExampleData.trigger()

    def legendInterface(self):
        """DockManager implements legend interface"""
        return self.dockManager

    def refreshLayerSymbology(self, layerId):
        pass

    def openMessageLog(self):

        pass

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
            final_layers.append(layer)
        for layer in layers:
            final_layers.append(layer)

        self.canvas.setLayers(final_layers)
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

        """Remove layers from the virtual QgsMapCanvas before they get deleted."""
        self.mQgisInterfaceMapCanvas.setLayers([])

    def newProject(self):
        """Create new project."""
        # noinspection PyArgumentList
        QgsProject.instance().removeAllMapLayers()

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
        layers = QgsProject.instance().mapLayers()
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
