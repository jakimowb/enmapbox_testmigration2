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
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


from typing import Optional

import enmapbox
from qgis import utils as qgsUtils
import qgis.utils

from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer, QgsProject, \
    QgsProcessingAlgorithm, QgsApplication, Qgis, QgsCoordinateReferenceSystem, QgsWkbTypes, \
    QgsMapLayerStore, QgsPointXY, QgsLayerTreeGroup, QgsLayerTree, QgsLayerTreeLayer, QgsVectorLayerTools, \
    QgsZipUtils, QgsProjectArchive, QgsSettings, \
    QgsStyle, QgsSymbolLegendNode, QgsSymbol

from qgis.gui import QgsMapCanvas, QgsLayerTreeView, \
    QgisInterface, QgsMessageBar, QgsMessageViewer, QgsMessageBarItem, QgsMapLayerConfigWidgetFactory, \
    QgsMapLayerConfigWidgetFactory, QgsAttributeTableFilterModel, QgsSymbolSelectorDialog, \
    QgsSymbolWidgetContext

from enmapbox import messageLog, debugLog
from enmapbox.gui.docks import *
from enmapbox.gui.dockmanager import DockManagerTreeModel, MapDockTreeNode
from enmapbox.gui.datasources import *
from enmapbox import DEBUG, DIR_ENMAPBOX
from enmapbox.gui.mapcanvas import *
from enmapbox.dependencycheck import requiredPackages, missingPackageInfo
from hubdsm.processing.importenmapl1b import ImportEnmapL1B
from hubdsm.processing.importenmapl1c import ImportEnmapL1C
from hubdsm.processing.importenmapl2a import ImportEnmapL2A
from hubdsm.processing.importprismal2d import ImportPrismaL2D
from enmapbox.externals.qps.cursorlocationvalue import CursorLocationInfoDock
from enmapbox.externals.qps.layerproperties import showLayerPropertiesDialog
from enmapbox.externals.qps.maptools import QgsMapToolSelectionHandler
from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider
from enmapbox.gui.spectralprofilesources import SpectralProfileSourcePanel, SpectralProfileBridge, SpectralProfileSource

HIDDEN_ENMAPBOX_LAYER_GROUP = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_GROUP'

MAX_MISSING_DEPENDENCY_WARNINGS = 3
KEY_MISSING_DEPENDENCY_VERSION = 'MISSING_PACKAGE_WARNING_VERSION'


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

        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(5)
        effect.setColor(QColor('white'))
        self.setGraphicsEffect(effect)

        css = "" \
              ""

    def showMessage(self, text: str, alignment: Qt.Alignment = None, color: QColor = None):
        """
        Shows a message
        :param text:
        :param alignment:
        :param color:
        :return:
        """
        if alignment is None:
            alignment = int(Qt.AlignCenter | Qt.AlignBottom)
        if color is None:
            color = QColor('black')
        super(EnMAPBoxSplashScreen, self).showMessage(text, alignment, color)
        QApplication.processEvents()


class EnMAPBoxUI(QMainWindow):
    def __init__(self, *args, **kwds):
        """Constructor."""
        super().__init__(*args, **kwds)
        loadUi(enmapboxUiPath('enmapbox_gui.ui'), self)
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

    def menusWithTitle(self, title: str):
        """
        Returns the QMenu with title `title`
        :param title: str
        :return: QMenu
        """
        assert isinstance(title, str)
        return [m for m in self.findChildren(QMenu) if m.title() == title]

    def closeEvent(event):
        pass


def getIcon() -> QIcon:
    """
    Returns the EnMAP icon
    :return: QIcon
    """
    warnings.warn(DeprecationWarning('Use enmapbox.icon() instead to return the EnMAP-Box icon'))
    return enmapbox.icon()


class EnMAPBoxLayerTreeLayer(QgsLayerTreeLayer):

    def __init__(self, *args, **kwds):

        canvas = None
        if 'canvas' in kwds.keys():
            canvas = kwds.pop('canvas')

        super().__init__(*args, **kwds)
        self.setUseLayerName(False)

        self.mCanvas: QgsMapCanvas = None
        lyr = self.layer()
        if isinstance(lyr, QgsMapLayer):
            lyr.nameChanged.connect(self.updateLayerTitle)

        if isinstance(canvas, QgsMapCanvas):
            self.setCanvas(canvas)

        self.updateLayerTitle()

    def updateLayerTitle(self, *args):
        """
        Updates node name and layer title (not name) to: [<location in enmapbox>] <layer name>
        """
        location = '[EnMAP-Box]'
        name = '<not connected>'
        if isinstance(self.mCanvas, QgsMapCanvas):
            location = '[{}]'.format(self.mCanvas.windowTitle())

        lyr = self.layer()
        if isinstance(lyr, QgsMapLayer):
            name = lyr.name()

        title = '{} {}'.format(location, name)
        if isinstance(lyr, QgsMapLayer):
            lyr.setTitle(title)

        self.setName(title)

    def setCanvas(self, canvas: QgsMapCanvas):
        if isinstance(self.mCanvas, QgsMapCanvas):
            self.mCanvas.windowTitleChanged.disconnect(self.updateLayerTitle)
        self.mCanvas = canvas
        if isinstance(self.mCanvas, QgsMapCanvas):
            self.mCanvas.windowTitleChanged.connect(self.updateLayerTitle)
        self.updateLayerTitle()


class EnMAPBoxHiddenLayerTreeGroup(QgsLayerTreeGroup):

    def __init__(self, name: str = HIDDEN_ENMAPBOX_LAYER_GROUP):
        super().__init__(name=name, checked=False)

    def clone(self):
        grp = EnMAPBoxHiddenLayerTreeGroup(name=self.name())
        return grp

    def writeXml(self, *arg, **kwds):
        # do not write anything!
        pass


class EnMAPBox(QgisInterface, QObject):
    _instance = None

    @staticmethod
    def instance():
        return EnMAPBox._instance

    MAPTOOLACTION = 'enmapbox/maptoolkey'

    sigDataSourceAdded = pyqtSignal([str], [DataSource])
    sigSpectralLibraryAdded = pyqtSignal([str], [SpectralLibrary], [DataSourceSpectralLibrary])
    sigRasterSourceAdded = pyqtSignal([str], [DataSourceRaster])
    sigVectorSourceAdded = pyqtSignal([str], [DataSourceVector])

    sigDataSourceRemoved = pyqtSignal([str], [DataSource])
    sigSpectralLibraryRemoved = pyqtSignal([str], [SpectralLibrary], [DataSourceSpectralLibrary])
    sigRasterSourceRemoved = pyqtSignal([str], [DataSourceRaster])
    sigVectorSourceRemoved = pyqtSignal([str], [DataSourceVector])

    sigMapLayersAdded = pyqtSignal([list], [list, MapCanvas])
    sigMapLayersRemoved = pyqtSignal([list], [list, MapCanvas])

    currentLayerChanged = pyqtSignal(QgsMapLayer)

    sigClosed = pyqtSignal()

    sigCurrentLocationChanged = pyqtSignal([SpatialPoint],
                                           [SpatialPoint, QgsMapCanvas])

    sigCurrentSpectraChanged = pyqtSignal(list)

    sigMapCanvasRemoved = pyqtSignal(MapCanvas)
    sigMapCanvasAdded = pyqtSignal(MapCanvas)

    sigProjectWillBeSaved = pyqtSignal()

    """Main class that drives the EnMAPBox_GUI and all the magic behind"""

    def __init__(self,
                 iface: QgisInterface = None,
                 load_core_apps: bool = True,
                 load_other_apps: bool = True):
        assert EnMAPBox.instance() is None, 'EnMAPBox already started. Call EnMAPBox.instance() to get a handle to.'

        settings = self.settings()

        splash = EnMAPBoxSplashScreen(parent=None)
        if not str(settings.value('EMB_SPLASHSCREEN', True)).lower() in ['0', 'false']:
            splash.show()

        splash.showMessage('Load UI')
        QApplication.processEvents()

        QObject.__init__(self)
        QgisInterface.__init__(self)

        self.ui = EnMAPBoxUI()
        self.ui.closeEvent = self.closeEvent

        self.initQgisInterfaceVariables()
        if not isinstance(iface, QgisInterface):
            iface = qgis.utils.iface
        self.iface = iface
        assert isinstance(iface, QgisInterface)

        self.mMapToolKey = MapTools.Pan
        self.mMapToolMode = None
        self.mMessageBarItems = []

        def removeItem(item):
            if item in self.mMessageBarItems:
                self.mMessageBarItems.remove(item)

        self.messageBar().widgetRemoved.connect(removeItem)
        self.mCurrentMapLayer: QgsMapLayer = None

        self.initPanels()

        if not DEBUG:
            msgLog = QgsApplication.instance().messageLog()
            msgLog.messageReceived.connect(self.onLogMessage)

        assert isinstance(qgsUtils.iface, QgisInterface)

        self.mCurrentMapLocation = None

        # define managers
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from enmapbox.gui.dockmanager import DockManager

        splash.showMessage('Init DataSourceManager')
        self.mDataSourceManager = DataSourceManager()
        self.mDataSourceManager.sigDataSourceRemoved.connect(self.onDataSourceRemoved)
        self.mDataSourceManager.sigDataSourceAdded.connect(self.onDataSourceAdded)
        # QgsProject.instance().layersAdded.connect(self.addMapLayers)
        QgsProject.instance().layersWillBeRemoved.connect(self.onLayersWillBeRemoved)
        QgsProject.instance().writeProject.connect(self.onWriteProject)
        QgsProject.instance().readProject.connect(self.onReadProject)

        # needed to keep a reference on created LayerTreeNodes
        self._layerTreeNodes = []
        self._layerTreeGroup: QgsLayerTreeGroup = None

        self.mDockManager = DockManager()
        self.mDockManager.setMessageBar(self.messageBar())
        self.mDockManager.connectDataSourceManager(self.mDataSourceManager)
        self.mDockManager.connectDockArea(self.ui.dockArea)
        self.ui.dataSourcePanel.connectDataSourceManager(self.mDataSourceManager)

        self.ui.dockPanel.connectDockManager(self.mDockManager)
        self.ui.dockPanel.dockTreeView.currentLayerChanged.connect(self.updateCurrentLayerActions)
        self.ui.dockPanel.dockTreeView.doubleClicked.connect(self.onDockTreeViewDoubleClicked)

        root = self.dockManagerTreeModel().rootGroup()
        assert isinstance(root, QgsLayerTree)
        root.addedChildren.connect(self.syncHiddenLayers)
        root.removedChildren.connect(self.syncHiddenLayers)

        #
        self.updateCurrentLayerActions()
        self.ui.centralFrame.sigDragEnterEvent.connect(
            lambda event: self.mDockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragMoveEvent.connect(
            lambda event: self.mDockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDragLeaveEvent.connect(
            lambda event: self.mDockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))
        self.ui.centralFrame.sigDropEvent.connect(
            lambda event: self.mDockManager.onDockAreaDragDropEvent(self.ui.dockArea, event))

        self.mDockManager.sigDockAdded.connect(self.onDockAdded)
        self.mDockManager.sigDockRemoved.connect(self.onDockRemoved)

        self.initActions()
        self.initActionsAddProduct()

        from enmapbox.externals.qps.vectorlayertools import VectorLayerTools
        self.mVectorLayerTools = VectorLayerTools()
        self.mVectorLayerTools.sigMessage.connect(lambda title, text, level:
                                                  self.messageBar().pushItem(QgsMessageBarItem(title, text, level)))
        self.mVectorLayerTools.sigFreezeCanvases.connect(self.freezeCanvases)
        self.mVectorLayerTools.sigEditingStarted.connect(self.updateCurrentLayerActions)
        self.mVectorLayerTools.sigZoomRequest.connect(self.zoomToExtent)
        self.mVectorLayerTools.sigPanRequest.connect(self.panToPoint)

        self.ui.cursorLocationValuePanel.sigLocationRequest.connect(lambda: self.setMapTool(MapTools.CursorLocation))

        # load EnMAP-Box applications
        splash.showMessage('Load EnMAPBoxApplications...')

        debugLog('Load EnMAPBoxApplications...')
        self.initEnMAPBoxApplications(load_core_apps=load_core_apps, load_other_apps=load_other_apps)

        # add developer tools to the Tools menu
        debugLog('Modify menu...')
        m = self.menu('Tools')
        m.addSeparator()
        m = m.addMenu('Developers')
        m.addAction(self.ui.mActionAddMimeView)
        a = m.addAction('Resource Browser')
        a.setToolTip('Opens a Browser to inspect the Qt Resource system')
        a.triggered.connect(self.showResourceBrowser)

        debugLog('Set ui visible...')
        self.ui.setVisible(True)

        debugLog('Set pyqtgraph config')
        from ..externals.pyqtgraph import setConfigOption
        setConfigOption('background', 'k')
        setConfigOption('foreground', 'w')

        # check missing packages and show a message
        # see https://bitbucket.org/hu-geomatics/enmap-box/issues/366/start-enmap-box-in-standard-qgis
        debugLog('Run dependency checks...')

        from ..dependencycheck import requiredPackages

        KEY_CNT = 'MISSING_PACKAGE_WARNING_COUNT'
        if settings.value(KEY_MISSING_DEPENDENCY_VERSION, None) != self.version():
            # re-count with each new version
            settings.setValue(KEY_MISSING_DEPENDENCY_VERSION, self.version())
            settings.setValue(KEY_CNT, 0)

        if len([p for p in requiredPackages() if not p.isInstalled()]) > 0:

            n_warnings: int = int(settings.value(KEY_CNT, 0))
            if n_warnings < MAX_MISSING_DEPENDENCY_WARNINGS:
                # taken from qgsmessagebar.cpp
                # void QgsMessageBar::pushMessage( const QString &title, const QString &text, const QString &showMore, Qgis::MessageLevel level, int duration )

                title = 'Missing Python Package(s)!'

                a = QAction('Install missing')
                btn = QToolButton()
                btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: black; text-decoration: underline;")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
                btn.addAction(a)
                btn.setDefaultAction(a)
                btn.triggered.connect(self.showPackageInstaller)
                btn.triggered.connect(btn.deleteLater)
                self.__btn = btn
                item = QgsMessageBarItem(title, '', btn, Qgis.Warning, 200)
                self.messageBar().pushItem(item)

                n_warnings += 1
                settings.setValue(KEY_CNT, n_warnings)

        # finally, let this be the EnMAP-Box Singleton
        EnMAPBox._instance = self

        debugLog('Finish splashscreen')
        splash.finish(self.ui)

        debugLog('call QApplication.processEvents()')
        QApplication.processEvents()

        # debugLog('add QProject.instance()')
        # self.addProject(QgsProject.instance())

        debugLog('Load settings from QgsProject.instance()')
        self.onReloadProject()

    def addMessageBarTextBoxItem(self, title: str, text: str,
                                 level: Qgis.MessageLevel = Qgis.Info,
                                 buttonTitle='Show more',
                                 html=False):
        """
        Adds a message to the message bar that can be shown in detail using a text browser.
        :param title:
        :param text:
        :param level:
        :param buttonTitle:
        :param html:
        :return:
        """

        def showMessage(msg):
            viewer = QgsMessageViewer()
            viewer.setWindowTitle(title)
            if html:
                viewer.setMessageAsHtml(msg)
            else:
                viewer.setMessageAsPlainText(msg)
            viewer.showMessage(blocking=True)

        a = QAction(buttonTitle)
        btn = QToolButton()
        btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: black; text-decoration: underline;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        btn.addAction(a)
        btn.setDefaultAction(a)
        btn.triggered.connect(lambda *args, msg=text: showMessage(msg))
        btn.triggered.connect(btn.deleteLater)

        item = QgsMessageBarItem(title, '', btn, level, 200)
        item.__btn = btn
        self.mMessageBarItems.append(item)
        self.messageBar().pushItem(item)

    def onDockTreeViewDoubleClicked(self, index: QModelIndex):
        """
        Reacts on double click events
        :param index:
        :type index:
        :return:
        :rtype:
        """
        # reimplementation of void QgisApp::layerTreeViewDoubleClicked( const QModelIndex &index )

        settings = QgsSettings()
        mode = int(settings.value('qgis/legendDoubleClickAction', '0'))

        debugLog(f'Current MapCanvas: {self.currentMapCanvas().name()}')
        debugLog(f'Current MapLayer: {self.currentLayer()}')

        if mode == 0:
            # open layer properties

            node = self.dockTreeView().currentLegendNode()
            if isinstance(node, QgsSymbolLegendNode):
                originalSymbol = node.symbol()
                if not isinstance(originalSymbol, QgsSymbol):
                    return
                symbol = originalSymbol.clone()
                lyr = node.layerNode().layer()
                dlg = QgsSymbolSelectorDialog(symbol, QgsStyle.defaultStyle(), lyr, self.ui)


                context = QgsSymbolWidgetContext()
                context.setMapCanvas(self.currentMapCanvas())
                context.setMessageBar(self.messageBar())
                dlg.setContext(context)
                if dlg.exec():
                    node.setSymbol(symbol)
                return
            else:
                self.showLayerProperties(self.currentLayer())
            pass
        elif mode == 1:
            # open attribute table
            filterMode = settings.enumValue('qgis/attributeTableBehavior', QgsAttributeTableFilterModel.ShowAll)
            self.showAttributeTable(self.currentLayer(), filterMode = filterMode)
            pass
        elif mode == 2:
            # open layer styling dock
            pass

    def showAttributeTable(self, lyr: QgsVectorLayer,
                           filerExpression: str = "",
                           filterMode: QgsAttributeTableFilterModel.FilterMode = None):

        if lyr is None:
            lyr = self.currentLayer()
        if isinstance(lyr, QgsVectorLayer):
            dock = self.createDock(AttributeTableDock, lyr)


    def showPackageInstaller(self):
        """
        Opens a GUI to install missing PIP packages
        """
        from ..dependencycheck import PIPPackageInstaller, requiredPackages

        w = PIPPackageInstaller()
        w.addPackages(requiredPackages())
        w.show()

    def showResourceBrowser(self):
        """
        Opens a browser widget that lists all Qt Resources
        """
        from ..externals.qps.resources import showResources
        browser = showResources()
        browser.setWindowTitle('Resource Browser')
        self._browser = browser

    def disconnectQGISSignals(self):
        try:
            QgsProject.instance().layersAdded.disconnect(self.addMapLayers)
        except TypeError:
            pass
        try:
            QgsProject.instance().layersWillBeRemoved.disconnect(self.onLayersWillBeRemoved)
        except TypeError:
            pass

    def dataSourceManager(self) -> enmapbox.gui.datasourcemanager.DataSourceManager:
        return self.mDataSourceManager

    def dockManager(self) -> enmapbox.gui.dockmanager.DockManager:
        return self.mDockManager

    def addMapLayer(self, layer: QgsMapLayer):
        self.addMapLayers([layer])

    def addMapLayers(self, layers: typing.List[QgsMapLayer]):
        layers = [l for l in layers if isinstance(l, QgsMapLayer)]
        unregistered = [l for l in layers if l not in QgsProject.instance().mapLayers().values()]
        unknown = [l for l in layers if l not in self.mapLayers()]
        if len(unregistered) > 0:
            QgsProject.instance().addMapLayers(unregistered, False)
            # this triggers the DataSourceManager to add new sources
        if len(unknown) > 0:
            self.dataSourceManager().addSources(unknown)
        self.syncHiddenLayers()

    def onReloadProject(self, *args):

        proj: QgsProject = QgsProject.instance()
        path = proj.fileName()
        if os.path.isfile(path):
            archive = None
            if QgsZipUtils.isZipFile(path):
                archive = QgsProjectArchive()
                archive.unzip(path)
                path = archive.projectFile()

            file = QFile(path)

            doc = QDomDocument('qgis')
            doc.setContent(file)
            self.onReadProject(doc)

            if isinstance(archive, QgsProjectArchive):
                archive.clearProjectFile()

    def onWriteProject(self, dom: QDomDocument):

        node = dom.createElement('ENMAPBOX')
        root = dom.documentElement()

        # save time series
        self.timeSeries().writeXml(node, dom)

        # save map views
        self.mapWidget().writeXml(node, dom)
        root.appendChild(node)

    def onReadProject(self, doc: QDomDocument) -> bool:
        """
        Reads images and visualization settings from a QgsProject QDomDocument
        :param doc: QDomDocument
        :return: bool
        """
        if not isinstance(doc, QDomDocument):
            return False

        root = doc.documentElement()
        node = root.firstChildElement('ENMAPBOX')
        if node.nodeName() == 'ENMAPBOX':
            pass

        return True

    def onLayersWillBeRemoved(self, layerIDs):
        """
        Reacts on
        :param layerIDs:
        :type layerIDs:
        :return:
        :rtype:
        """
        assert isinstance(layerIDs, list)

        layers = [QgsProject.instance().mapLayer(lid) for lid in layerIDs]
        self.removeMapLayers(layers, remove_from_project=False)

    def syncHiddenLayers(self):
        grp = self.hiddenLayerGroup()
        if isinstance(grp, QgsLayerTreeGroup):
            knownInQGIS = [l.layerId() for l in grp.findLayers() if isinstance(l.layer(), QgsMapLayer)]

            # search in data sources
            knownAsDataSource = []
            for ds in self.dataSourceManager():
                if isinstance(ds, DataSourceSpatial):
                    id = ds.mapLayerId()
                    if id not in [None, '']:
                        knownAsDataSource.append(id)
            knownAsCanvasLayer = self.mapLayerIds()
            knownInEnMAPBox = knownAsDataSource + knownAsCanvasLayer
            knownInRegistry = list(QgsProject.instance().mapLayers().keys())

            L2C = dict()  # which layer is visible in which canvas?
            for lid in knownInEnMAPBox:
                L2C[lid] = None
                for c in self.mapCanvases():
                    assert isinstance(c, QgsMapCanvas)
                    for lyr in c.layers():
                        if isinstance(lyr, QgsMapLayer) and not sip.isdeleted(lyr) and lyr.id() == lid:
                            L2C[lid] = c
                            break

            toAdd = [l for l in knownInEnMAPBox if l not in knownInQGIS]
            toRemove = [l for l in knownInQGIS if l not in knownInEnMAPBox]

            # update QGIS layer tree
            for lid in toAdd:
                assert isinstance(lid, str)
                lyr = QgsProject.instance().mapLayer(lid)
                if isinstance(lyr, QgsMapLayer):
                    node = EnMAPBoxLayerTreeLayer(lyr)
                    self._layerTreeNodes.append(node)
                    grp.addChildNode(node)

            for lid in toRemove:
                # remove from hidden qgis layer tree
                layerTreeLayer = grp.findLayer(lid)
                if isinstance(layerTreeLayer, EnMAPBoxLayerTreeLayer):
                    if layerTreeLayer in self._layerTreeNodes:
                        self._layerTreeNodes.remove(layerTreeLayer)
                    layerTreeLayer.parent().removeChildNode(layerTreeLayer)

            # cleanup EnMAP-Box layer tree
            if len(toRemove) > 0:
                self.dockManagerTreeModel().removeLayers(toRemove)

            # update layer title according to its position in the EnMAP-Box
            for node in grp.children():
                if isinstance(node, EnMAPBoxLayerTreeLayer):
                    node.setCanvas(L2C.get(node.layerId(), None))

    def removeMapLayer(self, layer: QgsMapLayer, remove_from_project: bool = True):
        self.removeMapLayers([layer], remove_from_project=remove_from_project)

    def findGroupLayerIds(self, root: QgsLayerTreeGroup = None, exclude: typing.List[QgsLayerTreeGroup] = []):
        if root is None:
            ltv = qgis.utils.iface.layerTreeView()
            assert isinstance(ltv, QgsLayerTreeView)
            root: QgsLayerTreeGroup = ltv.model().rootGroup()

    def removeMapLayers(self, layers: typing.List[QgsMapLayer], remove_from_project=True):
        """
        Removes layers from the EnMAP-Box
        """
        grp = self.hiddenLayerGroup()
        enmapboxLayerIdsBefore = grp.findLayerIds()

        removedIds = [l.id() for l in layers]

        layersDS = self.dataSourceManager().mapLayers()
        layersTM = self.dockManagerTreeModel().mapLayers()
        layers = [l for l in layers if isinstance(l, QgsMapLayer) and l in layersDS + layersTM]
        self.syncHiddenLayers()

        ltv = qgis.utils.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        root: QgsLayerTreeGroup = ltv.model().rootGroup()
        remainingQgisLayerIDs = root.findLayerIds()
        if remove_from_project:
            QgsProject.instance().removeMapLayers([lid for lid in removedIds if lid not in remainingQgisLayerIDs])

    def updateCurrentLayerActions(self, *args):
        """
        Enables/disables actions and buttons that relate to the current layer and its current state
        """
        layer = self.currentLayer()
        isVector = isinstance(layer, QgsVectorLayer)

        hasSelectedFeatures = False

        for l in self.dockTreeView().model().mapLayers():
            if isinstance(l, QgsVectorLayer) and l.selectedFeatureCount() > 0:
                hasSelectedFeatures = True
                break

        self.ui.mActionDeselectFeatures.setEnabled(hasSelectedFeatures)
        self.ui.mActionSelectFeatures.setEnabled(isVector)
        self.ui.mActionToggleEditing.setEnabled(isVector)
        self.ui.mActionToggleEditing.setChecked(isVector and layer.isEditable())
        self.ui.mActionAddFeature.setEnabled(isVector and layer.isEditable())

        if isVector:
            if layer.geometryType() == QgsWkbTypes.PointGeometry:
                icon = QIcon(':/images/themes/default/mActionCapturePoint.svg')
            elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                icon = QIcon(':/images/themes/default/mActionCaptureLine.svg')
            elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                icon = QIcon(':/images/themes/default/mActionCapturePolygon.svg')
            else:
                icon = QIcon(':/images/themes/default/mActionCapturePolygon.svg')
            self.ui.mActionAddFeature.setIcon(icon)

        self.ui.mActionSaveEdits.setEnabled(isVector and layer.isEditable())

        if isinstance(layer, (QgsRasterLayer, QgsVectorLayer)):
            self.currentLayerChanged.emit(layer)

    def processingProvider(self) -> EnMAPBoxProcessingProvider:
        """
        Returns the EnMAPBoxAlgorithmProvider or None, if it was not initialized
        :return:
        """
        import enmapbox.algorithmprovider
        return enmapbox.algorithmprovider.instance()

    def classificationSchemata(self) -> list:
        """
        Returns a list of ClassificationSchemes, derived from datasets known to the EnMAP-Box
        :return: [list-of-ClassificationSchemes
        """
        return self.mDataSourceManager.classificationSchemata()

    def loadCursorLocationValueInfo(self, spatialPoint: SpatialPoint, mapCanvas: MapCanvas):
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

    def mapLayerStore(self) -> QgsMapLayerStore:
        """
        Returns the EnMAP-Box internal QgsMapLayerStore
        :return: QgsMapLayerStore
        """
        return QgsProject.instance()

    def mapLayerIds(self) -> typing.List[str]:
        return self.layerTreeView().layerTreeModel().mapLayerIds()

    def mapLayers(self) -> typing.List[QgsMapLayer]:
        """
        Returns a list of all EnMAP-Box map layers that are shown in a MapCanvas or the related Layer Tree View
        :return: [list-of-QgsMapLayers]
        """
        return self.layerTreeView().layerTreeModel().mapLayers()

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

    def freezeCanvases(self, b: bool):
        """
        Freezes/releases the map canvases
        """
        for c in self.mapCanvases():
            c.freeze(b)

    def initActions(self):
        # link action to managers
        self.ui.mActionAddDataSource.triggered.connect(self.mDataSourceManager.addDataSourceByDialog)
        self.ui.mActionAddSentinel2.triggered.connect(self.mDataSourceManager.addSentinel2ByDialog)
        self.ui.mActionAddSubDatasets.triggered.connect(self.mDataSourceManager.addSubDatasetsByDialog)

        self.ui.mActionAddMapView.triggered.connect(lambda: self.mDockManager.createDock('MAP'))
        self.ui.mActionAddTextView.triggered.connect(lambda: self.mDockManager.createDock('TEXT'))
        self.ui.mActionAddWebView.triggered.connect(lambda: self.mDockManager.createDock('WEBVIEW'))
        self.ui.mActionAddMimeView.triggered.connect(lambda: self.mDockManager.createDock('MIME'))
        self.ui.mActionAddSpeclibView.triggered.connect(lambda: self.mDockManager.createDock('SPECLIB'))
        self.ui.mActionLoadExampleData.triggered.connect(lambda: self.openExampleData(
            mapWindows=1 if len(self.mDockManager.docks(MapDock)) == 0 else 0))

        # activate map tools

        def initMapToolAction(action, key):
            assert isinstance(action, QAction)
            assert isinstance(key, MapTools)
            action.triggered.connect(lambda: self.setMapTool(key))
            # action.toggled.connect(lambda b, a=action : self.onMapToolActionToggled(a))
            action.setProperty(EnMAPBox.MAPTOOLACTION, key)

        initMapToolAction(self.ui.mActionPan, MapTools.Pan)
        initMapToolAction(self.ui.mActionZoomIn, MapTools.ZoomIn)
        initMapToolAction(self.ui.mActionZoomOut, MapTools.ZoomOut)
        initMapToolAction(self.ui.mActionZoomPixelScale, MapTools.ZoomPixelScale)
        initMapToolAction(self.ui.mActionZoomFullExtent, MapTools.ZoomFull)
        initMapToolAction(self.ui.mActionIdentify, MapTools.CursorLocation)
        initMapToolAction(self.ui.mActionSelectFeatures, MapTools.SelectFeature)
        initMapToolAction(self.ui.mActionAddFeature, MapTools.AddFeature)

        def onEditingToggled(b: bool):
            l = self.currentLayer()
            if b:
                self.mVectorLayerTools.startEditing(l)
            else:
                self.mVectorLayerTools.stopEditing(l, True)

        self.ui.mActionToggleEditing.toggled.connect(onEditingToggled)

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
        # self.ui.mActionAddFeature.triggered.connect(self.onAddFeatureTriggered)
        self.setMapTool(MapTools.CursorLocation)

        self.ui.mActionSaveProject.triggered.connect(lambda: self.saveProject(False))
        self.ui.mActionSaveProjectAs.triggered.connect(lambda: self.saveProject(True))

        # re-enable if there is a proper connection
        self.ui.mActionSaveProject.setVisible(False)
        self.ui.mActionSaveProjectAs.setVisible(False)

        from enmapbox.gui.mapcanvas import CanvasLinkDialog
        self.ui.mActionMapLinking.triggered.connect(
            lambda: CanvasLinkDialog.showDialog(parent=self.ui, canvases=self.mapCanvases()))
        from enmapbox.gui.about import AboutDialog
        self.ui.mActionAbout.triggered.connect(lambda: AboutDialog(parent=self.ui).show())
        from enmapbox.gui.settings import showSettingsDialog
        self.ui.mActionProjectSettings.triggered.connect(lambda: showSettingsDialog(self.ui))
        self.ui.mActionExit.triggered.connect(self.exit)

        import webbrowser
        self.ui.mActionOpenIssueReportPage.triggered.connect(lambda: webbrowser.open(enmapbox.CREATE_ISSUE))
        self.ui.mActionOpenProjectPage.triggered.connect(lambda: webbrowser.open(enmapbox.REPOSITORY))
        self.ui.mActionOpenOnlineDocumentation.triggered.connect(lambda: webbrowser.open(enmapbox.DOCUMENTATION))

        self.ui.mActionShowPackageInstaller.triggered.connect(self.showPackageInstaller)

        # finally, fix the popup mode of menus
        for toolBar in self.ui.findChildren(QToolBar):
            for toolButton in toolBar.findChildren(QToolButton):
                assert isinstance(toolButton, QToolButton)
                if isinstance(toolButton.defaultAction(), QAction) and isinstance(toolButton.defaultAction().menu(),
                                                                                  QMenu):
                    toolButton.setPopupMode(QToolButton.MenuButtonPopup)

    def initActionsAddProduct(self):
        """
        Initializes the product loaders under <menu> Project -> Add Product
        """
        menu = self.ui.menuAdd_Product
        separator = self.ui.mActionAddSentinel2
        assert isinstance(menu, QMenu)
        assert isinstance(separator, QAction)

        # add more product import actions hereafter
        a = QAction('EnMAP L1B', parent=menu)
        a.setToolTip('Import EnMAP L1B product')
        a.triggered.connect(lambda *args: self.showProcessingAlgorithmDialog(ImportEnmapL1B()))
        menu.insertAction(separator, a)

        a = QAction('EnMAP L1C', parent=menu)
        a.setToolTip('Import EnMAP L1C product')
        a.triggered.connect(lambda *args: self.showProcessingAlgorithmDialog(ImportEnmapL1C()))
        menu.insertAction(separator, a)

        a = QAction('EnMAP L2A', parent=menu)
        a.setToolTip('Import EnMAP L2A product')
        a.triggered.connect(lambda *args: self.showProcessingAlgorithmDialog(ImportEnmapL2A()))
        menu.insertAction(separator, a)

        a = QAction('PRISMA L2D', parent=menu)
        a.setToolTip('Import PRISMA L2D product')
        a.triggered.connect(lambda *args: self.showProcessingAlgorithmDialog(ImportPrismaL2D()))
        menu.insertAction(separator, a)

    def _mapToolButton(self, action) -> Optional[QToolButton]:
        for toolBar in self.ui.findChildren(QToolBar):
            for toolButton in toolBar.findChildren(QToolButton):
                if toolButton.defaultAction() == action:
                    return toolButton
        return None

    def _mapToolActions(self) -> list:
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

    def onCrosshairPositionChanged(self, spatialPoint: SpatialPoint):
        """
        Synchronizes all crosshair positions. Takes care of CRS differences.
        :param spatialPoint: SpatialPoint of the new Crosshair position
        """
        sender = self.sender()
        for mapCanvas in self.mapCanvases():
            if isinstance(mapCanvas, MapCanvas) and mapCanvas != sender:
                mapCanvas.setCrosshairPosition(spatialPoint, emitSignal=False)

    def spectralProfileBridge(self) -> SpectralProfileBridge:
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
            self.spectralProfileBridge().addDestination(slw)
            slw.sigFilesCreated.connect(self.addSources)
            self.dataSourceManager().addSource(slw.speclib())

        if isinstance(dock, MapDock):
            canvas = dock.mapCanvas()
            assert isinstance(canvas, MapCanvas)
            canvas.sigCrosshairPositionChanged.connect(self.onCrosshairPositionChanged)
            canvas.setCrosshairVisibility(True)
            canvas.mapTools().setVectorLayerTools(self.mVectorLayerTools)

            self.setMapTool(self.mMapToolKey, canvases=[canvas])
            canvas.mapTools().mtCursorLocation.sigLocationRequest[QgsCoordinateReferenceSystem, QgsPointXY].connect(
                lambda crs, pt, c=canvas: self.setCurrentLocation(SpatialPoint(crs, pt), canvas)
            )

            node = self.dockManagerTreeModel().mapDockTreeNode(canvas)
            assert isinstance(node, MapDockTreeNode)
            node.sigAddedLayers.connect(self.sigMapLayersAdded[list].emit)
            node.sigRemovedLayers.connect(self.sigMapLayersRemoved[list].emit)
            self.sigMapCanvasAdded.emit(canvas)

        if isinstance(dock, AttributeTableDock):
            dock.attributeTableWidget.setVectorLayerTools(self.mVectorLayerTools)

        if isinstance(dock, SpectralLibraryDock):
            dock.speclibWidget().setVectorLayerTools(self.mVectorLayerTools)

        self.sigDockAdded.emit(dock)

    def vectorLayerTools(self) -> QgsVectorLayerTools:
        return self.mVectorLayerTools

    def onDockRemoved(self, dock):
        if isinstance(dock, MapDock):
            self.sigMapCanvasRemoved.emit(dock.mapCanvas())

        if isinstance(dock, SpectralLibraryDock):
            self.spectralProfileBridge().removeDestination(dock.speclibWidget())

    @pyqtSlot(SpatialPoint, QgsMapCanvas)
    def loadCurrentMapSpectra(self, spatialPoint: SpatialPoint, mapCanvas: QgsMapCanvas = None, runAsync: bool = None):
        """
        Loads SpectralProfiles from a location defined by `spatialPoint`
        :param spatialPoint: SpatialPoint
        :param mapCanvas: QgsMapCanvas
        """

        if len(self.docks(SpectralLibraryDock)) == 0:
            self.createDock(SpectralLibraryDock)

        self.ui.spectralProfileSourcePanel.loadCurrentMapSpectra(spatialPoint, mapCanvas=mapCanvas, runAsync=runAsync)

    def setMapTool(self, mapToolKey: MapTools, *args, canvases=None, **kwds):
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
            # SpectralProfile is a shortcut for Identify + return with profile option
            self.ui.optionIdentifyProfile.setChecked(True)
            self.ui.mActionIdentify.setChecked(True)
            return

        if mapToolKey == MapTools.AddFeature:
            s = ""

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

    def initEnMAPBoxApplications(self,
                                 load_core_apps: bool = True,
                                 load_other_apps: bool = True):
        """
        Initialized EnMAPBoxApplications
        """
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)

        listingBasename = 'enmapboxapplications.txt'

        DIR_ENMAPBOX = pathlib.Path(enmapbox.DIR_ENMAPBOX)
        INTERNAL_APPS = DIR_ENMAPBOX / 'coreapps'
        EXTERNAL_APPS = DIR_ENMAPBOX / 'apps'
        # load internal "core" apps
        if load_core_apps:
            self.applicationRegistry.addApplicationFolder(INTERNAL_APPS, isRootFolder=True)
        # check for listing file
        p = INTERNAL_APPS / listingBasename
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        # load external / standard apps
        if load_other_apps:
            self.applicationRegistry.addApplicationFolder(EXTERNAL_APPS, isRootFolder=True)

        # check for listing file
        p = EXTERNAL_APPS / listingBasename
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        # check for listing file in root
        p = DIR_ENMAPBOX / listingBasename
        if os.path.isfile(p):
            self.applicationRegistry.addApplicationListing(p)

        # find other app-folders or listing files folders
        from enmapbox.gui.settings import enmapboxSettings
        settings = enmapboxSettings()
        for appPath in re.split('[;\n]', settings.value('EMB_APPLICATION_PATH', '')):
            if os.path.isdir(appPath):
                self.applicationRegistry.addApplicationFolder(appPath, isRootFolder=True)
            elif os.path.isfile(p):
                self.applicationRegistry.addApplicationListing(p)
            else:
                print('Unable to load EnMAPBoxApplication(s) from path: "{}"'.format(p), file=sys.stderr)

        errorApps = [app for app, v in self.applicationRegistry.mAppInitializationMessages.items()
                     if v is not True]
        settings = self.settings()

        KEY_COUNTS = 'APP_ERROR_COUNTS'
        if settings.value(KEY_MISSING_DEPENDENCY_VERSION, None) != self.version():
            settings.setValue(KEY_COUNTS, {})

        counts = settings.value(KEY_COUNTS, {})

        if len(errorApps) > 0:
            title = 'EnMAPBoxApplication error(s)'
            info = [title + ':']
            to_remove = [app for app in counts.keys() if app not in errorApps]
            for app in to_remove:
                counts.pop(app)

            for app in errorApps:

                v = self.applicationRegistry.mAppInitializationMessages[app]

                n_counts = counts.get(app, 0)
                if n_counts < MAX_MISSING_DEPENDENCY_WARNINGS:

                    info.append(r'</br><b>{}:</b>'.format(app))
                    info.append('<p>')
                    if v == False:
                        info.append(r'"{}" did not return any EnMAPBoxApplication\n'.format(v))
                    elif isinstance(v, str):
                        info.append('<code>{}</code>'.format(v.replace('\n', '<br />\n')))
                    info.append('</p>')
                    counts[app] = n_counts + 1

            self.addMessageBarTextBoxItem(title, '\n'.join(info), level=Qgis.Warning, html=True)

        settings.setValue(KEY_COUNTS, counts)

    def settings(self) -> QSettings:
        """
        Returns the EnMAP-Box user settings
        """
        from enmapbox import enmapboxSettings
        return enmapboxSettings()

    def exit(self):
        """Closes the EnMAP-Box"""
        self.ui.setParent(None)
        self.ui.close()
        self.deleteLater()

    def onLogMessage(self, message: str, tag: str, level):
        """
        Receives log messages and, if tag=EnMAP-Box, displays them in the EnMAP-Box message bar.
        :param message:
        :type message:
        :param tag:
        :type tag:
        :param level:
        :type level:
        :return:
        :rtype:
        """
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

        if level == Qgis.Critical:
            duration = 200
        else:
            duration = 50

        mbar.pushMessage(tag, line1, showMore, level, duration)

    def onDataDropped(self, droppedData):
        assert isinstance(droppedData, list)
        mapDock = None
        from enmapbox.gui.datasources import DataSourceSpatial
        for dataItem in droppedData:
            if isinstance(dataItem, DataSourceSpatial):
                dataSources = self.mDataSourceManager.addSource(dataItem)
                if mapDock is None:
                    mapDock = self.createDock('MAP')
                mapDock.addLayers([ds.createRegisteredMapLayer() for ds in dataSources])

            # any other types to handle?

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
            files = list(
                file_search(dir, re.compile('.*(bsq|bil|bip|tif|gpkg|sli|img|shp|pkl)$', re.I), recursive=True))

            added = self.addSources(files)

            for n in range(mapWindows):
                dock = self.createDock('MAP')
                assert isinstance(dock, MapDock)
                lyrs = []
                for src in added:
                    if isinstance(src, DataSourceSpatial):
                        lyr = src.createUnregisteredMapLayer()
                        if isinstance(lyr, QgsRasterLayer):
                            r = defaultRasterRenderer(lyr)
                            r.setInput(lyr.dataProvider())
                            lyr.setRenderer(r)
                        lyrs.append(lyr)

                # choose first none-geographic raster CRS as map CRS
                crs_is_set = False
                for lyr in lyrs:
                    if isinstance(lyr, QgsRasterLayer) and isinstance(lyr.crs(),
                                                                      QgsCoordinateReferenceSystem) and not lyr.crs().isGeographic():
                        dock.mapCanvas().setDestinationCrs(lyr.crs())
                        crs_is_set = True
                        break

                dock.addLayers(lyrs)
                dock.mapCanvas().zoomToFullExtent()

    def onDataSourceRemoved(self, dataSource: DataSource):
        """
        Reacts on removed data sources
        :param dataSource: DataSource
        """
        assert isinstance(dataSource, DataSource)

        # remove any layer that matches the same source uri
        model: DockManagerTreeModel = self.dockManagerTreeModel()
        model.removeDataSource(dataSource)

        self.sigDataSourceRemoved[str].emit(dataSource.uri())
        self.sigDataSourceRemoved[DataSource].emit(dataSource)

        if isinstance(dataSource, DataSourceRaster):
            self.sigRasterSourceRemoved[str].emit(dataSource.uri())
            self.sigRasterSourceRemoved[DataSourceRaster].emit(dataSource)
            self.spectralProfileBridge().removeSource(dataSource.uri())

        if isinstance(dataSource, DataSourceSpectralLibrary):
            to_remove = [d for d in self.dockManager().docks() \
                         if isinstance(d, SpectralLibraryDock) \
                         and d.speclib() == dataSource.speclib()]
            for d in to_remove:
                self.dockManager().removeDock(d)

            self.sigSpectralLibraryRemoved[str].emit(dataSource.uri())
            self.sigSpectralLibraryRemoved[SpectralLibrary].emit(dataSource.speclib())
            self.sigSpectralLibraryRemoved[DataSourceSpectralLibrary].emit(dataSource)

        if isinstance(dataSource, DataSourceVector):
            self.sigVectorSourceRemoved[str].emit(dataSource.uri())
            self.sigVectorSourceRemoved[DataSourceVector].emit(dataSource)

        # finally, remove related map layers
        if isinstance(dataSource, DataSourceSpatial):
            self.removeMapLayer(dataSource.mapLayer())
        self.syncHiddenLayers()

    def onDataSourceAdded(self, dataSource: DataSource):

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
            self.sigSpectralLibraryAdded[SpectralLibrary].emit(dataSource.speclib())
            self.sigSpectralLibraryAdded[DataSourceSpectralLibrary].emit(dataSource)

        if isinstance(dataSource, DataSourceSpatial):
            self.addMapLayer(dataSource.mapLayer())

    def restoreProject(self):
        raise NotImplementedError()

    def setCurrentLocation(self, spatialPoint: SpatialPoint, mapCanvas: QgsMapCanvas = None):
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
                pt = spatialPoint.toCrs(mapCanvas.mapSettings().destinationCrs())
                if isinstance(pt, SpatialPoint):
                    mapCanvas.setCenter(pt)
                    mapCanvas.refresh()

        if bSP:
            self.loadCurrentMapSpectra(spatialPoint, mapCanvas)

    def currentLocation(self) -> SpatialPoint:
        """
        Returns the current location, which is a SpatialPoint last clicked by a user on a map canvas.
        :return: SpatialPoint
        """
        return self.mCurrentMapLocation

    def setCurrentSpectra(self, spectra: list):
        """
        Sets the list of SpectralProfiles to be considered as current spectra
        :param spectra: [list-of-SpectralProfiles]
        """
        warnings.warn(DeprecationWarning(''))

        """        
        b = len(self.mCurrentSpectra) == 0
        self.mCurrentSpectra = spectra[:]

        # check if any SPECLIB window was opened
        if len(self.dockManager().docks('SPECLIB')) == 0:
            #and getattr(self, '_initialSpeclibDockCreated', False) == False:
            dock = self.createDock('SPECLIB')
            assert isinstance(dock, SpectralLibraryDock)

        self.sigCurrentSpectraChanged.emit(self.mCurrentSpectra[:])
        """

    def currentSpectra(self) -> list:
        """
        Returns the spectra currently selected using the profile tool.

        :return: [list-of-spectra]
        """
        return self.spectralProfileBridge().currentProfiles()

    def version(self) -> str:
        """
        Returns the version string
        """
        return enmapbox.__version__

    def dataSourceTreeView(self) -> QTreeView:
        return self.ui.dataSourcePanel.dataSourceTreeView

    def dataSources(self, sourceType='ALL', onlyUri: bool = True) -> list:
        """
        Returns a list of URIs to the data sources of type "sourceType" opened in the EnMAP-Box
        :param sourceType: ['ALL', 'RASTER', 'VECTOR', 'MODEL'],
                            see enmapbox.gui.datasourcemanager.DataSourceManager.SOURCE_TYPES
        :param onlyUri: bool, set on False to return the DataSource object instead of the uri only.
        :return: [list-of-datasource-URIs (str)]
        """

        sources = self.mDataSourceManager.sources(sourceTypes=sourceType)
        if onlyUri:
            sources = [ds.uri() for ds in sources]
        return sources

    def createDock(self, *args, **kwds) -> Dock:
        """
        Create and returns a new Dock
        :param args:
        :param kwds:
        :return:
        """
        return self.mDockManager.createDock(*args, **kwds)

    def removeDock(self, *args, **kwds):
        """
        Removes a Dock instance.
        See `enmapbox/gui/dockmanager.py` for details
        :param args:
        :param kwds:
        """
        self.mDockManager.removeDock(*args, **kwds)

    def dockTreeView(self) -> enmapbox.gui.dockmanager.DockTreeView:
        """
        Returns the DockTreeView
        """
        return self.ui.dockPanel.dockTreeView

    def dockManagerTreeModel(self) -> DockManagerTreeModel:
        """
        Returns the DockManagerTreeModel
        :return: DockManagerTreeModel
        """
        return self.dockTreeView().model()

    def docks(self, dockType=None):
        """
        Returns dock widgets
        :param dockType: optional, specifies the type of dock widgets to return
        :return: [list-of-DockWidgets]
        """
        return self.mDockManager.docks(dockType=dockType)

    def addSources(self, sourceList):
        """
        :param sourceList:
        :return: Returns a list of added DataSources or the list of DataSources that were derived from a single data source uri.
        """
        assert isinstance(sourceList, list)
        return self.mDataSourceManager.addSources(sourceList)

    def addSource(self, source, name=None):
        """
        Returns a list of added DataSources or the list of DataSources that were derived from a single data source uri.
        :param source:
        :param name:
        :return: [list-of-dataSources]
        """
        return self.mDataSourceManager.addSource(source, name=name)

    def removeSources(self, dataSourceList: list = None):
        """
        Removes data sources.
        Removes all sources available if `dataSourceList` remains unspecified.
        :param dataSourceList:[list-of-data-sources]
        """
        self.mDataSourceManager.removeSources(dataSourceList)

    def removeSource(self, source):
        """
        Removes a single datasource
        :param source: DataSource or str
        """
        self.mDataSourceManager.removeSource(source)

    def menu(self, title) -> QMenu:
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

    def showLayerProperties(self, mapLayer: QgsMapLayer):
        """
        Show a map layer property dialog
        :param mapLayer:
        :return:
        """
        if mapLayer is None:
            mapLayer = self.currentLayer()

        if isinstance(mapLayer, (QgsVectorLayer, QgsRasterLayer)):

            # 1. find the map canvas
            mapCanvas = None
            for canvas in self.mapCanvases():
                if mapLayer in canvas.layers():
                    mapCanvas = canvas
                    break
            # 2.
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
    def icon() -> QIcon:
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

    def closeEvent(self, event: QCloseEvent):
        assert isinstance(event, QCloseEvent)

        try:
            # remove all hidden layers
            self.mDataSourceManager.clear()
            QApplication.processEvents()
        except Exception as ex:
            messageLog(str(ex), Qgis.Critical)
        # de-refer the EnMAP-Box Singleton
        EnMAPBox._instance = None
        self.sigClosed.emit()

        try:
            import gc
            gc.collect()
        except Exception as ex:
            print(f'Errors when closing the EnMAP-Box: {ex}', file=sys.stderr)
            pass
        EnMAPBox._instance = None
        event.accept()

    def close(self):
        self.disconnectQGISSignals()
        self.mDataSourceManager.close()
        self.ui.close()

    def hiddenLayerGroup(self) -> QgsLayerTreeGroup:
        """
        Returns the hidden QgsLayerTreeGroup in the QGIS Layer Tree
        :return: QgsLayerTreeGroup
        """

        ltv = qgis.utils.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        root: QgsLayerTreeGroup = ltv.model().rootGroup()
        grp = root.findGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        if not isinstance(grp, EnMAPBoxHiddenLayerTreeGroup):
            # assert not isinstance(self._layerTreeGroup, QgsLayerTreeGroup)
            enmapbox.debugLog('CREATE HIDDEN LAYER GROUP')
            # print('CREATE HIDDEN LAYER GROUP')
            grp: EnMAPBoxHiddenLayerTreeGroup = EnMAPBoxHiddenLayerTreeGroup()
            root.addChildNode(grp)
            self._layerTreeGroup = grp

        ltv = qgis.utils.iface.layerTreeView()
        index = ltv.model().node2index(grp)
        grp.setItemVisibilityChecked(False)

        hide = str(os.environ.get('DEBUG')).lower() not in ['1', 'true']
        grp.setCustomProperty('nodeHidden', 'true' if hide else 'false')
        ltv.setRowHidden(index.row(), index.parent(), hide)

        return grp

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

    def layerTreeView(self) -> enmapbox.gui.dockmanager.DockTreeView:
        """
        Returns the Dock Panel Tree View
        :return: enmapbox.gui.dockmanager.DockTreeView
        """
        return self.dockTreeView()

    ### SIGNALS from QgisInterface ####

    initializationCompleted = pyqtSignal()
    layerSavedAs = pyqtSignal(QgsMapLayer, str)
    currentLayerChanged = pyqtSignal(QgsMapLayer)

    ### ACTIONS ###
    def actionAddSentinel2(self) -> QAction:
        return self.ui.mActionAddSentinel2

    def actionAddSubDatasets(self) -> QAction:
        return self.ui.mActionAddSubDatasets

    def actionAbout(self) -> QAction:
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

    def addProject(self, project: str):
        # 1- clear everything
        # restore
        if isinstance(project, str):
            self.addProject(pathlib.Path(project))
        elif isinstance(project, pathlib.Path) and project.is_file():
            p = QgsProject()
            p.read(project.as_posix())
            self.addProject(p)
        elif isinstance(project, QgsProject):
            scope = 'HU-Berlin'
            key = 'EnMAP-Box'

            self.onReloadProject()

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

    def openProject(self, project):
        if isinstance(project, str):
            project = pathlib.Path(project)
        if isinstance(project, pathlib.Path):
            p = QgsProject()
            p.read(project.as_posix())
            self.openProject(project)
        elif isinstance(project, QgsProject):
            self.addProject(project)

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
        return self.mActionSaveEdits

    def actionSaveMapAsImage(self):
        pass

    def actionSaveProject(self) -> QAction:
        return self.mActionSaveProject

    def actionSaveProjectAs(self) -> QAction:
        return self.mActionSaveProjectAs

    def saveProject(self, saveAs: bool):
        """
        Call to save EnMAP-Box settings in a QgsProject file
        :param saveAs: bool, if True, opens a dialog to save the project into another file
        """

        # todo: save EnMAP Project settings
        # 1. save data sources

        # 2. save docks / map canvases

        # inform others that the project will be saves
        self.sigProjectWillBeSaved.emit()

        # call QGIS standard functionality
        from qgis.utils import iface
        if saveAs:
            iface.actionSaveProjectAs().trigger()
        else:
            iface.actionSaveProject().trigger()

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

    def showProcessingAlgorithmDialog(self, algorithmName: typing.Union[str, QgsProcessingAlgorithm]) -> QWidget:
        """
        :param algorithmName:
        :type algorithmName:
        :return:
        :rtype: processing.gui.AlgorithmDialog.AlgorithmDialog
        """
        """Opens the dialog to start an QgsProcessingAlgorithm"""

        from processing.gui.AlgorithmDialog import AlgorithmDialog

        algorithm = None
        all_names = []
        for alg in QgsApplication.processingRegistry().algorithms():
            assert isinstance(alg, QgsProcessingAlgorithm)
            all_names.append(alg.id())
            if isinstance(algorithmName, QgsProcessingAlgorithm):
                algorithmId = algorithmName.id()
            elif isinstance(algorithmName, str):
                algorithmId = algorithmName
            else:
                raise ValueError(algorithmName)

            algId = alg.id().split(':')[1]  # remove provider prefix
            if algorithmId == algId:
                algorithm = alg
                break

        if not isinstance(algorithm, QgsProcessingAlgorithm):
            raise Exception('Algorithm {} not found in QGIS Processing Registry'.format(algorithmName))

        dlg = alg.createCustomParametersWidget(self.ui)
        if not dlg:
            dlg = AlgorithmDialog(alg.create(), parent=self.ui)
        dlg.show()
        return dlg

    def addLayerMenu(self):
        pass

    def mainWindow(self) -> EnMAPBoxUI:
        return self.ui

    def messageBar(self) -> QgsMessageBar:
        return self.ui.messageBar

    def iconSize(self, dockedToolbar=False):
        # return self.ui.mActionAddDataSource.icon().availableSizes()[0]
        return QSize(16, 16)

    def spectralLibraries(self) -> typing.List[SpectralLibrary]:
        """
        Returns a list of SpectraLibraries that either known as DataSource, added to one of the Maps or visible in a SpectralLibrary Widget).
        :return: [list-of-SpectralLibraries]
        """
        candidates = []
        for source in self.mDataSourceManager.sources():
            if isinstance(source, DataSourceSpectralLibrary):
                candidates.append(source.mapLayer())
        for lyr in self.mapLayers():
            if isinstance(lyr, SpectralLibrary):
                candidates.append(lyr)

        for dock in self.docks():
            if isinstance(dock, SpectralLibraryDock):
                candidates.append(dock.speclib())

        speclibs = []
        for c in candidates:
            if isinstance(c, SpectralLibrary) and c not in speclibs:
                speclibs.append(c)

        return speclibs

    def mapCanvases(self) -> typing.List[MapCanvas]:
        """
        Returns all MapCanvas(QgsMapCanvas) objects known to the EnMAP-Box
        :return: [list-of-MapCanvases]
        """
        return self.dockTreeView().mapCanvases()

    def mapCanvas(self, virtual=False) -> MapCanvas:
        """
        Returns a single MapCanvas.
        :param virtual: bool, set True to return an invisible QgsMapCanvas that contains all data source layers
        :return: MapCanvas
        """

        if virtual:
            assert isinstance(self.mQgisInterfaceMapCanvas, QgsMapCanvas)
            self.mQgisInterfaceMapCanvas.setLayers([])

            layers = []
            for ds in self.mDataSourceManager.sources():
                if isinstance(ds, DataSourceSpatial):
                    layers.append(ds.createUnregisteredMapLayer())
            self.mQgisInterfaceMapCanvas.setLayers(layers)
            if len(layers) > 0:
                self.mQgisInterfaceMapCanvas.mapSettings().setDestinationCrs(layers[0].crs())
                self.mQgisInterfaceMapCanvas.setExtent(layers[0].extent())

            return self.mQgisInterfaceMapCanvas
        mapDocks = self.mDockManager.docks(dockType='MAP')
        if len(mapDocks) > 0:
            return mapDocks[0].mapCanvas()
        else:
            return None

    def firstRightStandardMenu(self) -> QMenu:
        return self.ui.menuApplications

    def registerMainWindowAction(self, action, defaultShortcut):
        self.ui.addAction(action)

    def registerMapLayerConfigWidgetFactory(self, factory: QgsMapLayerConfigWidgetFactory):
        self.iface.registerMapLayerConfigWidgetFactory(factory)

    def unregisterMapLayerConfigWidgetFactory(self, factory):
        self.iface.unregisterMapLayerConfigWidgetFactory(factory)

    def vectorMenu(self):
        return QMenu()

    def addDockWidget(self, area, dockwidget: QDockWidget):

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
        return self.mDockManager

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

    def zoomToSelected(self):
        """
        Zooms the current map canvas to the selected features of the current map layer
        :return:
        """
        lyr = self.currentLayer()
        canvas = self.currentMapCanvas()

        if isinstance(lyr, QgsVectorLayer) and lyr.selectedFeatureCount() > 0 and isinstance(canvas, QgsMapCanvas):
            # todo: implement zoom to selected
            pass

        pass

    def zoomToExtent(self, extent: SpatialExtent):
        """
        Zooms the current map canvas to a requested extent
        """
        canvas = self.currentMapCanvas()
        if isinstance(canvas, QgsMapCanvas) and isinstance(extent, SpatialExtent):
            ext = extent.toCrs(canvas.mapSettings().destinationCrs())
            if isinstance(ext, SpatialExtent):
                canvas.setExtent(ext)
                canvas.refresh()

    def panToPoint(self, point: SpatialPoint):
        """
        pans the current map canvas to the provided point
        """
        canvas = self.currentMapCanvas()
        if isinstance(canvas, QgsMapCanvas) and isinstance(point, SpatialPoint):
            p = point.toCrs(canvas.mapSettings().destinationCrs())
            if isinstance(p, SpatialPoint):
                canvas.setCenter(p)
                canvas.refresh()

    def panToSelected(self):
        """
        Pans the current map canvas to the selected features in a current map canvas
        :return:
        """
        canvas = self.currentMapCanvas()
        lyr = self.currentLayer()
        if isinstance(lyr, QgsVectorLayer) and isinstance(canvas, QgsMapCanvas):
            s = ""

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zooms the current map canvas to its full extent"""
        canvas = self.currentMapCanvas()
        if isinstance(canvas, QgsMapCanvas):
            canvas.zoomToFullExtent()

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
        lyr = QgsRasterLayer(path, base_name, key)

        self.addSource(lyr, base_name)

    def currentMapCanvas(self) -> MapCanvas:
        """
        Returns the active map canvas, i.e. the MapCanvas that was clicked last.
        :return: MapCanvas
        """
        return self.dockTreeView().currentMapCanvas()

    def setCurrentMapCanvas(self, mapCanvas: MapCanvas) -> bool:
        """
        Sets the active map canvas
        :param mapCanvas: MapCanvas
        :return: bool, True, if mapCanvas exists in the EnMAP-Box, False otherwise
        """
        return self.dockTreeView().setCurrentMapCanvas(mapCanvas)

    def setActiveLayer(self, mapLayer: QgsMapLayer) -> bool:
        return self.setCurrentLayeer(mapLayer)

    def setCurrentLayer(self, mapLayer: QgsMapLayer) -> bool:
        """
        Set the active layer (layer gets selected in the Data View legend).
        :param mapLayer: QgsMapLayer
        :return: bool. True, if mapLayer exists, False otherwise.
        """

        self.dockTreeView().setCurrentLayer(mapLayer)
        return isinstance(mapLayer, QgsMapLayer)

    def currentLayer(self) -> QgsMapLayer:
        """
        Returns the current layer of the active map canvas
        :return: QgsMapLayer
        """
        return self.ui.dockPanel.dockTreeView.currentLayer()

    def activeLayer(self):
        return self.currentLayer()

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
