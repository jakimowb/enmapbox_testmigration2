import traceback

from PyQt5.uic import loadUi
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from pyqtgraph.widgets.PlotWidget import PlotWidget as PlotWidget_

from hubflow.core import *

pathUi = join(dirname(__file__), 'ui')

class ProgressBar(CUIProgressBar):

    def __init__(self, bar):
        assert isinstance(bar, QProgressBar)
        self.bar = bar
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)

    def setPercentage(self, percentage):
        self.bar.setValue(int(percentage))


class PlotWidget(PlotWidget_):
    def __init__(self, parent, background='#ffffff'):
        PlotWidget_.__init__(self, parent=parent, background=background)

class ImageStatisticsApp(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(pathUi, 'main.ui'), self)
        #self.setupUi(self)
        self.uiRaster().setCurrentIndex(0)
        self.uiMask().setCurrentIndex(0)
        self.uiTableView().setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tableModel = TableModel(parent=self)
        self.uiTableView().setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiTableView().setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiTableView().clicked.connect(self.plotSelection)
        self.uiPlotAll().clicked.connect(self.plotAll)

        #        self.table_view.clicked.connect(self.selectRow)
        self.uiTableView().setModel(self.tableModel)

        self.uiClearPlots().clicked.connect(self.clearPlots)
        self.uiExecute().clicked.connect(self.execute)

    def uiRaster(self):
        assert isinstance(self.uiRaster_, QgsMapLayerComboBox)
        return self.uiRaster_

    def uiMask(self):
        assert isinstance(self.uiMask_, QgsMapLayerComboBox)
        return self.uiMask_

    def uiAccuracy(self):
        assert isinstance(self.uiAccuracy_, QComboBox)
        return self.uiAccuracy_

    def uiTableView(self):
        assert isinstance(self.uiTableView_, QTableView)
        return self.uiTableView_

    def uiExecute(self):
        assert isinstance(self.uiExecute_, QToolButton)
        return self.uiExecute_

    def uiPlot(self):
        assert isinstance(self.uiPlot_, PlotWidget)
        return self.uiPlot_

    def uiProgressBar(self):
        assert isinstance(self.uiProgressBar_, QProgressBar)
        return self.uiProgressBar_

    def uiCollectPlots(self):
        assert isinstance(self.uiCollectPlots_, QToolButton)
        return self.uiCollectPlots_

    def uiLinePlots(self):
        assert isinstance(self.uiLinePlots_, QToolButton)
        return self.uiLinePlots_

    def uiClearPlots(self):
        assert isinstance(self.uiClearPlots_, QToolButton)
        return self.uiClearPlots_

    def uiPlotAll(self):
        assert isinstance(self.uiPlotAll_, QToolButton)
        return self.uiPlotAll_

    def uiBins(self):
        assert isinstance(self.uiBins_, QComboBox)
        return self.uiBins_

    def bins(self):
        options = [256, 'auto', 'fd', 'doane', 'scott', 'rice', 'sturges', 'sqrt']
        return options[self.uiBins().currentIndex()]

    def clearPlots(self):
        self.uiPlot().clear()
        self.uiPlot().getAxis('bottom').setPen('#000000')
        self.uiPlot().getAxis('left').setPen('#000000')


    def plotSelection(self, index, *args, **kwargs):
        try:
            assert isinstance(index, QModelIndex)
            if not self.uiCollectPlots().isChecked():
                self.clearPlots()
            i = index.row()
            self.plotI(i)
        except:
            traceback.print_exc()

    def plotAll(self):
        self.clearPlots()
        for i, stat in enumerate(self.tableModel.statistics):
            self.plotI(i)

    def plotI(self, i):
        stat = self.tableModel.statistics[i]

        if self.uiLinePlots().isChecked():
            currentColor = pg.intColor(i * 20 + i, 100) #, alpha=120)
            plot = self.uiPlot().plot(x=stat.histo.bin_edges, y=stat.histo.hist,
                               stepMode=True, brush=currentColor)
            plot.setPen(color=currentColor, width=1)
        else:
            currentColor = pg.intColor(i * 20 + i, 100)#, alpha=120)
            plot = self.uiPlot().plot(x=stat.histo.bin_edges, y=stat.histo.hist,
                               stepMode=True, fillLevel=0, brush=currentColor)
            plot.setPen(color=currentColor, width=1)

    def execute(self, *args):
        try:
            if self.uiRaster().currentLayer() is not None:

                if not self.uiCollectPlots().isChecked():
                    self.clearPlots()


                raster = Raster(filename=self.uiRaster().currentLayer().source())
                if isinstance(self.uiMask().currentLayer(), QgsRasterLayer):
                    mask = Raster(filename=self.uiMask().currentLayer().source())
                elif isinstance(self.uiMask().currentLayer(), QgsVectorLayer):
                    mask = Vector(filename=self.uiMask().currentLayer().source())
                else:
                    mask = None


                #self.uiTableView().set # setColumnCount(5)
                #self.uiTable().setRowCount(raster.dataset().zsize())
                #self.uiTable().setHorizontalHeaderLabels(['Band', 'N', 'Min', 'Max', 'Mean'])

                bandNames = [band.description() for band in raster.dataset().bands()]
                grid = raster.grid()
                fast = self.uiAccuracy().currentIndex() == 0
                if fast:
                    n = 100
                    grid = Grid(extent=grid.extent(),
                                 resolution=Resolution(x=max(grid.size().x(), n) / n * grid.resolution().x(),
                                                       y=max(grid.size().y(), n) / n * grid.resolution().y()))

                statistics = raster.statistics(mask=mask, calcHistogram=True, calcMean=True, calcStd=True,
                                               histogramBins=[self.bins()] * len(bandNames),
                                               grid=grid, progressBar=ProgressBar(bar=self.uiProgressBar()))

                self.tableModel.setDataList(statistics=statistics, bandNames=bandNames)

                #self.plotAll()

                self.uiProgressBar().setValue(0)
                self.clearPlots()
        except:
            traceback.print_exc()

class TableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    KEYS = [None, None, 'nvalid', 'ninvalid', 'min', 'max', 'mean']

    def __init__(self, parent, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.statistics = []
        self.bandNames = []
        self.header = ['Description', 'Band', 'N Valid', 'N Invalid', 'Min', 'Max', 'Mean']

    def setDataList(self, statistics, bandNames):
        self.statistics = statistics
        self.bandNames = bandNames
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(), self.columnCount()))
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.statistics)

    def columnCount(self, parent=None):
        return len(self.KEYS)

    def data(self, index, role):

        if not index.isValid():
            return None

        try:
            if (index.column() == 0):
                value = self.bandNames[index.row()]
            elif (index.column() == 1):
                value = index.row()+1
            else:
                key = self.KEYS[index.column()]
                value = str(getattr(self.statistics[index.row()],key))
                #print(key, value)
        except:
            traceback.print_exc()

        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        #elif role == QtCore.Qt.CheckStateRole:
        #    if index.column() == 0:
        #        if self.statistics[index.row()][index.column()].isChecked():
        #            return QtCore.Qt.Checked
        #        else:
        #            return QtCore.Qt.Unchecked

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        #if orientation == Qt.Vertical and role == Qt.DisplayRole:
        #    return self.bandNames[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return None
        # print(">>> flags() index.column() = ", index.column())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value == QtCore.Qt.Checked:
                self.basicStatistics[index.row()][index.column()].setChecked(True)
                self.basicStatistics[index.row()][index.column()].setText("开")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
            else:
                self.basicStatistics[index.row()][index.column()].setChecked(False)
                self.basicStatistics[index.row()][index.column()].setText("关")
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        print(">>> setData() index.row = ", index.row())
        print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True