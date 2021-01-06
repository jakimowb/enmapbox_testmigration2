from os.path import dirname, join

from PyQt5.QtWidgets import QMainWindow, QTableWidget, QComboBox, QTableWidgetItem
from PyQt5.uic import loadUi
from osgeo import gdal
import numpy as np

from hubdsm.algorithm.changemap import changeMap
from hubdsm.core.category import Category
from hubdsm.core.raster import Raster
from hubdsm.processing.enmapalgorithm import *


class ChangeMap(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Change Map'

    def description(self):
        return 'Create a change map from two classifications.'

    def group(self):
        return Group.Classification.value

    P_CLASSIFICATION1 = 'classification1'
    P_CLASSIFICATION2 = 'classification2'
    P_SHOW_STATISTICS = 'showStatistics'
    P_OUTRASTER = 'outraster'

    def defineCharacteristics(self):

        self.addParameter(
            EnMAPProcessingParameterPalettedRasterLayer(
                name=self.P_CLASSIFICATION1, description='Classification 1'
            )
        )

        self.addParameter(
            EnMAPProcessingParameterPalettedRasterLayer(
                name=self.P_CLASSIFICATION2, description='Classification 2'
            )
        )

        self.addParameter(
            EnMAPProcessingParameterBoolean(
                name=self.P_SHOW_STATISTICS, description='Show Change Matrix'
            )
        )

        self.addParameter(
            EnMAPProcessingParameterRasterDestination(
                name=self.P_OUTRASTER, description='Output Raster'
            )
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):

        layer1: QgsRasterLayer = self.parameter(parameters, self.P_CLASSIFICATION1, context)
        layer2: QgsRasterLayer = self.parameter(parameters, self.P_CLASSIFICATION2, context)
        filename = self.parameter(parameters, self.P_OUTRASTER, context)

        categories1 = Category.fromQgsPalettedRasterRenderer(renderer=layer1.renderer())
        categories2 = Category.fromQgsPalettedRasterRenderer(renderer=layer2.renderer())

        changeMap(
            band1=Raster.open(layer1.source()).band(1),
            band2=Raster.open(layer2.source()).band(1),
            categories1=categories1,
            categories2=categories2,
            filename=filename
        )

        return {self.P_OUTRASTER: filename}

class ChangeMapTable(QMainWindow):
    mTable: QTableWidget
    mUnitUnknown: QComboBox
    mUnitStandard: QComboBox
    mUnitGeographic: QComboBox

    def __init__(self, layer: QgsRasterLayer, parent=None):
        QMainWindow.__init__(self, parent)
        loadUi(join(dirname(__file__), 'changemap.ui'), self)
        self.layer = layer
        self.readData()
        distanceUnit = layer.crs().mapUnits()
        areaUnit = QgsUnitTypes.distanceToAreaUnit(distanceUnit)
        if areaUnit == QgsUnitTypes.AreaUnit.AreaUnknownUnit:
            self.mUnit = self.mUnitUnknown
            self.mUnitStandard.hide()
            self.mUnitGeographic.hide()
        elif areaUnit == QgsUnitTypes.AreaUnit.AreaSquareDegrees:
            self.mUnit = self.mUnitGeographic
            self.mUnitUnknown.hide()
            self.mUnitStandard.hide()
        else:
            self.mUnit = self.mUnitStandard
            self.mUnitUnknown.hide()
            self.mUnitGeographic.hide()
        self.mUnit.currentIndexChanged.connect(self.onUnitChanged)
        self.onUnitChanged(index=0)

    def readData(self):
        self.categories = {
            c.id: c for c in Category.fromQgsPalettedRasterRenderer(renderer=self.layer.renderer())
            if c.name != 'n/a' and c.id != 0
        }
        values, counts = np.unique(gdal.Open(self.layer.source()).ReadAsArray(), return_counts=True)
        assert len(values) == len(self.categories)
        self.xlabels = list()
        self.ylabels = list()
        self.counts = dict()
        for value, count in zip(values, counts):
            category = self.categories[value]
            assert '->' in category.name
            xlabel, ylabel = category.name.split('->')
            if xlabel == '0' or ylabel == '0':
                continue
            if not xlabel in self.xlabels:
                self.xlabels.append(xlabel)
            if not ylabel in self.ylabels:
                self.ylabels.append(ylabel)
            self.counts[(xlabel, ylabel)] = count
        self.mTable.setColumnCount(len(self.xlabels))
        self.mTable.setRowCount(len(self.ylabels))
        self.mTable.setHorizontalHeaderLabels(self.xlabels)
        self.mTable.setVerticalHeaderLabels(self.ylabels)

    def onUnitChanged(self, index: int):
        matrix = np.zeros((len(self.xlabels), len(self.ylabels)))
        for x, xlabel in enumerate(self.xlabels):
            for y, ylabel in enumerate(self.ylabels):
                matrix[x, y] = self.counts.get((xlabel, ylabel), 0)
        if index == 0:  # pixel
            matrix = matrix.astype(np.uint64)
        elif index == 1:  # percentage
            matrix = np.round(matrix / matrix.sum() * 100, 4)
        else:
            areaUnitLabel = f"Area{self.mUnit.currentText().replace(' ', '')}"
            fromUnit: QgsUnitTypes.AreaUnit = QgsUnitTypes.distanceToAreaUnit(self.layer.crs().mapUnits())
            toUnit: QgsUnitTypes.AreaUnit = getattr(QgsUnitTypes.AreaUnit, areaUnitLabel)
            factor = QgsUnitTypes.fromUnitToUnitFactor(fromUnit=fromUnit, toUnit=toUnit)
            xsize = self.layer.rasterUnitsPerPixelX()
            ysize = self.layer.rasterUnitsPerPixelY()
            matrix = np.round(matrix * xsize * ysize * factor, 4)

        for y, values in enumerate(matrix):
            for x, value in enumerate(values):
                if value == 0:
                    value = ''
                else:
                    value = str(value)
                self.mTable.setItem(y, x, QTableWidgetItem(value))
