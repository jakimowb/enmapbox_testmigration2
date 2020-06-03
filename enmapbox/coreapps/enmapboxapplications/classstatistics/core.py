import traceback
from datetime import datetime
from os.path import join, dirname
from typing import Optional, Dict

from PyQt5.uic import loadUi
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from hubdsm.algorithm.processingoptions import ProcessingOptions
from hubdsm.algorithm.uniquebandvaluecounts import uniqueBandValueCounts
from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.raster import Raster
from pyqtgraph import AxisItem
from pyqtgraph.widgets.PlotWidget import PlotWidget as PlotWidget_

pathUi = join(dirname(__file__), 'ui')


class PlotWidget(PlotWidget_):
    def __init__(self, parent, background='#ffffff'):
        PlotWidget_.__init__(self, parent=parent, background=background)


class ClassStatistics(QMainWindow):
    mMessageBar: QgsMessageBar
    mRaster: QgsMapLayerComboBox
    mBand: QgsRasterBandComboBox
    mMask: QgsMapLayerComboBox
    mRun: QToolButton
    mPlot: PlotWidget

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(pathUi, 'main.ui'), self)
        self.mRaster.setCurrentIndex(0)
        self.mMask.setCurrentIndex(0)
        self.mRun.clicked.connect(self.onRunClicked)

    def onCancelClicked(self):
        self.task.cancel()

    def onProgressChanged(self, progress: float):
        self.mProgressBar.setValue(int(round(progress)))

    def onRunClicked(self):

        self.mMessageBar.clearWidgets()
        self.mPlot.clear()

        if self.mRaster.currentLayer() is None:
            self.mMessageBar.pushWarning(title='Missing parameter value', message='Raster')
            return
        else:
            rasterLayer: QgsRasterLayer = self.mRaster.currentLayer()
            number = self.mBand.currentBand()
            categories = dict()
            if isinstance(rasterLayer.renderer(), QgsPalettedRasterRenderer):
                renderer: QgsPalettedRasterRenderer = rasterLayer.renderer()
                for c in renderer.classes():
                    assert isinstance(c, QgsPalettedRasterRenderer.Class)
                    qcolor: QColor = c.color
                    category = Category(
                        id=c.value,
                        name=c.label,
                        color=Color(red=qcolor.red(), green=qcolor.green(), blue=qcolor.blue())
                    )
                    categories[c.value] = category
            filenameRaster = rasterLayer.source()

        if self.mMask.currentLayer() is None:
            filenameMask = None
        else:
            maskLayer: QgsRasterLayer = self.mMask.currentLayer()
            filenameMask = maskLayer.source()

        self.task = Task(widget=self, filenameRaster=filenameRaster, filenameMask=filenameMask, number=number, categories=categories)
        self.task.progressChanged.connect(self.onProgressChanged)
        QgsApplication.taskManager().addTask(self.task)


class CanceledError(Exception):
    pass


class Task(QgsTask):

    def __init__(
            self, widget: ClassStatistics, filenameRaster: str, number: int, categories: Dict[float, Category],
            filenameMask: Optional[str]
    ):
        super().__init__(widget.windowTitle(), QgsTask.CanCancel)
        self.widget = widget
        self.filenameRaster = filenameRaster
        self.number = number
        self.categories = categories
        self.filenameMask = filenameMask

        def callbackProgress(i: int, n: int):
            # set progress
            percentage = int(round(i / n * 100))
            self.setProgress(progress=percentage)
            # check if task was canceled
            if self.isCanceled():
                raise CanceledError('Task canceled by the user.')

        self.processingOptions = ProcessingOptions(
            callbackStart=lambda *args, **kwargs: datetime.now(),
            callbackFinish=lambda *args, **kwargs: datetime.now(),
            callbackProgress=callbackProgress
        )
        self.exception = None
        self.traceback = None
        self.widget.mRun.setEnabled(False)
        self.widget.mCancel.setEnabled(True)

    def run(self):
        try:
            raster = Raster.open(self.filenameRaster)
            if self.filenameMask:
                mask = Raster.open(self.filenameMask)
                raster = raster.withMask(mask=mask)
            band = raster.band(number=self.number)
            self.result = uniqueBandValueCounts(band=band, po=self.processingOptions)
        except Exception as exception:
            self.exception = exception
            self.traceback = traceback.format_exc()
            return False
        return True

    def finished(self, result):

        if result:
            for i, (x, y) in enumerate(self.result.items()):
                if x in self.categories:
                    color = self.categories[x].color
                    color = QColor(color.red, color.green, color.blue)
                else:
                    color = QColor(0, 0, 0)
                plot = self.widget.mPlot.plot(x=[i + 0.1, i + 0.9], y=[y], stepMode=True, fillLevel=0, brush=color)
                plot.setPen(color=QColor(0, 0, 0), width=1)
            axis: AxisItem = self.widget.mPlot.getAxis('bottom')
            axis.setTicks([[(i + 0.5, v if v not in self.categories else self.categories[v].name) for i, v in enumerate(self.result.keys())]])

        else:
            self.pushError(exception=self.exception, traceback=self.traceback)

        self.setProgress(0)
        self.widget.mRun.setEnabled(True)
        self.widget.mCancel.setEnabled(False)

    def pushError(self, exception: Exception, traceback: str):
        errorText = traceback
        errorTitle = f'{str(exception)}'

        def showError():
            class Dialog(QDialog):
                def __init__(self, title, text, parent, *args, **kwds):
                    super().__init__(parent, *args, **kwds)
                    self.setWindowTitle(title)
                    self.setFont(QFont("Fixed", 10))
                    self.setMinimumSize(500, 500)
                    self.setLayout(QVBoxLayout())
                    self.text = QTextEdit()
                    self.text.setText(text)
                    self.layout().addWidget(self.text)

            dialog = Dialog(title=f'{self.widget.windowTitle()}: {errorTitle}', text=errorText, parent=self.widget)
            dialog.exec_()

        messageBar = self.widget.mMessageBar
        if isinstance(exception, CanceledError):
            messageBar.pushInfo('Warning', str(exception))
        else:
            widget = messageBar.createMessage(errorTitle, '')
            button = QPushButton(widget)
            button.setText("Show Traceback")
            button.pressed.connect(showError)
            widget.layout().addWidget(button)
            messageBar.pushWidget(widget, Qgis.Critical)
            print(traceback)
