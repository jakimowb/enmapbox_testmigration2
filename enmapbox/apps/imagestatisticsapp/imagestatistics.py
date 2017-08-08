# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types

"""

#import initExample ## Add path to library (just for examples; you do not need this)

from qgis.gui import QgsFileWidget, QgsRasterFormatSaveOptionsWidget

import os

#import pyqtgraph as pg
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph

from osgeo import osr
from hub.gdal.api import *

import multiprocessing as mp

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from enmapbox.gui.enmapboxgui import EnMAPBox

import time

class Stats(QWidget):
    def __init__(self, inDS, index, approximate, *args, **kwds):
        super(Stats, self).__init__(*args, **kwds)

        stats = inDS.GetRasterBand(index + 1).ComputeStatistics(approximate, False)
        print(inDS.GetRasterBand(index + 1).ComputeStatistics(approximate, False))

        statLayout = QVBoxLayout()

        label = QLabel(str(inDS.GetRasterBand(index + 1).GetDescription()))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        statLayout.addWidget(label)
        statLayout.addWidget(QLabel("Samples: " + str(inDS.RasterXSize * inDS.RasterYSize)))
        statLayout.addWidget(QLabel("Mean: " + str(stats[2])))
        statLayout.addWidget(QLabel("Standard Deviation: " + str(stats[3])))
        statLayout.addWidget(QLabel("Min: " + str(stats[0]) + " Max: " + str(stats[1])))

        data = numpy.array(inDS.GetRasterBand(index + 1).ReadAsArray())
        img = pyqtgraph.ImageItem()
        img.setImage(data)

        histWidget = pyqtgraph.HistogramLUTWidget(None, img)
        histWidget.plot.rotate(-90)
        histWidget.vb.setMouseEnabled(x=True, y=True)
        histWidget.vb.setMaximumWidth(1000)

        statLayout.addWidget(histWidget)

        self.setLayout(statLayout)


class Win(QtGui.QDialog):

    inDS = None

    start = None
    emd = None

    def __init__(self, parent=None):
        super(Win, self).__init__(parent=parent)
        self.setLayout(QtGui.QGridLayout())
        layout = self.layout()

        #self.t.setWindowTitle('imagestatistics')
        #QScrollArea
        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        self.inputFile = QComboBox()
        self.inputFile.currentIndexChanged.connect(
            lambda: self.comboIndexChanged()
        )

        self.selectInputFile = QPushButton('...')
        self.selectInputFile.clicked.connect(
            lambda: self.fileFound(self.inputFile)
        )

        self.bandList = QListWidget()
        self.bandList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.approximateStats = QCheckBox("Calculate approximate statistics")

        self.computebtn = QPushButton("Compute Statistics")
        self.computebtn.clicked.connect(
            lambda: self.computeStats()
        )

        self.selectionTable = QtGui.QTableWidget()
        self.selectionTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        # scroll area widget contents - layout
        self.scrollLayout = QtGui.QFormLayout()

        # scroll area widget contents
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        self.switchHistogramView = QPushButton("Show/Update Histograms")
        self.switchHistogramView.clicked.connect(
            lambda: self.showHistograms()
        )

        self.splitter = QSplitter()


        layout.addWidget(QtGui.QLabel("Select file and calculate statistics."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(self.bandList, 2, 0, 3, 8)
        layout.addWidget(self.approximateStats, 5, 0, 1, 8)
        layout.addWidget(self.computebtn, 6, 0, 1, 8)
        layout.addWidget(self.scrollArea, 7, 0, 1, 8)

        layout.addWidget(self.selectionTable, 8 ,0 ,1 , 8)
        layout.addWidget(self.switchHistogramView, 9 ,0 ,1 , 8)
        layout.addWidget(self.splitter, 10, 0, 1, 8)

        self.resize(600,800)

        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            print("enmapbox found")
            for src in sorted(enmapBox.dataSources('RASTER')):
                print("raster found")
                self.addSrcRaster(src)

    def addSrcRaster(self, src):
        addedItems = [self.inputFile.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile.count())]
        if src not in addedItems: #hasClassification(src) and src not in addedItems:
            bn = os.path.basename(src)
            self.inputFile.addItem(src) #(bn, src)
        self.validatePath(src)

    def fileFound(self, inputFile):
        self.inputFile.addItem(QFileDialog.getOpenFileName(self, 'Input image', directory = "/Workspaces/QGIS-Plugins/enmap-box/enmapbox/testdata"))
        counter = self.inputFile.count()
        self.inputFile.setCurrentIndex(counter - 1)

    def comboIndexChanged(self):
        if self.validatePath(str(self.inputFile.currentText())):
            self.inDS = gdal.Open(str(self.inputFile.currentText()))

            self.selectionTable.setRowCount(self.inDS.RasterCount - 1)
            self.selectionTable.setColumnCount(5) # Samples, Min , Max, Mean, Stdev

            self.selectionTable.setHorizontalHeaderLabels(["Samples", "Min", "Max", "Mean", "Stand. Dev."]) # Name, Samples, Min , Max, Mean, Stdev

            rowlabels = []

            for index in range(1, self.inDS.RasterCount):
                rowlabels.append(self.inDS.GetRasterBand(index).GetDescription())
                self.bandList.addItem(self.inDS.GetRasterBand(index).GetDescription())

            self.selectionTable.setVerticalHeaderLabels(rowlabels)  # Name, Samples, Min , Max, Mean, Stdev

    def clearHistograms(self):
        for i in range(0, self.splitter.count()):
            self.splitter.widget(i).deleteLater()

    def showHistograms(self):
        self.clearHistograms()
        if len(self.selectionTable.selectionModel().selectedRows()) < 4:
            for j in range(0, len(self.selectionTable.selectionModel().selectedRows())):
                if self.selectionTable.selectionModel().selectedRows()[j]:
                    data = numpy.array(self.inDS.GetRasterBand(self.selectionTable.selectionModel().selectedRows()[j].row() + 1).ReadAsArray())

                    # histogram through np.plot
                    y, x = numpy.histogram(data)
                    win = pyqtgraph.GraphicsWindow()
                    plt1 = win.addPlot()
                    win.setMinimumSize(200,200)
                    plt1.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))

                    splitterV = QSplitter(Qt.Vertical)
                    splitterV.addWidget(QLabel(self.inDS.GetRasterBand(self.selectionTable.selectionModel().selectedRows()[0].row() + 1).GetDescription()))
                    splitterV.addWidget(win)
                    self.splitter.addWidget(splitterV)

    def computeStats(self):

        self.clearLayout(self.scrollLayout)

        # band list
        stats = []
        for index in range(0, len(self.bandList.selectedIndexes())):
            stats.append(Stats(self.inDS, self.bandList.selectedIndexes()[index].row(), self.approximateStats.isChecked())) # index, apprximate y/n

        for jndex in range(0, len(stats)):
            self.scrollLayout.addWidget(stats[jndex])

        # band table
        for index in range(0, len(self.selectionTable.selectedIndexes()) / 5): # /5, since 1 index = 1 cell. we want nbr of rows, not cells
            #print(self.selectionTable.selectionModel().selectedRows()[index].row())

            bandInd = self.selectionTable.selectionModel().selectedRows()[index].row()
            stats = self.inDS.GetRasterBand(bandInd + 1).ComputeStatistics(self.approximateStats.isChecked(), False)

            #item = QTableWidgetItem(QLabel(str(self.inDS.RasterXSize * self.inDS.RasterYSize)))
            wid = QLabel(str(self.inDS.RasterXSize * self.inDS.RasterYSize))
            wid.setTextInteractionFlags(Qt.TextSelectableByMouse)


            #self.selectionTable.setItem(bandInd, 0, QTableWidgetItem(str(self.inDS.RasterXSize * self.inDS.RasterYSize), 0)) # Samples
            #self.selectionTable.setItem(bandInd, 0, item) # Samples
            self.selectionTable.setCellWidget(bandInd, 0, wid) # Samples
            self.selectionTable.setItem(bandInd, 1, QTableWidgetItem(str(stats[0]), 0)) # Min
            self.selectionTable.setItem(bandInd, 2, QTableWidgetItem(str(stats[1]), 0)) # Max
            self.selectionTable.setItem(bandInd, 3, QTableWidgetItem(str(stats[2]), 0)) # Mean
            self.selectionTable.setItem(bandInd, 4, QTableWidgetItem(str(stats[3]), 0)) # Stdev

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def validatePath(self, dataset, *args, **kwds):
        print("File List")
        print(dataset)
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True
        if sender == self.inputFile:
            path = self.inputFile.currentText()
            #print(path)
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