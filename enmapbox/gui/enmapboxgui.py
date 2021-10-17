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
import os
import pathlib
import re
import sys
import enum
import typing
import warnings
from typing import Optional, Dict, Union


from PyQt5.QtCore import pyqtSignal, Qt, QObject, QModelIndex, pyqtSlot, QSettings, QEventLoop, QRect, QSize, QFile
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent, QDropEvent, QPixmap, QColor, QIcon, QKeyEvent, \
    QCloseEvent, QGuiApplication, QPainter
from PyQt5.QtWidgets import QFrame, QToolBar, QToolButton, QAction, QMenu, QSplashScreen, QGraphicsDropShadowEffect, \
    QMainWindow, QApplication, QSizePolicy, QWidget, QDockWidget, QStyle, QFileDialog, QDialog
from PyQt5.QtXml import QDomDocument
from qgis.core import QgsRectangle

import enmapbox.gui.datasources.manager
from enmapboxprocessing.algorithm.importdesisl1balgorithm import ImportDesisL1BAlgorithm
from enmapboxprocessing.algorithm.importdesisl1calgorithm import ImportDesisL1CAlgorithm
from enmapboxprocessing.algorithm.importdesisl2aalgorithm import ImportDesisL2AAlgorithm
from enmapboxprocessing.algorithm.importenmapl1balgorithm import ImportEnmapL1BAlgorithm
from enmapboxprocessing.algorithm.importenmapl1calgorithm import ImportEnmapL1CAlgorithm
from enmapboxprocessing.algorithm.importenmapl2aalgorithm import ImportEnmapL2AAlgorithm
from enmapboxprocessing.algorithm.importlandsatl2algorithm import ImportLandsatL2Algorithm
from enmapboxprocessing.algorithm.importprismal1algorithm import ImportPrismaL1Algorithm
from enmapboxprocessing.algorithm.importprismal2dalgorithm import ImportPrismaL2DAlgorithm
from enmapboxprocessing.algorithm.importsentinel2l2aalgorithm import ImportSentinel2L2AAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm
from processing.gui.AlgorithmDialog import AlgorithmDialog
import enmapbox
from qgis import utils as qgsUtils
from qgis.PyQt import sip
import qgis.utils


from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer, QgsProject, \
    QgsProcessingAlgorithm, Qgis, QgsCoordinateReferenceSystem, QgsWkbTypes, \
    QgsMapLayerStore, QgsPointXY, QgsLayerTreeGroup, QgsLayerTree, QgsLayerTreeLayer, QgsVectorLayerTools, \
    QgsZipUtils, QgsProjectArchive, QgsSettings, \
    QgsStyle, QgsSymbolLegendNode, QgsSymbol, QgsTaskManager, QgsApplication, QgsProcessingAlgRunnerTask

from qgis.gui import QgsMapCanvas, QgsLayerTreeView, \
    QgisInterface, QgsMessageBar, QgsMessageViewer, QgsMessageBarItem, QgsMapLayerConfigWidgetFactory, QgsAttributeTableFilterModel, QgsSymbolSelectorDialog, \
    QgsSymbolWidgetContext

from enmapbox import messageLog, debugLog, DEBUG

from enmapbox.gui.dataviews.dockmanager import DockManagerTreeModel, MapDockTreeNode, SpeclibDockTreeNode
from .datasources.datasources import DataSource, RasterDataSource, VectorDataSource, SpatialDataSource
from enmapbox.externals.qps.cursorlocationvalue import CursorLocationInfoDock
from enmapbox.externals.qps.layerproperties import showLayerPropertiesDialog
from enmapbox.externals.qps.maptools import QgsMapToolSelectionHandler, MapTools
from enmapbox.algorithmprovider import EnMAPBoxProcessingProvider
from enmapbox.externals.qps.speclib.core.spectrallibrary import SpectralLibrary
from enmapbox.externals.qps.speclib.gui.spectralprofilesources import SpectralProfileSourcePanel, \
    MapCanvasLayerProfileSource
from enmapbox.externals.qps.speclib.gui.spectrallibrarywidget import SpectralLibraryWidget
from enmapbox.gui.dataviews.docks import SpectralLibraryDock, Dock, AttributeTableDock, MapDock
from .mapcanvas import MapCanvas
from .utils import enmapboxUiPath
from ..externals.qps.speclib.core import is_spectral_library
from ..externals.qps.subdatasets import SubDatasetSelectionDialog
from ..externals.qps.utils import SpatialPoint, loadUi, SpatialExtent, file_search

HIDDEN_ENMAPBOX_LAYER_GROUP = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_GROUP'

MAX_MISSING_DEPENDENCY_WARNINGS = 3
KEY_MISSING_DEPENDENCY_VERSION = 'MISSING_PACKAGE_WARNING_VERSION'

from .dataviews.docks import DockTypes


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
            alignment = int(Qt.AlignLeft | Qt.AlignBottom)
        if color is None:
            color = QColor('black')
        super(EnMAPBoxSplashScreen, self).showMessage(text, alignment, color)
        QApplication.processEvents()

    """
    def drawContents(self, painter: QPainter) -> None:
        # color = QColor('black')
        color = QColor('white')
        color.setAlpha(125)

        painter.setBrush(color)
        painter.setPen(color)
        size = self.size()
        h = 25
        d = 10
        rect = QRect(QRect(0, size.height()-h-d, size.width(), size.height()-d) )
        painter.drawRect(rect)
        #painter.setPen(QColor('white'))
        super().drawContents(painter)
    """

class EnMAPBoxUI(QMainWindow):
    mActionProcessingToolbox: QAction

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
    warnings.warn(DeprecationWarning('Use enmapbox.icon() instead to return the EnMAP-Box icon'), stacklevel=2)
    return enmapbox.icon()


class EnMAPBoxLayerTreeLayer(QgsLayerTreeLayer):

    def __init__(self, *args, **kwds):

        widget = None
        if 'widget' in kwds.keys():
            widget = kwds.pop('widget')

        # assert isinstance(canvas, QgsMapCanvas)
        super().__init__(*args, **kwds)
        self.setUseLayerName(False)

        self.mWidget: QWidget = None
        lyr = self.layer()
        if isinstance(lyr, QgsMapLayer):
            lyr.nameChanged.connect(self.updateLayerTitle)
        self.setWidget(widget)

        self.updateLayerTitle()

    def updateLayerTitle(self, *args):
        """
        Updates node name and layer title (not name) to: [<location in enmapbox>] <layer name>
        """
        location = '[EnMAP-Box]'
        name = '<not connected>'
        if isinstance(self.mWidget, QWidget):
            location = '[{}]'.format(self.mWidget.windowTitle())

        lyr = self.layer()
        if isinstance(lyr, QgsMapLayer):
            name = lyr.name()

        title = '{} {}'.format(location, name)
        if isinstance(lyr, QgsMapLayer):
            lyr.setTitle(title)

        self.setName(title)

    def setWidget(self, widget: QWidget):
        if isinstance(self.mWidget, QWidget):
            try:
                self.mWidget.windowTitleChanged.disconnect(self.updateLayerTitle)
            except:
                pass
        self.mWidget = widget
        if isinstance(self.mWidget, QgsMapCanvas):
            self.mWidget.windowTitleChanged.connect(self.updateLayerTitle)
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
    def instance() -> Optional['EnMAPBox']:
        return EnMAPBox._instance

    MAPTOOLACTION = 'enmapbox/maptoolkey'

    sigDataSourcesAdded = pyqtSignal(list)
    sigSpectralLibraryAdded = pyqtSignal([str], [VectorDataSource])
    sigRasterSourceAdded = pyqtSignal([str], [RasterDataSource])
    sigVectorSourceAdded = pyqtSignal([str], [VectorDataSource])

    sigDataSourcesRemoved = pyqtSignal(list)
    sigSpectralLibraryRemoved = pyqtSignal([str], [VectorDataSource])
    sigRasterSourceRemoved = pyqtSignal([str], [RasterDataSource])
    sigVectorSourceRemoved = pyqtSignal([str], [VectorDataSource])

    sigMapLayersAdded = pyqtSignal([list], [list, MapCanvas])
    sigMapLayersRemoved = pyqtSignal([list], [list, MapCanvas])

    currentLayerChanged = pyqtSignal(QgsMapLayer)

    sigClosed = pyqtSignal()

    sigCurrentLocationChanged = pyqtSignal([SpatialPoint],
                                           [SpatialPoint, QgsMapCanvas])

    sigCurrentSpectraChanged = pyqtSignal(list)

    sigMapCanvasRemoved = pyqtSignal(MapCanvas)
    sigMapCanvasAdded = pyqtSignal(MapCanvas)
    sigMapCanvasKeyPressed = pyqtSignal(MapCanvas, QKeyEvent)

    sigProjectWillBeSaved = pyqtSignal()

    sigDockAdded = pyqtSignal(Dock)

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

        self.mHiddenLayerGroup: QgsLayerTreeGroup = None

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
        from enmapbox.gui.datasources.manager import DataSourceManager
        from enmapbox.gui.dataviews.dockmanager import DockManager

        splash.showMessage('Init DataSourceManager')
        self.mDataSourceManager = DataSourceManager()
        self.mDataSourceManager.sigDataSourcesRemoved.connect(self.onDataSourcesRemoved)
        self.mDataSourceManager.sigDataSourcesAdded.connect(self.onDataSourcesAdded)
        self.mDataSourceManager.setEnMAPBoxInstance(self)

        # QgsProject.instance().layersAdded.connect(self.addMapLayers)
        QgsProject.instance().layersWillBeRemoved.connect(self.onLayersWillBeRemoved)
        QgsProject.instance().writeProject.connect(self.onWriteProject)
        QgsProject.instance().readProject.connect(self.onReadProject)

        QgsApplication.taskManager().taskAdded.connect(self.onTaskAdded)

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
        self.mVectorLayerTools.sigZoomRequest[QgsCoordinateReferenceSystem, QgsRectangle].connect(
            lambda crs, extent: self.zoomToExtent(SpatialExtent(crs, extent)))
        self.mVectorLayerTools.sigPanRequest[QgsCoordinateReferenceSystem, QgsPointXY].connect(
            lambda crs, pt: self.panToPoint(SpatialPoint(crs, pt)))

        self.ui.cursorLocationValuePanel.sigLocationRequest.connect(lambda: self.setMapTool(MapTools.CursorLocation))

        # load EnMAP-Box applications
        splash.showMessage('Load EnMAPBoxApplications...')

        debugLog('Load EnMAPBoxApplications...')
        from enmapbox.gui.applications import ApplicationRegistry
        self.applicationRegistry = ApplicationRegistry(self, parent=self)
        self.applicationRegistry.sigLoadingInfo.connect(splash.showMessage)
        self.applicationRegistry.sigLoadingFinished.connect(lambda success, msg:
                                                splash.showMessage(msg, color=QColor('red') if not success else None)
                                                            )

        self.initEnMAPBoxApplications(load_core_apps=load_core_apps,
                                      load_other_apps=load_other_apps)

        # add developer tools to the Tools menu
        debugLog('Modify menu...')
        m = self.menu('Tools')
        m.addSeparator()
        m = m.addMenu('Developers')
        m.addAction(self.ui.mActionAddMimeView)

        self.ui.actionShowResourceBrowser.triggered.connect(self.showResourceBrowser)
        m.addAction(self.ui.actionShowResourceBrowser)

        self.ui.optionShowHiddenLayersNode.toggled.connect(self.showHiddenLayersNode)
        m.addAction(self.ui.optionShowHiddenLayersNode)

        debugLog('Set ui visible...')
        self.ui.setVisible(True)

        debugLog('Set pyqtgraph config')
        from ..externals.pyqtgraph import setConfigOption
        setConfigOption('background', 'k')
        setConfigOption('foreground', 'w')

        # check missing packages and show a message
        # see https://bitbucket.org/hu-geomatics/enmap-box/issues/366/start-enmap-box-in-standard-qgis
        splash.showMessage('Check dependencies...')
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

        splash.finish(self.ui)
        splash.showMessage('Load project settings...')
        debugLog('Load settings from QgsProject.instance()')
        self.onReloadProject()

    def showMessage(self, msg: str, title: str = 'Message', html: bool = False):
        viewer = QgsMessageViewer()
        viewer.setWindowTitle(title)
        if html:
            viewer.setMessageAsHtml(msg)
        else:
            viewer.setMessageAsPlainText(msg)
        viewer.showMessage(blocking=True)

    def addMessageBarTextBoxItem(self,
                                 title: str,
                                 text: str,
                                 level: Qgis.MessageLevel = Qgis.Info,
                                 button_text: str = 'Show more',
                                 html: bool = False):
        """
        Adds a message to the message bar that can be shown in detail using a text browser.
        :param title:
        :param text:
        :param level:
        :param button_text:
        :param html:
        :return:
        """
        a = QAction(button_text)

    def showMessage(self, msg: str, title: str = 'Message', html: bool = False):
        viewer = QgsMessageViewer()
        viewer.setWindowTitle(title)
        if html:
            viewer.setMessageAsHtml(msg)
        else:
            viewer.setMessageAsPlainText(msg)
        viewer.showMessage(blocking=True)

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
        a = QAction(buttonTitle)
        btn = QToolButton()
        btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: black; text-decoration: underline;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        btn.addAction(a)
        btn.setDefaultAction(a)
        btn.triggered.connect(lambda *args, msg=text, tit=title, showHTML=html:
                              self.showMessage(msg, html=showHTML, title=tit))
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

        debugLog(f'Current MapCanvas: {self.currentMapCanvas()}')
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
            self.showAttributeTable(self.currentLayer(), filterMode=filterMode)
            pass
        elif mode == 2:
            # open layer styling dock
            pass

    def showAttributeTable(self, lyr: QgsVectorLayer,
                           filerExpression: str = "",
                           filterMode: QgsAttributeTableFilterModel.FilterMode = None):

        if lyr is None:
            lyr = self.currentLayer()
        if is_spectral_library(lyr):
            dock = self.createDock(SpectralLibraryDock, speclib=lyr)
        elif isinstance(lyr, QgsVectorLayer):
            dock = self.createDock(AttributeTableDock, layer=lyr)

    def showPackageInstaller(self):
        """
        Opens a GUI to install missing PIP packages
        """
        from ..dependencycheck import PIPPackageInstaller, requiredPackages

        w = PIPPackageInstaller()
        w.addPackages(requiredPackages())
        w.show()

    def showHiddenLayersNode(self, visibility: bool):

        b = self.ui.optionShowHiddenLayersNode.isChecked()
        if visibility != b:
            self.ui.optionShowHiddenLayersNode.setChecked(visibility)
        else:
            # call to change
            n = self.hiddenLayerGroup()

    def showResourceBrowser(self, *args):
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

    def dataSourceManager(self) -> enmapbox.gui.datasources.manager.DataSourceManager:
        return self.mDataSourceManager

    def dockManager(self) -> enmapbox.gui.dataviews.dockmanager.DockManager:
        return self.mDockManager

    def addMapLayer(self, layer: QgsMapLayer):
        self.addMapLayers([layer])

    def addMapLayers(self, layers: typing.List[QgsMapLayer]):
        self.dataSourceManager().addDataSources(layers)

    def onMapCanvasKeyPressed(self, mapCanvas: MapCanvas, e: QKeyEvent):

        is_ctrl = bool(QApplication.keyboardModifiers() & Qt.ControlModifier)
        if e.key() == Qt.Key_S and is_ctrl:
            # add current profiles (if collected)
            self.spectralProfileSourcePanel().addCurrentProfilesToSpeclib()

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
        # self.timeSeries().writeXml(node, dom)

        # save map views
        # self.mapWidget().writeXml(node, dom)
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
        layers = [l for l in layers if isinstance(l, QgsMapLayer)]
        self.removeMapLayers(layers, remove_from_project=False)

    def syncHiddenLayers(self):
        """
        Updates the hidden layers node in the QGIS LayerTree.
        This is important as only layers in the QGIS LayerTree will be shown in
        the QgsMapLayerComboBox / QgsMapLayer (until QGIS 3.20)

        :return:
        """

        if Qgis.versionInt() >= 32000:
            return

        grp = self.hiddenLayerGroup()
        if isinstance(grp, EnMAPBoxHiddenLayerTreeGroup):
            knownInQGIS = [l.layerId() for l in grp.findLayers() if isinstance(l.layer(), QgsMapLayer)]

            # which layer is visible in which widget? e.g. QgsMapCanvas or SpectralLibrary Widget?
            L2W = dict()
            SPECLIBS = dict()
            for dockNode in self.dockManagerTreeModel().dockTreeNodes():
                if isinstance(dockNode, MapDockTreeNode):
                    for lid in dockNode.findLayerIds():
                        if lid not in L2W.keys():
                            L2W[lid] = dockNode.mapCanvas()
                elif isinstance(dockNode, SpeclibDockTreeNode):
                    slw = dockNode.speclibWidget()
                    speclib = slw.speclib()
                    SPECLIBS[speclib.id()] = speclib
                    L2W[speclib.id()] = slw

            knownInEnMAPBox = list(L2W.keys())
            # knownInEnMAPBox = self.dockManagerTreeModel().rootNode.findLayerIds()

            toAdd = [l for l in knownInEnMAPBox if l not in knownInQGIS]
            toRemove = [l for l in knownInQGIS if l not in knownInEnMAPBox]

            # update QGIS layer tree
            for lid in toAdd:
                assert isinstance(lid, str)
                if lid in SPECLIBS.keys() and not lid in QgsProject.instance().mapLayers().keys():
                    lyr: QgsVectorLayer = SPECLIBS[lid]
                    QgsProject.instance().addMapLayer(lyr, False)
                    if lyr.dataProvider().name() == 'memory':
                        lyr.setCustomProperty("skipMemoryLayersCheck", 1)

                lyr = QgsProject.instance().mapLayer(lid)

                if isinstance(lyr, QgsMapLayer) and not sip.isdeleted(lyr):
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
                    widget = L2W.get(node.layerId(), None)
                    node.setWidget(widget)

            # in case the currentNode is the hidden group, set the current QGIS node to the top
            currentGroupNode = qgis.utils.iface.layerTreeView().currentGroupNode()
            if currentGroupNode == grp:
                qgis.utils.iface.layerTreeView().setCurrentIndex(QModelIndex())

    def removeMapLayer(self, layer: QgsMapLayer, remove_from_project: bool = True):
        self.removeMapLayers([layer], remove_from_project=remove_from_project)

    def removeMapLayers(self, layers: typing.List[QgsMapLayer], remove_from_project=True):
        """
        Removes layers from the EnMAP-Box
        """
        # grp = self.hiddenLayerGroup()
        layers = [l for l in layers if isinstance(l, QgsMapLayer)]
        removedIds = [l.id() for l in layers]

        layersTM = self.dockManagerTreeModel().mapLayers()
        layers = [l for l in layers if isinstance(l, QgsMapLayer) and l in layersTM]
        self.syncHiddenLayers()

        ltv = qgis.utils.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        root: QgsLayerTreeGroup = ltv.layerTreeModel().rootGroup()
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

        for l in self.dockTreeView().layerTreeModel().mapLayers():
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

        import enmapbox.gui.dataviews.dockmanager

        area = Qt.LeftDockWidgetArea
        self.ui.dataSourcePanel = self.addPanel(area, enmapbox.gui.datasources.manager.DataSourceManagerPanelUI(self.ui))
        self.ui.dockPanel = self.addPanel(area, enmapbox.gui.dataviews.dockmanager.DockPanelUI(self.ui))

        self.ui.cursorLocationValuePanel = self.addPanel(area, CursorLocationInfoDock(self.ui), show=False)
        self.ui.cursorLocationValuePanel.mLocationInfoModel.setCountFromZero(False)

        self.ui.spectralProfileSourcePanel: SpectralProfileSourcePanel = \
            self.addPanel(area, SpectralProfileSourcePanel(self.ui))

        sources = [
            MapCanvasLayerProfileSource(mode=MapCanvasLayerProfileSource.MODE_FIRST_LAYER),
            MapCanvasLayerProfileSource(mode=MapCanvasLayerProfileSource.MODE_BOTTOM_LAYER)
        ]

        self.ui.spectralProfileSourcePanel.addSources(sources)
        self.ui.spectralProfileSourcePanel.setDefaultSource(sources[0])
        self.sigMapCanvasKeyPressed.connect(self.onMapCanvasKeyPressed)

        area = Qt.RightDockWidgetArea

        try:
            import processing.gui.ProcessingToolbox
            panel = processing.gui.ProcessingToolbox.ProcessingToolbox()
            self.ui.processingPanel = self.addPanel(area, panel, False)
        except Exception as ex:
            print(ex, file=sys.stderr)

        self.ui.resizeDocks([self.ui.dataSourcePanel, self.ui.dockPanel, self.ui.spectralProfileSourcePanel],
                            [40, 50, 10], Qt.Vertical)

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

    def openAddDataSourceDialog(self):
        """
        Shows a fileOpen dialog to select new data sources
        :return:
        """

        from enmapbox import enmapboxSettings
        SETTINGS = enmapboxSettings()
        lastDataSourceDir = SETTINGS.value('lastsourcedir', None)

        if lastDataSourceDir is None:
            lastDataSourceDir = enmapbox.DIR_EXAMPLEDATA

        if not os.path.exists(lastDataSourceDir):
            lastDataSourceDir = None

        uris, filter = QFileDialog.getOpenFileNames(None, "Open a data source(s)", lastDataSourceDir)
        self.addSources(uris)

        if len(uris) > 0:
            SETTINGS.setValue('lastsourcedir', os.path.dirname(uris[-1]))

    def openSubDatasetsDialog(self, *args, title:str='Add Sub-Datasets', filter: str = 'All files (*.*)'):

        SETTINGS = enmapbox.enmapboxSettings()
        defaultRoot = SETTINGS.value('lastsourcedir', None)

        if defaultRoot is None:
            defaultRoot = enmapbox.DIR_EXAMPLEDATA

        if not os.path.exists(defaultRoot):
            defaultRoot = None

        d = SubDatasetSelectionDialog()
        d.setWindowTitle(title)
        d.setFileFilter(filter)
        d.setDefaultRoot(defaultRoot)
        result = d.exec_()

        if result == QDialog.Accepted:
            subdatasets = d.selectedSubDatasets()
            layers = []
            loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
            for i, s in enumerate(subdatasets):
                lyr = QgsRasterLayer(s, options=loptions)
                if i == 0:
                    paths = d.fileWidget.splitFilePaths(d.fileWidget.filePath())
                    SETTINGS.setValue('lastsourcedir', os.path.dirname(paths[0]))

                layers.append(lyr)
            self.addSources(layers)


    def initActions(self):
        # link action to managers
        self.ui.mActionAddDataSource.triggered.connect(self.openAddDataSourceDialog)
        self.ui.mActionAddSubDatasets.triggered.connect(self.openSubDatasetsDialog)

        self.ui.mActionAddMapView.triggered.connect(lambda: self.mDockManager.createDock(DockTypes.MapDock))
        self.ui.mActionAddTextView.triggered.connect(lambda: self.mDockManager.createDock(DockTypes.TextDock))
        self.ui.mActionAddWebView.triggered.connect(lambda: self.mDockManager.createDock(DockTypes.WebViewDock))
        self.ui.mActionAddMimeView.triggered.connect(lambda: self.mDockManager.createDock(DockTypes.MimeDataDock))
        self.ui.mActionAddSpeclibView.triggered.connect(lambda: self.mDockManager.createDock(DockTypes.SpectralLibraryDock))
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
        self.ui.mActionProcessingToolbox.triggered.connect(
            lambda: self.ui.processingPanel.setVisible(self.ui.processingPanel.isHidden()))
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
            toolBar: QToolBar
            for toolButton in toolBar.findChildren(QToolButton):
                assert isinstance(toolButton, QToolButton)
                if isinstance(toolButton.defaultAction(), QAction) and isinstance(toolButton.defaultAction().menu(),
                                                                                  QMenu):
                    toolButton.setPopupMode(QToolButton.MenuButtonPopup)

            # add toolbar to menu
            if len(toolBar.windowTitle()) > 0:
                self.ui.menuToolBars.addAction(toolBar.toggleViewAction())

    def initActionsAddProduct(self):
        """
        Initializes the product loaders under <menu> Project -> Add Product
        """
        menu: QMenu = self.ui.menuAdd_Product
        # separator = self.ui.mActionAddSentinel2  # outdated

        menu.addSeparator()

        # add more product import actions hereafter
        algs = [
            ImportDesisL1BAlgorithm(),
            ImportDesisL1CAlgorithm(),
            ImportDesisL2AAlgorithm(),
            ImportEnmapL1BAlgorithm(),
            ImportEnmapL1CAlgorithm(),
            ImportEnmapL2AAlgorithm(),
            ImportLandsatL2Algorithm(),
            ImportPrismaL1Algorithm(),
            ImportPrismaL2DAlgorithm(),
            ImportSentinel2L2AAlgorithm(),
        ]

        for alg in algs:
            name = alg.displayName()[7:-8]  # remove "Import " and " product" parts
            tooltip = alg.shortDescription()
            a = QAction(name, parent=menu)
            a.setToolTip(tooltip)
            a.alg = alg
            a.triggered.connect(self.onActionAddProductTriggered)
            menu.addAction(a)

    def onActionAddProductTriggered(self):
        a = self.sender()
        alg: EnMAPProcessingAlgorithm = a.alg
        self.showProcessingAlgorithmDialog(alg)

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

    def spectralProfileSourcePanel(self) -> SpectralProfileSourcePanel:
        return self.ui.spectralProfileSourcePanel

    def onTaskAdded(self, taskID: int):
        """
        Connects QgsTasks that have been added to the QgsTaskManager with signales, e.g. to react in outputs.
        :param taskID:
        :return:
        """
        tm: QgsTaskManager = QgsApplication.taskManager()
        task = tm.task(taskID)
        if isinstance(task, QgsProcessingAlgRunnerTask):
            task.executed.connect(self.onProcessingAlgTaskCompleted)

    def onProcessingAlgTaskCompleted(self, ok: bool, results: dict):
        """
        Handles results of QgsProcessingAlgRunnerTasks that have been processed with the QgsTaskManager
        :param ok:
        :param results:
        :return:
        """
        if ok:
            if isinstance(results, dict):
                self.addSources(list(results.values()))

    def onDockAdded(self, dock):
        assert isinstance(dock, Dock)


        if isinstance(dock, SpectralLibraryDock):
            dock.sigLoadFromMapRequest.connect(lambda: self.setMapTool(MapTools.SpectralProfile))
            slw = dock.speclibWidget()
            assert isinstance(slw, SpectralLibraryWidget)
            slw.plotWidget().backgroundBrush().setColor(QColor('black'))
            self.spectralProfileSourcePanel().addSpectralLibraryWidgets(slw)
            slw.sigFilesCreated.connect(self.addSources)
            # self.dataSourceManager().addSource(slw.speclib())
            # self.mapLayerStore().addMapLayer(slw.speclib(), addToLegend=False)

        if isinstance(dock, MapDock):
            canvas = dock.mapCanvas()
            assert isinstance(canvas, MapCanvas)
            canvas.sigCrosshairPositionChanged.connect(self.onCrosshairPositionChanged)
            canvas.setCrosshairVisibility(True)
            canvas.keyPressed.connect(lambda e, c=canvas: self.sigMapCanvasKeyPressed.emit(canvas, e))
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

            if len(self.docks()) == 1:
                # dirty hack for #488 (zoom to full extent does not work if map dock is the first of all docks)
                QApplication.processEvents(QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers)
                # QTimer.singleShot(1000, lambda *args, mc=dock.mapCanvas(): mc.zoomToFullExtent())

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
            if not sip.isdeleted(dock.speclib()):
                dock.speclib().rollBack()
                dock.speclib().commitChanges()
            self.spectralProfileSourcePanel().removeSpectralLibraryWidgets(dock.speclibWidget())

        # lid = dock.speclib().id()
        # if self.mapLayerStore().mapLayer(lid):
        #     self.mapLayerStore().removeMapLayer(lid)

    @pyqtSlot(SpatialPoint, QgsMapCanvas)
    def loadCurrentMapSpectra(self, spatialPoint: SpatialPoint, mapCanvas: QgsMapCanvas = None, runAsync: bool = None):
        """
        Loads SpectralProfiles from a location defined by `spatialPoint`
        :param spatialPoint: SpatialPoint
        :param mapCanvas: QgsMapCanvas
        """

        panel: SpectralProfileSourcePanel = self.spectralProfileSourcePanel()
        if len(self.docks(SpectralLibraryDock)) == 0:
            dock = self.createDock(SpectralLibraryDock)
            if isinstance(dock, SpectralLibraryDock):
                slw: SpectralLibraryWidget = dock.speclibWidget()
                slw.setViewVisibility(SpectralLibraryWidget.ViewType.ProfileView)

        if len(panel.mBridge) == 0:
            panel.createRelation()

        panel.loadCurrentMapSpectra(spatialPoint, mapCanvas=mapCanvas, runAsync=runAsync)

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

    def settings(self) -> QSettings:
        """
        Returns the EnMAP-Box user settings
        """
        from enmapbox import enmapboxSettings
        return enmapboxSettings()

    def initEnMAPBoxApplications(self,
                                 load_core_apps: bool = True,
                                 load_other_apps: bool = True):
        """
        Initialized EnMAPBoxApplications
        """
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

            n_errors_to_show = 0
            for app in errorApps:

                v = self.applicationRegistry.mAppInitializationMessages[app]

                n_counts = counts.get(app, 0)
                if n_counts < MAX_MISSING_DEPENDENCY_WARNINGS:
                    n_errors_to_show += 1
                    counts[app] = n_counts + 1

                info.append(r'<br /><b>{}:</b>'.format(app))
                info.append('<p>')
                if v == False:
                    info.append(r'"{}" did not return any EnMAPBoxApplication\n'.format(v))
                elif isinstance(v, str):
                    info.append('<code>{}</code>'.format(v.replace('\n', '<br />\n')))
                info.append('</p>')

            info = '\n'.join(info)
            if n_errors_to_show > 0:
                self.addMessageBarTextBoxItem(title, info, level=Qgis.Warning, html=True)
            else:
                QgsApplication.instance().messageLog().logMessage(info, 'EnMAP-Box',
                                                                  level=Qgis.Warning,
                                                                  notifyUser=False)

        settings.setValue(KEY_COUNTS, counts)

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
        # self.showMessage()
        # mbar.pushMessage(tag, line1, showMore, level, duration)
        contains_html = re.search(r'<(html|br|a|p/?>)', message) is not None
        self.addMessageBarTextBoxItem(line1, message, level=level, html=contains_html)

    def onDataDropped(self, droppedData):
        assert isinstance(droppedData, list)
        mapDock = None
        from enmapbox.gui.datasources.datasources import SpatialDataSource
        for dataItem in droppedData:
            if isinstance(dataItem, SpatialDataSource):
                dataSources = self.mDataSourceManager.addDataSources(dataItem)
                if mapDock is None:
                    mapDock = self.createDock('MAP')
                mapDock.addLayers([ds.createRegisteredMapLayer() for ds in dataSources])

            # any other types to handle?

    def openExampleData(self, mapWindows=0, testData:bool = False):
        """
        Opens the example data
        :param mapWindows: number of new MapDocks to be opened
        """
        from enmapbox.dependencycheck import missingTestData, installTestData
        if missingTestData():
            installTestData()

        rx = re.compile('.*(bsq|bil|bip|tif|gpkg|sli|img|shp|pkl)$', re.I)
        if not missingTestData():
            import enmapbox.exampledata
            dir_exampledata = os.path.dirname(enmapbox.exampledata.__file__)
            files = list(pathlib.Path(f).as_posix() for f in file_search(dir_exampledata, rx, recursive=True))

            self.addSources(files)
            exampleSources = [s for s in self.dataSourceManager().dataSources()
                              if isinstance(s, SpatialDataSource) and s.source() in files]

            for n in range(mapWindows):
                dock: MapDock = self.createDock('MAP')
                assert isinstance(dock, MapDock)
                lyrs = []
                for src in exampleSources:
                    if isinstance(src, SpatialDataSource):
                        lyr = src.asMapLayer()
                        if isinstance(lyr, QgsVectorLayer):
                            lyr.updateExtents()

                        if isinstance(lyr, QgsMapLayer):
                            ext = lyr.extent()
                            if not ext.isNull() and ext.width() > 0:
                                lyrs.append(lyr)

                # sort layers by type and spatial extent (to not hide vectors by rasters etc.)
                canvas = dock.mapCanvas()

                def niceLayerOrder(lyr: QgsMapLayer) -> (int, int):
                    oType = 0
                    area = 0

                    if isinstance(lyr, QgsVectorLayer):
                        gt = lyr.geometryType()
                        if gt == QgsWkbTypes.LineGeometry:
                            oType = 1
                        elif gt == QgsWkbTypes.PolygonGeometry:
                            oType = 2
                        else:
                            oType = 0

                    elif isinstance(lyr, QgsRasterLayer):
                        oType = 3
                    try:
                        area = SpatialExtent.fromLayer(lyr).toCrs(canvas.mapSettings().destinationCrs()).area()
                    except:
                        pass
                    return oType, area

                lyrs = sorted(lyrs, reverse=True, key=niceLayerOrder)
                dock.mapCanvas().setLayers(lyrs)

        if testData:
            from enmapbox import DIR_REPO
            dir_testdata = pathlib.Path(DIR_REPO) / 'tests' / 'testdata'

            if dir_testdata.is_dir():
                files = list(pathlib.Path(f).as_posix() for f in file_search(dir_testdata, rx, recursive=True))
                self.addSources(files)

    def onDataSourcesRemoved(self, dataSources: typing.List[DataSource]):
        """
        Reacts on removed data sources
        :param dataSource: DataSource
        """

        # remove where we can remove lists of data sources
        self.spectralProfileSourcePanel().removeSources(dataSources)
        self.dockManagerTreeModel().removeDataSources(dataSources)

        # emit signals that are connected to single datasource types
        for dataSource in dataSources:
            if isinstance(dataSource, RasterDataSource):
                self.sigRasterSourceRemoved[str].emit(dataSource.source())
                self.sigRasterSourceRemoved[RasterDataSource].emit(dataSource)

            if isinstance(dataSource, VectorDataSource):
                self.sigVectorSourceRemoved[str].emit(dataSource.source())
                self.sigVectorSourceRemoved[VectorDataSource].emit(dataSource)

                if dataSource.isSpectralLibrary():
                    self.sigSpectralLibraryRemoved[str].emit(dataSource.source())
                    self.sigSpectralLibraryRemoved[VectorDataSource].emit(dataSource)

        self.syncHiddenLayers()

        self.sigDataSourcesRemoved[list].emit(dataSources)

    def onDataSourcesAdded(self, dataSources: typing.List[DataSource]):

        self.sigDataSourcesAdded[list].emit(dataSources)

        for dataSource in dataSources:
            if isinstance(dataSource, RasterDataSource):
                self.sigRasterSourceAdded[str].emit(dataSource.source())
                self.sigRasterSourceAdded[RasterDataSource].emit(dataSource)

                self.spectralProfileSourcePanel().addSources(dataSource.asMapLayer())

            if isinstance(dataSource, VectorDataSource):
                self.sigVectorSourceAdded[str].emit(dataSource.source())
                self.sigVectorSourceAdded[VectorDataSource].emit(dataSource)

                if dataSource.isSpectralLibrary():
                    self.sigSpectralLibraryAdded[str].emit(dataSource.source())
                    self.sigSpectralLibraryAdded[VectorDataSource].emit(dataSource)

        self.syncHiddenLayers()

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

    def currentSpectra(self) -> list:
        """
        Returns the spectra currently selected using the profile tool.

        :return: [list-of-spectra]
        """
        return self.spectralProfileSourcePanel().currentProfiles()

    def version(self) -> str:
        """
        Returns the version string
        """
        return enmapbox.__version__

    def dataSourceTreeView(self) -> 'DataSourceManagerTreeView':
        warnings.warn('Use .dataSourceManagerTreeView()', DeprecationWarning, stacklevel=2)
        return self.dataSourceManagerTreeView()

    def dataSourceManagerTreeView(self) -> 'DataSourceManagerTreeView':
        return self.ui.dataSourcePanel.dataSourceManagerTreeView()

    def dataSources(self, sourceType='ALL', onlyUri=True) -> typing.List[str]:
        """
        Returns a list of URIs to the data sources of type "sourceType" opened in the EnMAP-Box
        :param sourceType: ['ALL', 'RASTER', 'VECTOR', 'MODEL'],
        :param onlyUri: bool, set on False to return the DataSource object instead of the uri only.
        :return: [list-of-datasource-URIs (str)]
        """

        if sourceType == 'ALL':
            sourceType = None
        sources = self.mDataSourceManager.dataSources(filter=sourceType)
        if onlyUri:
            sources = [s.source() for s in sources]
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

    def dockTreeView(self) -> enmapbox.gui.dataviews.dockmanager.DockTreeView:
        """
        Returns the DockTreeView
        """
        return self.ui.dockPanel.dockTreeView

    def dockManagerTreeModel(self) -> DockManagerTreeModel:
        """
        Returns the DockManagerTreeModel
        :return: DockManagerTreeModel
        """
        return self.dockTreeView().layerTreeModel()

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
        return self.mDataSourceManager.addDataSources(sourceList)

    def addSource(self, source, name=None):
        """
        Returns a list of added DataSources or the list of DataSources that were derived from a single data source uri.
        :param source:
        :param name:
        :return: [list-of-dataSources]
        """
        return self.mDataSourceManager.addDataSources(source, name=name)

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
            showLayerPropertiesDialog(mapLayer, canvas=mapCanvas, messageBar=self.messageBar(), modal=True)

    @staticmethod
    def getIcon():
        """
        Returns the EnMAP-Box icon.
        :return: QIcon
        """
        warnings.warn('Use EnMAPBoxicon() instead', DeprecationWarning, stacklevel=2)
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
        self.ui.close()

    def hiddenLayerGroup(self) -> EnMAPBoxHiddenLayerTreeGroup:
        """
        Returns the hidden QgsLayerTreeGroup in the QGIS Layer Tree
        :return: QgsLayerTreeGroup
        """

        ltv = qgis.utils.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        root: QgsLayerTreeGroup = ltv.layerTreeModel().rootGroup()
        grp = root.findGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        if not isinstance(grp, EnMAPBoxHiddenLayerTreeGroup):
            # assert not isinstance(self._layerTreeGroup, QgsLayerTreeGroup)
            enmapbox.debugLog('CREATE HIDDEN LAYER GROUP')
            # print('CREATE HIDDEN LAYER GROUP')
            grp: EnMAPBoxHiddenLayerTreeGroup = EnMAPBoxHiddenLayerTreeGroup()
            root.addChildNode(grp)
            self._layerTreeGroup = grp

        ltv = qgis.utils.iface.layerTreeView()
        index = ltv.layerTreeModel().node2index(grp)

        ltv_model = ltv.model()

        # takes care of differences between 3.16 an 3.18
        # if isinstance(ltv_model, QSortFilterProxyModel):
        #    index = ltv_model.mapFromSource(index)

        grp.setItemVisibilityChecked(False)

        hide: bool = self.ui.optionShowHiddenLayersNode.isChecked() is False
        grp.setCustomProperty('nodeHidden', 'true' if hide else 'false')
        ltv.setRowHidden(index.row(), index.parent(), hide)
        self.mHiddenLayerGroup = grp
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

    def layerTreeView(self) -> enmapbox.gui.dataviews.dockmanager.DockTreeView:
        """
        Returns the Dock Panel Tree View
        :return: enmapbox.gui.dataviews.dockmanager.DockTreeView
        """
        return self.dockTreeView()

    ### SIGNALS from QgisInterface ####

    initializationCompleted = pyqtSignal()
    layerSavedAs = pyqtSignal(QgsMapLayer, str)
    currentLayerChanged = pyqtSignal(QgsMapLayer)

    ### ACTIONS ###
    # def actionAddSentinel2(self) -> QAction:  # AR: this is outdated; replaced by "Import Sentinel-2 L2A product" algo
    #    return self.ui.mActionAddSentinel2

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

    def showProcessingAlgorithmDialog(
            self, algorithmName: Union[str, QgsProcessingAlgorithm], parameters: Dict = None, show=True, modal=False,
            wrapper: type = None, autoRun=False, parent=None
    ) -> AlgorithmDialog:
        """
        Create an algorithm dialog.

        Optionally, provide a wrapper class to get full control over individual components like the feedback or results.
        E.g. to get a handle on the results do something like that:

        .. code-block:: python

            class Wrapper(AlgorithmDialog):
                def finish(self, successful, result, context, feedback, in_place=False):
                    super().finish(successful, result, context, feedback, in_place=False)
                    if successful:
                        # do something useful

        """
        if parent is None:
            parent = self.ui

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

        dlg = algorithm.createCustomParametersWidget(parent)
        if not dlg:
            if wrapper is None:
                dlg = AlgorithmDialog(algorithm.create(), parent=parent)
            else:
                dlg = wrapper(algorithm.create(), parent=parent)
        else:
            assert wrapper is None  # todo: dialog wrapper for custom parameter widget
        dlg.setModal(modal)

        if parameters is not None:
            dlg.setParameters(parameters)

        # auto-running the algorithm is useful, if all required parameters are filled in
        if autoRun:
            dlg.runButton().animateClick(500)

        if show and not modal:
            dlg.show()
        if show and modal:
            dlg.exec_()
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

    def spectralLibraryWidgets(self) -> typing.List[SpectralLibraryWidget]:
        """
        Returns a list with SpectralLibraryWidgets known to the EnMAP-Box.
        :return: [list-of-SpectralLibraryWidget]
        """
        return [d.speclibWidget() for d in self.docks() if isinstance(d, SpectralLibraryDock)]

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
                if isinstance(ds, SpatialDataSource):
                    layers.append(ds.asMapLayer())
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
        if not isinstance(canvas, QgsMapCanvas):
            debugLog(f'zoomToExtent: no current map canvas')
            return

        if isinstance(extent, SpatialExtent):
            ext = extent.toCrs(canvas.mapSettings().destinationCrs())
            if isinstance(ext, SpatialExtent):
                canvas.setExtent(ext)
                canvas.refresh()
        else:
            debugLog(f'zoomToExtent problem: extent={extent} currentMapCanvas={canvas}')

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
