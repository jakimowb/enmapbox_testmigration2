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
        QScrollArea
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

        # scroll area widget contents - layout
        self.scrollLayout = QtGui.QFormLayout()

        # scroll area widget contents
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        layout.addWidget(QtGui.QLabel("Select file and calculate statistics."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile, 1, 6, 1, 2)
        layout.addWidget(self.bandList, 2, 0, 3, 8)
        layout.addWidget(self.approximateStats, 5, 0, 1, 8)
        layout.addWidget(self.computebtn, 6, 0, 1, 8)
        layout.addWidget(self.scrollArea, 7, 0, 1, 8)

        self.resize(600,600)

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

            for index in range(1, self.inDS.RasterCount):
                self.bandList.addItem(self.inDS.GetRasterBand(index).GetDescription())

    def computeStats(self):

        self.clearLayout(self.scrollLayout)

        stats = []
        for index in range(0, len(self.bandList.selectedIndexes())):
            stats.append(Stats(self.inDS, index, self.approximateStats.isChecked())) # index, apprximate y/n

        for jndex in range(0, len(stats)):
            self.scrollLayout.addWidget(stats[jndex])

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def save(self):
        global state
        state = self.p.saveState()

    def restore(self):
        global state
        #add = self.p['Save/Restore functionality', 'Restore State', 'Add missing items']
        #rem = self.p['Save/Restore functionality', 'Restore State', 'Remove extra items']
        #self.ndv.getParameter().sigValueChanged.disconnect()
        self.p.restoreState(state) #, addChildren=add, removeChildren=rem)
        self.ndv.getParameter().sigValueChanged.connect(lambda param, data: self.ndvChanged(0, data))

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