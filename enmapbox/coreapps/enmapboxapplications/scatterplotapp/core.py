import traceback

from PyQt5.uic import loadUi
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

from hubdc.progressbar import CUIProgressBar
from hubflow.core import *

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

pathUi = join(dirname(__file__), 'ui')

class ProgressBar(CUIProgressBar):

    def __init__(self, bar):
        assert isinstance(bar, QProgressBar)
        self.bar = bar
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)

    def setText(self, text):
        pass

    def setPercentage(self, percentage):
        self.bar.setValue(int(percentage))
        QApplication.processEvents()


class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        self.plotItem_ = pg.PlotItem()
        pg.ImageView.__init__(self, *args, view=self.plotItem_, **kwargs)
        self.plotItem().setAspectLocked(lock=False)

    def plotItem(self):
        assert isinstance(self.plotItem_, pg.PlotItem)
        return self.plotItem_

    def setSidePlotVisible(self, bool):
        self.ui.roiBtn.setVisible(bool)
        self.ui.menuBtn.setVisible(bool)
        self.ui.histogram.setVisible(bool)

class ScatterPlotApp(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(pathUi, 'main.ui'), self)
        #self.setupUi(self)
        self.uiInfo_ = QLabel()
        self.uiFit_.hide()
        self.statusBar().addWidget(self.uiInfo_, 1)
        self.uiRaster1().setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiRaster2().setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.uiExecute().clicked.connect(self.execute)
        self.uiImageView().hide()
        self.uiImageView().view.invertY(False)

        self.actualPoints = pg.ScatterPlotItem(pen=pg.mkPen(width=1, color=(255, 255, 255)), symbol='o', size=1)
        self.uiImageView().plotItem().addItem(self.actualPoints)

        self.minMaxLine = self.uiImageView().plotItem().plot([0, 0],[0, 0], pen=pg.mkPen(color=(255, 0, 0), width=2,
                                                                                         style=QtCore.Qt.SolidLine))
        self.fittedLine = self.uiImageView().plotItem().plot([0, 0], [0, 0], pen=pg.mkPen(color=(0, 255, 0), width=2,
                                                                                          style=QtCore.Qt.DashLine))

        self._progressBar = ProgressBar(bar=self.uiProgressBar_)

    def uiShowMinMaxLine(self):
        assert isinstance(self.uiShowMinMaxLine_, QCheckBox)
        return self.uiShowMinMaxLine_

    def progressBar(self):
        return self._progressBar

    def showFittedLine(self):
        assert isinstance(self.showFittedLine_, QCheckBox)
        return self.showFittedLine_

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

    def log(self, text):
        self.uiInfo_.setText(str(text))
        QCoreApplication.processEvents()

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

        if self.uiBins().isEnabled():
            bins = self.uiBins().value()
        else:
            bins = None

        fast = self.uiAccuracy().currentIndex() == 0

        return raster1, raster2, band1, band2, min1, min2, max1, max2, mask, bins, fast

    def execute(self, *args):

        self.uiImageView().hide()
        self.fittedLine.clear()
        self.minMaxLine.clear()
        self.actualPoints.clear()
        self.uiExecute().setEnabled(False)
        self.log('')
        self.uiFit_.hide()
        try:

            raster1, raster2, band1, band2, min1, min2, max1, max2, mask, bins, fast  = self.inputs()
            plotBinnedData = bins is not None
            plotActualData = not plotBinnedData
            plotFittedLine = self.showFittedLine().isChecked()

            if raster1 is None or raster2 is None:
                return

            grid = Grid(extent=raster1.grid().extent().intersection(other=raster2.grid().extent().reproject(projection=raster1.grid().projection())),
                        resolution=raster1.grid().resolution())

            fast = self.uiAccuracy().currentIndex() == 0
            if fast:
                n = 100
                grid = Grid(extent=grid.extent(),
                             resolution=Resolution(x=max(grid.size().x(), n) / n * grid.resolution().x(),
                                                   y=max(grid.size().y(), n) / n * grid.resolution().y()))

            if min1 is None or max1 is None:
                statistics1 = raster1.statistics(bandIndices=[band1], mask=mask, grid=grid, **ApplierOptions(progressBar=self.progressBar()))[0]
                if min1 is None:
                    min1 = statistics1.min
                    self.uiMin1().setText(str(min1))
                if max1 is None:
                    max1 = statistics1.max
                    self.uiMax1().setText(str(max1))

            if min2 is None or max2 is None:
                statistics2 = raster2.statistics(bandIndices=[band2], mask=mask, grid=grid, **ApplierOptions(progressBar=self.progressBar()))[0]
                if min2 is None:
                    min2 = statistics2.min
                    self.uiMin2().setText(str(min2))
                if max2 is None:
                    max2 = statistics2.max
                    self.uiMax2().setText(str(max2))

            if plotBinnedData:
                self.uiImageView().setSidePlotVisible(True)
                scatter = raster1.scatterMatrix(raster2=raster2, bandIndex1=band1, bandIndex2=band2,
                                                range1=[min1, max1], range2=[min2, max2],
                                                bins=bins, mask=mask, grid=grid, **ApplierOptions(progressBar=self.progressBar()))

                scale1 = (max1 - min1) / float(bins)
                scale2 = (max2 - min2) / float(bins)

                self.uiImageView().setImage(scatter.H, pos=[min1,min2], scale=[scale1, scale2])
                self.uiImageView().setLevels(*np.percentile(scatter.H, (2,98))) # stretch ramp between 2% - 98%
            else:
                self.uiImageView().clear()

            xlabel = '{}: {} in {}'.format(band1+1, raster1.dataset().band(index=band1).description(), basename(raster1.filename()))
            ylabel = '{}: {} in {}'.format(band2+1, raster2.dataset().band(index=band2).description(), basename(raster2.filename()))

            self.uiImageView().plotItem().getAxis(name='bottom').setLabel(text=xlabel)
            self.uiImageView().plotItem().getAxis(name='left').setLabel(text=ylabel)

            if self.uiShowMinMaxLine().isChecked():
                self.minMaxLine.setData([min1, max1], [min2, max2])

            if plotActualData or plotFittedLine:
                self.uiImageView().setSidePlotVisible(False)
                self.progressBar().setPercentage(99)

                ds1 = raster1.dataset().translate(grid=grid, bandList=[band1 + 1], filename='/vsimem/scatterplotapp/band1.vrt', driver=VrtDriver())
                ds2 = raster2.dataset().translate(grid=grid, bandList=[band2 + 1], filename='/vsimem/scatterplotapp/band2.vrt', driver=VrtDriver())

                sample = RegressionSample(raster=Raster.fromRasterDataset(rasterDataset=ds2),
                                          regression=Regression.fromRasterDataset(rasterDataset=ds1),
                                          mask=mask)
                r2, r1 = sample.extractAsRaster(filenames=['/vsimem/scatterplotapp/extracted2.bsq', '/vsimem/scatterplotapp/extracted1.bsq'], onTheFlyResampling=True, **ApplierOptions(progressBar=self.progressBar()))
                sample = RegressionSample(raster=r1, regression=Regression(filename=r2.filename()))

                if plotFittedLine:
                    from sklearn.linear_model import LinearRegression
                    olsr = Regressor(sklEstimator=LinearRegression())
                    olsr.fit(sample=sample)
                    # f(x) = m*x + n
                    n = olsr.sklEstimator().intercept_
                    m = olsr.sklEstimator().coef_[0]
                    self.fittedLine.setData([min1, max1], [m*min1+n, m*max1+n])

                    p = RegressionPerformance.fromRaster(prediction=olsr.predict(filename='/vsimem/p.bsq', raster=sample.raster()),
                                                         reference=sample.regression(), **ApplierOptions(progressBar=self.progressBar(), emitFileCreated=False))

                    self.uiFit_.setText('f(x) = {} * x {} {}, n = {}, r^2 = {}'.format(round(m, 5), '+' if n >= 0 else '-', abs(round(n, 5)), p.n, p.r2_score[0]))
                    self.uiFit_.show()

                if plotActualData:
                    x, y = sample.extractAsArray()
                    self.actualPoints.setData(x.ravel(), y.ravel())

            self.uiImageView().show()

        except Exception as error:
            traceback.print_exc()
            message = traceback.format_exc()
            self.log('Error: {}'.format(message))# str(error)))

        self.progressBar().setPercentage(0)
        self.uiExecute().setEnabled(True)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    app = QApplication([])
    #app = QApplication.instance()
    w = ScatterPlotApp()
    w.show()
    app.exec_()