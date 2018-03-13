# -*- coding: utf-8 -*-

"""
***************************************************************************
    scatterplotapp/scatterplot.py

    Package definition.
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
import gdal
import ogr
from enmapbox.gui.enmapboxgui import EnMAPBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#from enmapbox.coreapps.scatterplotapp import APP_DIR
from pyqtgraph.Qt import QtCore, QtGui

import pyqtgraph
from pyqtgraph.colormap import ColorMap
from pyqtgraph.widgets.ColorMapWidget import ColorMapParameter
from pyqtgraph.widgets.GradientWidget import GradientWidget
from hubflow.types import *

class Win(QtGui.QDialog):

    inDS1 = None
    inDS2 = None
    bins = 100
    approximateGrid = 100

    plotCol = QColor(200, 200, 200, 255)

    defaultGradientColors = numpy.array([[0, 0, 0, 255], [255, 0, 0, 255]], dtype=numpy.ubyte)

    def __init__(self, parent=None):
        super(Win, self).__init__(parent=parent)

        self.initLayout()

    def initLayout(self):
        self.setLayout(QtGui.QGridLayout())
        layout = self.layout()
        self.setMinimumWidth(600)

        # select input file name via QFileDialog in case the file is not open in the enmap box yet
        self.inputFile1 = QComboBox()
        self.inputFile1.currentIndexChanged.connect(lambda: self.comboIndexChanged1())

        self.selectInputFile1 = QPushButton('...')
        self.selectInputFile1.clicked.connect(lambda: self.fileFound(self.inputFile1))

        self.inputFile2 = QComboBox()
        self.inputFile2.currentIndexChanged.connect(lambda: self.comboIndexChanged2())

        self.selectInputFile2 = QPushButton('...')
        self.selectInputFile2.clicked.connect(lambda: self.fileFound(self.inputFile2))

        self.inputMask = QComboBox()
        self.inputMask.currentIndexChanged.connect(lambda: self.maskIndexChanged())
        # add empty slots for combobox
        self.inputMask.addItem("")

        self.selectMaskFile = QPushButton('...')
        self.selectMaskFile.clicked.connect(lambda: self.maskFound())

        self.band1 = QComboBox()
        self.band2 = QComboBox()

        self.approximateStats = QCheckBox("Use approximate statistics")

        self.scatterplot = pyqtgraph.ScatterPlotItem(pxMode=False, symbol='s')

        #self.colordiag = QColorDialog()
        self.colorbut = QPushButton()
        self.colorbut.clicked.connect(self.backgroundColorSelection)

        self.colorbutPlots = QPushButton()
        self.colorbutPlots.clicked.connect(self.plotColorSelection)

        self.scatterview = pyqtgraph.PlotWidget()
        self.scatterview.setMinimumSize(300, 300)
        self.scatterview.sigRangeChanged.connect(self.onSigRangeChanged)

        self.plotXbins = pyqtgraph.PlotWidget()
        self.plotXbins.setMaximumWidth(100)
        self.plotXbins.sigRangeChanged.connect(self.onSigRangeChanged)

        self.plotYbins = pyqtgraph.PlotWidget()
        self.plotYbins.setMaximumHeight(100)
        self.plotYbins.sigRangeChanged.connect(self.onSigRangeChanged)

        self.scatterLayout = QGridLayout()
        self.scatterLayout.addWidget(self.plotXbins, 0 ,0, 1, 1)
        self.scatterLayout.addWidget(self.plotYbins, 1 ,1 , 1, 1)
        self.scatterLayout.addWidget(self.scatterview, 0 ,1 , 1, 1)

        displaybtn = QPushButton("Compute Scatterplot")
        #displaybtn.setIcon(QIcon(os.path.join(APP_DIR, 'scatterplot.png')))
        displaybtn.clicked.connect(self.displayScatterplot)

        closebtn = QPushButton("Close")
        closebtn.clicked.connect(self.close)

        self.nbrBins = QSpinBox()
        self.nbrBins.setMaximum(1000)
        self.nbrBins.setValue(self.bins)

        self.colorStretch = QSplitter(Qt.Horizontal)

        self.colorLabels = QHBoxLayout()

        layout.addWidget(QtGui.QLabel("Select one or two raster files and create two-band-scatterplots."), 0, 0, 1, 8)
        layout.addWidget(self.inputFile1, 1, 0, 1, 6)
        layout.addWidget(self.selectInputFile1, 1, 6, 1, 2)
        layout.addWidget(self.inputFile2, 2, 0, 1, 6)
        layout.addWidget(self.selectInputFile2, 2, 6, 1, 2)
        layout.addWidget(QtGui.QLabel("Select raster or vector mask (optional)."), 3, 0, 1, 8)
        layout.addWidget(self.inputMask, 4, 0, 1, 6)
        layout.addWidget(self.selectMaskFile, 4, 6, 1, 2)
        layout.addWidget(QtGui.QLabel("Select two bands for comparison."), 5, 0, 1, 8)
        layout.addWidget(self.band1, 6, 0, 1, 4)
        layout.addWidget(self.band2, 6, 4, 1, 4)
        layout.addWidget(self.approximateStats, 7, 0, 1, 8)
        layout.addWidget(QLabel("Plot color: "), 7, 5, 1, 2)
        layout.addWidget(self.colorbutPlots, 7, 7, 1, 1)
        layout.addWidget(displaybtn, 8, 0, 1, 2)
        layout.addWidget(self.nbrBins, 8, 2, 1, 1)
        layout.addWidget(QLabel(" bins"), 8, 3, 1, 1)
        layout.addWidget(QLabel("Background color: "), 8, 5, 1, 2)
        layout.addWidget(self.colorbut, 8, 7, 1, 1)
        layout.addLayout(self.scatterLayout, 9, 0, 1, 8)
        layout.addWidget(self.colorStretch, 10, 0, 1, 8)
        layout.addLayout(self.colorLabels, 11, 0, 1, 8)
        layout.addWidget(closebtn, 12, 0, 1, 8)

        self.resize(600, 600)

        enmapBox = EnMAPBox.instance()

        if isinstance(enmapBox, EnMAPBox):
            for src in sorted(enmapBox.dataSources('RASTER')):
                self.addSrcRaster(src)

    def backgroundColorSelection(self):
        color = QtGui.QColorDialog.getColor()
        #self.backgroundCol = color

        self.scatterview.setBackground(color.name())
        self.plotXbins.setBackground(color.name())
        self.plotYbins.setBackground(color.name())

        self.colorbut.setStyleSheet("background-color: " + color.name())

    def plotColorSelection(self):
        col = QtGui.QColorDialog.getColor()
        self.plotCol = col

        self.scatterview.getPlotItem().getAxis('left').setPen(QPen(col))
        self.scatterview.getPlotItem().getAxis('bottom').setPen(QPen(col))
        self.plotXbins.getPlotItem().getAxis('left').setPen(QPen(col))
        self.plotXbins.getPlotItem().getAxis('bottom').setPen(QPen(col))
        self.plotYbins.getPlotItem().getAxis('left').setPen(QPen(col))
        self.plotYbins.getPlotItem().getAxis('bottom').setPen(QPen(col))

        if(len(self.plotYbins.listDataItems()) != 0):
            self.plotYbins.listDataItems()[0].setPen(QPen(col))
            self.plotXbins.listDataItems()[0].setPen(QPen(col))

        self.colorbutPlots.setStyleSheet("background-color: " + col.name())

    def addSrcRaster(self, src):
        addedItems = [self.inputFile1.itemData(i, role=Qt.UserRole) for
            i in range(self.inputFile1.count())]
        if src not in addedItems:
            #bn = os.path.basename(src)
            self.inputFile1.addItem(src)
        self.validatePath(src)

    def fileFound(self, item):
        item.addItem(QFileDialog.getOpenFileName(self, 'Input image', directory = "/Workspaces/QGIS-Plugins/enmap-box/enmapboxtestdata"))
        counter = item.count()
        item.setCurrentIndex(counter - 1)

    def comboIndexChanged1(self):
        if self.validatePath(self.inputFile1):
            self.inDS1 = gdal.Open(self.inputFile1.currentText())

            self.inputFile2.addItem(self.inputFile1.currentText())
            counter = self.inputFile2.count()
            self.inputFile2.setCurrentIndex(counter - 1)
            self.inDS2 = gdal.Open(self.inputFile1.currentText())

            self.clearBandList()
            self.populateBandList()
        else:
            self.inDS1 = None

    def comboIndexChanged2(self):
        if self.validatePath(self.inputFile2):
            self.inDS2 = gdal.Open(self.inputFile2.currentText())

            self.clearBandList()
            self.populateBandList()
        else:
            self.inDS2 = None

    def maskFound(self):
        self.inputMask.addItem(QFileDialog.getOpenFileName(self, 'Mask',
                                                               directory="/Workspaces/QGIS-Plugins/enmap-box/enmapboxtestdata"))
        counter = self.inputMask.count()
        self.inputMask.setCurrentIndex(counter - 1)

    def maskIndexChanged(self):
        self.validatePath(self.inputMask)

    def clearBandList(self):
        self.band1.clear()
        self.band2.clear()

    def populateBandList(self):
        for i in range(1, self.inDS1.RasterCount):
            self.band1.addItem(self.inDS1.GetRasterBand(i).GetDescription())

        for i in range(1, self.inDS2.RasterCount):
            self.band2.addItem(self.inDS2.GetRasterBand(i).GetDescription())

    def displayScatterplot(self):

        self.scatterplot.clear()
        self.scatterview.clear()
        self.scatterview.addItem(self.scatterplot)
        self.plotYbins.clear()
        self.plotXbins.clear()

        image1 = Image(filename=self.inDS1.GetFileList()[0])
        image2 = Image(filename=self.inDS2.GetFileList()[0])

        pathMask = self.inputMask.currentText()
        if os.path.isfile(pathMask) and gdal.Open(pathMask):
            mask = Mask(filename=pathMask)
        elif os.path.isfile(pathMask) and ogr.Open(pathMask):
            mask = Vector(filename=pathMask)
        else:
            mask = None

        displayedBandName1 = self.band1.currentText()
        displayedBandName2 = self.band2.currentText()

        i1, i2 = self.band1.currentIndex(), self.band2.currentIndex()

        if self.approximateStats.isChecked():
            xRes = (self.inDS1.RasterXSize / self.approximateGrid) * self.inDS1.GetGeoTransform()[1]
            yRes = self.inDS1.RasterYSize / self.approximateGrid * self.inDS1.GetGeoTransform()[5] * -1
            if (xRes < self.inDS1.GetGeoTransform()[1]):
                xRes = self.inDS1.GetGeoTransform()[1]
            if (yRes < self.inDS1.GetGeoTransform()[5] * -1):
                yRes = self.inDS1.GetGeoTransform()[5] * -1

            grid1 = image1.pixelGrid.newResolution(xRes=xRes, yRes=yRes)

            (min1), (max1), (mean1), (n1) = image1.basicStatistics(bandIndicies=[i1], mask = mask, grid = grid1)

            xRes = (self.inDS2.RasterXSize / self.approximateGrid) * self.inDS2.GetGeoTransform()[1]
            yRes = self.inDS2.RasterYSize / self.approximateGrid * self.inDS2.GetGeoTransform()[5] * -1
            if (xRes < self.inDS2.GetGeoTransform()[1]):
                xRes = self.inDS2.GetGeoTransform()[1]
            if (yRes < self.inDS2.GetGeoTransform()[5] * -1):
                yRes = self.inDS2.GetGeoTransform()[5] * -1

            grid2 = image2.pixelGrid.newResolution(xRes=xRes, yRes=yRes)

            (min2), (max2), (mean2), (n2) = image2.basicStatistics(bandIndicies=[i2], mask = mask, grid = grid2)
        else:
            (min1), (max1), (mean1), (n1) = image1.basicStatistics(bandIndicies=[i1],
                                                                                         mask=mask)
            (min2), (max2), (mean2), (n2) = image2.basicStatistics(bandIndicies=[i2],
                                                                                         mask=mask)

        self.H, self.xedges, self.yedges = image1.scatterMatrix(image2=image2, bandIndex1=i1, bandIndex2=i2, range1=[min1, max1],
                                                range2=[min2, max2], bins=self.nbrBins.value())

        self.min1 = min1
        self.min2 = min2

        sy = []
        for u in range(0, len(self.H)):
            temp = 0
            for v in range(0, len(self.H[0])):
                temp += self.H[u][v]
            sy.append(temp)

        sx = self.H[0]
        for t in range(1,self.nbrBins.value()):
            sx = sx + self.H[t]

        cx = []
        rx = max1 - min1
        self.rx = rx
        for b in range(0,self.nbrBins.value()):
            cx.append(float(self.xedges[b]))

        cy = []
        ry = max2 - min2
        self.ry = ry
        for b in range(0,self.nbrBins.value()):
            cy.append(float(self.yedges[b]))

        #print(cx)
        #print(cy)
        #print(sy)
        #print(sx)

        self.plotXbins.plot(sx, cx, stepMode=False, fillLevel=0, pen = QPen(self.plotCol),
                              brush=pyqtgraph.intColor(12, 100, alpha=0))

        self.plotYbins.plot(cy, sy, stepMode=False, fillLevel=0, pen = QPen(self.plotCol),
                              brush=pyqtgraph.intColor(12, 100, alpha=0))

        mx = max(self.H.ravel())

        positions = []
        step = mx / (len(self.defaultGradientColors) - 1)
        for z in range(0, len(self.defaultGradientColors)):
            positions.append(z * step)

        self.colorMap = ColorMap(pos = positions, color = self.defaultGradientColors, mode = None)
        colorMap = self.colorMap.map(self.H)

        gradientWidget = GradientWidget(allowAdd = True)

        # Clear color labels
        while len(self.colorLabels) > 0:
            self.colorLabels.takeAt(0).widget().deleteLater()

        # Create new clor labels for max and min values
        colorLabel0 = QLabel(str(0))
        colorLabel1 = QLabel(str(mx))
        colorLabel0.setAlignment(QtCore.Qt.AlignLeft)
        colorLabel1.setAlignment(QtCore.Qt.AlignRight)
        self.colorLabels.addWidget(colorLabel0)
        self.colorLabels.addWidget(colorLabel1)

        while len(gradientWidget.listTicks()) > 0:
            gradientWidget.removeTick(gradientWidget.listTicks()[0][0])

        step = 1.0 / (len(self.defaultGradientColors) - 1)
        for u in range(0, len(self.defaultGradientColors)):
            col = self.defaultGradientColors[u]
            gradientWidget.addTick(x = u * step, color = QColor(col[0],col[1],col[2],col[3]), movable = True)

        if(self.colorStretch.widget(0) is not None):
            self.colorStretch.widget(0).deleteLater()

        self.colorStretch.addWidget(gradientWidget)

        # todo: find a method to update only when gradientchange completed!
        gradientWidget.sigGradientChangeFinished.connect(lambda: self.updateScatter(gradientWidget.colorMap()))

        spots = []
        for i in range(0, self.nbrBins.value()):
            for j in range(0,self.nbrBins.value()):
                red = colorMap[i,j][0]
                green = colorMap[i,j][1]
                blue = colorMap[i,j][2]
                alpha = colorMap[i,j][3]

                pen = QPen(QColor(0,0,0,0))

                # if value is 0, make pixel transparent
                if (self.H[i, j] == 0):
                    spots.append({'pos': ((self.xedges[i]),
                                          (self.yedges[j])),
                                  'size': ry / self.nbrBins.value(), 'pen': pen,
                                  'brush': QColor(red, green, blue, 0)})
                else:
                    spots.append({'pos': ((min1 + (float(i) * ry / self.nbrBins.value())), (min2 + (float(j) * rx / self.nbrBins.value()))), 'size': ry/self.nbrBins.value(), 'pen': pen,
                              'brush': QColor(red,green,blue,alpha)})

        self.scatterplot.addPoints(spots)
        #self.scatterplot.sigClicked.connect(self.clicked)

        # SCatterplot labels
        self.scatterview.getPlotItem().setLabel(axis = 'left', text = displayedBandName2)
        self.scatterview.getPlotItem().setLabel(axis = 'bottom', text = displayedBandName1)

        # bin distribution labels
        self.plotXbins.getPlotItem().setLabel(axis = 'bottom', text = "bins")
        self.plotYbins.getPlotItem().setLabel(axis = 'left', text = "bins")

        self.col = ColorMapParameter()
        self.col.setFields([
            ('Colors', {'units': 'uint64'}),
        ])

        self.scatterview.plotItem.getViewBox().autoRange()
        self.plotXbins.plotItem.getViewBox().autoRange()
        self.plotYbins.plotItem.getViewBox().autoRange()

    #lastClicked = []
    #def clicked(self, points):
    #    #global lastClicked
    #    for p in self.lastClicked:
    #        p.resetPen()
    #    print("clicked points", points)
    #    for p in points:
    #        p.setPen('b', width=2)
    #    self.lastClicked = points


    def updateScatter(self, cMap):

        self.scatterplot.clear()

        mx = max(self.H.ravel())

        self.defaultGradientColors = cMap.getColors()

        positions = []
        step = mx / (len(self.defaultGradientColors) - 1)
        for z in range(0, len(self.defaultGradientColors)):
            positions.append(z * step)

        self.colorMap = ColorMap(pos = positions, color = self.defaultGradientColors, mode=None)
        colorMap = self.colorMap.map(self.H)

        spots = []
        for i in range(0, self.nbrBins.value()):
            for j in range(0, self.nbrBins.value()):
                red = colorMap[i, j][0]
                green = colorMap[i, j][1]
                blue = colorMap[i, j][2]
                alpha = colorMap[i, j][3]

                pen = QPen(QColor(0, 0, 0, 0))

                if(self.H[i,j] == 0):
                    spots.append({'pos': ((self.xedges[i]),
                                          (self.yedges[j])),
                                  'size': self.ry / self.nbrBins.value(), 'pen': pen,
                                  'brush': QColor(red, green, blue, 0)})
                else:
                    spots.append({'pos': ((self.min1 + (float(i) * self.ry / self.nbrBins.value())), (self.min2 + (float(j) * self.rx / self.nbrBins.value()))), 'size': self.ry/self.nbrBins.value(), 'pen': pen,
                              'brush': QColor(red,green,blue,alpha)})

        self.scatterplot.addPoints(spots)
        #self.scatterplot.sigClicked.connect(self.clicked)

    def onSigRangeChanged(self, r):
        for t in range(0, self.scatterLayout.count()):
            self.scatterLayout.itemAt(t).widget().sigRangeChanged.disconnect(self.onSigRangeChanged)

        if(r == self.plotYbins):
            self.scatterview.setRange(xRange=r.getAxis('bottom').range, padding=0.0)

        if(r == self.plotXbins):
            self.scatterview.setRange(yRange=r.getAxis('left').range, padding=0.0)

        if(r == self.scatterview):
            self.plotYbins.setRange(xRange=r.getAxis('bottom').range, padding=0.0)
            self.plotXbins.setRange(yRange=r.getAxis('left').range, padding=0.0)

        for t in range(0, self.scatterLayout.count()):
            self.scatterLayout.itemAt(t).widget().sigRangeChanged.connect(self.onSigRangeChanged)

    def validatePath(self, item, *args, **kwds):
        sender = self.sender()
        hexRed = QColor(Qt.red).name()
        hexGreen = QColor(Qt.green).name()

        result = True

        if sender == item:
            path = item.currentText()

            from osgeo import gdal

            if(item.currentText() != ""):
                ds = gdal.Open(path)

                vs = None
                if(item is self.inputMask):
                    vs = ogr.Open(path)

                    if ds and vs is None:
                        style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                        item.setStyleSheet(style)
                        result = False

                else:
                    if ds is None: #and vs is None:
                        style = 'QComboBox {{ background-color: {} }}'.format(hexRed)
                        item.setStyleSheet(style)
                        result = False
                    else:
                        style = 'QComboBox {{ }}'.format(hexGreen)
                        item.setStyleSheet(style)

            return result

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        w = Win()
        w.setWindowFlags(w.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        w.show()
        app.exec_()