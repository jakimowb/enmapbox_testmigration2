# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    plotting.py
    Functionality to plot SpectralLibraries
    ---------------------
    Date                 : Okt 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This file is part of the EnMAP-Box.                                   *
*                                                                         *
*   The EnMAP-Box is free software; you can redistribute it and/or modify *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   The EnMAP-Box is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with the EnMAP-Box. If not, see <http://www.gnu.org/licenses/>. *
*                                                                         *
***************************************************************************
"""
import sys, re, os
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from pyqtgraph.functions import mkPen
import pyqtgraph as pg
from pyqtgraph.widgets.PlotWidget import PlotWidget
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from enmapbox.gui.plotstyling import PlotStyle, PlotStyleDialog, MARKERSYMBOLS2QGIS_SYMBOLS, createSetPlotStyleAction
from enmapbox.gui.plotstyling import EDITOR_WIDGET_REGISTRY_KEY as PlotSettingsEditorWidgetKey
from .spectrallibraries import SpectralProfile, SpectralLibrary, FIELD_FID, FIELD_STYLE, FIELD_VALUES, FIELD_NAME, MIMEDATA_SPECLIB_LINK



class SpectralXAxis(pg.AxisItem):

    def __init__(self, *args, **kwds):
        super(SpectralXAxis, self).__init__(*args, **kwds)
        self.setRange(1,3000)
        self.enableAutoSIPrefix(True)
        self.labelAngle = 0



class SpectralLibraryPlotWidget(pg.PlotWidget):
    """
    A widget to PlotWidget SpectralProfiles
    """

    def __init__(self, parent=None):
        super(SpectralLibraryPlotWidget, self).__init__(parent)

        self.plotItem = pg.PlotItem(
            axisItems={'bottom': SpectralXAxis(orientation='bottom')}
            , viewBox=SpectralViewBox()
        )

        self.setCentralItem(self.plotItem)


        pi = self.getPlotItem()
        assert isinstance(pi, pg.PlotItem) and pi == self.plotItem
        pi.getAxis('bottom').setLabel('X (Bands)')
        pi.getAxis('left').setLabel('Y (Spectral Value)')
        self.mSpeclib = None
        self.mPlotDataItems = dict()
        self.setAntialiasing(True)
        self.setAcceptDrops(True)
        self.mMaxProfiles = 256
        self.mPlotOverlayItems = []

        self.setBackground(QColor('black'))
        self.mInfoColor = QColor('yellow')
        self.mCrosshairLineV = pg.InfiniteLine(angle=90, movable=False)
        self.mCrosshairLineH = pg.InfiniteLine(angle=0, movable=False)
        self.mInfoLabelCursor = pg.TextItem(text='<cursor position>', anchor=(1.0, 0.0))
        self.mInfoLabelCursor.setColor(self.mInfoColor)

        self.scene().addItem(self.mInfoLabelCursor)
        self.mInfoLabelCursor.setParentItem(self.getPlotItem())

        pi.addItem(self.mCrosshairLineV, ignoreBounds=True)
        pi.addItem(self.mCrosshairLineH, ignoreBounds=True)

        self.proxy2D = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self.onMouseMoved2D)


    def onMouseMoved2D(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple

        plotItem = self.getPlotItem()
        if plotItem.sceneBoundingRect().contains(pos):
            vb = plotItem.vb
            assert isinstance(vb, SpectralViewBox)
            mousePoint = vb.mapSceneToView(pos)
            x = mousePoint.x()
            if x >= 0:
                y = mousePoint.y()
                vb.updateCurrentPosition(x, y)
                self.mInfoLabelCursor.setText('x:{:0.5f}\ny:{:0.5f}'.format(x, y), color=self.mInfoColor)

                s = self.size()
                pos = QPointF(s.width(), 0)
                self.mInfoLabelCursor.setVisible(vb.mActionShowCursorValues.isChecked())
                self.mInfoLabelCursor.setPos(pos)

                b = vb.mActionShowCrosshair.isChecked()
                self.mCrosshairLineH.setVisible(b)
                self.mCrosshairLineV.setVisible(b)
                self.mCrosshairLineH.pen.setColor(self.mInfoColor)
                self.mCrosshairLineV.pen.setColor(self.mInfoColor)
                self.mCrosshairLineV.setPos(mousePoint.x())
                self.mCrosshairLineH.setPos(mousePoint.y())



    def setPlotOverlayItems(self, items):
        """
        Adds a list of PlotItems to be overlayed
        :param items:
        :return:
        """
        if not isinstance(items, list):
            items = [items]
        assert isinstance(items, list)

        for item in items:
            assert isinstance(item, PlotDataItem)

        toRemove = self.mPlotOverlayItems[:]
        for item in toRemove:
            if item in self.plotItem.items:
                item
                self.plotItem.removeItem(item)

        self.mPlotOverlayItems.clear()
        self.mPlotOverlayItems.extend(items)
        for item in items:
            self.plotItem.addItem(item)



    def _spectralProfilePDIs(self)->list:
        return [i for i in self.getPlotItem().items if isinstance(i, SpectralProfilePlotDataItem)]

    def _removeSpectralProfilePDIs(self, pdis:list):

        pi = self.getPlotItem()
        assert isinstance(pi, pg.PlotItem)

        for pdi in pdis:
            assert isinstance(pdi, SpectralProfilePlotDataItem)
            pi.removeItem(pdi)
            assert pdi not in pi.dataItems
            self.mPlotDataItems.pop(pdi.id())


    def setSpeclib(self, speclib:SpectralLibrary):
        """
        Sets the SpectralLibrary to be visualized
        :param speclib: SpectralLibrary
        """
        assert isinstance(speclib, SpectralLibrary)
        #self.plotItem.clear()
        #self.plotItem.clearPlots()
        self._removeSpectralProfilePDIs(self._spectralProfilePDIs())
        self.mSpeclib = speclib

        self.mSpeclib.featureAdded.connect(self.onProfilesAdded)
        self.mSpeclib.featuresDeleted.connect(self.onProfilesRemoved)
        self.mSpeclib.selectionChanged.connect(self.onSelectionChanged)
        self.mSpeclib.attributeValueChanged.connect(self.onAttributeChanged)

        self.onProfilesAdded(self.speclib().allFeatureIds())

        self.updatePlot()

    def onAttributeChanged(self, fid, idx, value):

        name = self.mSpeclib.fields()[idx].name()
        if name == FIELD_STYLE:
            style = PlotStyle.fromJSON(value)
            if isinstance(style, PlotStyle) and fid in self.mPlotDataItems:
                pdi = self.mPlotDataItems[fid]
                pdi.setStyle(style)

    def onSelectionChanged(self, selected, deselected):

        for pdi in self.plotItem.items:
            if isinstance(pdi, SpectralProfilePlotDataItem):
                w = pdi.pen().width()
                if pdi.mID in selected:
                    pdi.setSelected(True)
                elif pdi.mID in deselected:
                    pdi.setSelected(False)
        s = ""




    def updatePlot(self):
        i = 0
        #b = self.plotItem.blockSignals(True)

        pi = self.getPlotItem()
        assert isinstance(pi, pg.PlotItem)

        existing = list(self.mPlotDataItems.values())

        to_add = [i for i in existing if isinstance(i, SpectralProfilePlotDataItem) and i not in pi.dataItems]
        to_remove = [pdi for pdi in pi.dataItems if isinstance(pdi, SpectralProfilePlotDataItem) and pdi not in existing]

        for i in to_remove:
            pi.removeItem(i)

        for i in to_add:
            pi.addItem(i)

        pi.update()

    def updateProfileStyles(self, listOfProfiles:list):
        """
        Updates the styles for a set of SpectralProfilePlotDataItems
        :param listOfProfiles: [list-of-SpectralProfiles]
        """
        for profile in listOfProfiles:
            assert isinstance(profile, SpectralProfile)
            id = profile.id()
            if id in self.mPlotDataItems.keys():
                pdi = self.mPlotDataItems[id]
                pdi.setStyle(profile.style())
            else:
                pdi = SpectralProfilePlotDataItem(profile)
                pdi.setClickable(True)
                pdi.sigClicked.connect(self.onProfileClicked)
                self.mPlotDataItems[profile.id()] = pdi

    def onProfileClicked(self, pdi):

        if isinstance(pdi, SpectralProfilePlotDataItem) and pdi in self.mPlotDataItems.values():
            modifiers = QApplication.keyboardModifiers()
            speclib = self.speclib()
            assert isinstance(speclib, SpectralLibrary)
            fid = pdi.id()

            fids = speclib.selectedFeatureIds()
            if modifiers == Qt.ShiftModifier:
                if fid in fids:
                    fids.remove(fid)
                else:
                    fids.append(fid)
                speclib.selectByIds(fids)
            else:
                speclib.selectByIds([fid])


    def speclib(self)->SpectralLibrary:
        """
        :return: SpectralLibrary
        """
        return self.mSpeclib

    def onProfilesAdded(self, fids):

        profiles = self.speclib().profiles(fids=fids)
        self.updateProfileStyles(profiles)
        self.updatePlot()



    def onProfilesRemoved(self, fids):

        if len(fids) == 0:
            return
        pi = self.getPlotItem()
        assert isinstance(pi, pg.PlotItem)
        to_remove = [pdi for pdi in self._spectralProfilePDIs() if pdi.id() in fids]
        self._removeSpectralProfilePDIs(to_remove)

    def dragEnterEvent(self, event):
        assert isinstance(event, QDragEnterEvent)
        if MIMEDATA_SPECLIB_LINK in event.mimeData().formats():
            event.accept()


    def dragMoveEvent(self, event):
        if MIMEDATA_SPECLIB_LINK in event.mimeData().formats():
            event.accept()

    #if containsSpeclib(event.mimeData()):
        #    event.accept()

    def dropEvent(self, event):
        assert isinstance(event, QDropEvent)
        #log('dropEvent')
        mimeData = event.mimeData()

        speclib = SpectralLibrary.readFromMimeData(mimeData)
        if isinstance(speclib, SpectralLibrary) and len(speclib) > 0:

            slib = self.speclib()
            slib.startEditing()
            slib.addSpeclib(speclib)
            event.accept()


class SpectralViewBox(pg.ViewBox):
    """
    Subclass of ViewBox
    """
    def __init__(self, parent=None):
        """
        Constructor of the CustomViewBox
        """
        super(SpectralViewBox, self).__init__(parent)
        #self.menu = None # Override pyqtgraph ViewBoxMenu
        #self.menu = self.getMenu() # Create the menu
        #self.menu = None
        self.mXAxisUnit = 'index'
        xAction = [a for a in self.menu.actions() if a.text() == 'X Axis'][0]
        yAction = [a for a in self.menu.actions() if a.text() == 'Y Axis'][0]

        menuXAxis = self.menu.addMenu('X Axis')
        #define the widget to set X-Axis options
        frame = QFrame()
        l = QGridLayout()

        frame.setLayout(l)
        #l.addWidget(self, QWidget, int, int, alignment: Qt.Alignment = 0): not enough arguments

        self.rbXManualRange = QRadioButton('Manual')

        self.rbXAutoRange = QRadioButton('Auto')
        self.rbXAutoRange.setChecked(True)

        l.addWidget(self.rbXManualRange, 0,0)
        l.addWidget(self.rbXAutoRange, 1, 0)

        l.setMargin(1)
        l.setSpacing(1)
        frame.setMinimumSize(l.sizeHint())
        wa = QWidgetAction(menuXAxis)
        wa.setDefaultWidget(frame)
        menuXAxis.addAction(wa)

        self.menu.insertMenu(xAction, menuXAxis)
        self.menu.removeAction(xAction)

        self.mActionShowCrosshair = self.menu.addAction('Show Crosshair')
        self.mActionShowCrosshair.setCheckable(True)
        self.mActionShowCrosshair.setChecked(True)
        self.mActionShowCursorValues = self.menu.addAction('Show Mouse values')
        self.mActionShowCursorValues.setCheckable(True)
        self.mActionShowCursorValues.setChecked(True)

    sigXAxisUnitChanged = pyqtSignal(str)
    def setXAxisUnit(self, unit:str):
        old = self.mXAxisUnit
        self.mXAxisUnit = unit
        if old != self.mXAxisUnit:
            self.sigXAxisUnitChanged.emit(self.mXAxisUnit)

    def xAxisUnit(self):
        return self.mXAxisUnit


    def raiseContextMenu(self, ev):

        pt = self.mapDeviceToView(ev.pos())

        xRange, yRange = self.viewRange()

        menu = self.getMenu(ev)
        self.scene().addParentContextMenus(self, menu, ev)
        menu.exec_(ev.screenPos().toPoint())


    def updateCurrentPosition(self, x,y):
        self.mCurrentPosition = (x,y)
        pass

class SpectralProfilePlotDataItem(PlotDataItem):



    def __init__(self, spectralProfile:SpectralProfile):
        assert isinstance(spectralProfile, SpectralProfile)
        super(SpectralProfilePlotDataItem, self).__init__()

        self.mID = spectralProfile.id()
        x = spectralProfile.xValues()
        if x is not None:
            x = x[:]
        y = spectralProfile.yValues()
        if y is not None:
            y = y[:]
        self.setData(x=x, y=y)
        self.mDefaultStyle = None
        self.setStyle(spectralProfile.style())

    def id(self)->int:
        """
        Returns the profile id
        :return: int
        """
        return self.mID

    def setClickable(self, b:bool, width=None):
        """

        :param b:
        :param width:
        :return:
        """
        assert isinstance(b, bool)
        self.curve.setClickable(b, width=width)

    def setSelected(self, b:bool):
        """
        Sets if this profile should appear as "selected"
        :param b: bool
        """
        if isinstance(self.mDefaultStyle, PlotStyle):
            if b:
                self.setLineWidth(self.mDefaultStyle.linePen.width() + 3)
            else:
                self.setLineWidth(self.mDefaultStyle.linePen.width())

    def setStyle(self, style:PlotStyle):
        assert isinstance(style, PlotStyle)
        self.mDefaultStyle = style

        self.setVisible(style.isVisible())

        self.setSymbol(style.markerSymbol)
        self.setSymbolBrush(style.markerBrush)
        self.setSymbolSize(style.markerSize)
        self.setSymbolPen(style.markerPen)
        self.setPen(style.linePen)


    def setColor(self, color:QColor):
        """
        Sets the profile color
        :param color: QColor
        """
        if not isinstance(color, QColor):
            color = QColor(color)
        self.setPen(color)

    def pen(self):
        """
        Returns the QPen of the profile
        :return: QPen
        """
        return mkPen(self.opts['pen'])

    def color(self):
        """
        Returns the profile color
        :return: QColor
        """
        return self.pen().color()

    def setLineWidth(self, width):
        """
        Set the profile width in px
        :param width: int
        """
        pen = mkPen(self.opts['pen'])
        assert isinstance(pen, QPen)
        pen.setWidth(width)
        self.setPen(pen)

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.RightButton:
            if self.raiseContextMenu(ev):
                ev.accept()


    def raiseContextMenu(self, ev):
        menu = self.contextMenu()

        # Let the scene add on to the end of our context menu
        # (this is optional)
        menu = self.scene().addParentContextMenus(self, menu, ev)

        pos = ev.screenPos()
        menu.popup(QPoint(pos.x(), pos.y()))
        return True

    # This method will be called when this item's _children_ want to raise
    # a context menu that includes their parents' menus.
    def contextMenu(self, event=None):


        self.menu = QMenu()
        self.menu.setTitle(self.name + " options..")

        green = QAction("Turn green", self.menu)
        green.triggered.connect(self.setGreen)
        self.menu.addAction(green)
        self.menu.green = green

        blue = QAction("Turn blue", self.menu)
        blue.triggered.connect(self.setBlue)
        self.menu.addAction(blue)
        self.menu.green = blue

        alpha = QWidgetAction(self.menu)
        alphaSlider = QSlider()
        alphaSlider.setOrientation(Qt.Horizontal)
        alphaSlider.setMaximum(255)
        alphaSlider.setValue(255)
        alphaSlider.valueChanged.connect(self.setAlpha)
        alpha.setDefaultWidget(alphaSlider)
        self.menu.addAction(alpha)
        self.menu.alpha = alpha
        self.menu.alphaSlider = alphaSlider
        return self.menu
