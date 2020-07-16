from os.path import dirname, join

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QComboBox
from PyQt5.uic import loadUi

from hubdsm.core.size import Size
from pyqtgraph import AxisItem
from pyqtgraph.widgets.PlotWidget import PlotWidget as PlotWidget_

from hubdsm.algorithm.uniquebandvaluecounts import uniqueBandValueCounts
from hubdsm.core.category import Category
from hubdsm.core.raster import Raster
from hubdsm.processing.enmapalgorithm import *


class ClassificationStatistics(EnMAPAlgorithm):
    def displayName(self):
        return 'Classification Statistics'

    def description(self):
        return 'Show classification statistics plot.'

    def group(self):
        return Group.Auxilliary.value

    P_CLASSIFICATION = 'classification'
    P_OUTPUT_CATEGORIES = 'outputCategories'
    P_OUTPUT_COUNTS = 'outputCounts'

    def defineCharacteristics(self):

        self.addParameter(
            EnMAPProcessingParameterPalettedRasterLayer(
                name=self.P_CLASSIFICATION, description='Classification'
            )
        )

        self.addOutput(
            EnMAPProcessingOutputString(
                name=self.P_OUTPUT_CATEGORIES, description='Output Categories'
            )
        )

        self.addOutput(
            EnMAPProcessingOutputString(
                name=self.P_OUTPUT_COUNTS, description='Output Counts'
            )
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):

        layer: QgsRasterLayer = self.parameter(parameters, self.P_CLASSIFICATION, context)
        renderer = layer.renderer()
        categories = Category.fromQgsPalettedRasterRenderer(renderer=renderer)

        raster = Raster.open(layer.source())
        band = raster.band(number=renderer.band())
        counts = uniqueBandValueCounts(band=band)
        for category in categories:
            feedback.pushInfo(f'{category}: {counts.get(category.id, 0)} px')

        return {
            self.P_OUTPUT_CATEGORIES: str(categories),
            self.P_OUTPUT_COUNTS: str([counts.get(category.id, 0) for category in categories]),
        }


class PlotWidget(PlotWidget_):
    def __init__(self, parent, background='#ffffff'):
        PlotWidget_.__init__(self, parent=parent, background=background)


class ClassificationStatisticsPlot(QMainWindow):
    mPlot: PlotWidget
    mUnit: QComboBox

    def __init__(self, categories: List[Category], counts: List[int], layer: QgsRasterLayer, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(dirname(__file__), 'classificationstatistics.ui'), self)
        self.categories = categories
        self.counts = counts
        self.layer = layer
        self.mUnit.currentIndexChanged.connect(self.onUnitChanged)
        self.onUnitChanged(index=0)

    def onUnitChanged(self, index: int):

        if index == 0:  # pixel
            ys = self.counts
            ylabel = 'Pixel'
        elif index == 1:  # percentage
            n = sum(self.counts)
            ys = [count / n * 100 for count in self.counts]
            ylabel = 'Percentage'
        elif index == 2:
            xsize = self.layer.rasterUnitsPerPixelX()
            ysize = self.layer.rasterUnitsPerPixelY()
            ys = [count * xsize * ysize for count in self.counts]
            crs: QgsCoordinateReferenceSystem = self.layer.crs()
            unit = QgsUnitTypes.toString(crs.mapUnits())
            ylabel = f'Square {unit.title()}'
        else:
            assert 0

        self.mPlot.clear()
        for i, (category, y) in enumerate(zip(self.categories, ys)):
            color = QColor(category.color.red, category.color.green, category.color.blue)
            plot = self.mPlot.plot(x=[i + 0.1, i + 0.9], y=[y], stepMode=True, fillLevel=0, brush=color)
            plot.setPen(color=QColor(0, 0, 0), width=1)
        axis: AxisItem = self.mPlot.getAxis('bottom')
        axis.setTicks(
            [[(i + 0.5, category.name)
              for i, category in enumerate(self.categories)]])
        axis: AxisItem = self.mPlot.getAxis('left')
        axis.setLabel(text=ylabel, units=None, unitPrefix=None)
