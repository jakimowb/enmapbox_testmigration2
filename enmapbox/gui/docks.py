from __future__ import absolute_import

import itertools
import os
import uuid
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from enmapbox.gui.datasources import *
from enmapbox.gui.utils import *
import pyqtgraph.dockarea.Dock
from pyqtgraph.widgets.VerticalLabel import VerticalLabel




class CanvasLink():

    def __init__(self, canvas1, canvas2, linktype):
        assert linktype in CanvasLinkSet.LINKTYPES

        self.linktype = linktype
        self.canvases = set([canvas1, canvas2])

    def theOtherCanvas(self, canvas):
        assert canvas in self.canvases
        assert len(self.canvases) == 2
        diff = list(self.canvases - set([canvas]))
        assert len(diff) == 1
        return diff[0]

    def __repr__(self):
        cs = list(self.canvases)
        return 'CanvasLink "{}" {} <-> {}'.format(self.linktype, cs[0], cs[1])

class CanvasLinkSet(object):
    """
    A link between two QgsMapCanvases
    """
    LINKTYPES = ['center', 'scale', 'center_scale']

    def __init__(self, canvases, linktype):
        assert linktype in CanvasLinkSet.LINKTYPES

        for c in canvases:
            assert isinstance(c, QgsMapCanvas)
        self.links = set()
        for c1, c2 in itertools.combinations(canvases,2):
            self.links.add(CanvasLink(c1,c2, linktype))
        self.linktype = linktype

    def contains(self, canvas):
        assert isinstance(canvas, QgsMapCanvas)
        return canvas in self.canvases

    def removeLinksBetween(self, canvases):
        for c1, c2 in itertools.combinations(canvases, 2):
            c = set([c1,c2])
            to_remove = [link for link in self.links if c <= link.canvases]
            for link in to_remove:
                self.links.remove(link)


    def removeCanvas(self, canvas):
        assert isinstance(canvas, QgsMapCanvas)
        to_remove = [l for l in self.links if canvas in l.canvases]
        for l in to_remove:
            self.links.remove(l)

    def addCanvas(self, canvas):
        assert isinstance(canvas, QgsMapCanvas)
        canvases = self.canvases() - canvas
        for c in canvases:
            self.links.append(CanvasLink(canvas, c , self.linktype))

    def canvases(self):
        canvases = set()
        for link in self.links:
            canvases.update(link.canvases)
        return canvases

    def __len__(self):
        return len(self.links)

    def __repr__(self):
        return 'CanvasLinkSet "{}" between {{{}}}'.format(self.linktype, ', '.join([str(c) for c in self.canvases() ]))


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
        self.LINKSETS = set()
        self.registeredCanvases = set()
        self.handledCanvases = set()



    def addLinkSet(self, newLinkSet):
        assert isinstance(newLinkSet, CanvasLinkSet)

        # there can be only one link type between two canvases
        # remove canvas links defined in this link set from previous link sets
        for link in newLinkSet.links:
            for linkSet in self.LINKSETS:
                assert isinstance(linkSet, CanvasLinkSet)
                linkSet.removeLinksBetween(link.canvases)

        #remove empty link sets
        self.removeEmptyLinkSets()

        # register signals
        to_register = [canvas for canvas in newLinkSet.canvases() if canvas not in self.registeredCanvases]
        for canvas in to_register:
            canvas.sigExtentsChanged.connect(self.setChanges)
            self.registeredCanvases.add(canvas)

        # add link set to registered link sets
        self.LINKSETS.add(newLinkSet)

    def unlink(self, canvas):
        """
        Removes all links to a given canvas
        :param canvas:
        """
        for linkSet in self.LINKSETS:
            linkSet.removeCanvas(canvas)
        self.removeEmptyLinkSets()

    def removeEmptyLinkSets(self):
        to_remove = [linkSet for linkSet in self.LINKSETS if len(linkSet) == 0]
        for linkSet in to_remove:
            self.LINKSETS.remove(linkSet)
            del linkSet


    def connectedLinks(self, canvas):

        links = set()
        for linkSet in self.LINKSETS:
            links.update(set([link for link in linkSet.links if canvas in link.canvases]))
        return links

    def canvases(self):
        """
        Returns all canvases handeled
        :return:
        """
        canvases = set()
        for linkSet in self.LINKSETS:
            assert isinstance(linkSet, CanvasLinkSet)
            canvases.update(linkSet.canvases())
        assert len(canvases - self.registeredCanvases) == 0
        return canvases



    def dump(self):
        """
        prints the state of the link manager. For debugging
        """
        l = []
        for linkSet in self.LINKSETS:
            l.append(str(linkSet))
        return l

    def setChanges(self, masterCanvas):
        #canvas = the canvas that signaled a map change

        #all_canvases = CanvasLinkSet.getCanvases()
        #for c in all_canvases: c.blockSignals(True)
        #...
        #for c in all_canvases: c.blockSignals(False)

        assert isinstance(masterCanvas, MapCanvas)


        if len(self.handledCanvases) == 0:
            logger.debug('START LINKING FROM: {}'.format(masterCanvas))

        self.handledCanvases.add(masterCanvas)

        mst_extent = SpatialExtent.fromMapCanvas(masterCanvas)
        mst_center = SpatialPoint.fromMapCanvasCenter(masterCanvas)

        changed = set()
        #apply changes to L1 generation of connected canvases = directly connecte to canvas
        to_change = [link for link in self.connectedLinks(masterCanvas)
                     if len(link.canvases.difference(self.handledCanvases)) > 0]



        for link in to_change:


            assert isinstance(link, CanvasLink)
            dstCanvas = link.theOtherCanvas(masterCanvas)
            assert isinstance(dstCanvas, MapCanvas)

            if True:
                dstCanvas.blockSignals(True)
            #original center and extent
            centerO = SpatialPoint.fromMapCanvasCenter(dstCanvas)
            extentO = SpatialExtent.fromMapCanvas(dstCanvas)

            #transform (T) to target CRS
            dstCrs = dstCanvas.mapSettings().destinationCrs()
            extentT = mst_extent.toCrs(dstCrs)
            centerT = mst_center.toCrs(dstCrs)

            w, h = masterCanvas.width(), masterCanvas.height()
            if w == 0:
                w = max([10, dstCanvas.width()])
            if h == 0:
                h = max([10, dstCanvas.height()])

            mapUnitsPerPx_x = extentT.width() / w
            mapUnitsPerPx_y = extentT.height() / h

            scaledWidth = mapUnitsPerPx_x * dstCanvas.width()
            scaledHeight = mapUnitsPerPx_y * dstCanvas.height()
            scaledBox = SpatialExtent(dstCrs, scaledWidth, scaledHeight).setCenter(centerO)

            if link.linktype == 'center':
                dstCanvas.setCenter(centerT)

            elif link.linktype == 'scale':
                dstCanvas.zoomToFeatureExtent(scaledBox)

            elif link.linktype == 'center_scale':
                dstCanvas.zoomToFeatureExtent(extentT)



            else:
                raise NotImplementedError()

            dstCanvas.blockSignals(False)

            #dst.refresh()
            changed.add(dstCanvas)


        #set applied changes to L2 generation of connected canvases
        for canvas in changed:
            self.setChanges(canvas)

        self.handledCanvases.remove(masterCanvas)



    def convert_CRS(self, c_src, c_dst):
        src_ext = c_src.extent()
        src_center = c_src.center()
        src_scale = c_src.scale()
        print('CANVAS:: {} {} [{} {}]'.format(src_scale,src_center,src_ext.width(), src_ext.height() ))
        src_crs = c_src.mapSettings().destinationCrs()
        dst_crs = c_dst.mapSettings().destinationCrs()

        if src_crs == dst_crs:
            dst_ext = src_ext
            dst_center = src_center
            dst_scale = src_scale
        else:
            raise NotImplementedError()

        return dst_ext, dst_center, dst_scale




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


class CanvasLinkTargetWidget(QFrame):

    LINK_TARGET_WIDGETS = set()


    @staticmethod
    def ShowMapLinkTargets(mapDock):

        assert isinstance(mapDock, MapDock)
        canvas1 = mapDock.canvas
        assert isinstance(canvas1, QgsMapCanvas)
        CanvasLinkTargetWidget.RemoveMapLinkTargetWidgets(True)

        target_canvases = [d.canvas for d in mapDock.enmapbox.dockManager.DOCKS
                           if isinstance(d, MapDock) and d != mapDock]

        for canvas_source in target_canvases:

            w = CanvasLinkTargetWidget(canvas1, canvas_source)
            w.setAutoFillBackground(False)
            w.show()
            CanvasLinkTargetWidget.LINK_TARGET_WIDGETS.add(w)
            canvas_source.freeze()
            s = ""

        s = ""

    @staticmethod
    def linkMaps(maplinkwidget, linktype):
        canvases = [maplinkwidget.canvas1, maplinkwidget.canvas2]
        CanvasLinkManager.instance().addLinkSet(CanvasLinkSet(canvases, linktype))
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
        bt = QToolButton(self)
        bt.setToolTip('Link map center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'center'))
        icon = QIcon(':/enmapbox/icons/link_center.png')
        bt.setIcon(icon)
        bt.setIconSize(QSize(16,16))
        self.buttons.append(bt)

        bt = QToolButton(self)
        bt.setToolTip('Link map scale ("Zoom")')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'scale'))
        bt.setIcon(QIcon(':/enmapbox/icons/link_mapscale.png'))
        self.buttons.append(bt)

        bt = QToolButton(self)
        bt.setToolTip('Link map scale and center')
        bt.clicked.connect(lambda: CanvasLinkTargetWidget.linkMaps(self, 'center_scale'))
        bt.setIcon(QIcon(':/enmapbox/icons/link_mapscale_center.png'))
        self.buttons.append(bt)


        btStyle = """
        QToolButton { /* all types of tool button */
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
        }

        QToolButton[popupMode="1"] { /* only for MenuButtonPopup */
            padding-right: 20px; /* make way for the popup button */
        }

        QToolButton:pressed {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #dadbde, stop: 1 #f6f7fa);
        }"""

        for bt in self.buttons:
            bt.setAttribute(Qt.WA_PaintOnScreen)
            bt.setStyleSheet(btStyle)
            bt.setIconSize(QSize(100, 100))
            bt.setAutoRaise(True)
            ly.addWidget(bt)

        self.layout.addLayout(ly, 0,0)
        self.setStyleSheet('background-color:rgba(125, 125, 125, 125);')
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
        mw = min([mw, 120])
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

        self.addMapLink = QToolButton(self)
        self.addMapLink.setToolTip('Link with other map(s)')
        self.addMapLink.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        self.buttons.append(self.addMapLink)

        self.removeMapLink = QToolButton(self)
        self.removeMapLink.setToolTip('Remove links to this map')
        self.removeMapLink.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        self.buttons.append(self.removeMapLink)


class MapCanvas(QgsMapCanvas):
    sigDragEnterEvent = pyqtSignal(QDragEnterEvent)
    sigDragMoveEvent = pyqtSignal(QDragMoveEvent)
    sigDragLeaveEvent = pyqtSignal(QDragLeaveEvent)
    sigDropEvent = pyqtSignal(QDropEvent)
    sigContextMenuEvent = pyqtSignal(QContextMenuEvent)
    sigExtentsChanged = pyqtSignal(object)
    sigLayersRemoved = pyqtSignal(list)
    sigLayersAdded = pyqtSignal(list)

    _cnt = 0

    def __init__(self, parentMapDock, *args, **kwds):
        super(MapCanvas, self).__init__(*args, **kwds)


        assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        MapCanvas._cnt += 1
        self._extentInitialized = False
        self.mapdock = parentMapDock
        self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()
        self.extentsChanged.connect(self.sandbox)

    def zoomToFeatureExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        self.setSpatialExtent(spatialExtent)

    def sandbox(self):
        self.sigExtentsChanged.emit(self)

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

    def contextMenuEvent(self, event):
        self.sigContextMenuEvent.emit(event)

    def setSpatialExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        if self.spatialExtent() != spatialExtent:
            self.blockSignals(True)
            self.setDestinationCrs(spatialExtent.crs())
            self.setExtent(spatialExtent)
            self.blockSignals(False)
            self.refresh()

    def setExtent(self, QgsRectangle):
        super(MapCanvas, self).setExtent(QgsRectangle)
        self.setRenderFlag(True)

    def spatialExtent(self):
        return SpatialExtent.fromMapCanvas(self)

    def setLayerSet(self, *arg, **kwds):
        raise Exception('Depricated: Not supported any more (QGIS 3)')

    def setLayers(self, mapLayers):

        lastSet = self.layers()
        newSet = mapLayers[:]

        #register not-registered layers
        reg = QgsMapLayerRegistry.instance()
        for l in newSet:
            assert isinstance(l, QgsMapLayer)
            if l not in reg.children():
                reg.addMapLayer(l, False)

        #set the new layers (QGIS 2 style)
        #todo: change with QGIS 3
        super(MapCanvas,self).setLayerSet([QgsMapCanvasLayer(l) for l in newSet])

        if not self._extentInitialized and len(newSet) > 0:
            # set canvas to first layer's CRS and full extent
            self.mapSettings().setDestinationCrs(newSet[0].crs())
            self.setSpatialExtent(SpatialExtent.fromMapCanvas(self, fullExtent=True))
            self._extentInitialized = True
        self.refresh()

        #signal what has been added, what has been removed
        removedLayers = [l for l in lastSet if l not in newSet]
        addedLayers = [l for l in newSet if l not in lastSet]


        if len(removedLayers) > 0:
            self.sigLayersRemoved.emit(removedLayers)
        if len(addedLayers) > 0:
            self.sigLayersAdded.emit(addedLayers)



class MapDock(Dock):
    """
    A dock to visualize geodata that can be mapped
    """
    #sigCursorLocationValueRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    from enmapbox.gui.utils import SpatialPoint, SpatialExtent
    sigCursorLocationValueRequest = pyqtSignal(SpatialPoint)

    sigLayersAdded = pyqtSignal(list)
    sigLayersRemoved = pyqtSignal(list)

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

        self.label.addMapLink.clicked.connect(lambda:CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        self.label.removeMapLink.clicked.connect(lambda: CanvasLinkManager.instance().unlink(self.canvas))
        #set default map tool
        self.canvas.setMapTool(self.toolPan)


    def cursorLocationValueRequest(self,*args):
        self.sigCursorLocationValueRequest.emit(*args)

    def getDockContentContextMenu(self):
        menu = QMenu()

        action = QAction('Link with other maps', menu)
        action.setIcon(QIcon(':/enmapbox/icons/link_basic.png'))
        action.triggered.connect(lambda: CanvasLinkTargetWidget.ShowMapLinkTargets(self))
        menu.addAction(action)

        action = QAction('Remove links to other maps', menu)
        action.setIcon(QIcon(':/enmapbox/icons/link_open.png'))
        action.triggered.connect(lambda: CanvasLinkManager.instance().unlink(self.canvas))
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
        w.setLayerCrs(crs)
        w.setCrs(crs)

        d = w.dialog()
        d.setMessage('Select CRS for {}'.format(self.title))
        w.crsChanged.connect(lambda returned_crs: self.canvas.setDestinationCrs(returned_crs))
        w.selectCrs()


    def setMapTool(self, mapTool):
        self.canvas.setMapTool(mapTool)

    def test(self):
        print('START LINKING')

        w = CanvasLinkTargetWidget(self.enmapbox.gui)
        s = ""

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

    def linkWithMapDock(self, mapDock, linktype):
        assert isinstance(mapDock, MapDock)
        self.linkWithCanvas(mapDock.canvas, linktype)


    def linkWithCanvas(self, canvas, linktype):
        assert isinstance(canvas, QgsMapCanvas)
        CanvasLinkManager.instance().addLinkSet(self, canvas, linktype)


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





