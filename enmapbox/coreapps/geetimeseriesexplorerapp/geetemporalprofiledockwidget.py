import math
import pickle
import traceback
from math import nan, isnan
from os import remove
from os.path import join, dirname, exists
from tempfile import gettempdir
from typing import Optional, List, Tuple

import ee
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDateTime, QDate, QModelIndex, QSize
from PyQt5.QtGui import QColor, QPen, QBrush, QIcon, QTransform, QPixmap
from PyQt5.QtWidgets import (QPlainTextEdit, QToolButton, QListWidget, QApplication, QSpinBox,
                             QColorDialog, QComboBox, QMainWindow, QCheckBox, QLineEdit,
                             QFileDialog, QListWidgetItem, QWidget)
from qgis.PyQt import uic
from qgis._core import (QgsProject, QgsCoordinateReferenceSystem, QgsPointXY, QgsCoordinateTransform, QgsGeometry,
                        QgsFeature, QgsVectorLayer, QgsMapLayerProxyModel, QgsFields)
from qgis._gui import (QgsDockWidget, QgsFeaturePickerWidget,
                       QgsMapLayerComboBox, QgsFieldComboBox, QgsMessageBar)

import enmapbox.externals.pyqtgraph as pg
from enmapbox import EnMAPBox
from enmapbox.externals.qps.externals.pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from enmapbox.externals.qps.utils import SpatialPoint
from geetimeseriesexplorer.runcmd import runCmd
from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import GeeTimeseriesExplorerDockWidget
from typeguard import typechecked


@typechecked
class GeeTemporalProfileDockWidget(QgsDockWidget):
    mMessageBar: QgsMessageBar
    mIdentify: QToolButton
    mLocation: QLineEdit
    mPan: QToolButton
    mRefresh: QToolButton
    mShowImageLine: QToolButton
    mShowCompositeBox: QToolButton
    mLiveStretch: QCheckBox
    mLiveUpdate: QCheckBox
    mCalculatePercentiles: QToolButton

    mGraphicsLayoutWidget: pg.GraphicsLayoutWidget
    mFirst: QToolButton
    mPrevious: QToolButton
    mNext: QToolButton
    mLast: QToolButton
    mStepValue: QSpinBox
    mStepUnits: QComboBox
    mLegend: QListWidget
    mShowLines: QCheckBox
    mShowPoints: QCheckBox
    mShowInfo: QCheckBox
    mShowId: QCheckBox
    mShowDateTime: QCheckBox
    mSkipNan: QCheckBox
    mLineSize: QSpinBox
    mPointSize: QSpinBox
    mInfoFormat: QComboBox
    mInfoDigits: QSpinBox
    mLayer: QgsMapLayerComboBox
    mField: QgsFieldComboBox
    mFeaturePicker: QgsFeaturePickerWidget
    mDownload: QToolButton

    def __init__(self, enmapBox: EnMAPBox, mainDock: GeeTimeseriesExplorerDockWidget, parent=None):
        QgsDockWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.enmapBox = enmapBox
        self.mainDock = mainDock
        self.legendItemTemplate: QListWidgetItem = self.mLegend.item(0).clone()

        self.mInfoLabelItem = pg.LabelItem(justify='right')
        self.mGraphicsLayoutWidget.addItem(self.mInfoLabelItem)
        self.mPlotWidget: pg.PlotItem = self.mGraphicsLayoutWidget.addPlot(row=1, col=0)
        self.mPlotWidget.showGrid(x=True, y=True, alpha=0.5)
        self.mPlotWidgetMouseMovedSignalProxy = pg.SignalProxy(
            self.mPlotWidget.scene().sigMouseMoved, rateLimit=60, slot=self.onPlotWidgetMouseMoved
        )
        self.mPlotWidgetMouseClickedSignalProxy = pg.SignalProxy(
            self.mPlotWidget.scene().sigMouseClicked, rateLimit=60, slot=self.onPlotWidgetMouseClicked
        )
        #self.mPlotWidget.scene().sigMouseClicked.connect(self.onPlotWidgetMouseClicked)
        self.plotItems = list()
        self.data = None

        # add info line
        self.infoLabelLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#FF09', style=Qt.DashLine))
        self.mPlotWidget.addItem(self.infoLabelLine, ignoreBounds=True)

        # add composite selection box
        pen = pg.mkPen(color='#FF0', style=Qt.SolidLine)
        brush = pg.mkBrush(color='#00F5')
        self.compositeBox = pg.LinearRegionItem(values=[nan, nan], pen=pen, brush=brush)
        self.mPlotWidget.addItem(self.compositeBox, ignoreBounds=True)
        self.compositeBoxLabels = list()
        self.compositeBoxLabels.append(
            pg.InfLineLabel(
                self.compositeBox.lines[0], '', movable=False, position=0.95, rotateAxis=(0, 0), color='#FF0',
                fill='#FF00'
            )
        )
        self.compositeBoxLabels.append(
            pg.InfLineLabel(
                self.compositeBox.lines[1], '', movable=False, position=0.95, rotateAxis=(0, 0), color='#FF0',
                fill='#FF00'
            )
        )
        self.compositeBox.hide()

        # add image selection line
        self.imageLine = pg.InfiniteLine(
            movable=True, angle=90, label='', pen=pg.mkPen(color='#FF0', style=Qt.SolidLine),
            labelOpts={'position': 0.95, 'color': '#FF0', 'fill': '#FF00', 'movable': False}
        )
        self.mPlotWidget.addItem(self.imageLine, ignoreBounds=True)
        #self.imageLine.hide()

        self.mLayer.setLayer(None)
        self.mLayer.setFilters(QgsMapLayerProxyModel.PointLayer)

        # connect signals
        self.mShowCompositeBox.toggled.connect(self.toggleSelectionHandlerVisibility)
        self.mShowImageLine.toggled.connect(self.toggleSelectionHandlerVisibility)
        self.mCalculatePercentiles.clicked.connect(self.onCalculatePercentilesClicked)
        self.mainDock.mImageExplorerTab.currentChanged.connect(self.setSelectionHandlerFromMainDock)
        self.mainDock.mImageId.textChanged.connect(self.setImageLineFromMainDock)
        self.mainDock.mAvailableImages.itemSelectionChanged.connect(self.plotProfile)
        self.mainDock.mCompositeDateStart.dateChanged.connect(self.setCompositeBoxFromMainDock)
        self.mainDock.mCompositeDateEnd.dateChanged.connect(self.setCompositeBoxFromMainDock)

        self.compositeBox.sigRegionChanged.connect(lambda: self.compositeBoxLabels[0].setPosition(0.95))  # fix bug
        self.compositeBox.sigRegionChanged.connect(lambda: self.compositeBoxLabels[1].setPosition(0.95))  # fix bug
        self.compositeBox.sigRegionChanged.connect(self.onCompositeBoxRegionChanged)
        self.compositeBox.lines[0].sigPositionChanged.connect(self.onCompositeBoxRegionChanged)
        self.compositeBox.lines[1].sigPositionChanged.connect(self.onCompositeBoxRegionChanged)
        self.compositeBox.sigRegionChangeFinished.connect(self.onCompositeRegionChangeFinished)

        self.imageLine.sigPositionChanged.connect(self.onImageLinePositionChanged)
        self.imageLine.sigPositionChangeFinished.connect(self.onImageLinePositionChangeFinished)

        self.mLegend.itemChanged.connect(self.plotProfile)
        self.mLegend.doubleClicked.connect(self.onLegendDoubleClicked)
        self.mShowLines.clicked.connect(self.plotProfile)
        self.mShowPoints.clicked.connect(self.plotProfile)
        self.mShowInfo.clicked.connect(self.clearInfo)
        self.mLineSize.valueChanged.connect(self.plotProfile)
        self.mPointSize.valueChanged.connect(self.plotProfile)
        self.mLayer.layerChanged.connect(self.mFeaturePicker.setLayer)
        self.mLayer.layerChanged.connect(self.mField.setLayer)
        self.mField.fieldChanged.connect(self.mFeaturePicker.setDisplayExpression)
        self.mFeaturePicker.featureChanged.connect(self.onFeaturePickerFeatureChanged)
        self.mPan.clicked.connect(self.onPanClicked)
        self.mRefresh.clicked.connect(self.onRefreshClicked)
        self.mDownload.clicked.connect(self.onDownloadClicked)

        self.mFirst.clicked.connect(self.onFirstClicked)
        self.mPrevious.clicked.connect(self.onPreviousClicked)
        self.mNext.clicked.connect(self.onNextClicked)
        self.mLast.clicked.connect(self.onLastClicked)

        self.enmapBox.sigCurrentLocationChanged.connect(self.onCurrentLocationChanged)
        self.mainDock.sigCollectionChanged.connect(self.onCollectionChanged)

        self.toggleSelectionHandlerVisibility()

    def toggleSelectionHandlerVisibility(self):
        if self.mShowImageLine.isChecked():
            self.imageLine.setVisible(True)
            self.compositeBox.setVisible(False)
            self.mainDock.mImageExplorerTab.setCurrentIndex(0)
            self.mStepValue.hide()
            self.mStepUnits.hide()
        if self.mShowCompositeBox.isChecked():
            self.imageLine.setVisible(False)
            self.compositeBox.setVisible(True)
            self.mainDock.mImageExplorerTab.setCurrentIndex(1)
            self.mStepValue.show()
            self.mStepUnits.show()

    def setSelectionHandlerFromMainDock(self):
        if self.mainDock.mImageExplorerTab.currentIndex() == 0:
            self.mShowImageLine.click()
        if self.mainDock.mImageExplorerTab.currentIndex() == 1:
            self.mShowCompositeBox.click()

    def setImageLineFromMainDock(self):
        imageId = self.mainDock.mImageId.text()
        if not self.isDataAvailable():
            return
        try:
            index = self.dataIds().index(imageId)
        except ValueError:
            return
        pos = self.dataDecimalYears()[index]
        self.imageLine.setPos(pos)

        # update layer
        self.onSelectionHandlerChangeFinished()

    def setCompositeBoxFromMainDock(self):
        d1, d2 = self.currentCompositeDateRange()
        pos1 = self.utilsDateTimeToDecimalYear(QDateTime(d1))
        pos2 = self.utilsDateTimeToDecimalYear(QDateTime(d2))

        self.compositeBox.lines[0].blockSignals(True)
        self.compositeBox.lines[1].blockSignals(True)
        self.compositeBox.lines[0].setPos(pos1)
        self.compositeBox.lines[1].setPos(pos2)
        self.compositeBox.lines[0].blockSignals(False)
        self.compositeBox.lines[1].blockSignals(False)
        self.mPlotWidget.update()

        # update layer
        self.onSelectionHandlerChangeFinished()

    def onCalculatePercentilesClicked(self):
        self.mainDock.mCalculatePercentiles.click()
        self.mainDock.mCreateLayer.click()

    def onCreateLayerClicked(self):
        self.mainDock.mCreateLayer.click()

    def onImageLinePositionChanged(self):
        if self.isDataAvailable():
            x, index = self.findClosestImage(self.imageLine.pos().x(), False)
            self.imageLine.setPos(x)
            imageId = self.dataIds()[index]
            self.imageLine.label.setText(imageId)
            self.mainDock.mImageId.blockSignals(True)
            self.mainDock.mImageId.setText(imageId)
            self.mainDock.mImageId.blockSignals(False)

    def onCompositeBoxRegionChanged(self):
        positions = [line.pos().x() for line in self.compositeBox.lines]
        if any(map(isnan, positions)):
            return
        positions = sorted(positions)
        dateTimes = [self.utilsDecimalYearToDateTime(position) for position in positions]
        datestamps = [dateTime.toString('yyyy-MM-dd') for dateTime in dateTimes]
        text = ' to '.join(datestamps)
        self.compositeBoxLabels[0].setText(text)

        # update date range in main dock
        self.mainDock.mCompositeDateStart.blockSignals(True)
        self.mainDock.mCompositeDateEnd.blockSignals(True)
        self.mainDock.mCompositeDateStart.setDate(dateTimes[0].date())
        self.mainDock.mCompositeDateEnd.setDate(dateTimes[1].date())
        self.mainDock.mCompositeDateStart.blockSignals(False)
        self.mainDock.mCompositeDateEnd.blockSignals(False)

    def onImageLinePositionChangeFinished(self):
        self.onSelectionHandlerChangeFinished()

    def onCompositeRegionChangeFinished(self):
        self.onSelectionHandlerChangeFinished()

    def onSelectionHandlerChangeFinished(self):
        if self.mLiveStretch.isChecked():
            self.mCalculatePercentiles.click()
            return

        if self.mLiveUpdate.isChecked():
            self.mainDock.mCreateLayer.click()


    def selectedBandNames(self) -> Optional[List[str]]:
        bandNames = list()
        for i in range(self.mLegend.count()):
            item = self.mLegend.item(i)
            if item.checkState() == Qt.Checked:
                bandNames.append(item.text())
        if len(bandNames) == 0:
            self.pushInfoMissingBand()
            return None
        return bandNames

    def clearInfo(self):
        self.mInfoLabelItem.setText('')
        self.infoLabelLine.setPos(nan)

    def findClosestImage(self, x: float, skipNan: bool) -> Tuple[float, int]:
        xs = np.array(self.dataDecimalYears())
        if skipNan:
            for i in range(self.mLegend.count()):
                item: QListWidgetItem = self.mLegend.item(i)
                if item.checkState() == Qt.Checked:
                    bandName = item.text()
                    ys = self.dataProfile(bandName)
                    if ys is None:
                        continue
                    xs[~np.isfinite(ys)] = nan

        index = int(np.nanargmin(np.abs(np.subtract(xs, x))))
        return xs[index], index

    def onPlotWidgetMouseClicked(self, event):
        if not self.isDataAvailable():
            return

        mousePoint = self._currentMousePoint  # re-use position from mouse move

        if self.mShowImageLine.isChecked():
            x, index = self.findClosestImage(mousePoint.x(), self.mSkipNan.isChecked())
            imageId = self.dataIds()[index]
            self.setImage(imageId)
        if self.mShowCompositeBox.isChecked():
            d1, d2 = self.currentCompositeDateRange()
            days = d1.daysTo(d2)
            dateCenter = self.utilsDecimalYearToDateTime(mousePoint.x()).date()
            dateStart = dateCenter.addDays(-int(days / 2))
            dateEnd = dateStart.addDays(days)
            self.setComposite(dateStart, dateEnd)
            self.onCompositeBoxRegionChanged()

    def onPlotWidgetMouseMoved(self, event):

        # find mouse x value (decimal years)
        pos = event[0]  # using signal proxy turns original arguments into a tuple
        if not self.mPlotWidget.sceneBoundingRect().contains(pos):
            return
        mousePoint = self.mPlotWidget.vb.mapSceneToView(pos)

        self._currentMousePoint = mousePoint  # we store this here for later click events

        if not self.isDataAvailable() or not self.mShowInfo.isChecked():
            self.clearInfo()
            self.mInfoLabelItem.hide()
            return
        else:
            self.mInfoLabelItem.show()

        x, index = self.findClosestImage(mousePoint.x(), self.mSkipNan.isChecked())

        self.infoLabelLine.setPos(x)

        text = f"<span style='font-size: 8pt'>"

        # add datetime
        if self.mShowDateTime.isChecked():
            dateTime: QDateTime = self.dataDateTimes()[index]
            timestamp = dateTime.toString(self.mInfoFormat.currentText())
            text += timestamp + ' — '

        for i in range(self.mLegend.count()):
            item: QListWidgetItem = self.mLegend.item(i)
            if item.checkState() == Qt.Checked:
                bandName = item.text()
                color = item.color
                y = round(self.dataProfile(bandName)[index], self.mInfoDigits.value())
                if self.mInfoDigits.value() == 0:
                    y = int(y)
                text += f" <span style='color: {color.name()}'>{y}</span>"

        if self.mShowId.isChecked():
            text = self.dataIds()[index] + ' — ' + text

        self.mInfoLabelItem.setText(text)

    def onCurrentLocationChanged(self):
        if not self.mIdentify.isChecked():
            return
        crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        point = self.enmapBox.currentLocation().toCrs(crs)
        point = SpatialPoint(crs, point)
        self.setCurrentLocation(point.x(), point.y())
        #self.enmapBox.setCurrentLocation(point)
        self.readProfile()
        self.plotProfile()

    def onRefreshClicked(self):
        self.readProfile()
        self.plotProfile()

    def onCollectionChanged(self):
        self.clearPlot()
        self.clearData()
        self.updateLegend()

        # init image selection line position
        date = self.mainDock.eeFullCollectionJson.temporalInterval()[1]
        x = self.utilsDateTimeToDecimalYear(QDateTime(date))
        self.imageLine.setPos(x)

        # init collection selection box position
        pos1 = self.utilsDateTimeToDecimalYear(QDateTime(self.mainDock.mCompositeDateStart.date()))
        pos2 = self.utilsDateTimeToDecimalYear(QDateTime(self.mainDock.mCompositeDateEnd.date()))

        self.compositeBox.lines[0].blockSignals(True)
        self.compositeBox.lines[1].blockSignals(True)
        self.compositeBox.lines[0].setPos(pos1)
        self.compositeBox.lines[1].setPos(pos2)
        self.compositeBox.lines[0].blockSignals(False)
        self.compositeBox.lines[1].blockSignals(False)
        self.mPlotWidget.update()

    def updateLegend(self):
        defaultColors = [QColor(h)
                         for h in ('#FF0000', '#FFFF00', '#00EAFF', '#AA00FF', '#FF7F00', '#BFFF00', '#0095FF',
                                   '#FF00AA', '#FFD400', '#6AFF00', '#0040FF', '#EDB9B9', '#B9D7ED', '#E7E9B9',
                                   '#DCB9ED', '#B9EDE0', '#8F2323', '#23628F', '#8F6A23', '#6B238F', '#4F8F23',
                                   '#737373', '#CCCCCC')]
        defaultColors.extend([QColor(name) for name in QColor.colorNames() if name not in 'black'])
        colors = self.mainDock.eeFullCollectionInfo.bandColors
        names = self.mainDock.eeFullCollectionInfo.bandNames
        self.mLegend.clear()
        for bandNo, (name, color) in enumerate(zip(names, defaultColors), 1):
            if colors is not None:
                color = QColor(colors.get(name, color))
            item = self.legendItemTemplate.clone()
            item.setText(name)
            item.setCheckState(Qt.Unchecked)
            item.color = color
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            item.setIcon(icon)
            item.setToolTip(self.mainDock.eeFullCollectionJson.bandTooltip(bandNo))
            self.mLegend.addItem(item)

    def currentImageId(self) -> Optional[str]:
        imageId = self.mainDock.mImageId.text()
        if imageId in self.dataIds():
            return imageId
        else:
            return None

    def currentCompositeDateRange(self):
        return self.mainDock.compositeDates()

    def setImage(self, imageId: str):
        self.mainDock.mImageId.setText(imageId)

    def setComposite(self, dateStart: QDate, dateEnd: QDate):
        self.mainDock.mCompositeDateStart.blockSignals(True)
        self.mainDock.mCompositeDateEnd.blockSignals(True)
        self.mainDock.mCompositeDateStart.setDate(dateStart)
        self.mainDock.mCompositeDateEnd.setDate(dateEnd)
        self.mainDock.mCompositeDateStart.blockSignals(False)
        self.mainDock.mCompositeDateEnd.blockSignals(False)

        self.setCompositeBoxFromMainDock()

    def onFirstClicked(self):
        if self.mShowImageLine.isChecked():
            self.setImage(self.dataIds()[0])
        if self.mShowCompositeBox.isChecked():
            d1, d2 = self.currentCompositeDateRange()
            days = d1.daysTo(d2)
            dateStart = self.mainDock.mFilterDateStart.date()
            dateEnd = dateStart.addDays(days)
            self.setComposite(dateStart, dateEnd)

        return
        if self.mStepUnits.currentText() == 'Days':
            pass
        if self.mStepUnits.currentText() == 'Months':
            dateStart = QDate()
        if self.mStepUnits.currentText() == 'Years':
            pass

    def onLastClicked(self):
        if self.mShowImageLine.isChecked():
            self.setImage(self.dataIds()[-1])
        if self.mShowCompositeBox.isChecked():
            d1, d2 = self.currentCompositeDateRange()
            days = d1.daysTo(d2)
            dateEnd = self.mainDock.mFilterDateEnd.date()
            dateStart = dateEnd.addDays(-days)
            self.setComposite(dateStart, dateEnd)

    def onNextClicked(self):
        if self.mShowImageLine.isChecked():
            imageId = self.currentImageId()
            if imageId is None:
                return
            index = self.dataIds().index(imageId) + 1
            if index == len(self.dataIds()):
                return
            self.setImage(self.dataIds()[index])
        if self.mShowCompositeBox.isChecked():
            d1, d2 = self.currentCompositeDateRange()
            step = self.mStepValue.value()
            if self.mStepUnits.currentText() == 'Days':
                dateStart = d1.addDays(step)
                dateEnd = d2.addDays(step)
            elif self.mStepUnits.currentText() == 'Months':
                dateStart = d1.addMonths(step)
                dateEnd = d2.addMonths(step)
            elif self.mStepUnits.currentText() == 'Years':
                dateStart = d1.addYears(step)
                dateEnd = d2.addYears(step)
            else:
                assert 0
            self.setComposite(dateStart, dateEnd)

    def onPreviousClicked(self):
        if self.mShowImageLine.isChecked():
            imageId = self.currentImageId()
            if imageId is None:
                return
            index = self.dataIds().index(imageId) - 1
            if index == 0:
                return
            self.setImage(self.dataIds()[index])
        if self.mShowCompositeBox.isChecked():
            d1, d2 = self.currentCompositeDateRange()
            step = self.mStepValue.value()
            if self.mStepUnits.currentText() == 'Days':
                dateStart = d1.addDays(-step)
                dateEnd = d2.addDays(-step)
            elif self.mStepUnits.currentText() == 'Months':
                dateStart = d1.addMonths(-step)
                dateEnd = d2.addMonths(-step)
            elif self.mStepUnits.currentText() == 'Years':
                dateStart = d1.addYears(-step)
                dateEnd = d2.addYears(-step)
            else:
                assert 0
            self.setComposite(dateStart, dateEnd)


    def onDownloadClicked(self):
        if self.selectedBandNames() is None:
            return
        canceled = self._onSaveVectorPointsPreparePkl()
        if canceled:
            return
        cmdPy = join(dirname(__file__), 'cmd', 'savevectorpointsprofiles.py')
        cmd = rf'python {cmdPy}'
        with GeeWaitCursor():
            runCmd(cmd)
            self.mMessageBar.pushSuccess('Success', 'saved point-vector profiles')

    def _onSaveVectorPointsPreparePkl(self):
        canceled = True
        filenamePkl = join(dirname(__file__), 'cmd', 'parameters.pkl')
        if exists(filenamePkl):
            remove(filenamePkl)

        layer: QgsVectorLayer = self.mPointLayerBrowser.currentLayer()
        if layer is None:
            return canceled

        if self.imageCollection is None:
            return canceled

        evalType = type(self.imageProperties[self.mFilterMetadataName.currentText()])
        imageCollectionInfo = {
            'code': self.mImageCollectionCode.text(),
            'filterDate': self.mFilterDate.isChecked(),
            'filterDateStart': self.mFilterDateStart.date().toString('yyyy-MM-dd'),
            'filterDateEnd': self.mFilterDateEnd.date().addDays(1).toString('yyyy-MM-dd'),
            'filterMetadata': self.mFilterMetadata.isChecked(),
            'filterMetadataName': self.mFilterMetadataName.currentText(),
            'filterMetadataOperator': self.mFilterMetadataOperator.currentText(),
            'filterBands': self.selectedBandNames()
        }
        try:
            imageCollectionInfo['filterMetadataValue'] = evalType(self.mFilterMetadataValue.text())
        except:
            imageCollectionInfo['filterMetadataValue'] = None

        dirnameOutput = QFileDialog.getExistingDirectory(parent=self, directory=gettempdir())
        if dirnameOutput == '':
            return canceled
        scale = self.mReadPointScale.value()
        sourceCrs: QgsCoordinateReferenceSystem = layer.crs()
        destCrs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        fields: QgsFields = layer.fields()
        fieldNames = fields.names()
        argss = list()
        for feature in layer.getFeatures():
            assert isinstance(feature, QgsFeature)
            geometry = QgsGeometry(feature.geometry())
            geometry.transform(tr)
            destPoint: QgsPointXY = geometry.asPoint()
            argss.append(
                (
                    dirnameOutput, imageCollectionInfo, destPoint.x(), destPoint.y(), scale, feature.id(),
                    fieldNames, list(map(str, feature.attributes()))
                )
            )

        # Can't execute Pool.map inside QGIS, so we make an CMD call
        # - prepare args file

        import ee
        dirnameGee = dirname(dirname(ee.__file__))
        numReader = 50
        with open(filenamePkl, 'wb') as f:
            pickle.dump((argss, dirnameGee, numReader), f, protocol=pickle.HIGHEST_PROTOCOL)

        return not canceled

    def utilsTransformProjectCrsToWgs84(self, point: QgsPointXY) -> QgsPointXY:
        QgsCoordinateReferenceSystem = QgsProject.instance().crs()
        tr = QgsCoordinateTransform(
            QgsProject.instance().crs(),
            QgsCoordinateReferenceSystem.fromEpsgId(4326),
            QgsProject.instance()
        )
        geometry = QgsGeometry.fromPointXY(point)
        geometry.transform(tr)
        return geometry.asPoint()

    def utilsTransformWgs84ToProjectCrs(self, point: QgsPointXY) -> QgsPointXY:

        tr = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem.fromEpsgId(4326),
            self.enmapBox.currentMapCanvas().mapSettings().destinationCrs(),
            QgsProject.instance()
        )
        geometry = QgsGeometry.fromPointXY(point)
        geometry.transform(tr)
        return geometry.asPoint()

    def utilsMsecToDateTime(self, msec: int) -> QDateTime:
        return QDateTime(QDate(1970, 1, 1)).addMSecs(int(msec))

    def utilsDateTimeToDecimalYear(self, dateTime: QDateTime) -> float:
        date = dateTime.date()
        secOfYear = QDateTime(QDate(date.year(), 1, 1)).secsTo(dateTime)
        secsInYear = date.daysInYear() * 24 * 60 * 60
        return date.year() + secOfYear / secsInYear

    def utilsDecimalYearToDateTime (self, decimalYear: float) -> QDateTime:
        year = int(decimalYear)
        secsInYear = QDate(year, 1, 1).daysInYear() * 24 * 60 * 60
        secOfYear = int((decimalYear - year) * secsInYear)
        dateTime = QDateTime(QDate(year, 1, 1)).addSecs(secOfYear)
        return dateTime

    def onPanClicked(self):
        point = self.currentLocation()
        if point is None:
            return
        point = self.utilsTransformWgs84ToProjectCrs(point)
        mapCanvas = self.enmapBox.currentMapCanvas()
        if point is not None:
            mapCanvas.setCenter(point)
            mapCanvas.refresh()

    def onFeaturePickerFeatureChanged(self):
        layer: QgsVectorLayer = self.mLayer.currentLayer()
        sourceCrs: QgsCoordinateReferenceSystem = layer.crs()
        destCrs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        feature: QgsFeature = self.mFeaturePicker.feature()
        geometry = QgsGeometry(feature.geometry())
        geometry.transform(tr)
        destPoint: QgsPointXY = geometry.asPoint()
        self.setCurrentLocation(destPoint.x(), destPoint.y())
        self.onPanClicked()
        layer.removeSelection()
        layer.select(feature.id())

        point = SpatialPoint(destCrs, destPoint)
        self.enmapBox.setCurrentLocation(point, self.enmapBox.currentMapCanvas())


    def onShowDataClicked(self):
        if self.data is not None:
            self._dataWindow = QMainWindow(parent=self)
            self._dataWindow.setWindowTitle('Temporal Profile Data')
            self._dataWindow.resize(QSize(800, 600))
            lines = list()
            for line in self.data:
                lines.append(';'.join(map(str, line)))
            text = '\n'.join(lines)
            dataText = QPlainTextEdit(text, parent=self)
            self._dataWindow.setCentralWidget(dataText)
            self._dataWindow.show()

    def onLegendDoubleClicked(self, index: QModelIndex):
        bandItem = self.mLegend.item(index.row())
        currentColor = bandItem.color
        color = QColorDialog.getColor(initial=currentColor, parent=self)
        if color.name() != QColor(0, 0, 0).name():
            bandItem.color = color
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            bandItem.setIcon(icon)
            self.plotProfile()

    def currentLocation(self) -> Optional[QgsPointXY]:
        try:
            point = QgsPointXY(*map(float, self.mLocation.text().split(',')))
        except:
            self.mMessageBar.pushInfo('Missing parameter', 'location is invalid')
            point = None
        return point

    def setCurrentLocation(self, x: float, y: float, ndigits=5):
        self.mLocation.setText(str(round(x, ndigits)) + ', ' + str(round(y, ndigits)))

    def eePoint(self) -> Optional[ee.Geometry]:
        point = self.currentLocation()
        if point is None:
            return None
        eePoint = ee.Geometry.Point([point.x(), point.y()])
        return eePoint

    def readProfile(self):
        eePoint = self.eePoint()
        if eePoint is None:
            return

        eeCollection = self.mainDock.eeCollection()
        if eeCollection is None:
            self.pushInfoMissingCollection()

        bandNames = self.selectedBandNames()
        if bandNames is None:
            return

        eeCollection = eeCollection.select(bandNames)

        scale = self.mainDock.eeFullCollectionJson.groundSamplingDistance()
        with GeeWaitCursor():
            try:
                data = eeCollection.getRegion(eePoint, scale=scale).getInfo()
            except Exception as error:
                if str(error) == 'ImageCollection.getRegion: No bands in collection.':
                    self.pushInfoEmptyQueryResults()
                else:
                    self.pushRequestError(error)
                    self.setData(None)
                return
        self.setData(data)

    def clearData(self):
        self.header = None
        self.data = None

    def setData(self, data):
        self.header: List[str] = data[0]

        # sort data by time
        data = data[1:]
        msecs = np.array([row[3] for row in data])
        argsort = np.argsort(msecs)

        # prepare data
        self.data = [data[i] for i in argsort]
        self._dataMsecs = np.array([row[3] for row in self.data])

        self._dataIds = [row[0] for row in self.data]

        self._dataDateTimes = [self.utilsMsecToDateTime(int(msec)) for msec in self.dataMsecs()]
        self._dataDecimalYears = np.array([self.utilsDateTimeToDecimalYear(dateTime)
                                           for dateTime in self.dataDateTimes()])
        self._dataProfile = dict()
        for index, bandName in enumerate(self.header[4:], 4):
            bandNo = self.mainDock.eeFullCollectionInfo.bandNames.index(bandName)
            # todo scale data at collection level, not only when sampling profiles!
            offset = self.mainDock.eeFullCollectionJson.bandOffset(bandNo)
            scale = self.mainDock.eeFullCollectionJson.bandScale(bandNo)
            if offset is None:
                offset = 0
            if scale is None:
                scale = 1

            values = list()
            for row in self.data:
                value = row[index]
                if value is None:
                    value = nan
                else:
                    # scale to reflectance
                    if scale is not None:
                        value = value * scale
                    if offset is not None:
                        value = value + offset
                values.append(value)
            self._dataProfile[bandName] = np.array(values)

    def isDataAvailable(self) -> bool:
        return self.data is not None

    def dataN(self):
        return len(self._dataIds)

    def dataIds(self) -> List[str]:
        return self._dataIds

    def dataMsecs(self) -> np.array:
        return self._dataMsecs

    def dataDateTimes(self) -> List[QDateTime]:
        return self._dataDateTimes

    def dataDecimalYears(self) -> np.array:
        return self._dataDecimalYears

    def dataProfile(self, bandName: str) -> Optional[np.array]:
        return self._dataProfile.get(bandName)

    def clearPlot(self):
        for plotItem in self.plotItems:
            self.mPlotWidget.blockSignals(True)
            self.mPlotWidget.removeItem(plotItem)
            self.mPlotWidget.blockSignals(False)
        self.pgProfile = list()

    def plotProfile(self):
        self.clearPlot()

        if not self.isDataAvailable():
            return

        # find images that are selected in the available images list
        selectionFlags = np.full((self.dataN(), ), False, bool)
        modelIndex: QModelIndex
        for modelIndex in self.mainDock.mAvailableImages.selectedIndexes():
            imageId = self.mainDock.mAvailableImages.item(modelIndex.row(), 0).data(Qt.DisplayRole)
            try:
                selectionFlags[self.dataIds().index(imageId)] = True
            except:
                pass
        skipSelection = not any(selectionFlags)

        x = np.array(self.dataDecimalYears())
        for i in range(self.mLegend.count()):
            item: QListWidgetItem = self.mLegend.item(i)
            bandName = item.text()
            if item.checkState() == Qt.Checked:
                color = item.color
                y = self.dataProfile(bandName)

                if self.mShowLines.isChecked():
                    plotLine: pg.PlotDataItem = self.mPlotWidget.plot(x, y)
                    pen = QPen(QBrush(color), self.mLineSize.value())
                    pen.setCosmetic(True)
                    plotLine.setPen(pen)
                    self.plotItems.append(plotLine)

                # plot selected images
                if not skipSelection:
                    selectionColor = '#FF0'
                    plotSelection: pg.PlotDataItem = self.mPlotWidget.plot(x[selectionFlags], y[selectionFlags])
                    plotSelection.setSymbol('o')  # ['t', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'o']
                    plotSelection.setSymbolBrush(selectionColor)
                    plotSelection.setSymbolPen(selectionColor)
                    symbolSize = self.mPointSize.value() * 2
                    if (self.mPointSize.value() % 2) == 1:
                        symbolSize += 1
                    plotSelection.setSymbolSize(symbolSize)
                    plotSelection.setPen(None)
                    self.plotItems.append(plotSelection)

                if self.mShowPoints.isChecked():
                    plotPoints: pg.PlotDataItem = self.mPlotWidget.plot(x, y)
                    plotPoints.setSymbol('o')  # ['t', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'o']
                    plotPoints.setSymbolBrush(color)
                    plotPoints.setSymbolPen(color)
                    plotPoints.setSymbolSize(self.mPointSize.value())
                    plotPoints.setPen(None)
                    self.plotItems.append(plotPoints)




    def pushInfoMissingCollection(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a collection')

    def pushInfoMissingBand(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a band')

    def pushRequestError(self, error: Exception):
        self.mMessageBar.pushCritical('Request error', str(error))
        traceback.print_exc()

    def pushInfoEmptyQueryResults(self):
        self.mMessageBar.pushInfo('Query result', 'no images found')


class GeeWaitCursor(object):

    def __enter__(self):
        QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))

    def __exit__(self, exc_type, exc_value, tb):
        QApplication.restoreOverrideCursor()

