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

import traceback
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
#from pyqtgraph.widgets.PlotWidget import PlotWidget as PlotWidget_
#from pyqtgraph.imageview.ImageView import ImageView as ImageView_
from enmapboxapplications.utils import loadUIFormClass
from hubflow.core import *

pathUi = join(dirname(__file__), 'ui')

class PlotWidget(pg.PlotWidget):
    def __init__(self, parent, background='#ffffff'):
        pg.PlotWidget.__init__(self, parent=parent, background=background)

class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        self.plotItem_ = pg.PlotItem()
        pg.ImageView.__init__(self, *args, view=self.plotItem_, **kwargs)
        self.plotItem().setAspectLocked(lock=False)

    def plotItem(self):
        assert isinstance(self.plotItem_, pg.PlotItem)
        return self.plotItem_

class ScatterPlotApp(QMainWindow, loadUIFormClass(pathUi=join(pathUi, 'main.ui'))):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.uiRaster1().setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiRaster2().setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiExecute().clicked.connect(self.execute)

    def uiRaster1(self):
        assert isinstance(self.uiRaster1_, QgsMapLayerComboBox)
        return self.uiRaster1_

    def uiBand1(self):
        assert isinstance(self.uiBand1_, QgsRasterBandComboBox)
        return self.uiBand1_

    def uiMin1(self):
        assert isinstance(self.uiMin1_, QLineEdit)
        return self.uiMin1_

    def uiMax1(self):
        assert isinstance(self.uiMax1_, QLineEdit)
        return self.uiMax1_

    def uiRaster2(self):
        assert isinstance(self.uiRaster2_, QgsMapLayerComboBox)
        return self.uiRaster2_

    def uiBand2(self):
        assert isinstance(self.uiBand2_, QgsRasterBandComboBox)
        return self.uiBand2_

    def uiMin2(self):
        assert isinstance(self.uiMin2_, QLineEdit)
        return self.uiMin2_

    def uiMax2(self):
        assert isinstance(self.uiMax2_, QLineEdit)
        return self.uiMax2_

    def uiMask(self):
        assert isinstance(self.uiMask_, QgsMapLayerComboBox)
        return self.uiMask_

    def uiAccuracy(self):
        assert isinstance(self.uiAccuracy_, QComboBox)
        return self.uiAccuracy_

    def uiBins(self):
        assert isinstance(self.uiBins_, QSpinBox)
        return self.uiBins_

    def uiExecute(self):
        assert isinstance(self.uiExecute_, QToolButton)
        return self.uiExecute_

    def uiImageView(self):
        assert isinstance(self.uiImageView_, ImageView)
        return self.uiImageView_

    def inputs(self):
        if self.uiRaster1().currentLayer() is not None:
            raster1 = Raster(filename=self.uiRaster1().currentLayer().source())
            band1 = self.uiBand1().currentBand() - 1
        else:
            raster1 = None
            band1 = None

        if self.uiRaster2().currentLayer() is not None:
            raster2 = Raster(filename=self.uiRaster2().currentLayer().source())
            band2 = self.uiBand2().currentBand() -1
        else:
            raster2 = None
            band2 = None

        def getFloat(ui):
            try:
                v = float(ui.text())
            except:
                v = None
            return v

        min1 = getFloat(self.uiMin1())
        min2 = getFloat(self.uiMin2())
        max1 = getFloat(self.uiMax1())
        max2 = getFloat(self.uiMax2())

        if isinstance(self.uiMask().currentLayer(), QgsRasterLayer):
            mask = Raster(filename=self.uiMask().currentLayer().source())
        elif isinstance(self.uiMask().currentLayer(), QgsVectorLayer):
            mask = Vector(filename=self.uiMask().currentLayer().source())
        else:
            mask = None

        bins = self.uiBins().value()
        fast = self.uiAccuracy().currentIndex() == 0

        return raster1, raster2, band1, band2, min1, min2, max1, max2, mask, bins, fast

    def execute(self, *args):
        try:

            raster1, raster2, band1, band2, min1, min2, max1, max2, mask, bins, fast  = self.inputs()

            if raster1 is None or raster2 is None:
                return

            grid = Grid(extent=raster1.grid().spatialExtent().intersection(other=raster2.grid().spatialExtent()),
                        resolution=raster1.grid().resolution())

            fast = self.uiAccuracy().currentIndex() == 0
            if fast:
                n = 100
                grid = Grid(extent=grid.spatialExtent(),
                             resolution=Resolution(x=max(grid.size().x(), n) / n * grid.resolution().x(),
                                                   y=max(grid.size().y(), n) / n * grid.resolution().y()))

            if min1 is None or max1 is None:
                statistics1 = raster1.statistics(bandIndices=[band1], mask=mask, grid=grid)[0]
                if min1 is None:
                    min1 = statistics1.min
                    self.uiMin1().setText(str(min1))
                if max1 is None:
                    max1 = statistics1.max
                    self.uiMax1().setText(str(max1))

            if min2 is None or max2 is None:
                statistics2 = raster2.statistics(bandIndices=[band2], mask=mask, grid=grid)[0]
                if min2 is None:
                    min2 = statistics2.min
                    self.uiMin2().setText(str(min2))
                if max2 is None:
                    max2 = statistics2.max
                    self.uiMax2().setText(str(max2))

            scatter = raster1.scatterMatrix(raster2=raster2, bandIndex1=band1, bandIndex2=band2,
                                            range1=[min1, max1], range2=[min2, max2],
                                            bins=bins, mask=mask, grid=grid)

            scale1 = (max1 - min1) / float(bins)
            scale2 = (max2 - min2) / float(bins)

            self.uiImageView().setImage(scatter.H, pos=[min1,min2], scale=[scale1, scale2])
            self.uiImageView().view.invertY(False)
            xlabel = '{}: {} in {}'.format(band1+1, raster1.dataset().band(index=band1).description(), basename(raster1.filename()))
            ylabel = '{}: {} in {}'.format(band2+1, raster2.dataset().band(index=band2).description(), basename(raster2.filename()))

            self.uiImageView().plotItem().getAxis(name='bottom').setLabel(text=xlabel)
            self.uiImageView().plotItem().getAxis(name='left').setLabel(text=ylabel)


        except:
            traceback.print_exc()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QApplication([])
    #app = QApplication.instance()
    w = ScatterPlotApp()
    w.show()
    app.exec_()