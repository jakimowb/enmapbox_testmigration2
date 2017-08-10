# -*- coding: utf-8 -*-

"""
***************************************************************************
    imagestatisticsapp/imagestatistics.py

    Integratation of metadata editor into EnMAP-Box.
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

from qgis.gui import QgsFileWidget, QgsRasterFormatSaveOptionsWidget

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph
from hub.gdal.api import *
from enmapbox.gui.enmapboxgui import EnMAPBox

from hubdc.applier import Applier

app = QtGui.QApplication([])

class Win(QtGui.QDialog):

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
        self.selectInputFile.clicked.connect(lambda: self.fileFound(self.inputFile))

        self.approximateStats = QCheckBox("Calculate approximate statistics")

        self.computebtn = QPushButton("Compute Statistics")
        self.computebtn.clicked.connect(lambda: self.computeStats())

        self.infoLabel = QLabel("Select rows to compute statistics and display histograms")

        self.selectionTable = QtGui.QTableWidget()
        self.selectionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.selectionTable.setMinimumSize(0, 300)
        self.selectionTable.setMaximumHeight(500)

        self.switchHistogramView = QPushButton("Show/Update Histograms")
        self.switchHistogramView.clicked.connect(lambda: self.showHistograms())

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setMinimumSize(0, 300)

        self.splitterH = QSplitter(Qt.Horizontal)

        # Add layout elements to layout
        layout.addWidget(QtGui.QLabel("Select raster file and calculate statistics."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(self.approximateStats, 2, 0, 1, 8)
        layout.addWidget(self.computebtn, 3, 0, 1, 8)
        layout.addWidget(self.infoLabel, 4, 0, 1, 8)
        layout.addWidget(self.selectionTable, 5, 0, 1, 8)
        layout.addWidget(self.switchHistogramView, 6,0 ,1 , 8)
        layout.addWidget(self.splitter, 7, 0, 1, 8)

        self.resize(600,800)

        enmapBox = EnMAPBox.instance()
        if isinstance(enmapBox, EnMAPBox):
            print("enmapbox found")
            for src in sorted(enmapBox.dataSources('RASTER')):
                print("raster found")
                self.addSrcRaster(src)

    # Retrieves open raster files from enmap box
    def addSrcRaster(self, src):
        addedItems = [self.inputFile.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile.count())]
        if src not in addedItems: #hasClassification(src) and src not in addedItems:
            bn = os.path.basename(src)
            self.inputFile.addItem(src) #(bn, src)
        self.validatePath(src)

    # opens file search dialogue
    def fileFound(self, inputFile):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image', directory = "/Workspaces/QGIS-Plugins/enmap-box/enmapbox/testdata"))
        counter = self.inputFile.count()
        self.inputFile.setCurrentIndex(counter - 1)

    def comboIndexChanged(self):
        if self.validatePath(str(self.inputFile.currentText())):
            self.inDS = gdal.Open(str(self.inputFile.currentText()))

            self.selectionTable.setRowCount(self.inDS.RasterCount - 1)
            self.selectionTable.setColumnCount(5) # Samples, Min , Max, Mean, Stdev

            rowlabels = []
            for index in range(1, self.inDS.RasterCount):
                rowlabels.append(self.inDS.GetRasterBand(index).GetDescription())

            self.selectionTable.setVerticalHeaderLabels(rowlabels)  # Name, Samples, Min , Max, Mean, Stdev
            self.selectionTable.setHorizontalHeaderLabels(["Samples", "Min", "Max", "Mean", "Stand. Dev."]) # Name, Samples, Min , Max, Mean, Stdev

    def clearHistograms(self):
        if self.splitter.widget(0):
            self.splitter.widget(0).deleteLater() # delete synchronize box

        for i in range(0, self.splitterH.count()):
            self.splitterH.widget(i).deleteLater()

    def showHistograms(self):
        self.clearHistograms()

        plotSplitters = []

        gdal.TranslateOptions()
        self.synchronize = QCheckBox("Synchronize Histograms")
        self.splitter.addWidget(self.synchronize)

        for j in range(0, len(self.selectionTable.selectionModel().selectedRows())):
            # display a maximum of 3 histograms
            if j >=3:
                break

            if self.selectionTable.selectionModel().selectedRows()[j]:
                data = numpy.array(self.inDS.GetRasterBand(self.selectionTable.selectionModel().selectedRows()[j].row() + 1).ReadAsArray())

                # histogram through np.plot
                y, x = numpy.histogram(data)
                wid = pyqtgraph.PlotWidget()
                wid.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
                wid.sigRangeChanged.connect(self.onSigRangeChanged)

                splitterV = QSplitter(Qt.Vertical)
                splitterV.addWidget(QLabel(self.inDS.GetRasterBand(self.selectionTable.selectionModel().selectedRows()[j].row() + 1).GetDescription()))
                splitterV.addWidget(wid)
                plotSplitters.append(splitterV)


        for s in range(0, len(plotSplitters)):
            self.splitterH.addWidget(plotSplitters[s])

        self.splitter.addWidget(self.splitterH)

    def onSigRangeChanged(self, r):
        if self.synchronize.isChecked():
            for t in range(0, len(self.splitterH)):
                if r != self.splitterH.widget(t).widget(1):
                    self.splitterH.widget(t).widget(1).sigRangeChanged.disconnect(self.onSigRangeChanged)
                    self.splitterH.widget(t).widget(1).setRange(xRange=r.getAxis('bottom').range, padding = 0.0)
                    self.splitterH.widget(t).widget(1).setRange(yRange=r.getAxis('left').range, padding = 0.0)
                    self.splitterH.widget(t).widget(1).sigRangeChanged.connect(self.onSigRangeChanged)

    def computeStats(self):

        # band table
        for index in range(0, len(self.selectionTable.selectedIndexes()) / 5): # /5, since 1 index = 1 cell. we want nbr of rows, not cells
            bandInd = self.selectionTable.selectionModel().selectedRows()[index].row()

            applier = Applier()

            applier.setInput('in', filename=self.inDS.GetRasterBand(bandInd + 1))
            #applier.setOutput('out', filename=r'c:\output\out.tif')
            stats2 = applier.apply(operator=self.applyStats)
            print(stats2)

            stats = self.inDS.GetRasterBand(bandInd + 1).ComputeStatistics(self.approximateStats.isChecked(), False)

            #item = QTableWidgetItem(QLabel(str(self.inDS.RasterXSize * self.inDS.RasterYSize)))
            wid1 = QLabel(str(self.inDS.RasterXSize * self.inDS.RasterYSize))
            wid1.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid2 = QLabel(str(stats[0]))
            wid2.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid3 = QLabel(str(stats[1]))
            wid3.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid4 = QLabel(str(stats[2]))
            wid4.setTextInteractionFlags(Qt.TextSelectableByMouse)
            wid5 = QLabel(str(stats[3]))
            wid5.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self.selectionTable.setCellWidget(bandInd, 0, wid1) # Samples
            self.selectionTable.setCellWidget(bandInd, 1, wid2) # Min
            self.selectionTable.setCellWidget(bandInd, 2, wid3) # Max
            self.selectionTable.setCellWidget(bandInd, 3, wid4) # Mean
            self.selectionTable.setCellWidget(bandInd, 4, wid5) # Stdev

    def applyStats(operator):
        img = operator.getArray('in')
        s = img.statistics()

        return s

    def validatePath(self, dataset, *args, **kwds):
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.inputFile:
            path = self.inputFile.currentText()

            from osgeo import gdal
            ds = gdal.Open(str(path))

            if ds is None:
                style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                self.inputFile.setStyleSheet(style)
                result = False
            else:
                style = 'QComboBox {{ }}'.format(hexGreen)
                self.inputFile.setStyleSheet(style)

            return result

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        w = Win()
        w.show()
        app.exec_()