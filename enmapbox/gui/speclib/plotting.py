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
from pyqtgraph.widgets.PlotWidget import PlotWidget
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from enmapbox.gui.plotstyling import PlotStyle, PlotStyleDialog, MARKERSYMBOLS2QGIS_SYMBOLS, createSetPlotStyleAction
from enmapbox.gui.plotstyling import EDITOR_WIDGET_REGISTRY_KEY as PlotSettingsEditorWidgetKey
from .spectrallibraries import SpectralProfile, SpectralLibrary, FIELD_FID, FIELD_STYLE, FIELD_VALUES, FIELD_NAME, MIMEDATA_SPECLIB_LINK

class SpectralLibraryPlotWidget(PlotWidget):
    """
    A widget to PlotWidget SpectralProfiles
    """

    def __init__(self, parent=None):
        super(SpectralLibraryPlotWidget, self).__init__(parent)
        self.mSpeclib = None
        self.mPlotDataItems = dict()
        self.setAntialiasing(True)
        self.setAcceptDrops(True)
        self.mMaxProfiles = 256
        self.mPlotOverlayItems = []



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




    def setSpeclib(self, speclib:SpectralLibrary):
        """
        Sets the SpectralLibrary to be visualized
        :param speclib: SpectralLibrary
        """
        assert isinstance(speclib, SpectralLibrary)
        #self.plotItem.clear()
        #self.plotItem.clearPlots()

        for i in  self.plotItem.items:
            self.plotItem.removeItem(i)
        self.mPlotDataItems.clear()

        self.mSpeclib = speclib

        self.mSpeclib.featureAdded.connect(self.onProfilesAdded)
        self.mSpeclib.featuresDeleted.connect(self.onProfilesRemoved)
        self.mSpeclib.selectionChanged.connect(self.onSelectionChanged)
        self.mSpeclib.attributeValueChanged.connect(self.onAttributeChanged)
        self.updatePlot()


        #self.mModel.rowsAboutToBeRemoved.connect(self.onRowsAboutToBeRemoved)
        #self.mModel.rowsInserted.connect(self.onRowsInserted)
        #self.mModel.dataChanged.connect(self.onDataChanged)
        #if self.mModel.rowCount() > 0:
        #    self.onRowsInserted(self.mModel.index(0,0), 0, self.mModel.rowCount())

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
        self.updateProfiles(self.mSpeclib.profiles())

        i = 0
        b = self.plotItem.blockSignals(True)
        for id, pdi in self.mPlotDataItems.items():
            i+= 1
            if i > self.mMaxProfiles:
                break

            self.plotItem.addItem(pdi)
        self.plotItem.blockSignals(b)

    def updateProfiles(self, listOfProfiles):

        for profile in listOfProfiles:
            assert isinstance(profile, SpectralProfile)
            id = profile.id()
            if id in self.mPlotDataItems.keys():
                pdi = self.mPlotDataItems[id]
                pdi.setStyle(profile.style())
            else:
                self.mPlotDataItems[profile.id()] = SpectralProfilePlotDataItem(profile)

    def speclib(self)->SpectralLibrary:
        """
        :return: SpectralLibrary
        """
        return self.mSpeclib

    def onProfilesAdded(self, fids):

        self.updatePlot()

        return
        if len(features) == 0:
            return

        speclib = self.speclib()
        assert isinstance(speclib, SpectralLibrary)

        fids = [f.id() for f in features]
        #remove if existent
        self.onProfilesRemoved(layerID, fids)

        pdis = []
        for feature in features:
            profile = SpectralProfile.fromSpecLibFeature(feature)
            assert isinstance(profile, SpectralProfile)
            pdi = SpectralProfilePlotDataItem(profile)
            self.mPlotItems[pdi.mProfile.id()] = pdi
            pdis.append(pdi)

        for pdi in pdis:
            self.plotItem.addItem(pdi)


    def onProfilesRemoved(self, fids):

        if len(fids) == 0:
            return
        fids = [fid for fid in fids if fid in list(self.mPlotDataItems.keys())]
        pdis = [self.mPlotDataItems[fid] for fid in fids]
        pdis = [pdi for pdi in pdis if isinstance(pdi, SpectralProfilePlotDataItem)]
        for pdi in pdis:
            self.removeItem(pdi)

        pdis = [self.mPlotDataItems.pop(fid) for fid in fids]

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




class SpectralProfilePlotDataItem(PlotDataItem):

    def __init__(self, spectralProfile:SpectralProfile):
        assert isinstance(spectralProfile, SpectralProfile)
        super(SpectralProfilePlotDataItem, self).__init__()
        #self.mProfile = spectralProfile
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

    def setClickable(self, b:bool, width=None):
        assert isinstance(b, bool)
        self.curve.setClickable(b, width=width)

    def setSelected(self, b:bool):
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


    def setColor(self, color):
        if not isinstance(color, QColor):
            color = QColor(color)
        self.setPen(color)

    def pen(self):
        return mkPen(self.opts['pen'])

    def color(self):
        return self.pen().color()

    def setLineWidth(self, width):
        pen = mkPen(self.opts['pen'])
        assert isinstance(pen, QPen)
        pen.setWidth(width)
        self.setPen(pen)

