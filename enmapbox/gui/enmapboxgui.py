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
import enum, warnings
import enmapbox
from qgis import utils as qgsUtils
import qgis.utils
from enmapbox import messageLog
from enmapbox.gui import *
from enmapbox.gui.docks import *
from enmapbox.gui.dockmanager import DockManagerTreeModel, MapDockTreeNode
from enmapbox.gui.datasources import *
from enmapbox import DEBUG, DIR_ENMAPBOX
from enmapbox.gui.mapcanvas import *
from ..externals.qps.cursorlocationvalue import CursorLocationInfoDock
from ..externals.qps.layerproperties import showLayerPropertiesDialog
from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
from enmapbox.gui.spectralprofilesources import SpectralProfileSourcePanel, SpectralProfileBridge, SpectralProfileSource

SETTINGS = enmapbox.enmapboxSettings()
HIDE_SPLASHSCREEN = SETTINGS.value('EMB_SPLASHSCREEN', False)

HIDDEN_ENMAPBOX_LAYER_GROUP = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_GROUP'
HIDDEN_ENMAPBOX_LAYER_MAPCANVAS = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_MAPCANVAS'
HIDDEN_ENMAPBOX_LAYER_ID = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_ID'
HIDDEN_ENMAPBOX_LAYER_SOURCE = 'ENMAPBOX/HIDDEN_ENMAPBOX_SOURCE_URI'



class EnMAPBoxDocks(enum.Enum):
    MapDock = 'MAP'
    SpectralLibraryDock = 'SPECLIB'
    TextViewDock = 'TEXT'
    MimeDataDock = 'MIME'
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


class EnMAPBoxSplashScreen(QSplashScreen):
    """
    Thr EnMAP-Box Splash Screen
    """
    def __init__(self, parent=None):
        pm = QPixmap(':/enmapbox/gui/ui/logo/splashscreen.png')
        super(EnMAPBoxSplashScreen, self).__init__(parent, pixmap=pm)

    def showMessage(self, text:str, alignment:Qt.Alignment=None, color:QColor=None):
        """
        Shows a message
        :param text:
        :param alignment:
        :param color:
        :return:
        """
        if alignment is None:
            alignment = Qt.AlignCenter | Qt.AlignBottom
        if color is None:
            color = QColor('black')
        super(EnMAPBoxSplashScreen, self).showMessage(text, alignment, color)
        QApplication.processEvents()


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
        self.setCentralWidget(self.centralFrame)
        import enmapbox
        self.setWindowIcon(enmapbox.icon())
        self.setVisible(False)

        if sys.platform == 'darwin':
            self.menuBar().setNativeMenuBar(False)
        # self.showMaximized()
        self.setAcceptDrops(True)

        self.setWindowTitle('EnMAP-Box 3 ({})'.format(enmapbox.__version__))



    def addDockWidget(self, *args, **kwds):

        super(EnMAPBoxUI, self).addDockWidget(*args, **kwds)


    def menusWithTitle(self, title:str):
        """
        Returns the QMenu with title `title`
        :param title: str
        :return: QMenu
        """
        assert isinstance(title, str)
        return [m for m in self.findChildren(QMenu) if m.title() == title]

    def closeEvent(event):
        pass


def getIcon()->QIcon:
    """
    Returns the EnMAP icon
    :return: QIcon
    """
    warnings.warn(DeprecationWarning('Use enmapbox.icon() instead to return the EnMAP-Box icon'))
    return enmapbox.icon()




class EnMAPBox(QgisInterface, QObject):

    _instance = None
    @staticmethod
    def instance():
        return EnMAPBox._instance

    MAPTOOLACTION = 'enmapbox/maptoolkey'

    sigDataSourceAdded = pyqtSignal([str],[DataSource])
    sigSpectralLibraryAdded = pyqtSignal([str],[DataSourceSpectralLibrary])
    sigRasterSourceAdded = pyqtSignal([str],[DataSourceRaster])
    sigVectorSourceAdded = pyqtSignal([str],[DataSourceVector])

    sigDataSourceRemoved = pyqtSignal([str],[DataSource])
    sigSpectralLibraryRemoved = pyqtSignal([str],[DataSourceSpectralLibrary])
    sigRasterSourceRemoved = pyqtSignal([str],[DataSourceRaster])
    sigVectorSourceRemoved = pyqtSignal([str],[DataSourceVector])

    sigMapLayersAdded = pyqtSignal([list], [list, MapCanvas])
    sigMapLayersRemoved = pyqtSignal([list], [list, MapCanvas])

    currentLayerChanged = pyqtSignal(QgsMapLayer)

    sigClosed = pyqtSignal()

    sigCurrentLocationChanged = pyqtSignal([SpatialPoint],
                                           [SpatialPoint, QgsMapCanvas])

    sigCurrentSpectraChanged = pyqtSignal(list)

    sigMapCanvasRemoved = pyqtSignal(MapCanvas)
    sigMapCanvasAdded = pyqtSignal(MapCanvas)

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""
    def __init__(self, iface:QgisInterface=None):
        assert EnMAPBox.instance() is None

        splash = EnMAPBoxSplashScreen(parent=None)
        if not HIDE_SPLASHSCREEN:
            splash.show()

        splash.showMessage('Load UI')
        QApplication.processEvents()

        QObject.__init__(self)
        QgisInterface.__init__(self)

        self.ui = EnMAPBoxUI()


        self.ui.closeEvent = self.closeEvent

        self.mMapLayerStore = QgsMapLayerStore()
        MAP_LAYER_STORES.insert(0, self.mMapLayerStore)

        self.initQgisInterfaceVariables()
        if not isinstance(iface, QgisInterface):
            iface = qgis.utils.iface
        self.iface = iface
        assert isinstance(iface, QgisInterface)

        self.mMapToolKey = MapTools.Pan
        self.mMapToolMode = None

        self.initPanels()

        if not DEBUG:
            msgLog = QgsApplication.instance().messageLog()
            msgLog.messageReceived.connect(self.onLogMessage)

        assert isinstance(qgsUtils.iface, QgisInterface)

        self.mCurrentSpectra = []  # set of currently selected spectral profiles
        self.mCurrentMapLocation = None

        # define managers

        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager

        #
        splash.showMessage('Init DataSourceManager')
        self.dataSourceManager = DataSourceManager()

        self.dataSourceManager.sigDataSourceAdded.connect(self.updateHiddenQGISLayers)
        self.dataSourceManager.sigDataSourceRemoved.connect(self.updateHiddenQGISLayers)

        #self.sigMapCanvasAdded.connect(self.updateHiddenQGISLayers)
        self.sigMapCanvasRemoved.connect(self.updateHiddenQGISLayers)
        self.sigMapLayersAdded.connect(self.updateHiddenQGISLayers)
        self.sigMapLayersRemoved.connect(self.updateHiddenQGISLayers)

        QgsProject.instance().layersAdded.connect(self.addSources)

        self.dockManager = DockManager()
        self.dockManager.connectDataSourceManager(self.dataSourceManager)

        #
        self.dataSourceManager.sigDataSourceRemoved.connect(self.onDataSourceRemoved)
        self.dataSourceManager.sigDataSourceAdded.connect(self.onDataSourceAdded)

        self.dockManager.connectDockArea(self.ui.dockArea)
        self.ui.dataSourcePanel.connectDataSourceManager(self.dataSourceManager)

        self.ui.dockPanel.connectDockManager(self.dockManager)
        self.ui.dockPanel.dockTreeView.currentLayerChanged.connect(self.onCurrentLayerChanged)
        model = self.ui.dockPanel.dockTreeView.model()
        assert isinstance(model, DockManagerTreeModel)

        def onLayerNameChanged(node, name):
            hiddenLayers = []
            if type(node) == QgsLayerTreeLayer:
                eLyr = node.layer()
                hiddenLayers = [l for l in self._hiddenLayers() if l.customProperty(HIDDEN_ENMAPBOX_LAYER_ID) == eLyr.id()]
            elif type(node) == MapDockTreeNode:
                # refresh all layer names from this map canvas
                canvasID = id(node.mapCanvas())
                hiddenLayers = [l for l in self._hiddenLayers() if l.customProperty(HIDDEN_ENMAPBOX_LAYER_MAPCANVAS) == canvasID]

            if len(hiddenLayers) > 0:
                self.updateHiddenLayerNames(hiddenLayers=hiddenLayers)

        model.rootGroup().nameChanged.connect(onLayerNameChanged)

        self.onCurrentLayerChanged(None)
        self.ui.centralFrame.sigDragEnterEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragMoveEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragLeaveEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDropEvent.connect(
            lambda event: self.dockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))

        self.dockManager.sigDockAdded.connect(self.onDockAdded)
        self.dockManager.sigDockRemoved.connect(self.onDockRemoved)


        self.initActions()

        self.ui.cursorLocationValuePanel.sigLocationRequest.connect(lambda: self.setMapTool(MapTools.CursorLocation))

        # load EnMAP-Box applications
        splash.showMessage('Load EnMAPBoxApplications...')
        self.initEnMAPBoxApplications()

        self.ui.setVisible(True)
        splash.finish(self.ui)

        from ..externals.pyqtgraph import setConfigOption
        splash.showMessage('Load EnMAPBoxApplications...')
        setConfigOption('background', 'k')
        setConfigOption('foreground', 'w')

        # finally, let this be the EnMAP-Box Singleton
        EnMAPBox._instance = self
        QApplication.processEvents()
        splash.hide()

    def _hiddenQGISLayerGroup(self, bHide=True)->QgsLayerTreeGroup:
        """
        Returns the hidden QgsLayerTreeGroup in the QGIS Layer Tree
        :return: QgsLayerTreeGroup
        """
        ltv = self.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        root = ltv.model().rootGroup()
        assert isinstance(root, QgsLayerTreeGroup)
        grp = root.findGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        if not isinstance(grp, QgsLayerTreeGroup):
            grp = root.addGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        index = ltv.model().node2index(grp)
        grp.setItemVisibilityChecked(False)
        grp.setCustomProperty('nodeHidden',  'true' if bHide else 'false')
        ltv.setRowHidden(index.row(), index.parent(), bHide)
        return grp

    def _hiddenLayers(self)->list:
        return [l.layer() for l in self._hiddenQGISLayerGroup().findLayers()]


    def updateHiddenQGISLayers(self)->int:
        """
        Ensures that all Layers used in the EnMAP-Box are available and visible in the QGIS Layer Registry as well
        e.g. to be visible in the QgsMapLayerComboBox

        Naming:
            layer name - standard QGIS Layer
            [EnMAP-Box] filename.ext - EnMAP-Box raster/vector data source without any visible layer
            [Map Canvas#n] layer name - EnMAP-Box layer in MapCanvas#n


        Background: removing layers from the QGIS LayerTree releases its C++ memory. Therefore, we need to maintain
                    two separated QgsMapLayerRegistries:
                    1. EnMAPBox.mapLayerRegistry (QgsMapLayerRegistry)
                    2. QgsProject.instance() (QgsProject) -> same accessors to add/remove map layers
        """

        def removeHiddenLayers(layers):
            if len(layers) > 0:
                hiddenGroup = self._hiddenQGISLayerGroup()
                for lyr in layers:
                    assert isinstance(lyr, QgsMapLayer)
                    hiddenGroup.removeLayer(lyr)
                #print('REMOVE {} HIDDEN LAYERS'.format(len(layers)))
                #for l in layers:
                #    print(l)
                QgsProject.instance().removeMapLayers([l.id() for l in layers])

        def addHiddenLayers(layers):
            hiddenGroup = self._hiddenQGISLayerGroup()
            QgsProject.instance().addMapLayers(layers, False)
            for lyr in layers:
                assert isinstance(lyr, QgsMapLayer)
                hiddenGroup.addLayer(lyr)


        # create Lookup for existing MapCanvas layers
        LUT_ECANVAS_LAYERS = {}

        model = self.ui.dockPanel.dockTreeView.model()
        assert isinstance(model, DockManagerTreeModel)

        for mapNode in model.mapDockTreeNodes():
            assert isinstance(mapNode, MapDockTreeNode)
            canvas = mapNode.mapCanvas()
            assert isinstance(canvas, QgsMapCanvas)
            eCanvasID = id(canvas)
            for ltn in mapNode.findLayers():
                assert isinstance(ltn, QgsLayerTreeLayer)
                qLyr = ltn.layer()
                assert isinstance(qLyr, QgsMapLayer)
                eLayerId = qLyr.id()
                LUT_ECANVAS_LAYERS[(eCanvasID, eLayerId)] = qLyr

        enmapboxSourceUris = [src.uri() for src in self.dataSourceManager.sources('SPATIAL')]
        hiddenSourceUris = []
        hiddenCanvasLayers = []
        # remove layers that point to unknown, sources, MapCanvases or layer ids
        toRemove = []
        for qLyr in self._hiddenLayers():
            eLayerUri = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_SOURCE)
            eLayerId = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_ID)
            eCanvasID = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_MAPCANVAS)
            key = (eCanvasID, eLayerId)

            if eLayerUri is not None:
                if eLayerUri not in enmapboxSourceUris:
                    toRemove.append(qLyr)
                else:
                    hiddenSourceUris.append(eLayerUri)
            elif eLayerId is not None:
                if key not in LUT_ECANVAS_LAYERS.keys():
                    toRemove.append(qLyr)
                else:
                    hiddenCanvasLayers.append(key)
        removeHiddenLayers(toRemove)

        toAdd = []

        # add missing source layers
        for src in self.dataSourceManager.sources('SPATIAL'):
            assert isinstance(src, DataSourceSpatial)
            if src.uri() not in hiddenSourceUris:
                qLyr = src.createUnregisteredMapLayer()
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_SOURCE, src.uri())
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_MAPCANVAS, None)
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_ID, None)
                toAdd.append(qLyr)

        # add missing canvas layers.

        for key, eLyr in LUT_ECANVAS_LAYERS.items():
            if not isinstance(eLyr, QgsMapLayer):
                s = ""
            if key not in hiddenCanvasLayers:
                eCanvasID, eLayerId = key
                assert eLayerId == eLyr.id()
                qLyr = eLyr.clone()
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_SOURCE, None)
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_MAPCANVAS, eCanvasID)
                qLyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_ID, eLyr.id())
                eLyr.nameChanged.connect(lambda *args, eLyr=eLyr, qLyr=qLyr: self.updateHiddenLayerName(eLyr, qLyr))
                eLyr.rendererChanged.connect(lambda *args, eLyr=eLyr, qLyr=qLyr: self.updateHiddenLayerRenderer(eLyr, qLyr))
                toAdd.append(qLyr)
        addHiddenLayers(toAdd)
        self.updateHiddenLayerNames()

    def updateHiddenLayerName(self, eLyr:QgsMapLayer, qLyr:QgsMapLayer):
        self.updateHiddenLayerNames(hiddenLayers=[qLyr])

    def updateHiddenLayerRenderer(self, eLyr: QgsMapLayer, qLyr: QgsMapLayer):
        if qLyr.id() in QgsProject.instance().mapLayers().keys() and \
            qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_ID) == eLyr.id():
            qLyr.setRenderer(eLyr.renderer().clone())

    def updateHiddenLayerNames(self, hiddenLayers=None):
        hiddenGroup = self._hiddenQGISLayerGroup()
        enmapboxLayerNames = {}
        enmapboxCanvasNames = {}
        for eLyr in self.mapLayers():
            enmapboxLayerNames[eLyr.id()] = eLyr.name()
        for c in self.mapCanvases():
            assert isinstance(c, MapCanvas)
            enmapboxCanvasNames[id(c)] = c.windowTitle()

        if hiddenLayers is None:
            hiddenLayers = [ltn.layer() for ltn in hiddenGroup.findLayers()]

        for qLyr in hiddenLayers:
            assert isinstance(qLyr, QgsMapLayer)
            eLayerId = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_ID)
            eLayerUri = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_SOURCE)
            eCanvasID = qLyr.customProperty(HIDDEN_ENMAPBOX_LAYER_MAPCANVAS)

            eLayerName = enmapboxLayerNames.get(eLayerId)
            eCanvasName = enmapboxCanvasNames.get(eCanvasID)
            if eLayerId is None:
                # it's a source layer
                name = '[EnMAP-Box] {}'.format(os.path.basename(eLayerUri))
            else:
                # layer available in a map canvas
                name = '[{}] {}'.format(eCanvasName, eLayerName)

            ltn = self._hiddenQGISLayerGroup().findLayer(qLyr)
            if isinstance(ltn, QgsLayerTreeLayer):
                ltn.setName(name)


    def onCurrentLayerChanged(self, layer):

        b = isinstance(layer, QgsVectorLayer)

        self.ui.mActionSelectFeatures.setEnabled(b)
        self.ui.mActionToggleEditing.setEnabled(b)
        self.ui.mActionAddFeature.setEnabled(b)
        self.ui.mActionSaveEdits.setEnabled(b)

        if isinstance(layer, (QgsRasterLayer, QgsVectorLayer)):
            self.currentLayerChanged.emit(layer)

    def processingProvider(self)->EnMAPBoxAlgorithmProvider:
        """
        Returns the EnMAPBoxAlgorithmProvider or None, if it was not initialized
        :return:
        """
        import enmapbox.algorithmprovider
        return enmapbox.algorithmprovider.instance()

    def classificationSchemata(self)->list:
        """
        Returns a list of ClassificationSchemes, derived from datasets known to the EnMAP-Box
        :return: [list-of-ClassificationSchemes
        """
        return self.dataSourceManager.classificationSchemata()

    def loadCursorLocationValueInfo(self, spatialPoint:SpatialPoint, mapCanvas:MapCanvas):
        """
        Loads the cursor location info.
        :param spatialPoint: SpatialPoint
        :param mapCanvas: QgsMapCanvas
        """
        assert isinstance(spatialPoint, SpatialPoint)
        assert isinstance(mapCanvas, QgsMapCanvas)
        if not self.ui.cursorLocationValuePanel.isVisible():
            self.ui.cursorLocationValuePanel.show()
        self.ui.cursorLocationValuePanel.loadCursorLocation(spatialPoint, mapCanvas)

    def mapLayerStore(self)->QgsMapLayerStore:
        """
        Returns the EnMAP-Box internal QgsMapLayerStore
        :return: QgsMapLayerStore
        """
        return self.mMapLayerStore

    def mapLayers(self)->list:
        """
        Returns a list of all EnMAP-Box map layers that are shown in a MapCanvas or the related Layer Tree View
        :return: [list-of-QgsMapLayers]
        """
        from enmapbox.gui.dockmanager import MapDockTreeNode
        root = self.layerTreeView().layerTreeModel().rootGroup()
        assert isinstance(root, QgsLayerTreeGroup)

        lyrs = []
        for grp in root.findGroups():
            if isinstance(grp, MapDockTreeNode):

                lyrs.extend([ltn.layer() for ltn in grp.findLayers()])

        return lyrs

    def addPanel(self, area, panel, show=True):
        """
        shortcut to add a created panel and return it
        :param dock:
        :return:
        """
        self.addDockWidget(area, panel)
        if not show:
            panel.hide()
        return panel

    def initPanels(self):
        # add & register panels
        area = None

        import enmapbox.gui.dockmanager
        import enmapbox.gui.datasourcemanager

        area = Qt.LeftDockWidgetArea
        self.ui.dataSourcePanel = self.addPanel(area, enmapbox.gui.datasourcemanager.DataSourcePanelUI(self.ui))
        self.ui.dockPanel = self.addPanel(area, enmapbox.gui.dockmanager.DockPanelUI(self.ui))
        self.ui.cursorLocationValuePanel = self.addPanel(area, CursorLocationInfoDock(self.ui), show=False)
        self.ui.spectralProfileSourcePanel = self.addPanel(area, SpectralProfileSourcePanel(self.ui))
        area = Qt.RightDockWidgetArea

        try:
            import processing.gui.ProcessingToolbox
            panel = processing.gui.ProcessingToolbox.ProcessingToolbox()
            self.ui.processingPanel = self.addPanel(area, panel)

        except Exception as ex:
            print(ex, file=sys.stderr)



    def addApplication(self, app):
        """
        Adds an EnMAPBoxApplication
        :param app: EnMAPBoxApplication or string to EnMAPBoxApplication folder or file with EnMAPBoxApplication listing.
        """
        from enmapbox.gui.applications import EnMAPBoxApplication
        if isinstance(app, EnMAPBoxApplication):
            self.applicationRegistry.addApplication(app)
        elif isinstance(app, str):
            if os.path.isfile(app):
                self.applicationRegistry.addApplicationListing(app)
            elif os.path.isdir(app):
                self.applicationRegistry.addApplicationFolder(app)
            else:
                raise Exception('Unable to load EnMAPBoxApplication from "{}"'.format(app))
        else:
            raise Exception('argument "app" has unknown type: {}. '.format(str(app)))


    def initActions(self):
        # link action to managers
        self.ui.mActionAddDataSource.triggered.connect(lambda : self.dataSourceManager.addDataSourceByDialog())
        self.ui.mActionAddMapView.triggered.connect(lambda: self.dockManager.createDock('MAP'))
        self.ui.mActionAddTextView.triggered.connect(lambda: self.dockManager.createDock('TEXT'))
        self.ui.mActionAddWebView.triggered.connect(lambda: self.dockManager.createDock('WEBVIEW'))
        self.ui.mActionAddMimeView.triggered.connect(lambda: self.dockManager.createDock('MIME'))
        self.ui.mActionAddSpeclibView.triggered.connect(lambda: self.dockManager.createDock('SPECLIB'))
        self.ui.mActionLoadExampleData.triggered.connect(lambda: self.openExampleData(
            mapWindows=1 if len(self.dockManager.docks(MapDock)) == 0 else 0))

        # activate map tools

        def initMapToolAction(action, key):
            assert isinstance(action, QAction)
            assert isinstance(key, MapTools)
            action.triggered.connect(lambda : self.setMapTool(key))
            #action.toggled.connect(lambda b, a=action : self.onMapToolActionToggled(a))
            action.setProperty(EnMAPBox.MAPTOOLACTION, key)

        initMapToolAction(self.ui.mActionPan, MapTools.Pan)
        initMapToolAction(self.ui.mActionZoomIn, MapTools.ZoomIn)
        initMapToolAction(self.ui.mActionZoomOut, MapTools.ZoomOut)
        initMapToolAction(self.ui.mActionZoomPixelScale, MapTools.ZoomPixelScale)
        initMapToolAction(self.ui.mActionZoomFullExtent, MapTools.ZoomFull)
        initMapToolAction(self.ui.mActionIdentify, MapTools.CursorLocation)
        initMapToolAction(self.ui.mActionSelectFeatures, MapTools.SelectFeature)
        initMapToolAction(self.ui.mActionSelectFeatures, MapTools.AddFeature)

        m = QMenu()
        m.addAction(self.ui.optionSelectFeaturesRectangle)
        m.addAction(self.ui.optionSelectFeaturesPolygon)
        m.addAction(self.ui.optionSelectFeaturesFreehand)
        m.addAction(self.ui.optionSelectFeaturesRadius)
        self.ui.mActionSelectFeatures.setMenu(m)

        self.ui.optionSelectFeaturesRectangle.triggered.connect(self.onSelectFeatureOptionTriggered)
        self.ui.optionSelectFeaturesPolygon.triggered.connect(self.onSelectFeatureOptionTriggered)
        self.ui.optionSelectFeaturesFreehand.triggered.connect(self.onSelectFeatureOptionTriggered)
        self.ui.optionSelectFeaturesRadius.triggered.connect(self.onSelectFeatureOptionTriggered)
        self.ui.mActionDeselectFeatures.triggered.connect(self.deselectFeatures)

        self.setMapTool(MapTools.CursorLocation)

        self.ui.mActionSaveProject.triggered.connect(lambda: self.saveProject(saveAs=False))
        self.ui.mActionSaveProjectAs.triggered.connect(lambda: self.saveProject(saveAs=True))
        from enmapbox.gui.mapcanvas import CanvasLinkDialog
        self.ui.mActionMapLinking.triggered.connect(lambda : CanvasLinkDialog.showDialog(parent=self.ui, canvases=self.mapCanvases()))
        from enmapbox.gui.about import AboutDialog
        self.ui.mActionAbout.triggered.connect(lambda: AboutDialog(parent=self.ui).show())
        from enmapbox.gui.settings import showSettingsDialog
        self.ui.mActionProjectSettings.triggered.connect(lambda: showSettingsDialog(self.ui))
        self.ui.mActionExit.triggered.connect(self.exit)


        import webbrowser
        self.ui.mActionOpenIssueReportPage.triggered.connect(lambda : webbrowser.open(enmapbox.CREATE_ISSUE))
        self.ui.mActionOpenProjectPage.triggered.connect(lambda: webbrowser.open(enmapbox.REPOSITORY))
        self.ui.mActionOpenOnlineDocumentation.triggered.connect(lambda : webbrowser.open(enmapbox.DOCUMENTATION))

        # finally, fix the popup mode of menus
        for toolBar in self.ui.findChildren(QToolBar):
            for toolButton in toolBar.findChildren(QToolButton):
                assert isinstance(toolButton, QToolButton)
                if isinstance(toolButton.defaultAction(), QAction) and isinstance(toolButton.defaultAction().menu(), QMenu):
                    toolButton.setPopupMode(QToolButton.MenuButtonPopup)


    def _mapToolButton(self, action)->QToolButton:
        for toolBar in self.ui.findChildren(QToolBar):
            for toolButton in toolBar.findChildren(QToolButton):
                if toolButton.defaultAction() == action:
                    return toolButton
        return None

    def _mapToolActions(self)->list:
        """
        Returns a list of all QActions that can activate a map tools
        :return: [list-of-QActions]
        """
        return [a for a in self.ui.findChildren(QAction) if a.property(EnMAPBox.MAPTOOLACTION)]

    def onSelectFeatureOptionTriggered(self):

        a = self.sender()
        m = self.ui.mActionSelectFeatures.menu()
        if isinstance(a, QAction) and isinstance(m, QMenu) and a in m.actions():
            for ca in m.actions():
                assert isinstance(ca, QAction)
                if ca == a:
                    self.ui.mActionSelectFeatures.setIcon(a.icon())
                    self.ui.mActionSelectFeatures.setToolTip(a.toolTip())
                ca.setChecked(ca == a)
        self.setMapTool(MapTools.SelectFeature)

    def deselectFeatures(self):
        """
        Removes all feature selections (across all map canvases)
        """

        for canvas in self.mapCanvases():
            assert isinstance(canvas, QgsMapCanvas)
            for vl in [l for l in canvas.layers() if isinstance(l, QgsVectorLayer)]:
                assert isinstance(vl, QgsVectorLayer)
                vl.removeSelection()

    def onCrosshairPositionChanged(self, spatialPoint:SpatialPoint):
        """
        Synchronizes all crosshair positions. Takes care of CRS differences.
        :param spatialPoint: SpatialPoint of the new Crosshair position
        """
        sender = self.sender()
        for mapCanvas in self.mapCanvases():
            if isinstance(mapCanvas, MapCanvas) and mapCanvas != sender:
                mapCanvas.setCrosshairPosition(spatialPoint, emitSignal=False)




    def spectralProfileBridge(self)->SpectralProfileBridge:
        return self.ui.spectralProfileSourcePanel.bridge()

    sigDockAdded = pyqtSignal(Dock)

    def onDockAdded(self, dock):
        assert isinstance(dock, Dock)
        from enmapbox.gui.mapcanvas import MapDock

        if isinstance(dock, SpectralLibraryDock):
            dock.sigLoadFromMapRequest.connect(lambda: self.setMapTool(MapTools.SpectralProfile))
            slw = dock.speclibWidget()
            assert isinstance(slw, SpectralLibraryWidget)
            slw.plotWidget().backgroundBrush().setColor(QColor('black'))
            slw.sigFilesCreated.connect(self.addSources)
            #self.sigCurrentSpectraChanged.connect(dock.mSpeclibWidget.setCurrentSpectra)
            self.spectralProfileBridge().addDestination(slw)

        if isinstance(dock, MapDock):

            canvas = dock.mapCanvas()
            assert isinstance(canvas, MapCanvas)
            canvas.sigCrosshairPositionChanged.connect(self.onCrosshairPositionChanged)
            canvas.setCrosshairVisibility(True)
            canvas.sigLayersAdded.connect(lambda lyrs, c=canvas: self.sigMapLayersAdded[list, MapCanvas].emit(lyrs, c))
            canvas.sigLayersRemoved.connect(lambda lyrs, c=canvas: self.sigMapLayersRemoved[list, MapCanvas].emit(lyrs, c))

            self.setMapTool(self.mMapToolKey, canvases=[canvas])
            canvas.mapTools().mtCursorLocation.sigLocationRequest[SpatialPoint, QgsMapCanvas].connect(self.setCurrentLocation)

            for node in self.dockManageTreeModel().mapDockTreeNodes():
                assert isinstance(node, MapDockTreeNode)
                if node.mapCanvas() == canvas:
                    node.sigAddedLayers.connect(self.sigMapLayersAdded[list].emit)
                    node.sigRemovedLayers.connect(self.sigMapLayersRemoved[list].emit)


            self.sigMapCanvasAdded.emit(canvas)

        self.sigDockAdded.emit(dock)


    def onDockRemoved(self, dock):
        if isinstance(dock, MapDock):
            self.sigMapCanvasRemoved.emit(dock.mapCanvas())

        if isinstance(dock, SpectralLibraryDock):
            self.spectralProfileBridge().removeDestination(dock.speclibWidget())


    @pyqtSlot(SpatialPoint, QgsMapCanvas)
    def loadCurrentMapSpectra(self, spatialPoint:SpatialPoint, mapCanvas:QgsMapCanvas=None):
        """
        Loads SpectralProfiles from a location defined by `spatialPoint`
        :param spatialPoint: SpatialPoint
        :param mapCanvas: QgsMapCanvas
        """
        self.ui.spectralProfileSourcePanel.loadCurrentMapSpectra(spatialPoint, mapCanvas=mapCanvas)


    def setMapTool(self, mapToolKey:MapTools, *args, canvases=None, **kwds):
        """
        Sets the active QgsMapTool for all canvases know to the EnMAP-Box.
        :param mapToolKey: str, see MapTools documentation
        :param args:
        :param kwds:
        :return:
        """


        mode = None

        for btnSelectFeature in self.ui.toolBarVectorTools.findChildren(QToolButton):
            if btnSelectFeature.defaultAction() == self.ui.mActionSelectFeatures:
                break



        if mapToolKey == MapTools.SelectFeature:
            if self.ui.optionSelectFeaturesRectangle.isChecked():
                mode = QgsMapToolSelectionHandler.SelectionMode.SelectSimple
            elif self.ui.optionSelectFeaturesPolygon.isChecked():
                mode = QgsMapToolSelectionHandler.SelectionMode.SelectPolygon
            elif self.ui.optionSelectFeaturesFreehand.isChecked():
                mode = QgsMapToolSelectionHandler.SelectionMode.SelectFreehand
            elif self.ui.optionSelectFeaturesRadius.isChecked():
                mode = QgsMapToolSelectionHandler.SelectionMode.SelectRadius
            else:
                mode = QgsMapToolSelectionHandler.SelectionMode.SelectSimple
            btnSelectFeature.setChecked(True)
        else:
            btnSelectFeature.setChecked(False)


        if mapToolKey == MapTools.SpectralProfile:
            #SpectralProfile is a shortcut for Identify + return with profile option
            self.ui.optionIdentifyProfile.setChecked(True)
            self.ui.mActionIdentify.setChecked(True)
            return

        self.mMapToolKey = mapToolKey
        self.mMapToolMode = mode

        results = []
        if canvases is None:
            canvases = self.mapCanvases()
        elif isinstance(canvases, MapCanvas):
            canvases = [canvases]

        assert isinstance(canvases, list)
        for canvas in canvases:
            assert isinstance(canvas, MapCanvas)
            mapTools = canvas.mapTools()

            if mapToolKey == MapTools.SelectFeature:
                mapTools.mtSelectFeature.setSelectionMode(self.mMapToolMode)

            mapTools.activate(mapToolKey)

            results.append(canvas.mapTool())

        for action in self._mapToolActions():
            key = action.property(EnMAPBox.MAPTOOLACTION)
            if key == mapToolKey:
                action.setChecked(True)
            else:
                action.setChecked(False)


        b = self.ui.mActionIdentify.isChecked()
        self.ui.optionIdentifyCursorLocation.setEnabled(b)
        self.ui.optionIdentifyProfile.setEnabled(b)
        self.ui.optionMoveCenter.setEnabled(b)


        return results

    def initEnMAPBoxApplications(self):
        """
        Initialized EnMAPBoxApplications
        """
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)




        listingBasename = 'enmapboxapplications.txt'

        # load internal "core" apps
        INTERNAL_APPS = jp(DIR_ENMAPBOX, *['coreapps'])
        if enmapbox.LOAD_INTERNAL_APPS:
            self.applicationRegistry.addApplicationFolder(INTERNAL_APPS, isRootFolder=True)
        # check for listing file
        p = os.path.join(INTERNAL_APPS, listingBasename)
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        # load external / standard apps
        EXTERNAL_APPS = jp(DIR_ENMAPBOX, *['apps'])
        if enmapbox.LOAD_EXTERNAL_APPS:
            self.applicationRegistry.addApplicationFolder(EXTERNAL_APPS, isRootFolder=True)

        # check for listing file
        p = os.path.join(EXTERNAL_APPS, listingBasename)
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        # check for listing file in root
        p = os.path.join(DIR_ENMAPBOX, listingBasename)
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        #find other app-folders or listing files folders
        from enmapbox.gui.settings import enmapboxSettings
        settings = enmapboxSettings()
        for appPath in re.split('[;\n]', settings.value('EMB_APPLICATION_PATH', '')):
            if os.path.isdir(appPath):
                self.applicationRegistry.addApplicationFolder(appPath, isRootFolder=True)
            elif os.path.isfile(p):
                self.applicationRegistry.addApplicationListing(p)
            else:
                print('Unable to load EnMAPBoxApplication(s) from path: "{}"'.format(p), file=sys.stderr)


    def exit(self):
        """Closes the EnMAP-Box"""
        self.ui.setParent(None)
        self.ui.close()
        self.deleteLater()

    def onLogMessage(self, message, tag, level):
        msgLines = message.split('\n')
        if '' in message.split('\n'):
            msgLines = msgLines[0:msgLines.index('')]

        # use only messages relevant to "EnMAP-Box"
        if not re.search(r'enmap-?box', tag, re.I):
            return

        mbar = self.ui.messageBar
        assert isinstance(mbar, QgsMessageBar)
        line1 = msgLines[0]
        showMore = '' if len(msgLines) == 1 else '\n'.join(msgLines[1:])
        mbar.pushMessage(tag, line1, showMore, level, 50)

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
        from enmapbox.dependencycheck import missingTestData, outdatedTestData, installTestData
        if missingTestData() or outdatedTestData():
            installTestData()

        if not missingTestData():
            import enmapboxtestdata
            dir = os.path.dirname(enmapboxtestdata.__file__)
            files = list(file_search(dir, re.compile('.*(bsq|bil|bip|tif|gpkg|sli|img|shp|pkl)$', re.I), recursive=True))

            added = self.addSources(files)

            for n in range(mapWindows):
                dock = self.createDock('MAP')
                assert isinstance(dock, MapDock)
                lyrs = []
                for src in self.dataSourceManager.sources(sourceTypes=['RASTER', 'VECTOR']):
                    lyr = src.createUnregisteredMapLayer()
                    if isinstance(lyr, QgsRasterLayer):
                        r = defaultRasterRenderer(lyr)
                        r.setInput(lyr.dataProvider())
                        lyr.setRenderer(r)
                    lyrs.append(lyr)

                dock.addLayers(lyrs)



    def onDataSourceRemoved(self, dataSource:DataSource):
        """
        Reacts on removed data sources
        :param dataSource: DataSource
        """

        self.sigDataSourceRemoved[str].emit(dataSource.uri())
        self.sigDataSourceRemoved[DataSource].emit(dataSource)

        if isinstance(dataSource, DataSourceRaster):
            self.sigRasterSourceRemoved[str].emit(dataSource.uri())
            self.sigRasterSourceRemoved[DataSourceRaster].emit(dataSource)

        if isinstance(dataSource, DataSourceVector):
            self.sigVectorSourceRemoved[str].emit(dataSource.uri())
            self.sigVectorSourceRemoved[DataSourceVector].emit(dataSource)

        if isinstance(dataSource, DataSourceSpectralLibrary):
            self.sigSpectralLibraryRemoved[str].emit(dataSource.uri())
            self.sigSpectralLibraryRemoved[DataSourceSpectralLibrary].emit(dataSource)

        self.dockManager.removeDataSource(dataSource)

    def onDataSourceAdded(self, dataSource:DataSource):


        self.sigDataSourceAdded[DataSource].emit(dataSource)
        self.sigDataSourceAdded[str].emit(dataSource.uri())

        if isinstance(dataSource, DataSourceRaster):
            self.sigRasterSourceAdded[str].emit(dataSource.uri())
            self.sigRasterSourceAdded[DataSourceRaster].emit(dataSource)

            src = SpectralProfileSource(dataSource.uri(), dataSource.name(), dataSource.provider())
            self.spectralProfileBridge().addSource(src)


        if isinstance(dataSource, DataSourceVector):
            self.sigVectorSourceAdded[str].emit(dataSource.uri())
            self.sigVectorSourceAdded[DataSourceVector].emit(dataSource)

        if isinstance(dataSource, DataSourceSpectralLibrary):
            self.sigSpectralLibraryAdded[str].emit(dataSource.uri())
            self.sigSpectralLibraryAdded[DataSourceSpectralLibrary].emit(dataSource)




    def saveProject(self, saveAs=False):
        proj = QgsProject.instance()
        path = proj.fileName()
        if saveAs or not os.path.exists(path):
            path, filter = QFileDialog.getSaveFileName(self.ui, \
                                               'Choose a filename to save the QGIS project file',
                                               # directory=os.path.dirname(path)
                                               filter='QGIS files (*.qgs *.QGIS)')
            if len(path) > 0:
                proj.setFileName(path)

        proj.write()

    def restoreProject(self):
        raise NotImplementedError()


    def setCurrentLocation(self, spatialPoint:SpatialPoint, mapCanvas:QgsMapCanvas=None):
        """
        Sets the current "last selected" location, for which different properties might get derived,
        like cursor location values and SpectraProfiles.
        :param spatialPoint: SpatialPoint
        :param mapCanvas: QgsMapCanvas (optional), the canvas on which the location got selected
        """
        assert isinstance(spatialPoint, SpatialPoint)

        bCLV = self.ui.optionIdentifyCursorLocation.isChecked()
        bSP = self.ui.optionIdentifyProfile.isChecked()
        bCenter = self.ui.optionMoveCenter.isChecked()

        self.mCurrentMapLocation = spatialPoint

        self.sigCurrentLocationChanged[SpatialPoint].emit(self.mCurrentMapLocation)
        if isinstance(mapCanvas, QgsMapCanvas):
            self.sigCurrentLocationChanged[SpatialPoint, QgsMapCanvas].emit(self.mCurrentMapLocation, mapCanvas)


        if isinstance(mapCanvas, QgsMapCanvas):
            if bCLV:
                self.loadCursorLocationValueInfo(spatialPoint, mapCanvas)

            if bCenter:
                mapCanvas.setCenter(spatialPoint)

        if bSP:
            self.loadCurrentMapSpectra(spatialPoint, mapCanvas)




    def currentLocation(self)->SpatialPoint:
        """
        Returns the current location, which is a SpatialPoint last clicked by a user on a map canvas.
        :return: SpatialPoint
        """
        return self.mCurrentMapLocation



    def setCurrentSpectra(self, spectra:list):
        """
        Sets the list of SpectralProfiles to be considered as current spectra
        :param spectra: [list-of-SpectralProfiles]
        """
        warnings.warn(DeprecationWarning(''))

        """        
        b = len(self.mCurrentSpectra) == 0
        self.mCurrentSpectra = spectra[:]

        # check if any SPECLIB window was opened
        if len(self.dockManager.docks('SPECLIB')) == 0:
            #and getattr(self, '_initialSpeclibDockCreated', False) == False:
            dock = self.createDock('SPECLIB')
            assert isinstance(dock, SpectralLibraryDock)

        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra[:])
        """

    def currentSpectra(self)->list:
        """
        Returns the spectra currently selected using the profile tool.

        :return: [list-of-spectra]
        """
        return self.mCurrentSpectra[:]

    def dataSources(self, sourceType='ALL', onlyUri:bool=True)->list:
        """
        Returns a list of URIs to the data sources of type "sourceType" opened in the EnMAP-Box
        :param sourceType: ['ALL', 'RASTER', 'VECTOR', 'MODEL'],
                            see enmapbox.gui.datasourcemanager.DataSourceManager.SOURCE_TYPES
        :param onlyUri: bool, set on False to return the DataSource object instead of the uri only.
        :return: [list-of-datasource-URIs (str)]
        """

        sources = self.dataSourceManager.sources(sourceTypes=sourceType)
        if onlyUri:
            sources = [ds.uri() for ds in sources]
        return sources

    def createDock(self, *args, **kwds)->Dock:
        """
        Create and returns a new Dock
        :param args:
        :param kwds:
        :return:
        """
        return self.dockManager.createDock(*args, **kwds)

    def removeDock(self, *args, **kwds):
        """
        Removes a Dock instance.
        See `enmapbox/gui/dockmanager.py` for details
        :param args:
        :param kwds:
        """
        self.dockManager.removeDock(*args, **kwds)

    def dockManageTreeModel(self)->DockManagerTreeModel:
        """
        Retursn the DockManagerTreeModel
        :return: DockManagerTreeModel
        """
        return self.ui.dockPanel.dockTreeView.model()

    def docks(self, dockType=None):
        """
        Returns dock widgets
        :param dockType: optional, specifies the type of dock widgets to return
        :return: [list-of-DockWidgets]
        """
        return self.dockManager.docks(dockType=dockType)

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
        """
        Removes data sources.
        Removes all sources available if `dataSourceList` remains unspecified.
        :param dataSourceList:[list-of-data-sources]
        """
        self.dataSourceManager.removeSources(dataSourceList)

    def removeSource(self, source):
        """
        Removes a single datasource
        :param source: DataSource or str
        """
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
        """
        Returns the QMenu(s) with title `title`.
        :param title: str
        :return: QMenu
        """
        return self.ui.menusWithTitle(title)



    def showLayerProperties(self, mapLayer:QgsMapLayer):
        """
        Show a map layer property dialog
        :param mapLayer:
        :return:
        """
        if isinstance(mapLayer, (QgsVectorLayer, QgsRasterLayer)):

            #1. find the map canvas
            mapCanvas = None
            for canvas in self.mapCanvases():
                if mapLayer in canvas.layers():
                    mapCanvas = canvas
                    break
            #2.
            showLayerPropertiesDialog(mapLayer, mapCanvas, modal=True)



    @staticmethod
    def getIcon():
        """
        Returns the EnMAP-Box icon.
        :return: QIcon
        """
        warnings.warn(DeprecationWarning('Use EnMAPBoxicon() instras'))
        return EnMAPBox.icon()


    @staticmethod
    def icon()->QIcon:
        return enmapbox.icon()

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



    def close(self):
        self.ui.close()
        EnMAPBox._instance = None


    """
    Implementation of QGIS Interface 
    """

    def initQgisInterfaceVariables(self):
        """
        Initializes internal variables required to provide the QgisInterface
        :return:
        """
        self.mQgisInterfaceLayerSet = dict()
        self.mQgisInterfaceMapCanvas = MapCanvas()


    def layerTreeView(self)->QgsLayerTreeView:
        """
        Returns the Dock Panel Tree View
        :return: enmapbox.gui.dockmanager.DockTreeView
        """
        return self.ui.dockPanel.dockTreeView

    ### SIGNALS from QgisInterface ####

    initializationCompleted = pyqtSignal()
    layerSavedAs = pyqtSignal(QgsMapLayer, str)
    currentLayerChanged = pyqtSignal(QgsMapLayer)


    ### ACTIONS ###
    def actionAbout(self):
        return self.ui.mActionAbout

    def actionAddAfsLayer(self):
        return self.ui.mActionAddDataSource

    def actionAddAllToOverview(self):
        return self.ui.mActionAddDataSource

    def actionAddAmsLayer(self):
        return self.ui.mActionAddDataSource

    def actionAddFeature(self):
        return self.ui.mActionAddDataSource

    def actionAddOgrLayer(self):
        return self.ui.mActionAddDataSource

    # def actionAddPart(self): pass
    def actionAddPgLayer(self):
        return self.ui.mActionAddDataSource

    def actionAddRasterLayer(self):
        return self.ui.mActionAddDataSource

    # def actionAddRing(self):
    # def actionAddToOverview(self):
    def actionAddWmsLayer(self):
        return self.ui.mActionAddDataSource

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
        return self.ui.mActionExit()

    def actionFeatureAction(self):
        pass

    def actionHelpContents(self):
        pass

    def actionHideAllLayers(self):
        pass

    def actionHideSelectedLayers(self):
        pass

    def actionIdentify(self):
        return self.ui.mActionIdentify

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
        return self.ui.mActionPan

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
        return self.ui.mActionZoomPixelScale

    def actionZoomFullExtent(self):
        return self.ui.mActionZoomFullExtent

    def actionZoomIn(self):
        return self.ui.mActionZoomIn

    def actionZoomLast(self):
        pass

    def actionZoomNext(self):
        pass

    def actionZoomOut(self):
        return self.ui.mActionZoomOut

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
        """
        Add a dock widget to the main window
        :param area:
        :param dockWidget:
        :param orientation:
        """


        self.ui.addDockWidget(area, dockWidget, orientation=orientation)

    def addLayerMenu(self):
        pass

    def mainWindow(self)->EnMAPBoxUI:
        return self.ui

    def messageBar(self)->QgsMessageBar:
        return self.ui.messageBar

    def iconSize(self, dockedToolbar=False):
        #return self.ui.mActionAddDataSource.icon().availableSizes()[0]
        return QSize(16,16)

    def spectralLibraries(self)->typing.List[SpectralLibrary]:
        """
        Returns a list of SpectraLibraries that are registered to the internal MapLayerStore (i.e. opened in the
        DataSource panel or shown in a SpectralLibrary Widget).
        :return: [list-of-SpectralLibraries]
        """
        return [lyr for lyr in self.mapLayerStore().mapLayers().values() if isinstance(lyr, SpectralLibrary)]

    def mapCanvases(self)->typing.List[MapCanvas]:
        """
        Returns all MapCanvas(QgsMapCanvas) objects known to the EnMAP-Box
        :return: [list-of-MapCanvases]
        """
        from enmapbox.gui.mapcanvas import MapDock
        return [d.mCanvas for d in self.dockManager.docks() if isinstance(d, MapDock)]

    def mapCanvas(self, virtual=False)->MapCanvas:
        """
        Returns a single MapCanvas.
        :param virtual: bool, set True to return an invisible QgsMapCanvas that contains all data source layers
        :return: MapCanvas
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

    def addDockWidget(self, area, dockwidget:QDockWidget):



        self.ui.addDockWidget(area, dockwidget)
        self.ui.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.ui.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.ui.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.ui.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.ui.menuPanels.addAction(dockwidget.toggleViewAction())

    def loadExampleData(self):
        """
        Loads the EnMAP-Box example data
        """
        self.ui.mActionLoadExampleData.trigger()

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

    def addRasterLayer(self, path, base_name, key=None):
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        lyr= QgsRasterLayer(path, base_name, key)

        self.addSource(lyr, base_name)

    def activeMapCanvas(self)->MapCanvas:
        """
        Returns the active map canvas, i.e. the MapCanvas that was clicked last.
        :return: MapCanvas
        """
        from enmapbox.gui.mapcanvas import KEY_LAST_CLICKED
        canvases = sorted(self.mapCanvases(), key=lambda c:c.property(KEY_LAST_CLICKED))
        if len(canvases) > 0:
            return canvases[-1]
        else:
            return None

    def setActiveMapCanvas(self, mapCanvas:MapCanvas)->bool:
        """
        Sets the active map canvas
        :param mapCanvas: MapCanvas
        :return: bool, True, if mapCanvas exists in the EnMAP-Box, False otherwise
        """
        canvases = self.mapCanvases()
        from enmapbox.gui.mapcanvas import KEY_LAST_CLICKED
        if mapCanvas in canvases:
            mapCanvas.setProperty(KEY_LAST_CLICKED, time.time())
            return True
        else:
            return False


    def setActiveLayer(self, mapLayer:QgsMapLayer)->True:
        """
        Set the active layer (layer gets selected in the Data View legend).
        :param mapLayer: QgsMapLayer
        :return: bool. True, if mapLayer exists, False otherwise.
        """

        canvas = self.activeMapCanvas()
        if isinstance(canvas, MapCanvas) and mapLayer in canvas.layers():
            canvas.setCurrentLayer(mapLayer)
            return True

        for canvas in self.mapCanvases():
            if mapLayer in canvas.layers():
                self.setActiveMapCanvas(canvas)
                canvas.setCurrentLayer(mapLayer)
                return True
        return False

    def activeLayer(self)->QgsMapLayer:
        """
        Returns the current layer of the active map canvas
        :return: QgsMapLayer
        """
        # noinspection PyArgumentList
        canvas = self.activeMapCanvas()
        if isinstance(canvas, QgsMapCanvas):
            return canvas.currentLayer()
        else:
            return None


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
