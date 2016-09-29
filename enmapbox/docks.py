from __future__ import absolute_import
import six, sys, os, gc, re, collections, site
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import pyqtgraph.dockarea.Dock
from pyqtgraph.widgets.VerticalLabel import VerticalLabel


from enmapbox.utils import *
from enmapbox.datasources import *

class CanvasLink(object):
    """
    A link between two QgsMapCanvases
    """
    LINKTYPES = ['center', 'scale', 'center_scale']
    def __init__(self, follower, master, linktype):
        assert isinstance(follower, QgsMapCanvas)
        assert isinstance(master, QgsMapCanvas)
        assert linktype in CanvasLink.LINKTYPES
        self.follower = follower
        self.master = master
        self.linktype = linktype

    def contains(self, canvas):
        return self.follower == canvas or self.master == canvas

    def canvases(self):
        return set([self.follower, self.master])

    def theOther(self, canvas):
        if self.follower == canvas:
            return self.master
        elif self.master == canvas:
            return self.follower
        else:
            raise Exception('Canvas {} not part of this link definition'.format(canvas))

    def __repr__(self):
        return 'CanvasLink {}->{} on {}'.format(self.follower,self.master, self.linktype)


class CanvasLinkManager:

    _instance = None

    @staticmethod
    def instance():
        if CanvasLinkManager._instance is None:
            CanvasLinkManager._instance = CanvasLinkManager()
        return CanvasLinkManager._instance

    def __init__(self):
        """
        Stores CanvasLinks and ensures integrity
        """
        self.LINKS = set()
        self.registeredCanvases = set()

    def addLink(self, canvasLink):
        assert isinstance(canvasLink, CanvasLink)

        # remove previous link of same follower, if exists
        self.removeFollowerLink(canvasLink.follower)

        # avoid circle dependencies
        if canvasLink.follower in self.getMasters(canvasLink.master):
            s = ""
            dprint('CIRCLE MAPLINK:')
            for l in self.dump(): dprint(l)
            self.removeFollowerLink(canvasLink.master)

        # register signals
        #allCanvases = self.getAllCanvases()
        if canvasLink.master not in self.registeredCanvases:
            canvasLink.master.extentsChanged.connect(lambda : self.setChanges(canvasLink.master))
            self.registeredCanvases.add(canvasLink.master)
        # add link to the link set
        self.LINKS.add(canvasLink)

    def getAllCanvases(self):
        canvases = set()
        for link in self.LINKS:
            assert isinstance(link, CanvasLink)
            canvases.update([link.master,link.follower])
        return canvases


    def getDirectFollowerLinks(self, master_canvas):
        links = set()
        for link in self.LINKS:
            if link.master == master_canvas:
                links.add(link)
        return links

    def getMasters(self, following_canvas):
        canvases = set()
        for link in self.LINKS:
            if link.follower == following_canvas:
                canvases.add(link.master)
        n_added = len(canvases)
        while n_added > 0:
            for c in canvases:
                canvases.update(self.getMasters(c))
            n_added = len(canvases) - n_added

        return canvases



    def removeFollowerLink(self, canvas):
        to_remove = [l for l in self.LINKS if l.follower == canvas]
        assert len(to_remove) <= 1
        if len(to_remove) == 1:
            dprint('REMOVE {}'.format(to_remove[0]))
            self.LINKS.remove(to_remove[0])

    def dump(self):
        """
        prints the state of the link manager. For debugging
        """
        l = []
        for link in self.LINKS:
            l.append(str(link))
        return l

    def setChanges(self, master):
        #canvas = the canvas that signaled a map change

        #all_canvases = CanvasLinkSet.getCanvases()
        #for c in all_canvases: c.blockSignals(True)
        #...
        #for c in all_canvases: c.blockSignals(False)


        mst_extent = master.extent()
        mst_center = master.center()

        for link in self.getDirectFollowerLinks(master):
            assert isinstance(link, CanvasLink)
            c = link.theOther(master)
            assert isinstance(c, QgsMapCanvas)
            c.blockSignals(True)

            #if necessary, transform to target CRS,
            src_crs = master.mapRenderer().destinationCrs()
            dst_crs = c.mapRenderer().destinationCrs()
            trans = QgsCoordinateTransform(src_crs, dst_crs)
            trans.initialise()
            if trans.isShortCircuited():
                new_extent = mst_extent
                new_center = mst_center
            else:
                new_extent = trans.transform(mst_extent)
                new_center = trans.transform(mst_center)

            #the recent/old map center + extent
            new_muppx = new_extent.width() / master.width()
            w = master.width() * new_muppx * 0.5
            h = master.height() * new_muppx * 0.5
            x = c.center().x()
            y = c.center().y()
            old_center_scaled = QgsRectangle(x-w,y-h,x+w,y+h)

            if link.linktype == 'center':
                lockState = c.scaleLocked()
                c.setScaleLocked(True)
                c.setCenter(new_center)
                c.setScaleLocked(lockState)
            elif link.linktype == 'scale':
                c.zoomToFeatureExtent(old_center_scaled)
                #c.zoomScale(dst_scale)
            elif link.linktype == 'center_scale':
                c.zoomToFeatureExtent(new_extent)
            else:
                raise NotImplementedError()
            c.blockSignals(False)


    def convert_CRS(self, c_src, c_dst):
        src_ext = c_src.extent()
        src_center = c_src.center()
        src_scale = c_src.scale()
        print('CANVAS:: {} {} [{} {}]'.format(src_scale,src_center,src_ext.width(), src_ext.height() ))
        src_crs = c_src.mapRenderer().destinationCrs()
        dst_crs = c_dst.mapRenderer().destinationCrs()

        if src_crs == dst_crs:
            dst_ext = src_ext
            dst_center = src_center
            dst_scale = src_scale
        else:
            raise NotImplementedError()

        return dst_ext, dst_center, dst_scale




class DockWindow(QtGui.QMainWindow):
    def __init__(self, area, **kwargs):
        QtGui.QMainWindow.__init__(self, **kwargs)
        self.setWindowTitle('EnMAPBox')
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
    '''
    Handle style sheets etc., basic stuff that differs from pyqtgraph dockarea
    '''


    def __init__(self, enmapboxInstance, name='view', closable=True, *args, **kwds):
        super(Dock, self).__init__(name=name, closable=False, *args, **kwds)

        self.enmapbox = enmapboxInstance


        self.title = name
        self.setStyleSheet('background:#FFF')

        #change the enmapbox-like things
        self.topLayout.removeWidget(self.label)
        del self.label


        self.label = self._getLabel()
        self.topLayout.addWidget(self.label, 0, 1)

        if closable:
            self.label.sigCloseClicked.connect(self.close)

        self.raiseOverlay()


        self.hStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-top-width: 0px;
        }
        """
        self.vStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-left-width: 0px;
        }
        """
        self.nStyle = """
        EnMAPBoxDock > QWidget {
            border: 1px solid #000;
            border-radius: 5px;
        }"""
        self.dragStyle = """
        EnMAPBoxDock > QWidget {
            border: 4px solid #00F;
            border-radius: 5px;
        }"""

        self.widgetArea.setStyleSheet(self.hStyle)
        self.topLayout.update()


        self.sigClosed.connect(lambda: self.enmapbox.DOCKS.remove(self))
        self.enmapbox.DOCKS.add(self)


    def _getLabel(self):
        """
        This functions returns the Label that is used to style the Dock
        :return:
        """
        return DockLabel(self)

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

    def __init__(self, dock, allow_floating=True):
        assert isinstance(dock, Dock)
        self.dim = False
        self.fixedWidth = False
        self.dock = dock
        VerticalLabel.__init__(self, self.dock.title, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.updateStyle()
        self.setAutoFillBackground(False)
        self.startedDrag = False
        self.buttons = list() #think from right to left
        self.pressPos = QtCore.QPoint()

        closeButton = QtGui.QToolButton(self)
        closeButton.clicked.connect(self.sigCloseClicked)
        closeButton.setToolTip('Close window')
        closeButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))
        self.buttons.append(closeButton)

        if allow_floating:
            floatButton = QtGui.QToolButton(self)
            #testButton.clicked.connect(self.sigNormalClicked)
            floatButton.setToolTip('Float window')
            floatButton.clicked.connect(lambda : self.dock.float())
            floatButton.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_TitleBarNormalButton))
            self.buttons.append(floatButton)

    def updateStyle(self):
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
            self.vStyle = """EnMAPBoxDockLabel {
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
            self.hStyle = """EnMAPBoxDockLabel {
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
            ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
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


class CanvasLinkTargetWidget(QtGui.QFrame):

    LINK_TARGET_WIDGETS = set()


    @staticmethod
    def ShowMapLinkTargets(mapDock):

        assert isinstance(mapDock, MapDock)
        canvas_targed = mapDock.canvas
        assert isinstance(canvas_targed, QgsMapCanvas)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)

        target_canvases = [d.canvas for d in mapDock.enmapbox.DOCKS
                           if isinstance(d, MapDock) and d != mapDock]

        for canvas_source in target_canvases:

            w = CanvasLinkTargetWidget(canvas_targed, canvas_source)
            w.setAutoFillBackground(True)
            w.show()
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.add(w)
            canvas_source.freeze()
            s = ""

        s = ""

    @staticmethod
    def linkMaps(maplinkwidget, linktype):
        follower = maplinkwidget.canvas1
        master = maplinkwidget.canvas2
        CanvasLinkManager.instance().addLink(CanvasLink(follower, master, linktype))
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets()

    @staticmethod
    def RemoveMapLinkTargetWidgets(processEvents=True):
        for w in list(CanvasLinkTargetWidget.LINK_TARGET_WIDGETS):
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.remove(w)
            p = w.parent()
            w.hide()
            del(w)
            p.refresh()
            p.update()

        if processEvents:
            #qApp.processEvents()
            QCoreApplication.instance().processEvents()

    def __init__(self, canvas1, canvas2):
        assert isinstance(canvas1, QgsMapCanvas)
        assert isinstance(canvas2, QgsMapCanvas)

        QFrame.__init__(self, parent=canvas2)
        self.canvas1 = canvas1
        self.canvas2 = canvas2
        #self.canvas1.installEventFilter(self)
        self.canvas2.installEventFilter(self)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.setCursor(Qt.ArrowCursor)

        ly = QHBoxLayout()
        #add buttons with link functions
        self.buttons = list()
        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'center'))
        bt.setIcon(QIcon(IconProvider.Map_Link_Center))
        self.buttons.append(bt)

        if False:
            bt = QtGui.QToolButton(self)
            bt.setToolTip('Link map extent')
            bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'extent'))
            bt.setIcon(Icon(IconProvider.Map_Link_Extent))
            self.buttons.append(bt)

        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map scale ("Zoom")')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'scale'))
        bt.setIcon(QIcon(IconProvider.Map_Link_Scale))
        self.buttons.append(bt)

        bt = QtGui.QToolButton(self)
        bt.setToolTip('Link map scale and center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'center_scale'))
        bt.setIcon(QIcon(IconProvider.Map_Link_Scale_Center))
        self.buttons.append(bt)



        for bt in self.buttons:
            bt.setAttribute(Qt.WA_PaintOnScreen)
            #bt.setIconSize(QSize(100, 100))
            bt.setAutoRaise(True)
            ly.addWidget(bt)

        self.layout.addLayout(ly, 0,0)
        self.setStyleSheet('background-color:rgba(0, 0, 0, 25);')
        self.setAttribute(Qt.WA_PaintOnScreen)

        self.updatePosition()

    def updatePosition(self):
        if hasattr(self.parent(), 'viewport'):
            parentRect = self.parent().viewport().rect()

        else:
            parentRect = self.parent().rect()

        if not parentRect:
            return

        #get map center
        x = int(parentRect.width() / 2 - self.width() / 2)
        y = int(parentRect.height() / 2 - self.height() / 2)

        mw = int(min([self.width(),self.height()]) * 0.9)
        for bt in self.buttons:
            bt.setIconSize(QSize(mw, mw))

        #self.setGeometry(x, y, self.width(), self.height())
        self.setGeometry(parentRect)

    def setParent(self, parent):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).setParent(parent)

    def resizeEvent(self, event):
        super(CanvasLinkTargetWidget, self).resizeEvent(event)
        self.updatePosition()

    def showEvent(self, event):
        self.updatePosition()
        return super(CanvasLinkTargetWidget, self).showEvent(event)

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Resize:
            s  = ""
            self.updatePosition()
        return False

    def mousePressEvent(self, ev):

        if ev.button() == Qt.RightButton:
            #no choice, remove Widgets
            CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)
            ev.accept()


class MapDockLabel(DockLabel):

    def __init__(self, *args, **kwds):

        super(MapDockLabel, self).__init__(*args, **kwds)

        self.linkMap = QtGui.QToolButton(self)
        self.linkMap.setToolTip('Link with other map')
        #linkExtent.clicked.connect(lambda: self.dock.linkWithMapDock())
        #self.linkMap.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink))
        self.linkMap.setIcon(QIcon(IconProvider.Map_Link))

        self.removeMapLink = QtGui.QToolButton(self)
        self.removeMapLink.setToolTip('Remove links')
        self.linkMap.setIcon(QIcon(IconProvider.Map_Link_Remove))
        self.buttons.extend([self.linkMap, self.removeMapLink])


class MapCanvas(QgsMapCanvas):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)

    _cnt = 0

    def __init__(self, parentMapDock, *args, **kwds):
        super(MapCanvas, self).__init__(*args, **kwds)
        assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        MapCanvas._cnt += 1
        self.mapdock = parentMapDock
        self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()

    def __repr__(self):
        return self._id

    #forward to MapDock
    def dragEnterEvent(self, event):
        self.sigDragEnterEvent.emit(event)

    # forward to MapDock
    def dragMoveEvent(self, event):
        self.sigDragMoveEvent.emit(event)

    # forward to MapDock
    def dragLeaveEvent(self, event):
        self.sigDragLeaveEvent.emit(event)

    # forward to MapDock
    def dropEvent(self, event):
        self.sigDropEvent.emit(event)




class MapDock(Dock):

    """
    A dock to visualize geodata that can be mapped
    """
    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)



        super(MapDock, self).__init__(*args, **kwds)

        #self.actionLinkExtent = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Link to map extent', self)
        #self.actionLinkCenter = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Linkt to map center', self)
        #self.label.buttons.append(self.actionLinkCenter.getButton())
        self.canvas = MapCanvas(self)
        self.canvas.sigDropEvent.connect(self.canvasDrop)
        self.canvas.sigDragEnterEvent.connect(self.canvasDragEnter)
        self.canvas.customContextMenuRequested.connect(self.onCanvasContextMenu)
        settings = QSettings()
        assert isinstance(self.canvas, QgsMapCanvas)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.canvas)

        #link canvas to map tools
        g = self.enmapbox.gui
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

        self.toolIdentify = QgsMapToolIdentify(self.canvas)
        self.toolIdentify.setAction(g.actionIdentify)
        self.toolIdentify.action().triggered.connect(lambda: self.setMapTool(self.toolIdentify))

        self.label.linkMap.clicked.connect(lambda:CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        self.label.removeMapLink.clicked.connect(lambda: CanvasLinkManager.instance().removeFollowerLink(self.canvas))
        #set default map tool
        self.canvas.setMapTool(self.toolPan)

        #todo: context menu

        if initSrc:
            ds = self.enmapbox.addSource(initSrc)
            if isinstance(ds, DataSourceSpatial):
                self.addLayer(ds.createMapLayer())

    def onCanvasContextMenu(self, point):
        s  = ""
        pass

    def setMapTool(self, mapTool):
        if False:
            if isinstance(mapTool, QgsMapToolPan):
                self.canvas.setScaleLocked(True)
            else:
                self.canvas.setScaleLocked(False)

        self.canvas.setMapTool(mapTool)

    def test(self):
        print('START LINKING')

        w = CanvasLinkTargetWidget(self.enmapbox.gui)
        s = ""

    def canvasDragEnter(self, event):
        import enmapbox.utils
        ME = enmapbox.utils.MimeDataHelper(event.mimeData())
        #check mime types we can handle
        assert isinstance(event, QDragEnterEvent)
        if ME.hasUriList() or ME.hasQgsLayerTree():
            event.setDropAction(Qt.CopyAction) #copy but do not remove
            event.accept()
        else:
            event.ignore()

    def canvasDrop(self, event):
        import enmapbox.utils
        ME = enmapbox.utils.MimeDataHelper(event.mimeData())

        added_sources = []
        if ME.hasQgsLayerTree():
            for id, name in ME.getQgsLayerTreeLayers():
                ds = DataSource.Factory(id, name=name)
                if ds is not None:
                    added_sources.append(self.enmapbox.addSource(ds))


        if ME.hasUriList():
            for url in ME.getUriList():
                ds = DataSource.Factory(url)
                if ds is not None:
                    added_sources.append(self.enmapbox.addSource(ds))
        for ds in added_sources:
            self.addLayer(ds.createMapLayer())


    def _getLabel(self):
        return MapDockLabel(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                s = ""
        else:
            super(MapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linktype):
        assert isinstance(mapDock, MapDock)
        self.linkWithCanvas(mapDock.canvas, linktype)


    def linkWithCanvas(self, canvas, linktype):
        assert isinstance(canvas, QgsMapCanvas)
        CanvasLinkManager.instance().addLink(self, canvas, linktype)


    def addLayer(self, mapLayer, index=0):

        if isinstance(mapLayer, DataSourceSpatial):


            pass
        else:
            assert isinstance(mapLayer, QgsMapLayer)

            reg = QgsMapLayerRegistry.instance()
            reg.addMapLayer(mapLayer, False)

            newCanvasLayer = QgsMapCanvasLayer(mapLayer)
            newCanvasLayer.setVisible(True)
            canvasLayers = [QgsMapCanvasLayer(l) for l in self.canvas.layers()]
            canvasLayers.insert(index, newCanvasLayer)

            if len(canvasLayers) == 1:
                self.canvas.setExtent(mapLayer.extent())

            self.canvas.setLayerSet(canvasLayers)
            if self.canvas.isCachingEnabled():
                mapLayer.setCacheImage(None)
                newCanvasLayer.setCacheImage(None)
            self.canvas.refresh()



class TextDock(Dock):
    """
    A dock to visualize textural data
    """
    def __init__(self, *args, **kwds):
        html = kwds.pop('html', None)
        plainTxt = kwds.pop('plainTxt', None)

        super(TextDock, self).__init__(*args, **kwds)

        self.edit = QtGui.QTextEdit(self)

        if html:
            self.edit.insertHtml(html)
        elif plainTxt:
            self.edit.insertPlainText(plainTxt)
        self.layout.addWidget(self.edit)


class MimeDataDock(TextDock):
    """
    A dock to show dropped mime data
    """
    def __init__(self):

        pass

