from __future__ import absolute_import

import itertools
import os
import uuid
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *
from enmapbox.gui.mapcanvas import MapCanvas

import pyqtgraph.dockarea.Dock
from pyqtgraph.widgets.VerticalLabel import VerticalLabel




class DockWindow(QMainWindow):
    def __init__(self, area, **kwargs):
        QMainWindow.__init__(self, **kwargs)
        self.setWindowTitle('EnMAPBox')
        import enmapbox.gui.enmapboxgui
        self.setWindowIcon(enmapbox.gui.enmapboxgui.getIcon())
        self.setCentralWidget(area)

    def closeEvent(self, *args, **kwargs):
        self.centralWidget().clear()

class DockArea(pyqtgraph.dockarea.DockArea):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    def __init__(self, *args, **kwds):
        super(DockArea, self).__init__(*args, **kwds)
        self.setAcceptDrops(True)

    def apoptose(self):
        #print "apoptose area:", self.temporary, self.topContainer, self.topContainer.count()
        if self.topContainer.count() == 0:
            self.topContainer = None
            from enmapbox.gui.enmapboxgui import EnMAPBoxUI
            if not isinstance(self.topLevelWidget(), EnMAPBoxUI):
                s = ""

            if self.temporary and self.home is not None:
                self.home.removeTempArea(self)
        else:
            s = ""

    def addDock(self, enmapboxdock, position='bottom', relativeTo=None, **kwds):
        assert enmapboxdock is not None
        assert isinstance(enmapboxdock, Dock)
        return super(DockArea, self).addDock(dock=enmapboxdock, position=position, relativeTo=relativeTo, **kwds)


    def addTempArea(self):
        #overwrites the original method
        if self.home is None:
            area = DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = DockWindow(area)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area

    # forward to EnMAPBox
    def dragEnterEvent(self, event):
        self.sigDragEnterEvent.emit(event)

    # forward to EnMAPBox
    def dragMoveEvent(self, event):

        self.sigDragMoveEvent.emit(event)

    # forward to EnMAPBox
    def dragLeaveEvent(self, event):

        self.sigDragLeaveEvent.emit(event)

    # forward to EnMAPBox
    def dropEvent(self, event):
        self.sigDropEvent.emit(event)


class Dock(pyqtgraph.dockarea.Dock):
    @staticmethod
    def readXml(elem):


        return None

    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''
    sigTitleChanged = pyqtSignal(str)


    def __init__(self, enmapboxInstance, name='dock', closable=True, *args, **kwds):
        super(Dock, self).__init__(name=name, closable=False, *args, **kwds)

        assert enmapboxInstance is not None
        self.enmapbox = enmapboxInstance
        self.setStyleSheet('background:#FFF')

        #replace PyQtGraph Label by EnmapBox labels (could be done by inheritances as well)
        title = self.title()
        self.topLayout.removeWidget(self.label)
        del self.label
        self.label = self._createLabel(title=title)
        self.topLayout.addWidget(self.label, 0, 1)
        self.uuid = uuid.uuid4()
        print('UUID: {}'.format(self.uuid))
        if closable:
            self.label.sigCloseClicked.connect(self.close)

        self.raiseOverlay()


        self.hStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }
        """
        self.vStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }
        """
        self.nStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        Dock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""

        self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()

    def getDockContentContextMenu(self):
        """

        :return: None or QMenu
        """
        return None

    def setTitle(self, title):
        """
        Override setTitle to emit a signal after title was changed
        :param title:
        :return:
        """
        super(Dock, self).setTitle(title)
        self.sigTitleChanged.emit(title)

    def _createLabel(self, *args, **kwds):
        """
        Overide this function to provide a dock-specific label
        :return:
        """
        return DockLabel(self,  *args, **kwds)

    def append_hv_style(self, stylestr):
        obj_name = type(self).__name__
        style = ' \n{} {{\n{}\n}} '.format(obj_name, stylestr)
        self.hStyle += style
        self.vStyle += style

    def addTempArea(self):
        if self.home is None:
            area = DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = DockWindow(area)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area





class DockLabel(VerticalLabel):
    sigClicked = pyqtSignal(object, object)
    sigCloseClicked = pyqtSignal()
    sigNormalClicked = pyqtSignal()

    def __init__(self, dock, title=None, allow_floating=True):
        assert isinstance(dock, Dock)
        self.dim = False
        self.fixedWidth = False
        self.dock = dock
        if title is None:
            title = self.dock.title()
        VerticalLabel.__init__(self, title, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False
        self.buttons = list() #think from right to left
        self.pressPos = QtCore.QPoint()

        closeButton = QToolButton(self)
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setToolTip('Close window')
        closeButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.buttons.append(closeButton)

        if allow_floating:
            floatButton = QToolButton(self)
            #testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float window')
            floatButton.clicked.connect(lambda : self.dock.float())
            floatButton.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarNormalButton))
            self.buttons.append(floatButton)

    def updateStyle(self):

        if self.dock.hasFocus():
            s = ""

        r = '3px'
        if self.dim:
            fg = '#aaa'
            bg = '#44a'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'

        if self.orientation == 'vertical':
            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)

    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()

    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (
            ev.pos() - self.pressPos).manhattanLength() > QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            self.sigClicked.emit(self, ev)
        ev.accept()

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()

    def resizeEvent(self, ev):
        if self.orientation == 'vertical':
            size = ev.size().width()
        else:
            size = ev.size().height()

        for i, btn in enumerate([b for b in self.buttons if not b.isHidden()]):
            if self.orientation == 'vertical':
                pos = QtCore.QPoint(0, i * size)
            else:
                pos = QtCore.QPoint(ev.size().width() - (i+1)*size, 0)
            btn.setFixedSize(QtCore.QSize(size, size))
            btn.move(pos)

        super(DockLabel, self).resizeEvent(ev)


class MapDockLabel(DockLabel):

    def __init__(self, *args, **kwds):

        super(MapDockLabel, self).__init__(*args, **kwds)

        self.addMapLink = QToolButton(self)
        self.addMapLink.setToolTip('Link with other map(s)')
        self.addMapLink.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        self.buttons.append(self.addMapLink)

        self.removeMapLink = QToolButton(self)
        self.removeMapLink.setToolTip('Remove links to this map')
        self.removeMapLink.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        self.buttons.append(self.removeMapLink)

class MapDock(Dock):
    """
    A dock to visualize geodata that can be mapped
    """
    #sigCursorLocationValueRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    from enmapbox.gui.utils import SpatialPoint, SpatialExtent
    sigCursorLocationValueRequest = pyqtSignal(SpatialPoint)

    sigLayersAdded = pyqtSignal(list)
    sigLayersRemoved = pyqtSignal(list)
    sigCrsChanged = pyqtSignal(QgsCoordinateReferenceSystem)
    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)
        super(MapDock, self).__init__(*args, **kwds)
        self.basename = self.title()

        #self.actionLinkExtent = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Link to map extent', self)
        #self.actionLinkCenter = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Linkt to map center', self)
        #self.label.buttons.append(self.actionLinkCenter.getButton())

        self.canvas = MapCanvas(self)

        #self.label.setText(self.basename)
        #self.canvas.setScaleLocked(True)
        self.canvas.sigDropEvent.connect(self.canvasDrop)
        self.canvas.sigDragEnterEvent.connect(self.canvasDragEnter)
        #self.canvas.customContextMenuRequested.connect(self.onCanvasContextMenuEvent)
        self.canvas.sigContextMenuEvent.connect(self.onCanvasContextMenuEvent)
        self.canvas.sigLayersAdded.connect(self.sigLayersAdded.emit)
        self.canvas.sigLayersRemoved.connect(self.sigLayersRemoved.emit)
        self.canvas.sigCrsChanged.connect(self.sigCrsChanged.emit)
        settings = QSettings()
        assert isinstance(self.canvas, QgsMapCanvas)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        #self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.canvas)

        #link canvas to map tools
        g = self.enmapbox.ui
        #g.actionAddView.triggered.connect(lambda: self.enmapbox.dockarea.addDock(EnMAPBoxDock(self)))
        #g.actionAddMapView.triggered.connect(lambda : self.enmapbox.dockarea.addDock(EnMAPBoxMapDock(self)))
        #g.actionAddTextView.triggered.connect(lambda: self.enmapbox.dockarea.addDock(EnMAPBoxTextDock(self)))

        # create the map tools and linke them to the toolbar actions
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(g.actionPan)
        self.toolPan.action().triggered.connect(lambda: self.setMapTool(self.toolPan))

        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(g.actionZoomIn)
        self.toolZoomIn.action().triggered.connect(lambda: self.setMapTool(self.toolZoomIn))

        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(g.actionZoomOut)
        self.toolZoomOut.action().triggered.connect(lambda: self.setMapTool(self.toolZoomOut))

        from enmapbox.gui.mapcanvas import FullExtentMapTool, PixelScaleExtentMapTool
        self.toolZoomFull = FullExtentMapTool(self.canvas)
        self.toolZoomFull.setAction(g.actionZoomFullExtent)
        self.toolZoomFull.action().triggered.connect(lambda: self.setMapTool(self.toolZoomFull))

        self.toolZoomPixelScale = PixelScaleExtentMapTool(self.canvas)
        self.toolZoomPixelScale.setAction(g.actionZoomPixelScale)
        self.toolZoomPixelScale.action().triggered.connect(lambda: self.setMapTool(self.toolZoomPixelScale))

        from enmapbox.gui.cursorlocationvalue import CursorLocationValueMapTool
        self.toolCursorLocationValue = CursorLocationValueMapTool(self.canvas)
        self.toolCursorLocationValue.setAction(g.actionIdentify)
        self.toolCursorLocationValue.action().triggered.connect(lambda: self.setMapTool(self.toolCursorLocationValue))
        self.toolCursorLocationValue.sigLocationRequest.connect(self.cursorLocationValueRequest)



        #self.toolIdentify.identifyMessage.connect(self.identifyMessage)
        #self.toolIdentify.identifyProgress.connect(self.identifyProgress)
        #self.toolIdentify.sigLocationIdentified.connect(self.identifyResults)

        """
        The problem still exists in QGis 2.0.1-3 available through OSGeo4W distribution. New style connection always return the same error:
        TypeError: connect() failed between geometryChanged(QgsFeatureId,QgsGeometry) and unislot()
        A possible workaround is to use old signal/slot code:

        QObject.connect(my_vectlayer,SIGNAL("geometryChanged(QgsFeatureId, QgsGeometry&)"),mynicehandler)
        instead of expected:

        my_vectlayer.geometryChanged.connect(mynicehandler)
        """
        #QObject.connect(self.toolIdentify,
        #                SIGNAL("changedRasterResults(QList<QgsMapToolIdentify::IdentifyResult>&)"),
        #                self.identifyChangedRasterResults)
        #self.toolIdentify.changedRasterResults.connect(self.identifyChangedRasterResults)

        self.toolCursorLocationValue.setAction(g.actionIdentify)
        self.toolCursorLocationValue.action().triggered.connect(lambda: self.setMapTool(self.toolCursorLocationValue))
        from enmapbox.gui.mapcanvas import CanvasLinkTargetWidget
        self.label.addMapLink.clicked.connect(lambda:CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        self.label.removeMapLink.clicked.connect(lambda: self.canvas.removeAllCanvasLinks())

        #set default map tool
        self.canvas.setMapTool(self.toolPan)


    def cursorLocationValueRequest(self,*args):
        self.sigCursorLocationValueRequest.emit(*args)

    def getDockContentContextMenu(self):
        from enmapbox.gui.mapcanvas import CanvasLinkTargetWidget
        menu = QMenu()

        action = QAction('Link with other maps', menu)
        action.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        action.triggered.connect(lambda: CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        menu.addAction(action)

        action = QAction('Remove links to other maps', menu)
        action.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        action.triggered.connect(lambda: self.canvas.removeAllCanvasLinks())
        menu.addAction(action)

        menu.addSeparator()

        action = QAction('Zoom Full', menu)
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomFullExtent.png'))
        action.triggered.connect(lambda: self.canvas.setExtent(self.canvas.fullExtent()))
        menu.addAction(action)

        action = QAction('Zoom Native Resolution', menu)
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomActual.png'))
        action.triggered.connect(lambda: self.canvas.setExtent(self.canvas.fullExtent()))
        menu.addAction(action)


        menu.addSeparator()

        action = QAction('Refresh', menu)
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.png"))
        action.triggered.connect(lambda: self.canvas.refresh())
        menu.addAction(action)

        action = QAction('Refresh all layers', menu)
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.png"))
        action.triggered.connect(lambda: self.canvas.refreshAllLayers())
        menu.addAction(action)

        menu.addSeparator()

        action = QAction('Clear map', menu)
        action.triggered.connect(lambda: self.canvas.setLayers([]))
        menu.addAction(action)

        action = QAction('Change CRS', menu)
        action.triggered.connect(lambda: self.setCRSfromDialog())
        menu.addAction(action)

        return menu

    def onCanvasContextMenuEvent(self, event):
        menu = self.getDockContentContextMenu()
        menu.exec_(event.globalPos())


    def setCRSfromDialog(self):
        w  = QgsProjectionSelectionWidget(self)
        crs = self.canvas.mapSettings().destinationCrs()
        w.setCrs(crs) #set current CRS
        w.setLayerCrs(crs)


        d = w.dialog()
        d.setMessage('Select CRS {}'.format(self.title()))
        w.crsChanged.connect(self.sandboxSlot)
        w.selectCrs()

    def sandboxSlot(self,crs):
        self.canvas.setDestinationCrs(crs)

    def setMapTool(self, mapTool):
        self.canvas.setMapTool(mapTool)


    def mimeData(self):
        return ['']

    def canvasDragEnter(self, event):

        ME = MimeDataHelper(event.mimeData())
        #check mime types we can handle
        assert isinstance(event, QDragEnterEvent)
        if ME.hasMapLayers() or ME.hasUrls() or ME.hasDataSources():
            event.setDropAction(Qt.CopyAction) #copy but do not remove
            event.accept()
        else:
            event.ignore()

    def canvasDrop(self, event):
        ME = MimeDataHelper(event.mimeData())

        if ME.hasMapLayers():
            newLayers = ME.mapLayers()

            lyrs = self.canvas.layers()
            self.setLayers(newLayers + lyrs)
            event.accept()
            event.acceptProposedAction()
        if ME.hasDataSources():
            dataSources = [d for d in ME.dataSources() if isinstance(d, DataSourceSpatial)]
            dataSources = [self.enmapbox.dataSourceManager.addSource(d) for d in dataSources]
            layers = [d.createRegisteredMapLayer() for d in dataSources]

            self.addLayers(layers)




    def _createLabel(self, *args, **kwds):
        return MapDockLabel(self, *args, **kwds)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                s = ""
        else:
            super(MapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linkType):
        assert isinstance(mapDock, MapDock)
        self.linkWithCanvas(mapDock.canvas, linkType)


    def linkWithCanvas(self, canvas, linkType):
        assert isinstance(canvas, QgsMapCanvas)
        canvas.createCanvasLink(canvas, linkType)


    def layers(self):
        return self.canvas.layers()

    def setLayers(self, mapLayers):
        assert isinstance(mapLayers, list)
        self.canvas.setLayers(mapLayers)


    def addLayers(self, mapLayers):
        if not type(mapLayers) is list:
            mapLayers = [mapLayers]
        for l in mapLayers:
            assert isinstance(l, QgsMapLayer)
        self.setLayers(mapLayers + self.canvas.layers())

    def removeLayers(self, mapLayers):
        newSet = [l for l in self.canvas.layers() if l not in mapLayers]
        self.setLayers(newSet)





class CursorLocationValueDock(Dock):

    _instance = None

    """
    A dock to visualize cursor location values
    """

    def __init__(self, *args, **kwds):
        super(CursorLocationValueDock, self).__init__(*args, **kwds)
        from enmapbox.gui.cursorlocationvalue import CursorLocationValueWidget
        self.w = CursorLocationValueWidget(self)
        self.layout.addWidget(self.w)
        self.w.connectDataSourceManager(self.enmapbox.dataSourceManager)
        self.setTitle('Cursor Location Values')

    def showLocationValues(self, *args):
        self.w.showLocationValues(*args)

class TextDock(Dock):
    """
    A dock to visualize textural data
    """
    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(TextDock, self).__init__(*args, **kwds)

        self.textEdit = QTextEdit(self)

        if html:
            self.textEdit.insertHtml(html)
        elif plainTxt:
            self.textEdit.insertPlainText(plainTxt)
        self.layout.addWidget(self.textEdit)


class WebViewDock(Dock):
    def __init__(self, *args, **kwargs):
        uri = kwargs.pop('uri', None)
        url = kwargs.pop('url', None)
        super(WebViewDock,self).__init__(*args, **kwargs)
        #self.setLineWrapMode(QTextEdit.FixedColumnWidth)

        from PyQt4.QtWebKit import QWebView
        self.webView = QWebView(self)
        self.layout.addWidget(self.webView)

        if uri is not None:
            self.load(uri)
        elif url is not None:
            self.load(url)

    def load(self, uri):
        if os.path.isfile(uri):
            url = QUrl.fromLocalFile(uri)
        else:
            url = QUrl(uri)
        self.webView.load(url)
        settings = self.webView.page().settings()
        from PyQt4.QtWebKit import QWebSettings
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebSettings.AutoLoadImages, True)


class MimeDataTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(MimeDataTextEdit,self).__init__(*args, **kwargs)
        #self.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.setOverwriteMode(False)

    def canInsertFromMimeData(self, QMimeData):
        return True

    def insertFromMimeData(self, mimeData):
        assert isinstance(mimeData, QMimeData)
        formats = [str(f) for f in mimeData.formats()]
        self.clear()
        def append(txt):
            self.moveCursor(QTextCursor.End)
            self.insertPlainText(txt+'\n')
            self.moveCursor(QTextCursor.End)

        for format in formats:
            append('####{}####'.format(format))
            if format == 'text/uri-list':
                self.insertPlainText(str(mimeData.data('text/uri-list')))
            if format == 'text/html':
                self.insertHtml(mimeData.html())
            elif format == 'text/plain':
                self.insertPlainText(mimeData.text())
            else:
                append('### (raw data as string) ###')
                self.insertPlainText(str(mimeData.data(format)))
            append('\n')

    def dragEnterEvent(self, event):
        event.setDropAction(Qt.CopyAction)  # copy but do not remove
        event.accept()

    def dropEvent(self, event):
        self.insertFromMimeData(event.mimeData())
        event.setDropAction(Qt.CopyAction)
        event.accept()

class MimeDataDock(TextDock):
    """
    A dock to show dropped mime data
    """
    def __init__(self,*args, **kwds):
        super(MimeDataDock, self).__init__(*args, **kwds)



        self.layout.removeWidget(self.textEdit)
        self.textEdit = MimeDataTextEdit(self)
        self.layout.addWidget(self.textEdit)





