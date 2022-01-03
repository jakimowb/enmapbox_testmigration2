import pickle
import traceback
from math import nan, isnan
from os import remove, makedirs
from os.path import join, dirname, exists
from tempfile import gettempdir
from time import time
from typing import Optional, List, Tuple, Dict

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDateTime, QDate, QModelIndex, QPoint, QRectF, QStandardPaths, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QIcon, QPixmap
from PyQt5.QtWidgets import (QToolButton, QListWidget, QApplication, QSpinBox,
                             QColorDialog, QComboBox, QCheckBox, QLineEdit,
                             QFileDialog, QListWidgetItem, QSlider, QTableWidget, QLabel, QMenu, QAction, QProgressBar,
                             QDoubleSpinBox, QAbstractItemView)
from qgis.PyQt import uic
from qgis._core import (QgsProject, QgsCoordinateReferenceSystem, QgsPointXY, QgsCoordinateTransform, QgsGeometry,
                        QgsFeature, QgsVectorLayer, QgsMapLayerProxyModel, QgsFields, QgsTask, QgsTaskManager,
                        QgsApplication)
from qgis._gui import (QgsDockWidget, QgsFeaturePickerWidget,
                       QgsMapLayerComboBox, QgsFieldComboBox, QgsMessageBar, QgsColorButton, QgsFileWidget)
from sklearn.svm import SVR

import ee
import enmapbox.externals.pyqtgraph as pg
from enmapbox import EnMAPBox
from enmapbox.externals.qps.utils import SpatialPoint
from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from enmapboxprocessing.utils import Utils
from geetimeseriesexplorerapp.tasks.downloadimagechiptask import DownloadImageChipTask, DownloadImageChipBandTask
from geetimeseriesexplorerapp.geetimeseriesexplorerdockwidget import GeeTimeseriesExplorerDockWidget
from geetimeseriesexplorerapp.tasks.downloadprofiletask import DownloadProfileTask
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
    mStretchAndUpdateLayer: QToolButton

    mGraphicsLayoutWidget: pg.GraphicsLayoutWidget
    mFirst: QToolButton
    mPrevious: QToolButton
    mNext: QToolButton
    mLast: QToolButton
    mStepValue: QSpinBox
    mStepUnits: QComboBox
    mExplodeLayers: QToolButton
    mProgressBar: QProgressBar
    mCancelTaskManager: QToolButton

    # legend
    mLegend: QListWidget

    # symbology
    mShowLegend: QCheckBox

    mShowLines: QCheckBox
    mLineSize: QSpinBox

    mShowPoints: QCheckBox
    mPointSize: QSpinBox

    mShowInfo: QCheckBox
    mShowId: QCheckBox
    mShowDateTime: QCheckBox
    mSkipNan: QCheckBox
    mInfoFormat: QComboBox
    mInfoDigits: QSpinBox

    mShowImageSelection: QCheckBox
    mImageSelectionColor: QgsColorButton
    mImageSelectionOpacity: QSlider
    mImageSelectionSize: QSpinBox

    # analytics
    mShowFittedLine: QCheckBox
    mFittedLineSize: QSpinBox
    mUseFittedLineColor: QCheckBox
    mFittedLineColor: QgsColorButton
    mSvrParameters: QTableWidget
    mLiveUpdateFittedLine: QCheckBox
    mUpdateFittedLine: QToolButton

    # location browser
    mLayer: QgsMapLayerComboBox
    mField: QgsFieldComboBox
    mFeaturePicker: QgsFeaturePickerWidget
    mDownloadFolder: QgsFileWidget
    mDownloadLocationChips: QToolButton
    mDownloadLayerProfiles: QToolButton
    mDownloadLayerChips: QToolButton

    # profile data
    mData: QTableWidget

    sigCurrentLocationChanged = pyqtSignal()

    def __init__(self, mainDock: GeeTimeseriesExplorerDockWidget, parent=None):
        QgsDockWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.mainDock = mainDock
        self.legendItemTemplate: QListWidgetItem = self.mLegend.item(0).clone()
        self.cache = dict()
        self.refs = list()  # keep refs to prevent crashes

        # task manager
        #self.taskManager = QgsTaskManager()  # using this manager gives me crashes, when connected to a progress bar
        self.taskManager = QgsApplication.taskManager()
        self.taskManager.taskAdded.connect(self.mProgressBarFrame.show)
        self.taskManager.allTasksFinished.connect(self.mProgressBarFrame.hide)
        self.mCancelTaskManager.clicked.connect(self.taskManager.cancelAll)
        self.mProgressBarFrame.hide()

        # location
        self.mLocation.textChanged.connect(self.sigCurrentLocationChanged)

        # plot
        self.mInfoLabelItem = pg.LabelItem(justify='right')
        self.mGraphicsLayoutWidget.addItem(self.mInfoLabelItem)
        self.mPlotWidget: pg.PlotItem = self.mGraphicsLayoutWidget.addPlot(row=1, col=0)
        self.mPlotWidget.showGrid(x=True, y=True, alpha=0.5)
        self.mPlotWidget.addLegend()
        self.mPlotWidget.legend.setOffset((0.3, 0.3))
        self.mPlotWidgetMouseMovedSignalProxy = pg.SignalProxy(
            self.mPlotWidget.scene().sigMouseMoved, rateLimit=60, slot=self.onPlotWidgetMouseMoved
        )
        self.mPlotWidgetMouseClickedSignalProxy = pg.SignalProxy(
            self.mPlotWidget.scene().sigMouseClicked, rateLimit=60, slot=self.onPlotWidgetMouseClicked
        )
        self.plotItems = list()
        self.data = None
        self.highlightedImages = None
        self.ignoreOnDataSelectionChanged = False

        # - add info line
        self.infoLabelLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#FF09', style=Qt.DashLine))
        self.mPlotWidget.addItem(self.infoLabelLine, ignoreBounds=True)

        # - add composite selection box
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

        # - add image selection line
        self.imageLine = pg.InfiniteLine(
            movable=True, angle=90, label='', pen=pg.mkPen(color='#FF0', style=Qt.SolidLine),
            labelOpts={'position': 0.95, 'color': '#FF0', 'fill': '#FF00', 'movable': False}
        )
        self.mPlotWidget.addItem(self.imageLine, ignoreBounds=True)

        # location browser
        self.mLayer.setLayer(None)
        self.mLayer.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mDownloadFolder.setFilePath(
            join(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation), 'GEETSE')
        )

        # data
        #self.mData.itemSelectionChanged.connect(self.onDataSelectionChanged)
        self.mData.selectionModel().selectionChanged.connect(self.onDataSelectionChanged)

        # analytics
        gamma = QSpinBox()
        gamma.setRange(-20, 20)
        gamma.setValue(0)
        gamma.setPrefix('2^')
        gamma.valueChanged.connect(self.plotProfile)
        self.mSvrParameters.setCellWidget(0, 1, gamma)
        C = QSpinBox()
        C.setRange(-20, 20)
        C.setValue(0)
        C.setPrefix('2^')
        C.valueChanged.connect(self.plotProfile)
        self.mSvrParameters.setCellWidget(1, 1, C)
        epsilon = QLineEdit('0')
        epsilon.textChanged.connect(self.plotProfile)
        self.mSvrParameters.setCellWidget(2, 1, epsilon)

        # connect signals
        self.mShowCompositeBox.toggled.connect(self.toggleSelectionHandlerVisibility)
        self.mShowImageLine.toggled.connect(self.toggleSelectionHandlerVisibility)
        self.mStretchAndUpdateLayer.clicked.connect(self.mainDock.mStretchAndUpdateLayer.click)
        self.mainDock.mImageExplorerTab.currentChanged.connect(self.setSelectionHandlerFromMainDock)
        self.mainDock.mImageId.textChanged.connect(self.setImageIdFromMainDock)

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
        self.mShowLegend.clicked.connect(self.plotProfile)
        self.mShowLines.clicked.connect(self.plotProfile)
        self.mShowPoints.clicked.connect(self.plotProfile)
        self.mShowInfo.clicked.connect(self.clearInfo)
        self.mLineSize.valueChanged.connect(self.plotProfile)
        self.mPointSize.valueChanged.connect(self.plotProfile)
        self.mShowImageSelection.clicked.connect(self.plotProfile)
        self.mImageSelectionColor.colorChanged.connect(self.plotProfile)
        self.mImageSelectionOpacity.valueChanged.connect(self.plotProfile)
        self.mImageSelectionSize.valueChanged.connect(self.plotProfile)
        self.mShowFittedLine.clicked.connect(self.plotProfile)
        self.mFittedLineSize.valueChanged.connect(self.plotProfile)
        self.mUseFittedLineColor.clicked.connect(self.plotProfile)
        self.mFittedLineColor.colorChanged.connect(self.plotProfile)
        self.mSvrParameters.cellChanged.connect(self.onSvrParametersChanged)
        self.mUpdateFittedLine.clicked.connect(self.plotProfile)

        self.mLayer.layerChanged.connect(self.mFeaturePicker.setLayer)
        self.mLayer.layerChanged.connect(self.mField.setLayer)
        self.mField.fieldChanged.connect(self.mFeaturePicker.setDisplayExpression)
        self.mFeaturePicker.featureChanged.connect(self.onFeaturePickerFeatureChanged)
        self.mDownloadLayerProfiles.clicked.connect(self.onDownloadLayerProfilesClicked)
        self.mDownloadLayerChips.clicked.connect(self.onDownloadLayerChipsClicked)
        self.mDownloadLocationChips.clicked.connect(self.onDownloadLocationChipsClicked)

        self.mPan.clicked.connect(self.onPanClicked)
        self.mRefresh.clicked.connect(self.onRefreshClicked)
        self.mData.customContextMenuRequested.connect(self.onDataContextMenuEvent)
        self.mFirst.clicked.connect(self.onFirstClicked)
        self.mPrevious.clicked.connect(self.onPreviousClicked)
        self.mNext.clicked.connect(self.onNextClicked)
        self.mLast.clicked.connect(self.onLastClicked)
        self.mExplodeLayers.clicked.connect(self.onExplodeLayers)

        self.sigCurrentLocationChanged.connect(self.onCurrentLocationChanged)
        self.mainDock.sigCollectionChanged.connect(self.onCollectionChanged)

        self.toggleSelectionHandlerVisibility()

        # do we need those?
        self.mStretchAndUpdateLayer.hide()
        self.mLiveUpdate.hide()

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

    def clearHighlightedImages(self):
        self.highlightedImages = None

    def setHighlightedImagesFromMainDock(self):

        if not self.isDataAvailable():
            return

        # prepare data for faster plotting
        self.highlightedImages = np.full((self.dataN(),), False, bool)
        indexById = self.dataIndexByImageId()
        imageIds = [indexById[values[0]] for values in self.mainDock.availableImagesData[1]]
        selectedRows: List[QModelIndex] = self.mainDock.mAvailableImages.selectionModel().selectedRows()
        for modelIndex in selectedRows:
            self.highlightedImages[imageIds[modelIndex.row()]] = True

        # update data selection
        self.mData.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ignoreOnDataSelectionChanged = True
        self.mData.clearSelection()
        for modelIndex in selectedRows:
            self.mData.selectRow(modelIndex.row())
        self.mData.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ignoreOnDataSelectionChanged = False

        self.plotProfile()

    def setImageIdFromMainDock(self):
        imageId = self.mainDock.mImageId.text()

        if not self.isDataAvailable():
            return
        try:
            index = self.dataIds().index(imageId)
        except ValueError:
            return
        pos = self.dataDecimalYears()[index]
        self.imageLine.setPos(pos)

        # update selection
        row = self.dataIndexByImageId()[self.mainDock.mImageId.text()]
        self.mData.selectionModel().blockSignals(True)
        self.mData.selectRow(row)
        self.mData.selectionModel().blockSignals(False)

    def onCreateImageChipTaskCompleted(self, task: 'DownloadImageChipTask'):
        mapDock = self.imageChipMapDock()
        if mapDock is None:
            return

        if self.currentCreateImageChipTask is not task:
            return

        mapDock.setCenter(task.location)
        mapDock.setLayer(task.layer.clone())
        mapDock.mapCanvas().refresh()

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
        pass

    def selectedBandNames(self) -> Optional[List[str]]:
        bandNames = list()
        for i in range(self.mLegend.count()):
            item = self.mLegend.item(i)
            if item.checkState() == Qt.Checked:
                bandNames.append(item.text())
        if len(bandNames) == 0:
            # self.pushInfoMissingBand()
            return None
        return bandNames

    def selectedBandNumbers(self) -> Optional[List[int]]:
        bandNumbers = list()
        for i in range(self.mLegend.count()):
            item = self.mLegend.item(i)
            if item.checkState() == Qt.Checked:
                bandNumbers.append(i + 1)
        if len(bandNumbers) == 0:
            return None
        return bandNumbers

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

        try:
            index = int(np.nanargmin(np.abs(np.subtract(xs, x))))
            pos = xs[index]
        except ValueError:
            pos = nan
            index = -1

        return pos, index

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
        if isnan(x):
            return

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
                if bandName not in self._dataProfile:
                    continue
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
        point = self.mainDock.currentLocation().toCrs(crs)
        point = SpatialPoint(crs, point)
        self.setCurrentLocation(point.x(), point.y())
        self.readProfile()
        self.plotProfile()

    def onRefreshClicked(self):
        self.readProfile()
        self.plotProfile()

    def onSvrParametersChanged(self):
        if self.mLiveUpdateFittedLine.isChecked():
            self.mUpdateFittedLine.click()

    def onDataSelectionChanged(self):

        if self.ignoreOnDataSelectionChanged:
            return

        self.clearHighlightedImages()

        self.mainDock.mAvailableImages.blockSignals(True)
        self.mainDock.mAvailableImages.setSelectionMode(QAbstractItemView.MultiSelection)
        self.mainDock.mAvailableImages.clearSelection()
        for index in self.mData.selectionModel().selectedRows():
            self.mainDock.mAvailableImages.selectRow(index.row())
        self.mainDock.mAvailableImages.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.mainDock.mAvailableImages.blockSignals(False)
        self.mainDock.onAvailableImagesSelectionChanged()

    def onCollectionChanged(self):
        self.clearPlot()
        self.clearData()
        self.updateLegend()
        self.tabWidget.setCurrentIndex(0)  # show bands

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

        colors = self.mainDock.eeFullCollectionInfo.bandColors  # includes band and si colors

        bandNames = self.mainDock.eeFullCollectionInfo.bandNames
        bandToolTips = [self.mainDock.eeFullCollectionJson.bandTooltip(bandNo)
                        for bandNo in range(1, len(bandNames) + 1)]
        spectralIndices = self.mainDock.selectedSpectralIndices()
        siNames = [si['short_name'] for si in spectralIndices]
        # make some pretty toolTips
        siToolTips = list()
        for si in spectralIndices:
            bands = set(si['bands']).intersection(set(CreateSpectralIndicesAlgorithm.WavebandMapping.keys()))
            bandsText = 'with ' + \
                        ', '.join([f'{key} = {self.mainDock.eeFullCollectionInfo.wavebandMapping[key]}'
                                   for key in bands]) + '\n'
            constants = set(si['bands']).intersection(set(CreateSpectralIndicesAlgorithm.ConstantMapping.keys()))
            constantsText = 'and ' + ', '.join([f'{key} = {CreateSpectralIndicesAlgorithm.ConstantMapping[key]}'
                                                for key in constants]) + '\n'

            long_name = si['long_name']
            short_name = si['short_name']
            formula = si['formula']
            reference = si['reference']
            toolTip = f'<html><head/><body><p><span style=" font-weight:600;">{long_name}</span></p>' \
                      f'<p><span style=" font-weight:600;">{short_name}</span> = {formula}</p>' \
                      f'<p><span style=" color:#808080;">{bandsText}'
            if len(constants) > 0:
                toolTip += f'<br/>          ' \
                           f'{constantsText}</span>'
            toolTip += f'</p><p>Reference: {reference}</p></body></html>'
            siToolTips.append(toolTip)

        self.mLegend.clear()
        for name, color, toolTip in zip(bandNames + siNames, defaultColors, bandToolTips + siToolTips):
            color = QColor(colors.get(name, color))
            item = self.legendItemTemplate.clone()
            item.setText(name)
            item.setCheckState(Qt.Unchecked)
            item.color = color
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            item.setIcon(icon)
            toolTip += '\n(double-click to change color)'
            item.setToolTip(toolTip)
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
            if self.mSkipNan.isChecked():
                valid = list(np.all(np.isfinite(list(self._dataProfile.values())), axis=0))
                for index in range(index, self.dataN()):
                    if valid[index]:
                        break
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
            if self.mSkipNan.isChecked():
                valid = list(np.all(np.isfinite(list(self._dataProfile.values())), axis=0))
                for index in range(index, -1, -1):
                    if valid[index]:
                        break
            if index == -1:
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

    def onExplodeLayers(self):
        # just walk over every observation using the navigation buttons

        oldAppendIdChecked = self.mainDock.mAppendId.isChecked()
        self.mainDock.mAppendId.setChecked(True)

        self.onFirstClicked()
        for i in range(self.dataN() - 1):
            QApplication.processEvents()
            self.onNextClicked()

            #if self.mainDock.mStretchAndUpdateLayer.is



        self.mainDock.mAppendId.setChecked(oldAppendIdChecked)

    def downloadFilenameProfile(self, feature: QgsFeature, eeCollection: ee.ImageCollection):

        location: QgsPointXY = feature.geometry().asPoint()


        collectionId = self.mainDock.eeFullCollectionJson.id().replace('/', '_')
        filename = join(
            self.currentDownloadFolder(),
            'profiles',
            collectionId,
            str(hash(eeCollection.serialize())),
            'X%018.13f_Y%018.13f' % (location.x(), location.y()) + '.json'
        )
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        return filename

        #point: QgsPointXY = feature.geometry().asPoint()
        #pointState = point.x(), point.y()
        #collectionState = eeCollection.serialize()
        #key = f'location{hash(pointState)}_profile{hash(collectionState)}'.replace('-', '0')
        #return join(self.currentDownloadFolder(), key + '.json')

    def onDownloadLocationChipsClicked(self):
        bandNames = self.mainDock.currentImageChipBandNames()
        if bandNames is None:
            self.pushInfoMissingBand()
            return
        if self.isDataAvailable():
            imageIds = self.dataIds()
        else:
            eePoint = self.eePoint()
            eeCollection = self.mainDock.eeCollection(False, True, True, False)
            if eeCollection is None:
                self.pushInfoMissingCollection()
                return
            imageIds = eeCollection.filterBounds(eePoint)\
                .toList(999999) \
                .map(lambda eeImage: ee.Image(eeImage).get('system:index'))\
                .getInfo()

        #imageIds = imageIds[0:2]

        location = self.currentLocation()
        for imageId in imageIds:
            #eeImage = self.mainDock.eeFullCollection.filter(ee.Filter.eq('system:index', imageId)).first()
            eeImage, *_ = self.mainDock.eeImage(imageId)

            alreadyExists = True
            subFilenames = list()
            subTasks = list()
            for bandName in bandNames:
                subFilename = self.mainDock.downloadFilenameImageChipBandTif(location, imageId, bandName)
                subFilenames.append(subFilename)
                subTasks.append(DownloadImageChipBandTask(subFilename, location, eeImage, bandName))
                alreadyExists &= exists(subFilename)
            mainFilename = self.mainDock.downloadFilenameImageChipVrt(location, imageId, bandNames)
            alreadyExists &= exists(mainFilename)

            if alreadyExists:
                continue

            if not exists(dirname(mainFilename)):
                makedirs(mainFilename)

            # create task
            mainTask = DownloadImageChipTask(mainFilename, subFilenames, location)
            for subTask in subTasks:
                mainTask.addSubTask(subTask, [], QgsTask.ParentDependsOnSubTask)
                #subTask.run()

            #mainTask.run()
            self.taskManager.addTask(mainTask)

            # not sure if we need to keep the refs
            self.refs.append(mainTask)
            self.refs.append(subTasks)


    def onDownloadLayerChipsClicked(self, *args, onlySelected=False, updateUi=False):
        assert 0
        bandNames = self.mainDock.currentImageChipBandNames()
        layer: QgsVectorLayer = self.mLayer.currentLayer()
        if bandNames is None:
            self.pushInfoMissingBand()
            return
        if layer is None:
            self.pushInfoMissingLayer()
            return

        features = list(layer.getFeatures())
        n = len(features)
        if n == 0:
            return

        for feature in features:
            assert isinstance(feature, QgsFeature)
            location  = SpatialPoint(layer.crs(), QgsGeometry(feature.geometry()).asPoint())
            filenames = list()
            subTasks = list()
            for bandName in bandNames:
                pass

    def onDownloadLayerProfilesClicked(self, *args, onlySelected=False, updateUi=False):
        bandNames = self.selectedBandNames()
        folder = self.currentDownloadFolder()
        layer: QgsVectorLayer = self.mLayer.currentLayer()
        if bandNames is None:
            self.pushInfoMissingBand()
            return
        if folder == '':
            if onlySelected:
                return
            else:
                self.pushInfoMissingDownloadFolder()
            return
        if layer is None:
            self.pushInfoMissingLayer()
            return

        bandNumbers = self.selectedBandNumbers()
        eeCollection = self.mainDock.eeCollection()
        if eeCollection is None:
            return
        eeCollection = eeCollection.select(bandNames)
        scale = self.mainDock.eeFullCollectionJson.groundSamplingDistance()
        offsets = [self.mainDock.eeFullCollectionJson.bandOffset(bandNo) for bandNo in bandNumbers]
        scales = [self.mainDock.eeFullCollectionJson.bandScale(bandNo) for bandNo in bandNumbers]

        if onlySelected:
            features = list(layer.selectedFeatures())
        else:
            features = list(layer.getFeatures())
        n = len(features)
        if n == 0:
            return

        for feature in features:
            assert isinstance(feature, QgsFeature)
            point: QgsPointXY = QgsGeometry(feature.geometry()).asPoint()
            point = self.utilsTransformCrsToWgs84(point, layer.crs())
            eePoint = ee.Geometry.Point([point.x(), point.y()])
            filename = self.downloadFilenameProfile(feature, eeCollection)
            task = DownloadProfileTask(filename, eePoint, eeCollection, scale, offsets, scales)
            if updateUi:
                task.taskCompleted.connect(lambda: self.onDownloadProfileTaskCompleted(task))
            self.taskManager.addTask(task)

            self.refs.append(task)

    def onDownloadProfileTaskCompleted(self, task: DownloadProfileTask):

        if self.cache.get('currentDownloadProfileTask') is not task:  # ignore outdated task
            return

        data = task.data()
        if data is None:
            self.clearData()
        else:
            self.setData(data)
        self.plotProfile()

    def onDataContextMenuEvent(self, position: QPoint):
        self.menu = QMenu()

        def copyData():
            if self.isDataAvailable():
                header = [self.mData.horizontalHeaderItem(i).text() for i in range(self.mData.columnCount())]
                data = list()
                for row in range(self.mData.rowCount()):
                    data.append([])
                    for column in range(self.mData.columnCount()):
                        data[row].append(self.mData.cellWidget(row, column).text())
                data.insert(0, header)
                text = '\n'.join([';'.join(values) for values in data])
            else:
                text = ''
            QApplication.clipboard().setText(text)

        def selectAll():
            self.mData.blockSignals(True)
            self.mData.selectAll()
            self.mData.blockSignals(False)
            self.onDataSelectionChanged()

        def deselectAll():
            self.mData.blockSignals(True)
            self.mData.clearSelection()
            self.mData.blockSignals(False)
            self.onDataSelectionChanged()

        action = QAction('Select All', self)
        action.triggered.connect(selectAll)
        self.menu.addAction(action)

        action = QAction('Deselect All', self)
        action.triggered.connect(deselectAll)
        self.menu.addAction(action)

        self.menu.addSection('TEST')

        action = QAction('Copy Data to Clipboard', self)
        action.triggered.connect(copyData)
        self.menu.addAction(action)

        self.menu.exec_(self.mData.mapToGlobal(position))

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

    def utilsTransformCrsToWgs84(self, point: QgsPointXY, crs: QgsCoordinateReferenceSystem) -> QgsPointXY:
        tr = QgsCoordinateTransform(crs, QgsCoordinateReferenceSystem.fromEpsgId(4326), QgsProject.instance())
        geometry = QgsGeometry.fromPointXY(point)
        geometry.transform(tr)
        return geometry.asPoint()

    def utilsTransformProjectCrsToWgs84(self, point: QgsPointXY) -> QgsPointXY:
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
            self.mainDock.currentMapCanvas().mapSettings().destinationCrs(),
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

    def utilsDecimalYearToDateTime(self, decimalYear: float) -> QDateTime:
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
        mapCanvas = self.mainDock.currentMapCanvas()
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

        self.onDownloadLayerProfilesClicked(onlySelected=True, updateUi=True)

        point = SpatialPoint(destCrs, destPoint)
        self.setCurrentLocation(point.x(), point.y())

        if self.mainDock.enmapBox is not None:
            self.mainDock.enmapBox.currentMapCanvas().setCrosshairPosition(point, True)

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

    def currentDataScaling(self) -> Tuple[List[float], List[float]]:
        bandNumbers = self.selectedBandNumbers()
        if self.mainDock.mScaleBands.isChecked():
            offsets = [self.mainDock.eeFullCollectionJson.bandOffset(bandNo) for bandNo in bandNumbers]
            scales = [self.mainDock.eeFullCollectionJson.bandScale(bandNo) for bandNo in bandNumbers]
        else:
            offsets = [0] * len(bandNumbers)
            scales = [1] * len(bandNumbers)
        return offsets, scales

    def currentLocation(self) -> SpatialPoint:
        try:
            point = SpatialPoint(self.mainDock.crsEpsg4326, QgsPointXY(*map(float, self.mLocation.text().split(','))))
        except:
            mapCenter = self.mainDock.currentMapCanvas().center()
            point = SpatialPoint(self.mainDock.crsEpsg4326, mapCenter)
        return point

    def currentDownloadFolder(self) -> str:
        return self.mDownloadFolder.filePath()

    def setCurrentLocation(self, x: float, y: float, ndigits=5):
        self.mLocation.setText(str(round(x, ndigits)) + ', ' + str(round(y, ndigits)))

    def setCurrentLocationFromEnmapBox(self):
        point = self.mainDock.enmapBox.currentLocation().toCrs(self.mainDock.crsEpsg4326)
        self.setCurrentLocation(point.x(), point.y())

    def eePoint(self) -> Optional[ee.Geometry]:
        point = self.currentLocation()
        eePoint = ee.Geometry.Point([point.x(), point.y()])
        return eePoint

    def readProfile(self):

        self.clearHighlightedImages()

        eePoint = self.eePoint()
        if eePoint is None:
            return

        bandNames = self.selectedBandNames()
        if bandNames is None:
            return

        eeCollection = self.mainDock.eeCollection()
        if eeCollection is None:
            return

        eeCollection = eeCollection.select(bandNames)
        scale = self.mainDock.eeFullCollectionJson.groundSamplingDistance()
        offsets, scales = self.currentDataScaling()

        task = DownloadProfileTask(None, eePoint, eeCollection, scale, offsets, scales)
        self.cache['currentDownloadProfileTask'] = task
        task.taskCompleted.connect(lambda: self.onDownloadProfileTaskCompleted(task))
        self.taskManager.addTask(task)

        self.refs.append(task)

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
        self._dataIndexById = {imageId: i for i, imageId in enumerate(self._dataIds)}

        self._dataDateTimes = [self.utilsMsecToDateTime(int(msec)) for msec in self.dataMsecs()]
        self._dataDecimalYears = np.array([self.utilsDateTimeToDecimalYear(dateTime)
                                           for dateTime in self.dataDateTimes()])
        self._dataProfile = dict()
        for index, bandName in enumerate(self.header[4:], 4):
            values = list()
            for row in self.data:
                value = row[index]
                if value is None:
                    value = nan
                values.append(value)
            self._dataProfile[bandName] = np.array(values)

        # update GUI
        header = [s for i, s in enumerate(self.header) if i not in [1, 2]]
        data = [[str(v) for i, v in enumerate(values) if i not in [1, 2]] for values in data]
        header[1] = 'decimal year'
        for values in data:
            msec = int(values[1])
            dateTime = self.utilsMsecToDateTime(msec)
            dyear = self.utilsDateTimeToDecimalYear(dateTime)
            values[1] = str(dyear)
        self.mData.setRowCount(len(data))
        self.mData.setColumnCount(len(header))
        self.mData.setHorizontalHeaderLabels(header)
        for row, values in enumerate(data):
            for column, value in enumerate(values):
                self.mData.setCellWidget(row, column, QLabel(value))
        self.mData.resizeColumnsToContents()

    def isDataAvailable(self) -> bool:
        return self.data is not None

    def dataN(self):
        return len(self._dataIds)

    def dataIds(self) -> List[str]:
        return self._dataIds

    def dataIndexByImageId(self) -> Dict[str, int]:
        return self._dataIndexById

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

        legend: pg.LegendItem = self.mPlotWidget.legend
        legend.setVisible(self.mShowLegend.isChecked())

        x = np.array(self.dataDecimalYears())
        for i in range(self.mLegend.count()):
            item: QListWidgetItem = self.mLegend.item(i)
            bandName = item.text()
            if item.checkState() == Qt.Checked:
                color = item.color
                y = self.dataProfile(bandName)
                if y is None:
                    continue

                # highlight selected images
                if self.mShowImageSelection.isChecked() and self.highlightedImages is not None:
                    selectionColor: QColor = self.mImageSelectionColor.color()
                    selectionColor.setAlpha(self.mImageSelectionOpacity.value())
                    plotSelection: pg.PlotDataItem = self.mPlotWidget.plot(
                        x[self.highlightedImages], y[self.highlightedImages]
                    )
                    plotSelection.setSymbol('o')  # ['t', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'o']
                    plotSelection.setSymbolBrush(selectionColor)
                    plotSelection.setSymbolPen(selectionColor)
                    symbolSize = self.mPointSize.value() + self.mImageSelectionSize.value()
                    plotSelection.setSymbolSize(symbolSize)
                    plotSelection.setPen(None)
                    self.plotItems.append(plotSelection)

                if self.mShowLines.isChecked() or self.mShowPoints.isChecked():
                    plotProfile: pg.PlotDataItem = self.mPlotWidget.plot(x, y, name=bandName)
                    if self.mShowLines.isChecked() and not self.mShowPoints.isChecked():
                        pen = QPen(QBrush(color), self.mLineSize.value())
                        pen.setCosmetic(True)
                        plotProfile.setPen(pen)
                    if not self.mShowLines.isChecked() and self.mShowPoints.isChecked():
                        plotProfile.setSymbol('o')  # ['t', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'o']
                        plotProfile.setSymbolBrush(color)
                        plotProfile.setSymbolPen(color)
                        plotProfile.setSymbolSize(self.mPointSize.value())
                        plotProfile.setPen(None)
                    if self.mShowLines.isChecked() and self.mShowPoints.isChecked():
                        pen = QPen(QBrush(color), self.mLineSize.value())
                        pen.setCosmetic(True)
                        plotProfile.setPen(pen)
                        plotProfile.setSymbol('o')  # ['t', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd', 'o']
                        plotProfile.setSymbolBrush(color)
                        plotProfile.setSymbolPen(color)
                        plotProfile.setSymbolSize(self.mPointSize.value())
                    self.plotItems.append(plotProfile)

                if self.mShowFittedLine.isChecked():
                    if self.mUseFittedLineColor.isChecked():
                        color2 = self.mFittedLineColor.color()
                    else:
                        color2 = color
                    gamma = 2**self.mSvrParameters.cellWidget(0, 1).value()
                    C = 2**self.mSvrParameters.cellWidget(1, 1).value()
                    try:
                        epsilon = float(self.mSvrParameters.cellWidget(2, 1).text())
                    except:
                        epsilon = 0

                    svr = SVR(kernel='rbf', gamma=gamma, C=C, epsilon=epsilon)
                    valid = np.isfinite(y)
                    svr.fit(x[valid].reshape(-1, 1), y[valid])
                    rect: QRectF = self.mPlotWidget.viewRect()
                    rect.left()
                    xfit = np.linspace(min(x), max(x), int((max(x) - min(x)) * 366))
                    yfit = svr.predict(xfit.reshape(-1, 1))
                    plotProfile: pg.PlotDataItem = self.mPlotWidget.plot(xfit, yfit, name=bandName + ' Fit')
                    pen = QPen(QBrush(color2), self.mFittedLineSize.value())
                    pen.setCosmetic(True)
                    plotProfile.setPen(pen)
                    self.plotItems.append(plotProfile)

    def pushInfoMissingCollection(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a collection')

    def pushInfoMissingBand(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a band')

    def pushInfoMissingDownloadFolder(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a download folder')

    def pushInfoMissingLayer(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a locations layer')

    def pushRequestError(self, error: Exception):
        self.mMessageBar.pushCritical('Request error', str(error))
        traceback.print_exc()

    def pushInfoEmptyQueryResults(self):
        self.mMessageBar.pushInfo('Query result', 'no images found')

    def pushSuccessDownload(self):
        self.mMessageBar.pushSuccess('Success', 'layer location profiles downloaded')


class GeeWaitCursor(object):

    def __enter__(self):
        QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))

    def __exit__(self, exc_type, exc_value, tb):
        QApplication.restoreOverrideCursor()

