# -*- coding: utf-8 -*-

"""
***************************************************************************
    imagestatisticsapp/imagestatistics.py

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
from __future__ import absolute_import, unicode_literals
from enmapbox.gui.enmapboxgui import EnMAPBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from osgeo import gdal
import ogr
import unicodedata
import pyqtgraph
#from imagestatisticsapp import APP_DIR

from hubflow.types import *
from pyqtgraph.Qt import QtCore, QtGui
from enmapbox.gui.enmapboxgui import EnMAPBox

#BJ: es gibt immer nur eine QApplication. Zur Laufzeit ist das die von QGiS.
#  Daher sollte das nie eine Modul-Variable sein
#app = QtGui.QApplication([])

def u2s(s):
    if isinstance(s, unicode):
        try:
            s = str(s)
        except:
            try:
                s = s.encode('utf-8')
            except:
                s = unicodedata.normalize('NFKD', s).encode('utf-8', 'ignore')
    return s


class Win(QtGui.QDialog):

    approximateGrid = 100.0

    def __init__(self, parent=None):
        super(Win, self).__init__(parent=parent)
        self.initLayout()

    def initLayout(self):
        self.setLayout(QtGui.QGridLayout())
        layout = self.layout()

        ########## Init layout elements
        # Select input file name
        self.inputFile = QComboBox()
        self.inputFile.currentIndexChanged.connect(lambda: self.comboIndexChanged())

        self.selectInputFile = QPushButton('...')
        self.selectInputFile.clicked.connect(lambda: self.fileFound())

        self.inputMask = QComboBox()
        self.inputMask.currentIndexChanged.connect(lambda: self.maskIndexChanged())

        self.selectMaskFile = QPushButton('...')
        self.selectMaskFile.clicked.connect(lambda: self.maskFound())

        self.approximateStats = QCheckBox("Calculate approximate statistics")

        self.computebtn = QPushButton("  Compute Statistics")
        #self.computebtn.setIcon(QIcon(os.path.join(APP_DIR, 'raster-stats.png')))
        self.computebtn.clicked.connect(lambda: self.computeStats())

        self.selectionTable = QtGui.QTableWidget()
        self.selectionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.selectionTable.setMinimumSize(0, 300)

        self.switchHistogramView = QPushButton("  Histograms for selected rows")
        #self.switchHistogramView.setIcon(QIcon(os.path.join(APP_DIR, 'histogram.png')))
        self.switchHistogramView.clicked.connect(lambda: self.showHistograms())

        self.container = QSplitter(Qt.Horizontal)
        self.container.setMinimumSize(300,300)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setMinimumSize(0, 300)
        self.splitterH = QSplitter(Qt.Horizontal)

        # Add layout elements to layout
        layout.addWidget(QtGui.QLabel("Select raster file and calculate statistics."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(QtGui.QLabel("Select raster or vector mask (optional)."), 2, 0, 1, 8)
        layout.addWidget(self.inputMask, 3, 0, 1, 6)
        layout.addWidget(self.selectMaskFile, 3, 6, 1, 2)
        layout.addWidget(self.approximateStats, 4, 0, 1, 8)
        layout.addWidget(self.computebtn, 5, 0, 1, 2)
        layout.addWidget(QtGui.QLabel("Select rows to compute statistics and display histograms"), 6, 0, 1, 8)
        layout.addWidget(self.selectionTable, 7, 0, 1, 8)
        layout.addWidget(self.switchHistogramView, 8,0 ,1 , 2)
        layout.addWidget(self.container, 9, 0, 1, 8)

        self.resize(600,800)

        enmapBox = EnMAPBox.instance()
        if isinstance(enmapBox, EnMAPBox):
            #print("enmapbox found")
            for src in sorted(enmapBox.dataSources('RASTER')):
                #print("raster found")
                self.addSrcRaster(src)

    # Retrieves open raster files from enmap box
    def addSrcRaster(self, src):
        addedItems = [self.inputFile.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile.count())]
        if src not in addedItems:
            #bn = os.path.basename(src)
            self.inputFile.addItem(src)
        self.validatePath(src)

    # opens file search dialogue
    def fileFound(self):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image', directory = "/Workspaces/QGIS-Plugins/enmap-box/enmapboxtestdata"))
        counter = self.inputFile.count()
        self.inputFile.setCurrentIndex(counter - 1)

    def maskFound(self):
        self.inputMask.addItem(QFileDialog.getOpenFileName(self, 'Mask',
                                                               directory="/Workspaces/QGIS-Plugins/enmap-box/enmapboxtestdata"))
        counter = self.inputMask.count()
        self.inputMask.setCurrentIndex(counter - 1)

    def comboIndexChanged(self):
        if self.validatePath(self.inputFile.currentText()):
            self.selectionTable.clear()

            self.inDS = gdal.Open(self.inputFile.currentText())

            self.selectionTable.setRowCount(self.inDS.RasterCount)
            self.selectionTable.setColumnCount(4) # Samples, Min , Max, Mean, Stdev

            rowlabels = []
            for index in range(self.inDS.RasterCount):
                rowlabels.append(self.inDS.GetRasterBand(index+1).GetDescription())

            self.selectionTable.setVerticalHeaderLabels(rowlabels)  # Name, Samples, Min , Max, Mean, Stdev
            self.selectionTable.setHorizontalHeaderLabels(["Samples", "Min", "Max", "Mean"])#, "Stand. Dev."]) # Name, Samples, Min , Max, Mean, Stdev

    def maskIndexChanged(self):
        self.validatePath(self.inputMask.currentText())

    def clearHistograms(self):

        for i in range(0, self.container.count()):
            self.container.widget(i).deleteLater()

        #for i in range(0, self.splitterH.count()):
        #    self.splitterH.widget(i).deleteLater()

    def showHistograms(self):
        self.clearHistograms()

        #gdal.TranslateOptions()

        self.bandlegend = QVBoxLayout()
        overlapHist = pyqtgraph.PlotWidget()
        overlapHist.setMinimumSize(500,300)

        heightCounter = 0

        # sort selected rows
        allRows = []
        for s in range(0, len(self.selectionTable.selectionModel().selectedRows())):
           allRows.append(self.selectionTable.selectionModel().selectedRows()[s].row())

        sortedRows = sorted(allRows)

        # create histogram plots and legend
        for j in range(0, len(sortedRows)):
            data = numpy.array(self.inDS.GetRasterBand(sortedRows[j] + 1).ReadAsArray())
            currentColor = pyqtgraph.intColor(j * 20 + j, 100, alpha = 120)

            y, x = numpy.histogram(data, bins = 100)
            overlapHist.plot(x, y, stepMode=True, fillLevel=0, brush= currentColor)

            self.legendWrapper = QWidget()
            self.legendWrapper.setMinimumSize(50,50)

            bandcolorbox = QGraphicsView()
            bandcolorbox.setMaximumSize(20,20)
            bandcolorbox.setMinimumSize(20,20)
            p = bandcolorbox.palette()
            p.setColor(bandcolorbox.backgroundRole(), currentColor)
            bandcolorbox.setPalette(p)

            legendWidget = QSplitter(Qt.Horizontal)
            legendWidget.addWidget(bandcolorbox)

            lab = QLabel(self.inDS.GetRasterBand(sortedRows[j] + 1).GetDescription())
            lab.setMaximumSize(200,20)
            legendWidget.addWidget(lab)

            self.bandlegend.addWidget(legendWidget)

            heightCounter += 1

        self.bandlegend.addStretch(0)

        self.legendWrapper.setMaximumHeight(heightCounter * 30)
        self.legendWrapper.setLayout(self.bandlegend)

        self.legendScroll = QScrollArea()
        self.legendScroll.setWidget(self.legendWrapper)
        self.legendScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container.addWidget(overlapHist)
        self.container.addWidget(self.legendScroll)

    def computeStats(self):

        image = Image(filename=u2s(self.inDS.GetFileList()[0]))

        pathMask = self.inputMask.currentText()
        if os.path.isfile(pathMask) and gdal.Open(pathMask):
            mask = Mask(filename=pathMask)
        elif os.path.isfile(pathMask) and ogr.Open(pathMask):
            mask = Vector(filename=pathMask)
        else:
            mask = None

        # band table
        bandIndices = []
        for index in range(0, len(self.selectionTable.selectedIndexes()) / self.selectionTable.columnCount()): # /5, since 1 index = 1 cell. we want nbr of rows, not cells
            bandIndices.append(self.selectionTable.selectionModel().selectedRows()[index].row())
            bandInd = self.selectionTable.selectionModel().selectedRows()[index].row()

            # adapt resolution dynamically so that the selection contains 100x100 samples
            if self.approximateStats.isChecked():
                xRes = (self.inDS.RasterXSize/self.approximateGrid) * self.inDS.GetGeoTransform()[1]
                yRes = self.inDS.RasterYSize/self.approximateGrid * self.inDS.GetGeoTransform()[5]*-1
                if(xRes < self.inDS.GetGeoTransform()[1]):
                    xRes = self.inDS.GetGeoTransform()[1]
                if(yRes < self.inDS.GetGeoTransform()[5]*-1):
                    yRes = self.inDS.GetGeoTransform()[5]*-1

                grid = image.pixelGrid.newResolution(xRes=xRes, yRes=yRes)
                min, max, mean, n = image.basicStatistics(bandIndicies=[bandInd], mask=mask, grid = grid)  # , controls=controls)
            else:
                min, max, mean, n = image.basicStatistics(bandIndicies=[bandInd], mask=mask)  # , controls=controls)

            wid1 = QLabel(str(n[0]))
            wid1.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid2 = QLabel(str(min[0]))
            wid2.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid3 = QLabel(str(max[0]))
            wid3.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid4 = QLabel(str(mean[0]))
            wid4.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self.selectionTable.setCellWidget(bandInd, 0, wid1) # Samples
            self.selectionTable.setCellWidget(bandInd, 1, wid2) # Min
            self.selectionTable.setCellWidget(bandInd, 2, wid3) # Max
            self.selectionTable.setCellWidget(bandInd, 3, wid4) # Mean

    def applyStats(operator):
        img = operator.getArray('in')
        s = img.statistics()

        return s

    def validatePath(self, dataset, *args, **kwds):
        from osgeo import gdal

        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.inputFile:
            path = self.inputFile.currentText()

            ds = gdal.Open(path)

            if ds is None:
                style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                self.inputFile.setStyleSheet(style)
                result = False
            else:
                style = 'QComboBox {{ }}'.format(hexGreen)
                self.inputFile.setStyleSheet(style)

            return result

        if sender == self.inputMask:
            path = self.inputMask.currentText()

            ds = gdal.Open(str(path))
            vs = ogr.Open(str(path))

            if ds is None and vs is None:
                style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                self.inputMask.setStyleSheet(style)
                result = False
            else:
                style = 'QComboBox {{ }}'.format(hexGreen)
                self.inputMask.setStyleSheet(style)

            return result

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    #from enmapboxtestdata import enmap
    #assert os.path.isfile(enmap)
    w = Win()
    w.setWindowFlags(w.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
    #w.inputFile.addItem(enmap)
    w.show()
    app.exec_()