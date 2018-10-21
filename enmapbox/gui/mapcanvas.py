# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    mapcanvas.py
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

from qgis.core import *
from qgis.gui import *
from qgis.core import QgsCoordinateReferenceSystem, QgsMapLayer
from qgis.gui import QgsMapCanvas, QgisInterface, QgsMapMouseEvent
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

import numpy as np

from enmapbox.gui.utils import *
from enmapbox.gui.utils import KeepRefs
from enmapbox.gui.crosshair import CrosshairMapCanvasItem, CrosshairStyle
from enmapbox.gui.mimedata import *

LINK_ON_SCALE = 'SCALE'
LINK_ON_CENTER = 'CENTER'
LINK_ON_CENTER_SCALE = 'CENTER_SCALE'
UNLINK = 'UNLINK'

N_MAX_GRP = 2

DEBUG = False





class MapCanvasListModel(QAbstractListModel):
    def __init__(self, parent=None, mapCanvases=None):
        super(MapCanvasListModel, self).__init__(parent)

        self.mMapCanvases = []
        if mapCanvases:
            for m in mapCanvases:
                self.addMapCanvas(m)

    def __iter__(self):
        return self.mMapCanvases.__iter__()

    def __len__(self):
        return len(self.mMapCanvases)

    def mapCanvases(self):
        return self.mMapCanvases[:]

    def insertCanvases(self, canvases, i=None):
        assert isinstance(canvases, list)
        if i is None:
            i = len(self.mMapCanvases)
        canvases = [c for c in canvases if c not in self.mMapCanvases]
        if len(canvases) > 0:
            self.beginInsertRows(QModelIndex(), i, i + len(canvases) - 1)
            self.mMapCanvases.extend(canvases)
            for c in canvases:
                if isinstance(c, MapCanvas):
                    c.sigNameChanged.connect(lambda : self.onCanvasUpdate(c))
            self.endInsertRows()

    def removeCanvas(self, canvas):
        if isinstance(canvas, list):
            for c in canvas:
                self.removeCanvas(c)
        else:
            if isinstance(canvas, QgsMapCanvas) and canvas in self.mMapCanvases:
                idx = self.canvas2idx(canvas)
                self.beginRemoveRows(QModelIndex(), idx.row(), idx.row())
                self.mMapCanvases.remove(canvas)
                self.endRemoveRows()

    def onCanvasUpdate(self, canvas):
        if canvas in self.mMapCanvases:
            idx = self.canvas2idx(canvas)
            self.dataChanged.emit(idx, idx)

    def addMapCanvas(self, mapCanvas):
        self.insertCanvases([mapCanvas])

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.mMapCanvases)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def idx2canvas(self, index):
        if index.isValid():
            return self.mMapCanvases[index.row()]
        return None

    def canvas2idx(self, canvas):
        return self.createIndex(self.mMapCanvases.index(canvas), 0)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if (index.row() >= len(self.mMapCanvases)) or (index.row() < 0):
            return None

        mapCanvas = self.idx2canvas(index)

        value = None
        if isinstance(mapCanvas, MapCanvas):
            if role == Qt.DisplayRole:
                value = '{}'.format(mapCanvas.name())
            if role == Qt.DecorationRole:
                value = QIcon()
            if role == Qt.UserRole:
                value = mapCanvas
        return value



class CanvasLinkDialog(QDialog):

    LINK_TYPES = [LINK_ON_CENTER_SCALE, LINK_ON_SCALE, LINK_ON_CENTER, UNLINK]
    @staticmethod
    def showDialog(parent=None, canvases=None):
        """
        Opens a Dialog to specify the map linking
        """
        from enmapbox.gui.enmapboxgui import EnMAPBox
        emb = EnMAPBox.instance()

        if canvases is None:
            canvases = emb.mapCanvases()

        for c in canvases:
            assert isinstance(c, QgsMapCanvas)
        d = CanvasLinkDialog(parent=parent)
        d.addCanvas(canvases)
        d.setSourceCanvas(canvases[0])

        if isinstance(emb, EnMAPBox):
            emb.sigMapCanvasAdded.connect(d.addCanvas)
            emb.sigCanvasRemoved.connect(d.removeCanvas)
            emb.sigClosed.connect(d.close)

        d.show()


    def __init__(self, *args, **kwds):
        super(CanvasLinkDialog, self).__init__(*args, **kwds)

        self.setWindowIcon(QIcon(':/enmapbox/icons/enmapbox.svg'))
        self.setWindowTitle('Map Linking')
        self.setLayout(QVBoxLayout())

        self.grid = QGridLayout()
        self.cbSrcCanvas = QComboBox()
        self.cbSrcCanvas.currentIndexChanged.connect(self.onSourceCanvasChanged)
        self.mSrcCanvasModel = MapCanvasListModel()
        self.cbSrcCanvas.setModel(self.mSrcCanvasModel)

        self.mTargets = []
        hb = QHBoxLayout()
        hb.addWidget(QLabel('Link '))
        hb.addWidget(self.cbSrcCanvas)
        hb.addWidget(QLabel('with...'))
        hb.addSpacerItem(QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.mWidgetLUT = dict()
        self.layout().addLayout(hb)
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(hline)
        self.layout().addLayout(self.grid)
        self.layout().addSpacing(0)

    def onSourceCanvasChanged(self):
        pass
        self.setSourceCanvas(self.currentSourceCanvas())
        s = ""

    def onTargetSelectionChanged(self):
        sender = self.sender()
        s  =""

    def addCanvas(self, canvas):

        if isinstance(canvas, list):
            for c in canvas: self.addCanvas(c)
        else:
            self.mSrcCanvasModel.addMapCanvas(canvas)

        #force a refresh of widgets
        src = self.currentSourceCanvas()
        self.setSourceCanvas(src)


    def removeCanvas(self, canvas):
        if isinstance(canvas, list):
            for c in canvas: self.removeCanvas(c)
        else:
            self.mSrcCanvasModel.removeCanvas(canvas)

            # force a refresh of widgets
            src = self.currentSourceCanvas()
            self.setSourceCanvas(src)

    def currentSourceCanvas(self):
        return self.cbSrcCanvas.itemData(self.cbSrcCanvas.currentIndex(), Qt.UserRole)

    def currentTargetCanvases(self):
        srcCanvas = self.currentSourceCanvas()
        return [trgCanvas for trgCanvas in self.mSrcCanvasModel.mapCanvases() if trgCanvas != srcCanvas]

    def setSourceCanvas(self, canvas):

        if not isinstance(canvas, QgsMapCanvas):
            return


        if canvas not in self.mSrcCanvasModel:
            self.addCanvas(canvas)

        srcCanvas = self.currentSourceCanvas()


        #create a widget for each target canvas
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
            self.mWidgetLUT.clear()

        trgCanvases = self.currentTargetCanvases()


        if not isinstance(srcCanvas, MapCanvas):
            return


        def createButtonToAll(linkType, tooltip):
            a = CanvasLink.linkAction(None, None, linkType)
            a.setToolTip(tooltip)
            a.triggered.connect(lambda: self.linkToAll(linkType))
            btn1 = QToolButton()
            btn1.setDefaultAction(a)
            return btn1

        if len(trgCanvases) >= N_MAX_GRP:

            self.grid.addWidget(QLabel('All Canvases'), 0, 0)
            btn1 = createButtonToAll(LINK_ON_CENTER_SCALE, 'Link all canvases on center and scale.')
            btn2 = createButtonToAll(LINK_ON_SCALE, 'Link all canvases on scale.')
            btn3 = createButtonToAll(LINK_ON_CENTER, 'Link all canvases on center.')
            btn4 = createButtonToAll(UNLINK, 'Unlink all canvases.')
            self.grid.addWidget(QLabel('All Canvases'), 0, 0)
            btns = [btn1, btn2, btn3, btn4]
            for i, btn in enumerate(btns):
                self.grid.addWidget(btn, 0, i+1)


        offset = self.grid.rowCount()
        for iRow, trgCanvas in enumerate(trgCanvases):
            iRow += offset
            assert isinstance(trgCanvas, MapCanvas)

            if isinstance(trgCanvas, MapCanvas):
                label = QLabel(trgCanvas.name())
                trgCanvas.sigNameChanged.connect(label.setText)

            elif isinstance(trgCanvas, QgsMapCanvas):
                import qgis.utils
                if isinstance(qgis.utils.iface, QgisInterface) and \
                   isinstance(qgis.utils.iface.mapCanvas(), QgsMapCanvas):
                    label = QLabel('QGIS Map Canvas')



            self.grid.addWidget(label, iRow, 0)
            btnDict = {}
            for iCol, linkType in enumerate(CanvasLinkDialog.LINK_TYPES):
                btn = QToolButton(self)
                btn.setObjectName('btn{}{}_{}'.format(srcCanvas.name(), trgCanvas.name(), linkType).replace(' ','_'))
                a = CanvasLink.linkAction(srcCanvas, trgCanvas, linkType)
                assert isinstance(a, QAction)
                a.setCheckable(True)
                a.triggered.connect(self.updateLinkSelection)
                btn.setDefaultAction(a)
                self.grid.addWidget(btn, iRow, iCol+1)
                btnDict[linkType] = btn

            self.mWidgetLUT[trgCanvas] = btnDict

            if iRow == 0:
                self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), iRow, iCol+1)
        self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), self.grid.rowCount(), 0)

        self.updateLinkSelection()

    def linkToAll(self, linkType):
        src = self.currentSourceCanvas()
        for trg in self.currentTargetCanvases():
            CanvasLink.linkMapCanvases(src, trg, linkType)
        self.updateLinkSelection()

    def updateLinkSelection(self, *args):
        srcCanvas = self.currentSourceCanvas()
        assert isinstance(srcCanvas, MapCanvas)

        targetCanvases = self.mWidgetLUT.keys()
        for targetCanvas in targetCanvases:
            link = CanvasLink.between(srcCanvas, targetCanvas)
            if isinstance(link, CanvasLink):
                linkType = link.linkType
            else:
                linkType = UNLINK

            if linkType not in self.mWidgetLUT[targetCanvas].keys():
                s = ""

            for btnLinkType, btn in self.mWidgetLUT[targetCanvas].items():

                assert isinstance(btn, QToolButton)
                a = btn.defaultAction()
                a.setChecked(linkType == btnLinkType)






    def onButtonPressed(self, btnList, srcCanvas, targetCanvas, linkType):
        sender = self.sender()
        CanvasLink.linkMapCanvases(srcCanvas, targetCanvas, linkType)

        for btn in btnList:
            assert isinstance(btn, QToolButton)
            if btn == sender:
                s = ""
                #todo: highlight activated function
            else:
                s  =""
                #todo: de-highlight activated function




    pass





class CanvasLinkTargetWidget(QFrame):




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

        for linkType  in [LINK_ON_CENTER_SCALE, LINK_ON_SCALE, LINK_ON_CENTER]:
            bt = QToolButton(self)
            bt.setDefaultAction(CanvasLink.linkAction(self.canvas1, self.canvas2, linkType))
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
            CanvasLink.RemoveMapLinkTargetWidgets(True)
            ev.accept()



class CanvasLink(QObject):
    """
    A CanvasLink describes how two MapCanvas are linked to each other.
    """
    LINKTYPES = [LINK_ON_SCALE, LINK_ON_CENTER, LINK_ON_CENTER_SCALE]
    LINK_ON_SCALE = LINK_ON_SCALE
    LINK_ON_CENTER = LINK_ON_CENTER
    LINK_ON_CENTER_SCALE = LINK_ON_CENTER_SCALE
    UNLINK = UNLINK
    GLOBAL_LINK_LOCK = False

    @staticmethod
    def ShowMapLinkTargets(mapDockOrMapCanvas):
        if isinstance(mapDockOrMapCanvas, MapDock):
            mapDockOrMapCanvas = mapDockOrMapCanvas.mCanvas
        assert isinstance(mapDockOrMapCanvas, QgsMapCanvas)

        canvas1 = mapDockOrMapCanvas
        assert isinstance(canvas1, QgsMapCanvas)
        CanvasLink.RemoveMapLinkTargetWidgets(True)

        for canvas_source in MapCanvas.instances():
            if canvas_source != canvas1:
                w = CanvasLinkTargetWidget(canvas1, canvas_source)
                w.setAutoFillBackground(False)
                w.show()
                CanvasLink.LINK_TARGET_WIDGETS.add(w)
                #canvas_source.freeze()
            s = ""

        s = ""

    @staticmethod
    def linkMapCanvases(canvas1, canvas2, linktype):
        """
        Use this function to link or unlink two MapCanvases
        :param canvas1: MapCanvas
        :param canvas2: MapCanvas
        :param linktype: str

        """
        from enmapbox.gui.mapcanvas import CanvasLink
        if linktype in [UNLINK, None]:
            CanvasLink.unlinkMapCanvases(canvas1, canvas2)
        else:
            CanvasLink(canvas1, canvas2, linktype)

        CanvasLink.RemoveMapLinkTargetWidgets()

    @staticmethod
    def unlinkMapCanvases(canvas1, canvas2):
        if isinstance(canvas1, MapCanvas):
            canvas1.removeCanvasLink(canvas2)
        if isinstance(canvas2, MapCanvas):
            canvas2.removeCanvasLink(canvas1)
        CanvasLink.RemoveMapLinkTargetWidgets()

    @staticmethod
    def RemoveMapLinkTargetWidgets(processEvents=True):
        for w in list(CanvasLink.LINK_TARGET_WIDGETS):
            CanvasLink.LINK_TARGET_WIDGETS.remove(w)
            p = w.parent()
            w.hide()
            del(w)
            p.refresh()
            p.update()

        if processEvents:
            #qApp.processEvents()
            QCoreApplication.instance().processEvents()



    @staticmethod
    def resetLinkLock():
        CanvasLink.GLOBAL_LINK_LOCK = False

    @staticmethod
    def linkAction(canvas1, canvas2, linkType):
        """
        Create a QAction object with icon and description to be used in UIs
        :param linkType: see [LINK_ON_SCALE, LINK_ON_CENTER, LINK_ON_CENTER_SCALE]
        :return: QAction
        """
        assert linkType in [LINK_ON_SCALE, LINK_ON_CENTER, LINK_ON_CENTER_SCALE, UNLINK]

        if linkType == LINK_ON_CENTER:
            a = QAction('Link map center', None)
            a.setIcon(QIcon(':/enmapbox/icons/link_center.svg'))
            a.setToolTip('Link map center')
        elif linkType == LINK_ON_SCALE:
            a = QAction('Link map scale ("Zoom")', None)
            a.setIcon(QIcon(':/enmapbox/icons/link_mapscale.svg'))
            a.setToolTip('Link to scale between both maps')
        elif linkType == LINK_ON_CENTER_SCALE:
            a = QAction('Link map scale and center', None)
            a.setToolTip('Link map scale and center')
            a.setIcon(QIcon(':/enmapbox/icons/link_mapscale_center.svg'))
        elif linkType == UNLINK:
            a = QAction('Unlink', None)
            a.setToolTip('Removes an existing link between both canvases')
            a.setIcon(QIcon(':/enmapbox/icons/link_open.svg'))
        else:
            raise Exception('Unknown link type : {}'.format(linkType))

        if isinstance(canvas1, QgsMapCanvas) and isinstance(canvas2, QgsMapCanvas):
            a.triggered.connect(lambda : CanvasLink.linkMapCanvases(canvas1, canvas2, linkType))
        return a

    LINK_TARGET_WIDGETS = set()

    def __init__(self, canvas1, canvas2, linkType):
        super(CanvasLink, self).__init__()
        assert linkType in CanvasLink.LINKTYPES, linkType
        assert isinstance(canvas1, MapCanvas)
        assert isinstance(canvas2, MapCanvas)
        assert canvas1 != canvas2

        if linkType == UNLINK:
            CanvasLink.unlinkMapCanvases(canvas1, canvas2)
        else:

            self.linkType = linkType
            self.canvases = [canvas1, canvas2]

            canvas1.addCanvasLink(self)
            canvas2.addCanvasLink(self)

            self.applyTo(canvas2)

    def removeMe(self):
        """Call this to remove this think from both canvases."""
        self.canvases[0].removeCanvasLink(self)

    @staticmethod
    def existsBetween(canvas1, canvas2):
        return CanvasLink.between(canvas1, canvas2) is not None

    @staticmethod
    def between(canvas1, canvas2):
        if not (isinstance(canvas1, QgsMapCanvas) and isinstance(canvas2, QgsMapCanvas)):
            return False
        links = []
        if isinstance(canvas1, MapCanvas):
            links.extend([l for l in canvas1.canvasLinks if l.containsCanvas(canvas2)])
        if isinstance(canvas2, MapCanvas):
            links.extend([l for l in canvas2.canvasLinks if l.containsCanvas(canvas1)])

        links = list(set(links))
        l = len(links)
        if l > 1:
            raise Exception('More than two CanvasLinks between {} and {}'.format(canvas1, canvas2))
        if l == 1:
            return links[0]
        return None

    @staticmethod
    def applyLinking(initialSrcCanvas):
        """
        Applies all link actions related to MapCanvas "initialSrcCanvas"
        :param initialSrcCanvas: MapCanvas
        """
        if CanvasLink.GLOBAL_LINK_LOCK:
            #do not disturb ongoing linking by starting a new one
            return
        else:
            CanvasLink.GLOBAL_LINK_LOCK = True
            QTimer.singleShot(500, lambda: CanvasLink.resetLinkLock())

            #G0(A) -> G1(B) -> G3(E)
            #      -> G1(C) -> G3(A)
            #               -> G3(E)
            #Gx = Generation. G1 will be set before G2,...
            #A,B,..,E = MapCanvas Instances
            #Order of linking starting from A: B,C,E
            #Note: G3(A) will be not set, as A is already handled (initial signal)
            #      G3(E) receives link from G1(B) only.
            #      change related signals in-between will be blocked by GLOBAL_LINK_LOCK


            handledCanvases = [initialSrcCanvas]

            def nextLinkGeneration(srcCanvases:list):
                nonlocal handledCanvases

                generations = dict()
                for srcCanvas in srcCanvases:
                    assert isinstance(srcCanvas, MapCanvas)
                    linksToApply = []
                    for link in srcCanvas.canvasLinks:
                        assert isinstance(link, CanvasLink)
                        dstCanvas = link.theOtherCanvas(srcCanvas)
                        if dstCanvas not in handledCanvases:
                            linksToApply.append(link)
                    if len(linksToApply) > 0:
                        generations[srcCanvas] = linksToApply
                return generations

            nextGenerations = nextLinkGeneration(handledCanvases)

            while len(nextGenerations) > 0:
                #get the links that have to be set for the next generation
                assert isinstance(nextGenerations, dict)
                for srcCanvas, links in nextGenerations.items():
                    assert isinstance(srcCanvas, MapCanvas)
                    assert isinstance(links, list)

                    for link in links:
                        dstCanvas = link.theOtherCanvas(srcCanvas)
                        assert dstCanvas not in handledCanvases
                        assert dstCanvas == link.apply(srcCanvas, dstCanvas)
                        handledCanvases.append(dstCanvas)
                nextGenerations.clear()
                nextGenerations.update(nextLinkGeneration(handledCanvases))

            CanvasLink.GLOBAL_LINK_LOCK = False


    @staticmethod
    def depr_applyLinking(initialSrcCanvas):
        if CanvasLink.GLOBAL_LINK_LOCK:
            # do not disturb ongoing linking by starting a new one
            return
        else:
            CanvasLink.GLOBAL_LINK_LOCK = True
            QTimer.singleShot(500, lambda: CanvasLink.resetLinkLock())

            # G0(A) -> G1(B) -> G3(E)
            #      -> G1(C) -> G3(A)
            #               -> G3(E)
            # Gx = Generation. G1 will be set before G2,...
            # A,B,..,E = MapCanvas Instances
            # Order of linking starting from A: B,C,E
            # Note: G3(A) will be not set, as A is already handled (initial signal)
            #      G3(E) receives link from G1(B) only.
            #      change related signals in-between will be blocked by GLOBAL_LINK_LOCK

            handledCanvases = [initialSrcCanvas]

            def filterNextGenerationLinks(srcCanvas):
                linkList = []
                for link in srcCanvas.canvasLinks:
                    dstCanvas = link.theOtherCanvas(srcCanvas)
                    if dstCanvas not in handledCanvases:
                        linkList.append(link)
                return srcCanvas, linkList

            def removeEmptyEntries(nextGen):
                return [pair for pair in nextGen if len(pair[1]) > 0]

            nextGeneration = removeEmptyEntries([filterNextGenerationLinks(initialSrcCanvas)])

            while len(nextGeneration) > 0:
                # get the links that have to be set for the next generation
                _nextGeneration = []
                for item in nextGeneration:
                    srcCanvas, links = item

                    # apply links
                    srcExt = SpatialExtent.fromMapCanvas(srcCanvas)
                    for link in links:
                        dstCanvas = link.theOtherCanvas(srcCanvas)
                        if dstCanvas not in handledCanvases:
                            assert dstCanvas == link.apply(srcCanvas, dstCanvas)
                            handledCanvases.append(dstCanvas)

                    _nextGeneration.extend([filterNextGenerationLinks(srcCanvas)])
                nextGeneration = removeEmptyEntries(_nextGeneration)


    def containsCanvas(self, canvas):
        return canvas in self.canvases

    def theOtherCanvas(self, canvas):
        assert canvas in self.canvases
        assert len(self.canvases) == 2
        return self.canvases[1] if canvas == self.canvases[0] else self.canvases[0]

    def unlink(self):
        for canvas in self.canvases:
            canvas.removeCanvasLink(self)

    def icon(self):

        if self.linkType == LINK_ON_SCALE:
            src = ":/enmapbox/icons/link_mapscale.svg"
        elif self.linkType == LINK_ON_CENTER:
            src = ":/enmapbox/icons/link_center.svg"
        elif self.linkType == LINK_ON_CENTER_SCALE:
            src = ":/enmapbox/icons/link_mapscale_center.svg"
        elif self.linkType == UNLINK:
            src = ":/enmapbox/icons/link_open.svg"
        else:
            raise NotImplementedError('unknown link type: {}'.format(self.linkType))

        return QIcon(src)

    def apply(self, srcCanvas:QgsMapCanvas, dstCanvas:QgsMapCanvas):
        assert isinstance(srcCanvas, QgsMapCanvas)
        assert isinstance(dstCanvas, QgsMapCanvas)

        srcExt = SpatialExtent.fromMapCanvas(srcCanvas)

        # original center and extent
        centerO = SpatialPoint.fromMapCanvasCenter(dstCanvas)
        extentO = SpatialExtent.fromMapCanvas(dstCanvas)

        # transform (T) to target CRS
        dstCrs = dstCanvas.mapSettings().destinationCrs()
        extentT = srcExt.toCrs(dstCrs)
        centerT = SpatialPoint(srcExt.crs(), srcExt.center())

        w, h = srcCanvas.width(), srcCanvas.height()
        if w == 0:
            w = max([10, dstCanvas.width()])
        if h == 0:
            h = max([10, dstCanvas.height()])

        mapUnitsPerPx_x = extentT.width() / w
        mapUnitsPerPx_y = extentT.height() / h

        scaledWidth = mapUnitsPerPx_x * dstCanvas.width()
        scaledHeight = mapUnitsPerPx_y * dstCanvas.height()
        scaledBox = SpatialExtent(dstCrs, scaledWidth, scaledHeight).setCenter(centerO)

        if self.linkType == LINK_ON_CENTER:
            dstCanvas.setCenter(centerT)

        elif self.linkType == LINK_ON_SCALE:
            dstCanvas.zoomToFeatureExtent(scaledBox)

        elif self.linkType == LINK_ON_CENTER_SCALE:
            dstCanvas.zoomToFeatureExtent(extentT)

        else:
            raise NotImplementedError()

        s = ""

        return dstCanvas

    def applyTo(self, canvasTo):
        assert isinstance(canvasTo, QgsMapCanvas)
        canvasFrom = self.theOtherCanvas(canvasTo)
        return self.apply(canvasFrom, canvasTo)



    def isSameCanvasPair(self, canvasLink):
        """
        Returns True if canvasLink contains the same canvases
        :param canvasLink:
        :return:
        """
        assert isinstance(canvasLink, CanvasLink)
        return self.canvases[0] in canvasLink.canvases and \
               self.canvases[1] in canvasLink.canvases


    def __eq__(self, canvasLink):
        if not isinstance(canvasLink, CanvasLink):
            return False
        return self.isSameCanvasPair(canvasLink)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        cs = list(self.canvases)
        return 'CanvasLink "{}" {} <-> {}'.format(self.linkType, cs[0], cs[1])

class MapCanvas(QgsMapCanvas):

    from weakref import WeakSet
    _instances = WeakSet()
    @staticmethod
    def instances():
        return list(MapCanvas._instances)

    #sigContextMenuEvent = pyqtSignal(QContextMe7nuEvent)
    sigSpatialExtentChanged = pyqtSignal(SpatialExtent)
    sigCrsChanged  = pyqtSignal(QgsCoordinateReferenceSystem)

    sigLayersRemoved = pyqtSignal(list)
    sigLayersAdded = pyqtSignal(list)

    sigNameChanged = pyqtSignal(str)
    sigCanvasLinkAdded = pyqtSignal(CanvasLink)
    sigCanvasLinkRemoved = pyqtSignal(CanvasLink)
    sigCanvasClicked = pyqtSignal()

    _cnt = 0


    def __init__(self, parent=None):
        super(MapCanvas, self).__init__(parent=parent)
        #KeepRefs.__init__(self)
        #from enmapbox.gui.docks import MapDock
        #assert isinstance(parentMapDock, MapDock)

        self._id = 'MapCanvas.#{}'.format(MapCanvas._cnt)
        self.mName = self._id

        MapCanvas._cnt += 1
        self.mCrsExtentInitialized = False
        #self.mapdock = parentMapDock
        #self.enmapbox = self.mapdock.enmapbox
        self.acceptDrops()


        self.mCrosshairItem = CrosshairMapCanvasItem(self)

        self.setShowCrosshair(False)

        self.canvasLinks = []
        # register signals to react on changes
        self.scaleChanged.connect(self.onScaleChanged)
        self.extentsChanged.connect(self.onExtentsChanged)


        self.destinationCrsChanged.connect(lambda : self.sigCrsChanged.emit(self.mapSettings().destinationCrs()))
        #activate default map tool
        self.setMapTool(QgsMapToolPan(self))
        self.mMapMouseEvent = None
        MapCanvas._instances.add(self)


    def mousePressEvent(self, event:QMouseEvent):
        #print('MapCanvas::mousePressEvent')
        b = event.button() == Qt.LeftButton
        super(MapCanvas, self).mousePressEvent(event)
        if b:
            pointXY = self.mapSettings().mapToPixel().toMapCoordinates(event.x(), event.y())
            self.mCrosshairItem.setPosition(pointXY)
            self.sigCanvasClicked.emit()

    def mouseMoveEvent(self, event):
        self.mMapMouseEvent = QgsMapMouseEvent(self,event)
        return super(MapCanvas, self).mouseMoveEvent(event)

    def refresh(self, force=False):

        self.setRenderFlag(True)
        if self.renderFlag() or force:
            super(MapCanvas, self).refresh()
            #super(MapCanvas, self).refreshAllLayers()

    def contextMenu(self):
        """
        Create a context menu for common MapCanvas operations
        :return: QMenu
        """
        menu = QMenu()

        action = menu.addAction('Link with other maps')
        action.setIcon(QIcon(':/enmapbox/icons/link_basic.svg'))
        action.triggered.connect(lambda: CanvasLink.ShowMapLinkTargets(self))
        action = menu.addAction('Remove links to other maps')
        action.setIcon(QIcon(':/enmapbox/icons/link_open.svg'))
        action.triggered.connect(lambda: self.removeAllCanvasLinks())

        qgisApp = qgisAppQgisInterface()
        b = isinstance(qgisApp, QgisInterface)
        menu.addSeparator()
        action = menu.addAction('Use QGIS map center')
        action.setEnabled(b)
        if b: action.triggered.connect(lambda : self.setCenter(SpatialPoint.fromMapCanvasCenter(qgisApp.mapCanvas())))


        action = menu.addAction('Set QGIS map center')
        action.setEnabled(b)
        if b: action.triggered.connect(lambda: qgisApp.mapCanvas().setCenter(self.spatialCenter().toCrs(qgisApp.mapCanvas().mapSettings().destinationCrs())))


        action = menu.addAction('Use QGIS map extent')
        action.setEnabled(b)
        if b: action.triggered.connect(lambda: self.setExtent(SpatialExtent.fromMapCanvas(qgisApp.mapCanvas())))


        action = menu.addAction('Set QGIS map extent')
        action.setEnabled(b)
        if b: action.triggered.connect(lambda: qgisApp.mapCanvas().setExtent(self.spatialExtent().toCrs(qgisApp.mapCanvas().mapSettings().destinationCrs())))


        menu.addSeparator()

        if self.crosshairIsVisible():
            action = menu.addAction('Hide Crosshair')
            action.triggered.connect(lambda : self.setShowCrosshair(False))
        else:
            action = menu.addAction('Show Crosshair')
            action.triggered.connect(lambda: self.setShowCrosshair(True))

        from enmapbox.gui.crosshair import CrosshairDialog
        action = menu.addAction('Set Crosshair Style')
        action.triggered.connect(lambda : self.setCrosshairStyle(
            CrosshairDialog.getCrosshairStyle(
                crosshairStyle=self.crosshairStyle(), mapCanvas=self
            )
        ))

        menu.addSeparator()

        action = menu.addAction('Zoom Full')
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomFullExtent.svg'))
        action.triggered.connect(lambda: self.setExtent(self.fullExtent()))

        action = menu.addAction('Zoom Native Resolution')
        action.setIcon(QIcon(':/enmapbox/icons/mActionZoomActual.svg'))
        action.triggered.connect(lambda: self.setExtent(self.fullExtent()))

        menu.addSeparator()

        m = menu.addMenu('Save to...')
        action = m.addAction('PNG')
        action.triggered.connect(lambda: self.saveMapImageDialog('PNG'))
        action = m.addAction('JPEG')
        action.triggered.connect(lambda: self.saveMapImageDialog('JPG'))
        action = m.addAction('Clipboard')
        action.triggered.connect(lambda: QApplication.clipboard().setPixmap(self.pixmap()))
        action = menu.addAction('Copy layer paths')
        action.triggered.connect(lambda: QApplication.clipboard().setText('\n'.join(self.layerPaths())))

        menu.addSeparator()

        action = menu.addAction('Refresh')
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.svg"))
        action.triggered.connect(lambda: self.refresh())


        action = menu.addAction('Refresh all layers')
        action.setIcon(QIcon(":/enmapbox/icons/mActionRefresh.svg"))
        action.triggered.connect(lambda: self.refreshAllLayers())


        menu.addSeparator()

        action = menu.addAction('Clear map')
        action.triggered.connect(lambda: self.setLayers([]))

        menu.addSeparator()
        action = menu.addAction('Set CRS...')
        action.triggered.connect(self.setCRSfromDialog)

        return menu

    def layerPaths(self):
        """
        Returns the paths/URIs of presented QgsMapLayers
        :return:
        """
        return [l.source() for l in self.layers()]

    def pixmap(self):
        """
        Returns the current map image as pixmap
        :return: QPixmap
        """
        #deprectated
        #return QPixmap(self.map().contentImage().copy())
        return QPixmap.grabWidget(self)

    def saveMapImageDialog(self, fileType):
        from enmapbox.gui import settings
        lastDir = settings.value('EMB_SAVE_IMG_DIR', os.path.expanduser('~'))
        path = jp(lastDir, 'screenshot.{}'.format(fileType.lower()))

        path = QFileDialog.getSaveFileName(self, 'Save map as {}'.format(fileType), path)

        if len(path) > 0:
            self.saveAsImage(path, None, fileType)
            settings.setValue('EMB_SAVE_IMG_DIR', os.path.dirname(path))


    def setCRSfromDialog(self, *args):
        setMapCanvasCRSfromDialog(self)

    def setCrosshairStyle(self, crosshairStyle:CrosshairStyle):
        """
        Sets the crosshair style
        :param crosshairStyle: CrosshairStyle
        """
        if isinstance(crosshairStyle, CrosshairStyle):
            self.mCrosshairItem.setCrosshairStyle(crosshairStyle)

    def crosshairStyle(self):
        return self.mCrosshairItem.crosshairStyle

    def setShowCrosshair(self,b):
        self.mCrosshairItem.setShow(b)

    def crosshairIsVisible(self):
        return self.mCrosshairItem.mShow

    def onScaleChanged(self, scale):
        CanvasLink.applyLinking(self)
        pass



    def onExtentsChanged(self):

        CanvasLink.applyLinking(self)
        self.sigSpatialExtentChanged.emit(SpatialExtent.fromMapCanvas(self))

    def zoomToFeatureExtent(self, spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        self.setExtent(spatialExtent)

    def moveCenterToPoint(self, spatialPoint):
        assert isinstance(spatialPoint, SpatialPoint)


    def setName(self, name):
        assert isinstance(name, str)
        old = self.mName
        self.mName = name

        if old != self.mName:
            self.sigNameChanged.emit(self.mName)

    def name(self):
        return self.mName

    def zoomToPixelScale(self):
        unitsPxX = []
        unitsPxY = []
        for lyr in self.layers():
            if isinstance(lyr, QgsRasterLayer):
                unitsPxX.append(lyr.rasterUnitsPerPixelX())
                unitsPxY.append(lyr.rasterUnitsPerPixelY())

        if len(unitsPxX) > 0:
            unitsPxX = np.asarray(unitsPxX)
            unitsPxY = np.asarray(unitsPxY)
            if True:
                # zoom to largest pixel size
                i = np.nanargmax(unitsPxX)
            else:
                # zoom to smallest pixel size
                i = np.nanargmin(unitsPxX)
            unitsPxX = unitsPxX[i]
            unitsPxY = unitsPxY[i]
            f = 0.2
            width = f * self.size().width() * unitsPxX  # width in map units
            height = f * self.size().height() * unitsPxY  # height in map units

            center = SpatialPoint.fromMapCanvasCenter(self.canvas)
            extent = SpatialExtent(center.crs(), 0, 0, width, height)
            extent.setCenter(center, center.crs())
            self.setExtent(extent)
        s = ""

    def __repr__(self):
        return self._id

    #forward to MapDock
    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        assert isinstance(mimeData, QMimeData)



        # check mime types we can handle
        assert isinstance(event, QDragEnterEvent)

        if MDF_DATASOURCETREEMODELDATA in mimeData.formats() or \
            MDF_URILIST in mimeData.formats() or \
            MDF_LAYERTREEMODELDATA in mimeData.formats():
            event.setDropAction(Qt.CopyAction)  # copy but do not remove
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event:QDropEvent):
        """

        :param event: QDropEvent
        """

        mimeData = event.mimeData()
        assert isinstance(mimeData, QMimeData)

        #add map layers
        mapLayers = extractMapLayers(mimeData)

        if len(mapLayers) > 0:
            self.setLayers(mapLayers + self.layers())
            event.accept()
            event.acceptProposedAction()

    def contextMenuEvent(self, event):

        menu = self.contextMenu()
        menu.exec_(event.globalPos())

        #self.sigContextMenuEvent.emit(event)

    def setExtent(self, rectangle):
        """
        Sets the map extent
        :param rectangle: QgsRectangle or SpatialExtent (CRS differences will be considered)
        """
        if isinstance(rectangle, SpatialExtent):
            rectangle = rectangle.toCrs(self.mapSettings().destinationCrs())
            #rectangle = QgsRectangle(rectangle)
        super(MapCanvas, self).setExtent(rectangle)
        self.setRenderFlag(True)

    def spatialExtent(self)->SpatialExtent:
        """
        Returns the map extent as SpatialExtent (extent + CRS)
        :return: SpatialExtent
        """
        return SpatialExtent.fromMapCanvas(self)

    def spatialCenter(self)->SpatialPoint:
        """
        Returns the map center as SpatialPoint (QgsPointXY + CRS)
        :return: SpatialPoint
        """
        return SpatialPoint.fromMapCanvasCenter(self)

    def setLayerSet(self, *arg, **kwds):
        raise Exception('Deprecated: Not supported any more (QGIS 3)')


    def createCanvasLink(self, otherCanvas:QgsMapCanvas, linkType):
        assert isinstance(otherCanvas, MapCanvas)
        return self.addCanvasLink(CanvasLink(self, otherCanvas, linkType))

    def addCanvasLink(self, canvasLink:CanvasLink):
        assert isinstance(canvasLink, CanvasLink)
        toRemove = [cLink for cLink in self.canvasLinks if cLink.isSameCanvasPair(canvasLink)]
        for cLink in toRemove:
            self.removeCanvasLink(cLink)
        self.canvasLinks.append(canvasLink)
        self.sigCanvasLinkAdded.emit(canvasLink)
        return canvasLink

    def removeCanvasLink(self, canvasLink):
        """
        Removes the link to another canvas
        :param canvasLink: CanvasLink or QgsMapCanvas that might be connect to this MapCanvas.
        """
        if isinstance(canvasLink, QgsMapCanvas):
            toRemove  = [l for l in self.canvasLinks if l.containsCanvas(canvasLink)]
            for cl in toRemove:
                self.removeCanvasLink(cl)

        if canvasLink in self.canvasLinks:
            self.canvasLinks.remove(canvasLink)
            self.sigCanvasLinkRemoved.emit(canvasLink)

    def removeAllCanvasLinks(self):
        toRemove = self.canvasLinks[:]
        for cLink in toRemove:
            for canvas in cLink.canvases:
                canvas.removeCanvasLink(cLink)

    def setLayers(self, mapLayers):
        """
        Sets the list of mapLayers to show in the map canvas
        :param mapLayers: QgsMapLayer or [list-of-QgsMapLayers]
        :return: self
        """
        if not isinstance(mapLayers, list):
            mapLayers = [mapLayers]
        for l in mapLayers:
            assert isinstance(l, QgsMapLayer)

        lastSet = self.layers()
        newSet = mapLayers[:]

        #register not-registered layers
        #reg = QgsProject.instance()
        #reg.addMapLayers(newSet)
        from enmapbox import EnMAPBox

        #register map layers (required for drawing on a MapCanvas)
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            store = EnMAPBox.instance().mapLayerStore()
        else:
            store = QgsProject.instance()
        store.addMapLayers(newSet)

        super(MapCanvas,self).setLayers(newSet)

        if not self.mCrsExtentInitialized and len(newSet) > 0:
            # set canvas to first layer's CRS and full extent
            newExtent = SpatialExtent.fromLayer(newSet[0])
            self.setDestinationCrs(newExtent.crs())
            self.setExtent(newExtent)

            self.mCrsExtentInitialized = True
        self.setRenderFlag(True)
        self.refreshAllLayers()

        #signal what has been added, what has been removed
        removedLayers = [l for l in lastSet if l not in newSet]
        addedLayers = [l for l in newSet if l not in lastSet]

        if len(removedLayers) > 0:
            self.sigLayersRemoved.emit(removedLayers)
        if len(addedLayers) > 0:
            self.sigLayersAdded.emit(addedLayers)
        return self


from enmapbox.gui.docks import Dock, DockLabel
class MapDockLabel(DockLabel):

    def __init__(self, *args, **kwds):

        super(MapDockLabel, self).__init__(*args, **kwds)


        self.addMapLink = QToolButton(self)
        self.addMapLink.setToolTip('Link with other map(s)')
        self.addMapLink.setIcon(QIcon(':/enmapbox/icons/link_basic.svg'))
        self.buttons.append(self.addMapLink)

        self.removeMapLink = QToolButton(self)
        self.removeMapLink.setToolTip('Remove links to this map')
        self.removeMapLink.setIcon(QIcon(':/enmapbox/icons/link_open.svg'))
        self.buttons.append(self.removeMapLink)


def setMapCanvasCRSfromDialog(mapCanvas, crs=None):
    assert isinstance(mapCanvas, QgsMapCanvas)
    w  = QgsProjectionSelectionWidget(mapCanvas)
    if crs is None:
        crs = mapCanvas.mapSettings().destinationCrs()
    else:
        crs = QgsCoordinateReferenceSystem(crs)
    # set current CRS
    w.setCrs(crs)

    lyrs = mapCanvas.layers()
    if len(lyrs) > 0:
        w.setLayerCrs(lyrs[0].crs())

    w.crsChanged.connect(mapCanvas.setDestinationCrs)
    w.selectCrs()
    return w


class MapDock(Dock):
    """
    A dock to visualize geodata that can be mapped
    """
    #sigCursorLocationValueRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    from enmapbox.gui.utils import SpatialPoint, SpatialExtent
    #sigCursorLocationRequest = pyqtSignal(SpatialPoint)
    #sigSpectrumRequest = pyqtSignal(SpatialPoint)
    sigLayersAdded = pyqtSignal(list)
    sigLayersRemoved = pyqtSignal(list)
    sigCrsChanged = pyqtSignal(QgsCoordinateReferenceSystem)

    def __init__(self, *args, **kwds):
        initSrc = kwds.pop('initSrc', None)
        super(MapDock, self).__init__(*args, **kwds)
        self.mBaseName = self.title()

        #self.actionLinkExtent = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Link to map extent', self)
        #self.actionLinkCenter = QAction(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_CommandLink), 'Linkt to map center', self)
        #self.label.buttons.append(self.actionLinkCenter.getButton())

        self.mCanvas = MapCanvas(self)
        self.mCanvas.setName(self.title())
        self.mCanvas.sigNameChanged.connect(self.setTitle)
        self.sigTitleChanged.connect(self.mCanvas.setName)
        #self.label.setText(self.basename)
        #self.canvas.setScaleLocked(True)
        #self.canvas.customContextMenuRequested.connect(self.onCanvasContextMenuEvent)
        #self.canvas.sigContextMenuEvent.connect(self.onCanvasContextMenuEvent)
        self.mCanvas.sigLayersAdded.connect(self.sigLayersAdded.emit)
        self.mCanvas.sigLayersRemoved.connect(self.sigLayersRemoved.emit)
        self.mCanvas.sigCrsChanged.connect(self.sigCrsChanged.emit)

        settings = QSettings()
        assert isinstance(self.mCanvas, QgsMapCanvas)
        self.mCanvas.setCanvasColor(Qt.black)
        self.mCanvas.enableAntiAliasing(settings.value('/qgis/enable_anti_aliasing', False, type=bool))
        #self.canvas.useImageToRender(settings.value('/qgis/use_image_to_render', False, type=bool))
        self.layout.addWidget(self.mCanvas)

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


        self.label.addMapLink.clicked.connect(lambda:CanvasLink.ShowMapLinkTargets(self))
        self.label.removeMapLink.clicked.connect(lambda: self.mCanvas.removeAllCanvasLinks())

        if initSrc is not None:
            from enmapbox.gui.datasources import DataSourceFactory
            dataSources = DataSourceFactory.Factory(initSrc)
            lyrs = [ds.createUnregisteredMapLayer() for ds in dataSources]
            if len(lyrs) > 0:
                self.mCanvas.setLayers(lyrs)

    def cursorLocationValueRequest(self,*args):
        self.sigCursorLocationRequest.emit(*args)

    def contextMenu(self)->QMenu:
        m = super(MapDock, self).contextMenu()
        from enmapbox.gui.utils import appendItemsToMenu

        return appendItemsToMenu(m, self.mCanvas.contextMenu())

    def _createLabel(self, *args, **kwds)->MapDockLabel:
        return MapDockLabel(self, *args, **kwds)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                s = ""
        else:
            super(MapDock, self).mousePressEvent(event)

    def linkWithMapDock(self, mapDock, linkType):
        assert isinstance(mapDock, MapDock)
        self.linkWithCanvas(mapDock.mCanvas, linkType)


    def linkWithCanvas(self, canvas, linkType):
        assert isinstance(canvas, QgsMapCanvas)
        canvas.createCanvasLink(canvas, linkType)



    def layers(self)->list:
        return self.mCanvas.layers()

    def setLayers(self, mapLayers):
        assert isinstance(mapLayers, list)
        self.mCanvas.setLayers(mapLayers)


    def addLayers(self, mapLayers):
        if not type(mapLayers) is list:
            mapLayers = [mapLayers]
        for l in mapLayers:
            assert isinstance(l, QgsMapLayer)
        self.setLayers(mapLayers + self.mCanvas.layers())

    def removeLayersByURI(self, uri):
        to_remove = []
        uri = os.path.abspath(uri)

        for lyr in self.mCanvas.layers():
            lyrUri = os.path.abspath(lyr.dataProvider().dataSourceUri())
            if uri == lyrUri:
                to_remove.append(lyr)

        self.removeLayers(to_remove)

    def mapCanvas(self)->MapCanvas:
        return self.mCanvas

    def removeLayers(self, mapLayers):
        newSet = [l for l in self.mCanvas.layers() if l not in mapLayers]
        self.setLayers(newSet)

