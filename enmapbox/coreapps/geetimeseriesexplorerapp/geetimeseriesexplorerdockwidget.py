import json
import webbrowser
from collections import OrderedDict
from math import isnan, isfinite
from os import listdir, makedirs
from os.path import join, exists, dirname
from traceback import print_exc
from typing import Optional, Dict, List, Tuple
from unittest.mock import Mock

from enmapbox import EnMAPBox
from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from geetimeseriesexplorerapp.collectioninfo import CollectionInfo
from geetimeseriesexplorerapp.imageinfo import ImageInfo
from geetimeseriesexplorerapp.tasks.downloadimagechiptask import DownloadImageChipBandTask, DownloadImageChipTask
from geetimeseriesexplorerapp.tasks.queryavailableimagestask import QueryAvailableImagesTask
from geetimeseriesexplorerapp.utils import utilsMsecToDateTime

try:
    import ee
except ModuleNotFoundError:
    ee = Mock()

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QLocale, QDate, pyqtSignal, QModelIndex, QDateTime, QTime
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import (QToolButton, QApplication, QComboBox, QLineEdit,
                             QTableWidget, QDateEdit, QRadioButton, QListWidget, QCheckBox, QTableWidgetItem,
                             QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QTabWidget, QLabel, QMainWindow,
                             QStackedWidget, QListWidgetItem, QProgressBar, QFrame)
from enmapbox.qgispluginsupport.qps.utils import SpatialPoint, SpatialExtent
from enmapboxprocessing.utils import Utils
from geetimeseriesexplorerapp.codeeditwidget import CodeEditWidget
from geetimeseriesexplorerapp.externals.ee_plugin.provider import GeetseEarthEngineRasterDataProvider
from qgis.PyQt import uic
from qgis._core import QgsRasterLayer, QgsCoordinateReferenceSystem, QgsTask, QgsMapLayer, QgsMapSettings, \
    QgsColorRamp, QgsDateTimeRange, QgsMapLayerTemporalProperties, QgsApplication
from qgis._gui import (QgsDockWidget, QgsMessageBar, QgsColorRampButton, QgsSpinBox, QgsCheckableComboBox, QgsMapCanvas,
                       QgsDateTimeEdit, QgisInterface)
from typeguard import typechecked


@typechecked
class GeeTimeseriesExplorerDockWidget(QgsDockWidget):
    mMessageBar: QgsMessageBar
    mIconList: QListWidget

    # data catalog
    mUserCollection: QTableWidget
    mCollectionTitle: QLineEdit
    mOpenCatalog: QToolButton
    mOpenJson: QToolButton

    # collection metadata
    mCollectionMetadata: QPlainTextEdit

    # collection editor
    mPredefinedCollection: QComboBox
    mOpenDescription: QToolButton
    mCode: CodeEditWidget
    mLoadCollection: QToolButton

    # band properties
    mScaleBands: QCheckBox
    mBandProperty: QTableWidget

    # spectral indices
    mAsiVegatation: QListWidget
    mAsiBurn: QListWidget
    mAsiWater: QListWidget
    mAsiSnow: QListWidget
    mAsiDrought: QListWidget
    mAsiUrban: QListWidget
    mAsiOther: QListWidget
    mAsiCustom: QListWidget

    # filtering
    mFilterDateStart: QDateEdit
    mFilterDateEnd: QDateEdit
    mFilterProperties: QTableWidget
    mFilterBitmask: QTreeWidget

    # symbology
    mRendererType: QComboBox
    mVisualization: QComboBox
    mRedBand: QComboBox
    mGreenBand: QComboBox
    mBlueBand: QComboBox
    mPseudoColorBand: QComboBox
    mRedMin: QLineEdit
    mGreenMin: QLineEdit
    mBlueMin: QLineEdit
    mPseudoColorMin: QLineEdit
    mRedMax: QLineEdit
    mGreenMax: QLineEdit
    mBlueMax: QLineEdit
    mPseudoColorMax: QLineEdit
    mReducerRed: QComboBox
    mReducerGreen: QComboBox
    mReducerBlue: QComboBox
    mReducerPseudoColor: QComboBox
    mPseudoColorRamp: QgsColorRampButton

    mCalculatePercentiles: QToolButton
    mPercentileMinMax: QRadioButton
    mPercentileMin: QgsSpinBox
    mPercentileMax: QgsSpinBox

    # image explorer
    mImageExplorerTab: QTabWidget
    mImageExtent: QComboBox
    mLimitImages: QCheckBox
    mLimitImagesValue: QgsSpinBox
    mLiveQueryAvailableImages: QCheckBox
    mQueryAvailableImages: QToolButton
    mCopyAvailableImages: QToolButton
    mCopyImageInfo: QToolButton
    mShowImageInfo: QToolButton
    mAvailableImages: QTableWidget
    mImageId: QLineEdit

    # - compositing and mosaicking
    mCompositeDateStart: QDateEdit
    mCompositeDateEnd: QDateEdit
    mCompositeSeasonStart: QDateEdit
    mCompositeSeasonEnd: QDateEdit
    mReducerType: QTabWidget
    mReducerUniform: QComboBox
    mReducerBandWise: QTableWidget
    mCompositeExtent: QComboBox

    # update layer
    mLayerModeWms: QRadioButton
    mLayerModeImageChip: QRadioButton
    mImageChipBands: QgsCheckableComboBox
    mAppendName: QCheckBox
    mLayerName: QLineEdit
    mAppendId: QCheckBox
    mAppendDate: QCheckBox
    mAppendBandNames: QCheckBox
    mAppendType: QCheckBox
    mLayerNamePreview: QLineEdit
    mCenterLayer: QToolButton
    mLiveStretchLayer: QCheckBox
    mLiveUpdateLayer: QCheckBox
    mUpdateLayer: QToolButton
    mStretchAndUpdateLayer: QToolButton
    mTemporalEnabled: QCheckBox
    mTemporalRangeValue: QgsSpinBox
    mTemporalRangeUnits: QComboBox
    mTemporalStartFixed: QCheckBox
    mTemporalEndFixed: QCheckBox
    mTemporalStart: QgsDateTimeEdit
    mTemporalEnd: QgsDateTimeEdit

    mStackedWidgetBottom: QStackedWidget
    mProgressBarFrame: QFrame
    mProgressBar: QProgressBar
    mCancelTaskManager: QToolButton

    # additional typing

    sigCollectionChanged = pyqtSignal()

    def __init__(self, parent=None):
        QgsDockWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        # those are set from outside
        from geetimeseriesexplorerapp import GeeTemporalProfileDockWidget
        self.profileDock: GeeTemporalProfileDockWidget
        self.enmapBox: EnMAPBox
        self.qgisIface: QgisInterface

        self.eeInitialized = False
        self._currentCollection: Optional[ee.ImageCollection]
        self.backgroundLayer = QgsRasterLayer(
            'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0',
            'Google Maps', 'wms'
        )
        self.epsg4326 = 'EPSG:4326'
        self.crsEpsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        self.eeFullCollection: Optional[ee.ImageCollection] = None
        self.eeFullCollectionInfo: Optional[ImageInfo] = None
        self.eeFullCollectionJson: Optional[CollectionInfo] = None
        self.cache = dict()
        self.refs = list()  # keep refs to prevent crashes

        # list
        self.mIconList.setCurrentRow(0)

        self.mIconList.currentRowChanged.connect(lambda index: self.mStackedWidgetBottom.setCurrentIndex(min(index, 3)))

        # data catalog
        self.initDataCatalog()
        self.mUserCollection.itemSelectionChanged.connect(self.onCollectionClicked)
        self.mOpenCatalog.clicked.connect(self.onOpenCatalogClicked)
        self.mOpenJson.clicked.connect(self.onOpenJsonClicked)
        self.mLoadCollection.clicked.connect(self.onLoadCollectionClicked)

        # spectral indices
        self.initSpectralIndices()

        # symbology
        self.mGroupBoxBandRendering.setCollapsed(False)
        self.mGroupBoxMinMax.setCollapsed(False)
        self.mPseudoColorRamp.setColorRampFromName('RdYlGn')
        self.mPercentileMin.setClearValue(self.mPercentileMin.value())
        self.mPercentileMax.setClearValue(self.mPercentileMax.value())

        self.mVisualization.currentIndexChanged.connect(self.onVisualizationChanged)
        self.mCalculatePercentiles.clicked.connect(self.calculateCumulativeCountCutStretch)

        # image explorer
        self.mCenterLayer.clicked.connect(self.onCenterLayerClicked)
        self.mUpdateLayer.clicked.connect(self.onUpdateLayerClicked)
        self.mStretchAndUpdateLayer.clicked.connect(self.onStretchAndUpdateLayerClicked)
        # - image viewer
        self.mQueryAvailableImages.clicked.connect(self.queryAvailableImages)
        self.mCopyAvailableImages.clicked.connect(self.copyAvailableImages)
        self.mCopyImageInfo.clicked.connect(self.copyImageInfo)
        self.mShowImageInfo.clicked.connect(self.showImageInfo)
        self.mAvailableImages.itemSelectionChanged.connect(self.onAvailableImagesSelectionChanged)
        self.mAvailableImages.horizontalHeader().setSectionsMovable(True)
        self.mImageId.textChanged.connect(self.onImageIdChanged)
        self.mImageId.textChanged.connect(self.updateTemporalRange)
        # - compositing and mosaicking
        self.mCompositeSeasonStart.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.mCompositeSeasonEnd.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))

        # update layer bar
        self.mImageExplorerTab.currentChanged.connect(self.updateLayerNamePreview)
        self.mImageId.textChanged.connect(self.updateLayerNamePreview)
        self.mLayerName.textChanged.connect(self.updateLayerNamePreview)
        for w in [self.mLayerModeWms, self.mLayerModeImageChip, self.mAppendName, self.mAppendId, self.mAppendDate,
                  self.mAppendBandNames, self.mAppendType]:
            w.toggled.connect(self.updateLayerNamePreview)
        self.mImageChipBands.checkedItemsChanged.connect(self.updateLayerNamePreview)
        self.mTemporalEnabled.clicked.connect(self.updateTemporalRange)
        self.mTemporalRangeValue.valueChanged.connect(self.updateTemporalRange)
        self.mTemporalRangeUnits.currentIndexChanged.connect(self.updateTemporalRange)
        self.mTemporalStartFixed.clicked.connect(self.updateTemporalRange)
        self.mTemporalEndFixed.clicked.connect(self.updateTemporalRange)

        # task manager
        # self.taskManager = QgsTaskManager()  # using this manager gives me crashes, when connected to a progress bar
        self.taskManager = QgsApplication.taskManager()
        self.taskManager.taskAdded.connect(self.mProgressBarFrame.show)
        self.taskManager.allTasksFinished.connect(self.mProgressBarFrame.hide)
        self.mCancelTaskManager.clicked.connect(self.taskManager.cancelAll)
        self.mProgressBarFrame.hide()
        self.mProgressBar.setRange(0, 0)

        # init gui settings
        self.mImageChipBands.setItemCheckState(0, Qt.Checked)
        self.updateTemporalRange()

    def setProfileDock(self, profileDock):
        from geetimeseriesexplorerapp import GeeTemporalProfileDockWidget
        assert isinstance(profileDock, GeeTemporalProfileDockWidget)
        self.profileDock = profileDock

    def setEnmapBox(self, enmapBox: Optional[EnMAPBox]):
        self.enmapBox = enmapBox
        if enmapBox is not None:
            self.enmapBox.sigCurrentLocationChanged.connect(self.profileDock.setCurrentLocationFromEnmapBox)

    def setQgisInterface(self, qgisIface: Optional[QgisInterface]):
        self.qgisIface = qgisIface
        # todo connect mapTool --- see above: self.enmapbox.sigCurrentLocationChanged.connect(self.profileDock.setCurrentLocationFromEnmapBox)

    def initSpectralIndices(self):
        mAsiLists = {
            'vegetation': self.mAsiVegatation, 'burn': self.mAsiBurn, 'water': self.mAsiWater, 'snow': self.mAsiSnow,
            'drought': self.mAsiDrought, 'urban': self.mAsiUrban, 'other': self.mAsiOther
        }
        for name, spec in CreateSpectralIndicesAlgorithm.IndexDatabase.items():
            mList: QListWidget = mAsiLists.get(spec['type'])
            if mList is None:
                continue
            item = QListWidgetItem(f"{spec['short_name']}: {spec['long_name']}")
            item.setToolTip(f"{spec['formula']}")
            item.setCheckState(Qt.Unchecked)
            item.spec = spec
            mList.addItem(item)

    def updateSpectralIndices(self):
        # check all indices that have a default color specified
        mLists = [self.mAsiVegatation, self.mAsiBurn, self.mAsiWater, self.mAsiSnow, self.mAsiDrought, self.mAsiUrban,
                  self.mAsiOther]
        for mList in mLists:
            for row in range(mList.count()):
                item = mList.item(row)
                spec = item.spec
                if spec['short_name'] in self.eeFullCollectionInfo.bandColors:
                    item.setCheckState(Qt.Checked)

        # add custom spectral indices
        self.mAsiCustom.clear()
        for spec in self.eeFullCollectionInfo.spectralIndices.values():
            item = QListWidgetItem(f"{spec['short_name']}: {spec['long_name']}")
            item.setToolTip(f"{spec['formula']}")
            item.setCheckState(Qt.Checked)
            item.spec = spec
            self.mAsiCustom.addItem(item)

    def selectedSpectralIndices(self) -> List[Dict]:
        specs = list()
        mLists = [self.mAsiVegatation, self.mAsiBurn, self.mAsiWater, self.mAsiSnow, self.mAsiDrought, self.mAsiUrban,
                  self.mAsiOther, self.mAsiCustom]
        for mList in mLists:
            for row in range(mList.count()):
                item = mList.item(row)
                if item.checkState() == Qt.Checked:
                    specs.append(item.spec)
        return specs

    def initDataCatalog(self):
        self.mOpenCatalog.url = 'https://developers.google.com/earth-engine/datasets'

        self.mLANDSAT_LC08_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LE07_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LT05_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LT04_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_COMBINED_C02_T1_L2.clicked.connect(self.onUserCollectionClicked)
        self.mCOPERNICUS_S1_GRD.clicked.connect(self.onCollectionClicked)
        self.mCOPERNICUS_S2_SR.clicked.connect(self.onCollectionClicked)
        self.mCOPERNICUS_S3_OLCI.clicked.connect(self.onCollectionClicked)

        # load user defined collections
        @typechecked
        class UserCollection():

            def __init__(self, pyFilename: str):
                self.pyFilename = pyFilename
                self.jsonFilename = pyFilename.replace('.py', '.json')
                self.json = CollectionInfo(Utils.jsonLoad(self.jsonFilename))

            def id(self):
                return self.json.data['id']

            def title(self):
                return self.json.data['title']

            def temporalInterval(self):
                return self.json.temporalInterval()

            def code(self):
                with open(self.pyFilename) as file:
                    return file.read()

        root = join(__file__, '../user_collections')
        self.userCollections = [UserCollection(join(root, name)) for name in listdir(root) if name.endswith('.py')]
        self.mUserCollection.setRowCount(len(self.userCollections))
        for row, userCollection in enumerate(self.userCollections):
            d1, d2 = userCollection.temporalInterval()
            temporalInterval = f'{d1.year()} - '
            if d2.year() == QDate.currentDate().year():
                temporalInterval += 'Present'
            else:
                temporalInterval += str(d2.year())
            self.mUserCollection.setCellWidget(row, 0, QLabel(userCollection.id()))
            self.mUserCollection.setCellWidget(row, 1, QLabel(userCollection.title()))
            self.mUserCollection.setCellWidget(row, 2, QLabel(temporalInterval))
        self.mUserCollection.resizeColumnsToContents()

    def onVisualizationChanged(self):
        if self.mVisualization.currentIndex() > 0:
            v = self.eeFullCollectionJson.visualizations()[self.mVisualization.currentIndex() - 1]
            bandNames = v['image_visualization']['band_vis']['bands']
            for bandName, mBand in zip(bandNames, (self.mRedBand, self.mGreenBand, self.mBlueBand)):
                mBand.setCurrentText(bandName)

    def onAvailableImagesSelectionChanged(self):
        indices = self.mAvailableImages.selectedIndexes()
        if len(indices) == 0:
            return

        # set last image as current image
        index = indices[-1]
        imageId = self.mAvailableImages.item(index.row(), 0).data(Qt.DisplayRole)
        self.mImageId.setText(imageId)
        self.profileDock.setHighlightedImagesFromMainDock()

    def onImageIdChanged(self):
        if self.mLiveStretchLayer.isChecked():
            # self.mStretchAndUpdateLayer.click()
            # self.onUpdateLayerClicked()
            self.onStretchAndUpdateLayerClicked()
        else:
            if self.mLiveUpdateLayer.isChecked():
                # self.mUpdateLayer.click()
                self.onUpdateLayerClicked()

    def onCurrentLocationChanged(self):
        if self.mLiveQueryAvailableImages.isChecked():
            self.mQueryAvailableImages.click()

    def onLoadCollectionClicked(self):
        self.eeInitialize()

        namespace = dict(ee=ee)
        code = self.mCode.text()
        exec(code, namespace)

        with GeeWaitCursor():
            try:
                eeCollection = namespace['collection']
                assert isinstance(eeCollection, ee.ImageCollection)
            except Exception as error:
                self.mMessageBar.pushCritical('Error', str(error))
                self.eeFullCollection = None
                self.eeFullCollectionInfo = None
                return

        self.eeFullCollection = eeCollection
        self.eeFullCollectionInfo = ImageInfo(eeCollection.first().getInfo())
        self.eeFullCollectionInfo.addBandColors(namespace.get('bandColors', {}))
        self.eeFullCollectionInfo.addWavebandMappings(namespace.get('wavebandMapping', {}))
        self.eeFullCollectionInfo.addSpectralIndices(namespace.get('spectralIndices', {}))
        self.updateBandProperties()
        self.updateSpectralIndices()
        self.updateFilterProperties(namespace.get('propertyNames'))
        self.updateFilterBitmask()
        self.updateBandRendering()
        self.updateReducer()
        self.mVisualization.setCurrentIndex(1)
        self.mMessageBar.pushSuccess('Success', 'Image Collection loaded')

        self.sigCollectionChanged.emit()

    def onCenterLayerClicked(self):
        layer = self.currentLayer()
        mapCanvas = self.currentMapCanvas()
        if layer is None or mapCanvas is None:
            return

        if self.mImageExplorerTab.currentIndex() == 0:
            layer = self.currentLayer()
            if layer.customProperty('ee-layer'):
                provider: GeetseEarthEngineRasterDataProvider = layer.dataProvider()
                centroid = SpatialPoint(
                    'EPSG:4326', *provider.eeImage.geometry().centroid(0.01).getInfo()['coordinates']
                ).toCrs(self.currentCrs())
                mapCanvas.setCenter(centroid)
            else:
                raise NotImplementedError()

        if self.mImageExplorerTab.currentIndex() == 1:
            raise NotImplementedError()

        mapCanvas.refresh()

    def onUpdateLayerClicked(self, cumulativeCountCut=False):

        layerName = self.currentLayerName()
        temporalRange = self.currentImageLayerTemporalRange()

        if self.mImageExplorerTab.currentIndex() == 0:  # image viewer

            if self.eeImage() is None:
                return

            if self.mLayerModeWms.isChecked():
                eeImageProfile, eeImageRgb, visParams, visBands = self.eeImage()
                self.createWmsLayer(eeImageProfile, eeImageRgb, visParams, layerName, temporalRange)
            if self.mLayerModeImageChip.isChecked():
                eeImage, _, visParams, visBands = self.eeImage()
                renderTypeName = self.mRendererType.currentText()
                bandNames = self.currentImageChipBandNames()
                self.createImageChipLayer(
                    eeImage, bandNames, layerName, self.currentImageId(), self.currentLocation(), visParams, visBands,
                    renderTypeName, cumulativeCountCut, temporalRange
                )

        if self.mImageExplorerTab.currentIndex() == 1:  # compositing

            if self.eeComposite() is None:
                return

            if self.mLayerModeWms.isChecked():
                eeCompositeProfile, eeCompositeRgb, visParams = self.eeComposite()
                self.createWmsLayer(eeCompositeProfile, eeCompositeRgb, visParams, layerName, temporalRange)
            if self.mLayerModeImageChip.isChecked():
                assert 0

    def onStretchAndUpdateLayerClicked(self):
        if self.mLayerModeWms.isChecked():
            self.calculateCumulativeCountCutStretch()
            self.onUpdateLayerClicked()
        if self.mLayerModeImageChip.isChecked():
            self.onUpdateLayerClicked(cumulativeCountCut=True)

    def onOpenCatalogClicked(self):
        webbrowser.open_new_tab(self.mOpenCatalog.url)

    def onOpenJsonClicked(self):
        webbrowser.open_new_tab(self.mOpenJson.url)

    def onUserCollectionClicked(self):
        id = self.sender().objectName()[1:]
        for row in range(self.mUserCollection.rowCount()):
            if self.mUserCollection.cellWidget(row, 0).text() == id:
                self.mUserCollection.selectRow(row)
                return
        assert 0, f'unknown collection: {id}'

    def onCollectionClicked(self):

        if isinstance(self.sender(), QToolButton):
            mCollection: QToolButton = self.sender()
            id = mCollection.objectName()[1:]
            jsonUrl = f'https://earthengine-stac.storage.googleapis.com/catalog/{id}.json'
            with GeeWaitCursor():
                try:
                    import urllib.request, json
                    with urllib.request.urlopen(jsonUrl) as url:
                        data = json.loads(url.read().decode())
                except Exception as error:
                    self.mMessageBar.pushCritical('Error', str(error))
                    self.eeFullCollectionJson = None
                    return
            code = 'collection = ee.ImageCollection("' + data['id'] + '")\n\n'
            filename = join(__file__, '../standard_collections', id + '.py')
            if exists(filename):
                code += Utils.fileLoad(filename)

        elif isinstance(self.sender(), QTableWidget):
            indices: List[QModelIndex] = self.mUserCollection.selectedIndexes()
            if len(indices) == 0:
                return
            self.mUserCollection.clearSelection()
            collection = self.userCollections[indices[0].row()]

            jsonUrl = collection.jsonFilename
            data = collection.json.data
            code = collection.code()
        else:
            assert 0

        self.eeFullCollectionJson = CollectionInfo(data)
        self.mOpenCatalog.url = self.eeFullCollectionJson.googleEarthEngineUrl()
        self.mOpenJson.url = jsonUrl

        # update GUI and load collection
        self.mCollectionTitle.setText(data['title'])
        self.mCollectionTitle.setCursorPosition(0)
        self.mCode.setText(code)
        self.mAvailableImages.setRowCount(0)
        self.mAvailableImages.setColumnCount(2)
        self.mImageId.setText('')
        self.onLoadCollectionClicked()
        self.mIconList.setCurrentRow(5)  # show image viewer tab

    def eeInitialize(self):
        if not self.eeInitialized:
            ee.Initialize()
        self.eeInitialized = True

    def currentImageLayerTemporalRange(self) -> Optional[QgsDateTimeRange]:
        if self.mTemporalEnabled:
            if self.mTemporalStartFixed:
                start = self.mTemporalStart.dateTime()
            else:
                start = QDateTime()  # the bound is considered to be infinite
            if self.mTemporalEndFixed:
                end = self.mTemporalEnd.dateTime()
            else:
                end = QDateTime()  # the bound is considered to be infinite
            return QgsDateTimeRange(start, end)
        else:
            return None

    def updateTemporalRange(self):
        imageId = self.currentImageId()
        if imageId is None or not self.mTemporalEnabled.isChecked():
            self.mTemporalFrame.hide()
            return

        self.mTemporalFrame.show()
        dateTime = self.currentImageAcquisitionDate()
        units = self.mTemporalRangeUnits.currentText()
        if units == 'days':
            secs = self.mTemporalRangeValue.value() * 24 * 60 * 60
            dateTime.setTime(QTime(12, 0, 0, 0))
            self.mTemporalStart.setDateTime(dateTime.addSecs(-int(secs / 2)))
            self.mTemporalEnd.setDateTime(dateTime.addSecs(int(secs / 2)))
        else:
            raise NotImplementedError()

        # check for infinite range
        if not self.mTemporalStartFixed.isChecked():
            self.mTemporalStart.clear()
        if not self.mTemporalEndFixed.isChecked():
            self.mTemporalEnd.clear()

    def updateBandProperties(self):
        self.mBandProperty.setRowCount(len(self.eeFullCollectionInfo.bandNames))

        for i, bandName in enumerate(self.eeFullCollectionInfo.bandNames):
            wavelength = self.eeFullCollectionJson.bandWavelength(i + 1)
            if isnan(wavelength):
                wavelength = ''
            offset = self.eeFullCollectionJson.bandOffset(i + 1)
            if offset == 0.:
                offset = ''
            scale = self.eeFullCollectionJson.bandScale(i + 1)
            if scale == 1.:
                scale = ''
            sname = self.eeFullCollectionInfo.wavebandMapping.get(bandName)
            if sname is None:
                waveband = ''
            else:
                lname = CreateSpectralIndicesAlgorithm.LongNameMapping[sname]
                waveband = f' ({lname})'

            showInZProfile = QCheckBox()
            showInZProfile.setCheckState(Qt.Checked)
            label = self.eeFullCollectionJson.bandDescription(i + 1)

            self.mBandProperty.setCellWidget(i, 0, QLabel(bandName))
            self.mBandProperty.setCellWidget(i, 1, QLabel(f'{wavelength}{waveband}'))
            self.mBandProperty.setCellWidget(i, 2, QLabel(str(offset)))
            self.mBandProperty.setCellWidget(i, 3, QLabel(str(scale)))
            self.mBandProperty.setCellWidget(i, 4, showInZProfile)
            self.mBandProperty.setCellWidget(i, 5, QLabel(label))
        self.mBandProperty.resizeColumnsToContents()
        self.mBandProperty.horizontalHeader().setStretchLastSection(True)

    def updateFilterProperties(self, propertyNames: List[str] = None):
        self.mFilterProperties.setRowCount(10)
        operators = [
            '', 'equals', 'less_than', 'greater_than', 'not_equals', 'not_less_than', 'not_greater_than', 'starts_with',
            'ends_with', 'not_starts_with', 'not_ends_with', 'contains', 'not_contains'
        ]

        if propertyNames is None:
            propertyNames = self.eeFullCollectionInfo.propertyNames

        for row in range(10):
            w = QComboBox()
            w.addItems([''] + propertyNames)
            self.mFilterProperties.setCellWidget(row, 0, w)
            w = QComboBox()
            w.addItems(operators)
            self.mFilterProperties.setCellWidget(row, 1, w)
            w = QLineEdit()
            self.mFilterProperties.setCellWidget(row, 2, w)

        # self.mFilterProperties.resizeColumnsToContents()

        # set default date range filter dates
        d1, d2 = self.eeFullCollectionJson.temporalInterval()
        self.mFilterDateStart.setDate(d1)
        self.mFilterDateEnd.setDate(d2)

        # set default compositing dates to the last month of available data
        d1 = d2.addMonths(-1)
        d1 = d1.addDays(- d1.day() + 1)
        self.blockSignals(True)
        self.mCompositeDateStart.setDate(d1)
        self.mCompositeDateEnd.setDate(d2)
        self.blockSignals(False)

    def updateFilterBitmask(self):
        self.mFilterBitmask.clear()
        for eo_band in self.eeFullCollectionJson.data['summaries']['eo:bands']:

            # add bitmask bands
            if 'gee:bitmask' in eo_band:
                name = f"{eo_band['description']} [{eo_band['name']}]"
                bandItem = QTreeWidgetItem([name])
                self.mFilterBitmask.addTopLevelItem(bandItem)
                for part in eo_band['gee:bitmask']['bitmask_parts']:
                    values = part['values']
                    partsItem = PixelQualityBitmaskItem(
                        part['description'], eo_band['name'], part['first_bit'], part['bit_count'], 1
                    )
                    bandItem.addChild(partsItem)
                    if len(values) == 0:
                        partsItem.setCheckState(0, Qt.Unchecked)
                    for value in values:
                        valueItem = PixelQualityBitmaskItem(
                            value['description'], eo_band['name'], part['first_bit'], part['bit_count'], value['value']
                        )
                        valueItem.setCheckState(0, Qt.Unchecked)
                        partsItem.addChild(valueItem)
                    partsItem.setExpanded(True)
                bandItem.setExpanded(False)

            # add classification bands
            if 'gee:classes' in eo_band:
                name = f"{eo_band['description']} [{eo_band['name']}]"
                bandItem = QTreeWidgetItem([name])
                self.mFilterBitmask.addTopLevelItem(bandItem)
                for class_ in eo_band['gee:classes']:
                    classItem = CategoryMaskItem(class_['description'], eo_band['name'], class_['value'])
                    classItem.setCheckState(0, Qt.Unchecked)
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor('#' + class_['color']))
                    icon = QIcon(pixmap)
                    classItem.setIcon(0, icon)
                    classItem.setExpanded(True)
                    bandItem.addChild(classItem)
                bandItem.setExpanded(True)

    def updateBandRendering(self):
        for mBand in [self.mRedBand, self.mBlueBand, self.mGreenBand, self.mPseudoColorBand]:
            mBand.clear()
        if self.eeFullCollection is None:
            return

        bandNames = self.eeFullCollectionInfo.bandNames
        bandToolTips = [self.eeFullCollectionJson.bandTooltip(bandNo) for bandNo in range(1, len(bandNames) + 1)]
        spectralIndices = self.selectedSpectralIndices()
        siNames = [si['short_name'] for si in spectralIndices]
        siToolTips = [si['long_name'] for si in spectralIndices]

        for mBand in [self.mRedBand, self.mBlueBand, self.mGreenBand, self.mPseudoColorBand]:
            mBand.addItems(bandNames + siNames)
            for i, toolTip in enumerate(bandToolTips + siToolTips):
                mBand.setItemData(i, toolTip, Qt.ToolTipRole)

        self.mVisualization.clear()

        visualizations = [''] + [v['display_name'] for v in self.eeFullCollectionJson.visualizations()]
        self.mVisualization.addItems(visualizations)

    def eeReducers(self) -> Dict:
        return OrderedDict(
            [('Mean', ee.Reducer.mean()), ('StdDev', ee.Reducer.stdDev()), ('Variance', ee.Reducer.variance()),
             ('Kurtosis', ee.Reducer.kurtosis()), ('Skewness', ee.Reducer.skew()), ('First', ee.Reducer.firstNonNull()),
             ('Last', ee.Reducer.lastNonNull()), ('Min', ee.Reducer.min()), ('P5', ee.Reducer.percentile([5])),
             ('P10', ee.Reducer.percentile([10])), ('P25', ee.Reducer.percentile([25])),
             ('Median', ee.Reducer.median()), ('P75', ee.Reducer.percentile([75])),
             ('P90', ee.Reducer.percentile([90])), ('P95', ee.Reducer.percentile([95])), ('Max', ee.Reducer.max()),
             ('Count', ee.Reducer.count())]
        )

    def updateReducer(self):
        eeReducers = self.eeReducers()
        reducerNames = list(self.eeReducers().keys())
        self.mReducerRed.addItems(reducerNames)
        self.mReducerGreen.addItems(reducerNames)
        self.mReducerBlue.addItems(reducerNames)
        self.mReducerPseudoColor.addItems(reducerNames)
        self.mReducerUniform.addItems(reducerNames)
        self.mReducerBandWise.setRowCount(len(self.eeFullCollectionInfo.bandNames))
        for i, bandName in enumerate(self.eeFullCollectionInfo.bandNames):
            self.mReducerBandWise.setCellWidget(i, 0, QLabel(bandName))
            w = QComboBox()
            w.addItems(list(eeReducers.keys()))
            self.mReducerBandWise.setCellWidget(i, 1, w)
        self.mReducerBandWise.resizeColumnsToContents()

    def copyAvailableImages(self):

        model = self.mAvailableImages.model()
        header = [self.mAvailableImages.horizontalHeaderItem(i).text() for i in
                  range(self.mAvailableImages.columnCount())]
        data = [header]
        for row in range(model.rowCount()):
            data.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                data[row].append(model.data(index))

        text = '\n'.join([';'.join(row) for row in data])
        QApplication.clipboard().setText(text)

    def copyImageInfo(self):

        with GeeWaitCursor():
            try:
                eeImage, eeImageRgb, visParams, visBands = self.eeImage()
                info = eeImage.getInfo()
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

        text = json.dumps(info, indent=2)
        QApplication.clipboard().setText(text)

    def showImageInfo(self):
        self.copyImageInfo()
        text = QApplication.clipboard().text()
        mainWindow = QMainWindow(self)
        mainWindow.setWindowTitle('Image Info  — ' + self.mImageId.text())
        textEdit = QPlainTextEdit(text, self)
        textEdit.setReadOnly(True)
        mainWindow.setCentralWidget(textEdit)
        mainWindow.resize(600, 600)
        mainWindow.show()

    def queryAvailableImages(self):

        eeCollection = self.eeCollection()
        if eeCollection is None:
            self.pushInfoMissingCollection()
            return None

        point = self.currentLocation()
        point = point.toCrs(self.crsEpsg4326)
        eePoint = ee.Geometry.Point(point.x(), point.y())

        if self.mLimitImages.isChecked():
            limit = self.mLimitImagesValue.value()
        else:
            limit = int(1e6)

        task = QueryAvailableImagesTask(eeCollection, eePoint, limit, self.mMessageBar)
        task.taskCompleted.connect(lambda: self.onQueryAvailableImagesTaskCompleted(task))
        self.taskManager.addTask(task)

        self.refs.append(task)

    def onQueryAvailableImagesTaskCompleted(self, task: QueryAvailableImagesTask):
        if len(task.data) == 0:
            self.pushInfoQueryEmpty()

        if len(task.data) == task.limit:
            self.pushInfoQueryCut(task.limit)

        self.availableImagesData = task.header, task.data  # cache the data to avoid slow reading from table later

        # fill table
        self.mAvailableImages.setRowCount(len(task.data))
        self.mAvailableImages.setColumnCount(len(task.header))
        self.mAvailableImages.setHorizontalHeaderLabels(task.header)
        for row, values in enumerate(task.data):
            for column, value in enumerate(values):
                self.mAvailableImages.setItem(row, column, QTableWidgetItem(value))
        self.mAvailableImages.resizeColumnsToContents()

        # select first image
        self.mAvailableImages.clearSelection()
        self.mAvailableImages.selectRow(0)
        self.mIconList.setCurrentRow(5)

    def calculateCumulativeCountCutStretch(self):
        if self.mLayerModeWms.isChecked():
            self.calculateCumulativeCountCutStretchForWms()
        elif self.mLayerModeImageChip.isChecked():
            self.calculateCumulativeCountCutStretchForImageChip()

    def calculateCumulativeCountCutStretchForWms(self):

        if self.currentMapCanvas() is None:
            return

        extent = SpatialExtent(self.currentCrs(), self.currentMapCanvas().extent()).toCrs(self.crsEpsg4326)
        percentageMin = self.mPercentileMin.value()
        percentageMax = self.mPercentileMax.value()

        # calculate percentile stretch
        if self.mImageExplorerTab.currentIndex() == 0:  # Image Viewer
            eeImageProfile, eeImageRgb, visParams, visBands = self.eeImage()
        elif self.mImageExplorerTab.currentIndex() == 1:  # Composite Viewer
            limit = 100  # better limit the collection before calc stats!
            eeCompositeProfile, eeCompositeRgb, visParams = self.eeComposite(limit)
            eeImageRgb = eeCompositeRgb
        else:
            assert 0

        eeExtent = ee.Geometry.Rectangle(
            [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], None, False
        )

        with GeeWaitCursor():
            try:
                percentiles = eeImageRgb.reduceRegion(
                    ee.Reducer.percentile([percentageMin, percentageMax]),
                    bestEffort=True, maxPixels=100000, geometry=eeExtent,
                    scale=self.currentMapCanvas().mapUnitsPerPixel()
                ).getInfo()
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

        percentiles = {k: str(v) for k, v in percentiles.items()}

        # update min-max range
        ndigits = 3
        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            self.mRedMin.setText(str(tofloat(percentiles[f'vis-red_p{percentageMin}'], 0, ndigits)))
            self.mRedMax.setText(str(tofloat(percentiles[f'vis-red_p{percentageMax}'], 0, ndigits)))
            self.mGreenMin.setText(str(tofloat(percentiles[f'vis-green_p{percentageMin}'], 0, ndigits)))
            self.mGreenMax.setText(str(tofloat(percentiles[f'vis-green_p{percentageMax}'], 0, ndigits)))
            self.mBlueMin.setText(str(tofloat(percentiles[f'vis-blue_p{percentageMin}'], 0, ndigits)))
            self.mBlueMax.setText(str(tofloat(percentiles[f'vis-blue_p{percentageMax}'], 0, ndigits)))
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            self.mPseudoColorMin.setText(str(tofloat(percentiles[f'vis-pseudo_p{percentageMin}'], 0, ndigits)))
            self.mPseudoColorMax.setText(str(tofloat(percentiles[f'vis-pseudo_p{percentageMax}'], 0, ndigits)))

    def calculateCumulativeCountCutStretchForImageChip(self, layer: QgsRasterLayer = None):

        if self.currentMapCanvas() is None:
            return

        # find layer
        layerName = self.currentImageLayerName()
        if layer is None:
            for alayer in self.currentMapCanvas().layers():
                if isinstance(alayer, QgsRasterLayer) and alayer.name() == layerName:
                    layer = alayer
                    break

        assert layer is not None

        extent = self.currentExtent().toCrs(layer.crs())
        percentageMin = self.mPercentileMin.value() / 100.
        percentageMax = self.mPercentileMax.value() / 100.

        # calculate percentile stretch
        reader = RasterReader(layer)

        # update min-max range
        ndigits = 3
        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            vmin, vmax = reader.provider.cumulativeCut(
                reader.findBandName(self.mRedBand.currentText()), percentageMin, percentageMax, extent
            )
            self.mRedMin.setText(str(tofloat(vmin, 0, ndigits)))
            self.mRedMax.setText(str(tofloat(vmax, 0, ndigits)))
            vmin, vmax = reader.provider.cumulativeCut(
                reader.findBandName(self.mGreenBand.currentText()), percentageMin, percentageMax, extent
            )
            self.mGreenMin.setText(str(tofloat(vmin, 0, ndigits)))
            self.mGreenMax.setText(str(tofloat(vmax, 0, ndigits)))
            vmin, vmax = reader.provider.cumulativeCut(
                reader.findBandName(self.mBlueBand.currentText()), percentageMin, percentageMax, extent
            )
            self.mBlueMin.setText(str(tofloat(vmin, 0, ndigits)))
            self.mBlueMax.setText(str(tofloat(vmax, 0, ndigits)))
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            vmin, vmax = reader.provider.cumulativeCut(
                reader.findBandName(self.mPseudoColorBand.currentText()), percentageMin, percentageMax, extent
            )
            self.mPseudoColorMin.setText(str(tofloat(vmin, 0, ndigits)))
            self.mPseudoColorMax.setText(str(tofloat(vmax, 0, ndigits)))

    def eeVisualizationParameters(self) -> Dict:

        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            visParams = {
                'bands': [self.mRedBand.currentText(), self.mGreenBand.currentText(), self.mBlueBand.currentText()],
                'min': [tofloat(mMin.text()) for mMin in [self.mRedMin, self.mGreenMin, self.mBlueMin]],
                'max': [tofloat(mMax.text()) for mMax in [self.mRedMax, self.mGreenMax, self.mBlueMax]],
            }
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            ramp: QgsColorRamp = self.mPseudoColorRamp.colorRamp()
            colors = [ramp.color(i / (ramp.count() - 1)) for i in range(ramp.count())]
            visParams = {
                'bands': [self.mPseudoColorBand.currentText()],
                'min': tofloat(self.mPseudoColorMin.text()),
                'max': tofloat(self.mPseudoColorMax.text()),
                'palette': [color.name().strip('#') for color in colors]
            }
        else:
            assert 0
        return visParams

    def eeCollection(
            self, addIndices=True, filterDate=True, filterProperty=True, filterQuality=True
    ) -> Optional[ee.ImageCollection]:
        eeCollection = self.eeFullCollection

        if eeCollection is None:
            return None

        # add spectral index bands
        def addSpectralIndexBands(eeImage: ee.Image) -> ee.Image:
            for spectralIndex in self.selectedSpectralIndices():
                name = spectralIndex['short_name']  # NDVI
                formula = spectralIndex['formula']  # (N - R)/(N + R)
                mapping = {identifier: eeImage.select(bandName)
                           for identifier, bandName in self.eeFullCollectionInfo.wavebandMapping.items()}
                mapping.update({key: ee.Image(value)
                                for key, value in CreateSpectralIndicesAlgorithm.ConstantMapping.items()})
                eeImage = eeImage.addBands(eeImage.expression(formula, mapping).rename(name))
            return eeImage

        if addIndices:
            eeCollection = eeCollection.map(addSpectralIndexBands)

        # filter date range
        if filterDate:
            eeCollection = eeCollection.filterDate(
                self.mFilterDateStart.date().toString('yyyy-MM-dd'),
                self.mFilterDateEnd.date().addDays(1).toString('yyyy-MM-dd')  # GEE end date is exclusive
            )

        # filter metadata
        if filterProperty:
            for row in range(self.mFilterProperties.rowCount()):
                name: QComboBox = self.mFilterProperties.cellWidget(row, 0).currentText()
                operator: QComboBox = self.mFilterProperties.cellWidget(row, 1).currentText()
                value: QLineEdit = self.mFilterProperties.cellWidget(row, 2).text()
                if name == '' or operator == '' or value == '':
                    continue

                evalType = type(self.eeFullCollectionInfo.properties[name])
                eeCollection = eeCollection.filterMetadata(name, operator, evalType(value))

        # filter pixel quality
        if filterQuality:
            items = list()
            for i in range(self.mFilterBitmask.topLevelItemCount()):
                bandItem = self.mFilterBitmask.topLevelItem(i)
                for i2 in range(bandItem.childCount()):
                    classOrPartItem = bandItem.child(i2)
                    items.append(classOrPartItem)
                    for i3 in range(classOrPartItem.childCount()):
                        valueItem = classOrPartItem.child(i3)
                        items.append(valueItem)

            def maskPixel(eeImage: ee.Image) -> ee.Image:
                masks = list()
                for item in items:
                    if isinstance(item, (PixelQualityBitmaskItem, CategoryMaskItem)) and item.checkState(
                            0) == Qt.Checked:
                        masks.append(item.eeMask(eeImage))

                if len(masks) == 0:
                    return eeImage

                mask = ee.ImageCollection.fromImages(masks).reduce(ee.Reducer.bitwiseAnd())
                return eeImage.updateMask(mask)

            eeCollection = eeCollection.map(maskPixel)

        return eeCollection

    def compositeDates(self) -> Tuple[QDate, QDate]:
        dateStart = self.mCompositeDateStart.date()
        dateEnd = self.mCompositeDateEnd.date()
        if dateEnd >= dateStart:
            return dateStart, dateEnd
        else:
            return dateEnd, dateStart

    def eeComposite(self, limit: int = None) -> Optional[Tuple[ee.Image, ee.Image, Dict]]:

        eeCollection = self.eeCollection()

        if eeCollection is None:
            return None

        # filter date range
        dateStart, dateEnd = self.compositeDates()
        eeCollection = eeCollection.filterDate(
            dateStart.toString('yyyy-MM-dd'),
            dateEnd.addDays(1).toString('yyyy-MM-dd')  # GEE end date is exclusive
        )

        # filter season
        eeCollection = eeCollection.filter(
            ee.Filter.calendarRange(
                self.mCompositeSeasonStart.date().dayOfYear(), self.mCompositeSeasonEnd.date().dayOfYear()
            )
        )

        # filter extent
        extentIndex = self.mCompositeExtent.currentIndex()
        if limit is not None:
            extentIndex = self.MapViewExtent  # when limiting the collection always use the map extent

        if extentIndex == self.MapViewExtent:
            extent = Utils.transformMapCanvasExtent(self.currentMapCanvas(), self.crsEpsg4326)
            eeExtent = ee.Geometry.Rectangle(
                [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], self.epsg4326, False
            )
            eeCollection = eeCollection.filterBounds(eeExtent)
            eeCollection = eeCollection.map(lambda eeImage: eeImage.clip(eeExtent))

        if extentIndex == self.LocationExtent:
            point = self.currentLocation()
            if point is None:
                point = SpatialPoint.fromMapCanvasCenter(self.currentMapCanvas())
            point = point.toCrs(self.crsEpsg4326)
            eePoint = ee.Geometry.Point(point.x(), point.y())
            eeCollection = eeCollection.filterBounds(eePoint)

        if extentIndex == self.GlobalExtent:
            pass

        # limit the collection
        if limit is not None:
            eeCollection = eeCollection.limit(limit)

        # scale data
        spectralIndexCount = len(self.selectedSpectralIndices())
        if self.mScaleBands.isChecked():
            offsets = [self.eeFullCollectionJson.bandOffset(bandNo)
                       for bandNo in range(1, self.eeFullCollectionInfo.bandCount + spectralIndexCount + 1)]
            scales = [self.eeFullCollectionJson.bandScale(bandNo)
                      for bandNo in range(1, self.eeFullCollectionInfo.bandCount + spectralIndexCount + 1)]
            if any([scale != 1. for scale in scales]):
                eeCollection = eeCollection.map(lambda eeImage: eeImage.multiply(ee.Image(scales)))
            if any([offset != 0. for offset in offsets]):
                eeCollection = eeCollection.map(lambda eeImage: eeImage.add(ee.Image(offsets)))

        # composite
        eeReducers = self.eeReducers()
        bandNames = self.eeFullCollectionInfo.bandNames

        # - create composite used for z-profiles
        if self.mReducerType.currentIndex() == 0:  # uniform
            reducer = eeReducers[self.mReducerUniform.currentText()]
            eeCompositeProfile = eeCollection.reduce(reducer)
        elif self.mReducerType.currentIndex() == 1:  # band-wise
            eeBands = list()
            for i, bandName in enumerate(bandNames):
                w: QComboBox = self.mReducerBandWise.cellWidget(i, 1)
                reducer = eeReducers[w.currentText()]
                eeBand = eeCollection.select(bandName).reduce(reducer)
                eeBands.append(eeBand)
            eeCompositeProfile = ee.ImageCollection.fromImages(eeBands).toBands()
        else:
            assert 0
        eeCompositeProfile = eeCompositeProfile.rename(bandNames)

        # - create composite used for WMS layer
        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            bandNamesRgb = [self.mRedBand.currentText(), self.mGreenBand.currentText(), self.mBlueBand.currentText()]
            eeCompositeRed = eeCollection \
                .select(bandNamesRgb[0]) \
                .reduce(eeReducers[self.mReducerRed.currentText()])
            eeCompositeGreen = eeCollection \
                .select(bandNamesRgb[1]) \
                .reduce(eeReducers[self.mReducerGreen.currentText()])
            eeCompositeBlue = eeCollection \
                .select(bandNamesRgb[2]) \
                .reduce(eeReducers[self.mReducerBlue.currentText()])
            eeCompositeRgb = ee.Image.rgb(eeCompositeRed, eeCompositeGreen, eeCompositeBlue)

            visParams = {
                'min': [tofloat(mMin.text()) for mMin in [self.mRedMin, self.mGreenMin, self.mBlueMin]],
                'max': [tofloat(mMax.text()) for mMax in [self.mRedMax, self.mGreenMax, self.mBlueMax]],
            }

        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            bandNamePseudoColor = self.mPseudoColorBand.currentText()
            eeCompositeRgb = eeCollection \
                .select(bandNamePseudoColor) \
                .reduce(eeReducers[self.mReducerPseudoColor.currentText()]) \
                .rename('vis-pseudo')

            ramp = self.mPseudoColorRamp.colorRamp()
            colors = [ramp.color(i / (ramp.count() - 1)) for i in range(ramp.count())]
            visParams = {
                'min': tofloat(self.mPseudoColorMin.text()),
                'max': tofloat(self.mPseudoColorMax.text()),
                'palette': [color.name().strip('#') for color in colors]
            }
        else:
            assert 0

        return eeCompositeProfile, eeCompositeRgb, visParams

    def currentCompositeLayerName(self):
        seperator = ' – '
        items = list()
        if self.mAppendName.isChecked():
            items.append(self.mLayerName.text())

        if self.mAppendId.isChecked():
            items.append(self.eeFullCollectionJson.id().replace('/', '_'))

        if self.mAppendDate.isChecked():
            dateStart, dateEnd = self.compositeDates()
            if dateStart.daysTo(dateEnd) == 1:
                item = dateStart.CompositeDateStart.text()
            else:
                item = dateStart.toString('yyyy-MM-dd') + ' to ' + dateEnd.toString('yyyy-MM-dd')
            items.append(item)

            # append season if not the whole year
            seasonStart = self.mCompositeSeasonStart.date().toString('MM-dd')
            seasonEnd = self.mCompositeSeasonEnd.date().toString('MM-dd')
            if seasonStart != '01-01' or seasonEnd != '12-31':
                items.append(seasonStart + ' to ' + seasonEnd)

        if self.mAppendBandNames.isChecked():
            if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
                items.append(self.mRedBand.currentText())
                items.append(self.mGreenBand.currentText())
                items.append(self.mBlueBand.currentText())
            elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
                items.append(self.mPseudoColorBand.currentText())

        if self.mAppendType.isChecked():
            if self.mLayerModeWms.isChecked():
                items.append('WMS')
            if self.mLayerModeImageChip.isChecked():
                items.append('Image Chip')

        name = seperator.join(items)
        return name

    def eeImage(self, imageId: str = None) -> Optional[Tuple[ee.Image, ee.Image, Dict, List[str]]]:
        eeCollection = self.eeCollection(filterDate=False, filterProperty=False)

        if eeCollection is None:
            return None

        # select image by ID
        if imageId is None:
            imageId = self.mImageId.text()
            if imageId == '':
                self.pushInfoMissingImage()
                return

        eeImage = eeCollection.filter(ee.Filter.eq('system:index', imageId)).first()

        # scale data
        if self.mScaleBands.isChecked():
            spectralIndexCount = len(self.selectedSpectralIndices())
            offsets = [self.eeFullCollectionJson.bandOffset(bandNo)
                       for bandNo in range(1, self.eeFullCollectionInfo.bandCount + spectralIndexCount + 1)]
            scales = [self.eeFullCollectionJson.bandScale(bandNo)
                      for bandNo in range(1, self.eeFullCollectionInfo.bandCount + spectralIndexCount + 1)]

            if any([scale != 1. for scale in scales]):
                eeImage = eeImage.multiply(ee.Image(scales))
            if any([offset != 0. for offset in offsets]):
                eeImage = eeImage.add(ee.Image(offsets))

        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            visBands = [self.mRedBand.currentText(), self.mGreenBand.currentText(), self.mBlueBand.currentText()]
            eeImageRed = eeImage.select(visBands[0])
            eeImageGreen = eeImage.select(visBands[1])
            eeImageBlue = eeImage.select(visBands[2])
            eeImageRgb = ee.Image.rgb(eeImageRed, eeImageGreen, eeImageBlue)
            visParams = {
                'min': [tofloat(mMin.text()) for mMin in [self.mRedMin, self.mGreenMin, self.mBlueMin]],
                'max': [tofloat(mMax.text()) for mMax in [self.mRedMax, self.mGreenMax, self.mBlueMax]],
            }
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            visBands = [self.mPseudoColorBand.currentText()]
            eeImageRgb = eeImage.select(visBands[0]).rename('vis-pseudo')
            ramp = self.mPseudoColorRamp.colorRamp()
            colors = [ramp.color(i / (ramp.count() - 1)) for i in range(ramp.count())]
            visParams = {
                'min': tofloat(self.mPseudoColorMin.text()),
                'max': tofloat(self.mPseudoColorMax.text()),
                'palette': [color.name().strip('#') for color in colors]
            }
        else:
            assert 0

        return eeImage, eeImageRgb, visParams, visBands

    def currentImageAcquisitionDate(self) -> QDateTime:
        key = 'currentImageAcquisitionDate', self.mImageId.text()
        if key not in self.cache:  # cache date for later
            eeImage = self.eeCollection(False, False, False, False) \
                .filter(ee.Filter.eq('system:index', self.mImageId.text())).first()
            msec = eeImage.get('system:time_start').getInfo()
            self.cache[key] = msec
        msec = self.cache[key]
        return utilsMsecToDateTime(msec)

    def currentImageLayerName(self):

        if self.mImageId.text() == '':
            return ''

        seperator = ' – '
        items = list()
        if self.mAppendName.isChecked():
            items.append(self.mLayerName.text())

        if self.mAppendId.isChecked():
            items.append(self.mImageId.text())

        if self.mAppendDate.isChecked():
            dateTime = self.currentImageAcquisitionDate()
            items.append(dateTime.toString('yyyy-MM-dd'))

        if self.mAppendBandNames.isChecked():
            if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
                items.append(self.mRedBand.currentText())
                items.append(self.mGreenBand.currentText())
                items.append(self.mBlueBand.currentText())
            elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
                items.append(self.mPseudoColorBand.currentText())

        if self.mAppendType.isChecked():
            if self.mLayerModeWms.isChecked():
                items.append('WMS')
            if self.mLayerModeImageChip.isChecked():
                items.append('Image Chip')

        name = seperator.join(items)
        return name

    def currentLayerName(self) -> str:
        if self.mImageExplorerTab.currentIndex() == 0:  # image viewer
            return self.currentImageLayerName()
        elif self.mImageExplorerTab.currentIndex() == 1:  # compositing
            return self.currentCompositeLayerName()
        else:
            assert 0

    def updateLayerNamePreview(self):
        self.mLayerNamePreview.setText(self.currentLayerName())

    #    def enmapBoxOrQgisIface(self):
    #        assert 0
    #        return self.app.enmapbox

    def currentImageId(self) -> Optional[str]:
        imageId = self.mImageId.text()
        if imageId == '':
            return None
        return imageId

    def currentSpectralIndexBandNames(self) -> List[str]:
        return [si['short_name'] for si in self.selectedSpectralIndices()]

    def currentVisualizationBandNames(self) -> List[str]:
        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            return [self.mRedBand.currentText(), self.mGreenBand.currentText(), self.mBlueBand.currentText()]
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            return [self.mPseudoColorBand.currentText()]
        assert 0

    def currentImageChipBandNames(self) -> Optional[List[str]]:
        allBandNames = self.eeFullCollectionInfo.bandNames + self.currentSpectralIndexBandNames()
        selectedBandNames = set()

        VisualizationBands, ReflectanceBands, PixelQualityBands, SpectralIndexBands, ProfileBands, \
        AllBands = range(6)
        if self.mImageChipBands.itemCheckState(VisualizationBands) == Qt.Checked:
            selectedBandNames.update(self.currentVisualizationBandNames())
        if self.mImageChipBands.itemCheckState(ReflectanceBands) == Qt.Checked:
            reflectanceBandNames = [bandName for bandNo, bandName in enumerate(self.eeFullCollectionInfo.bandNames, 1)
                                    if isfinite(self.eeFullCollectionJson.bandWavelength(bandNo))]
            selectedBandNames.update(reflectanceBandNames)
        if self.mImageChipBands.itemCheckState(PixelQualityBands) == Qt.Checked:
            bitmaskBandNames = [bandName for bandNo, bandName in enumerate(self.eeFullCollectionInfo.bandNames, 1)
                                if self.eeFullCollectionJson.isBitmaskBand(bandNo)]
            classificationBandNames = [bandName for bandNo, bandName in
                                       enumerate(self.eeFullCollectionInfo.bandNames, 1)
                                       if self.eeFullCollectionJson.isClassificationBand(bandNo)]
            selectedBandNames.update(bitmaskBandNames)
            selectedBandNames.update(classificationBandNames)
        if self.mImageChipBands.itemCheckState(SpectralIndexBands) == Qt.Checked:
            selectedBandNames.update(self.currentSpectralIndexBandNames())
        if self.mImageChipBands.itemCheckState(ProfileBands) == Qt.Checked:
            profileBandNames = self.profileDock.selectedBandNames()
            if profileBandNames is not None:
                selectedBandNames.update(profileBandNames)
        if self.mImageChipBands.itemCheckState(AllBands) == Qt.Checked:
            selectedBandNames.update(allBandNames)

        bandNames = [bandName for bandName in allBandNames if bandName in selectedBandNames]  # this assures band order

        if len(bandNames) == 0:
            return None
        return bandNames

    def currentLocation(self) -> SpatialPoint:
        return self.profileDock.currentLocation()

    def currentMapCanvas(self) -> Optional[QgsMapCanvas]:
        if self.enmapBox is not None:
            return self.enmapBox.currentMapCanvas()
        if self.qgisIface is not None:
            return self.qgisIface.mapCanvas()
        assert 0

    def currentExtent(self) -> SpatialExtent:
        return SpatialExtent(self.currentCrs(), self.currentMapCanvas().extent())

    def currentCrs(self) -> QgsCoordinateReferenceSystem:
        mapSettings: QgsMapSettings = self.currentMapCanvas().mapSettings()
        return mapSettings.destinationCrs()

    def currentLayer(self) -> Optional[QgsMapLayer]:
        if self.enmapBox is not None:
            return self.enmapBox.currentLayer()
        if self.qgisIface is not None:
            return self.qgisIface.activeLayer()
        assert 0

    def setCurrentLayer(self, layer: QgsMapLayer):
        if self.enmapBox is not None:
            self.enmapBox.setCurrentLayer(layer)
        elif self.qgisIface is not None:
            self.qgisIface.setActiveLayer(layer)
        else:
            assert 0

    def currentDownloadFolder(self) -> str:
        return self.profileDock.currentDownloadFolder()

    def downloadFilenameImageChipBandTif(self, location: SpatialPoint, imageId: str, bandName: str):
        # eeCollection = self.eeCollection(filterDate=False, filterProperty=False, filterQuality=True)
        collectionId = self.eeFullCollectionJson.id().replace('/', '_')
        filename = join(
            self.profileDock.mDownloadFolder.filePath(),
            'chips',
            collectionId,
            # str(hash(eeCollection.serialize())),
            'X%018.13f_Y%018.13f' % (location.x(), location.y()),
            imageId,
            imageId + '_' + bandName + '.tif'
        )
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        return filename

    def downloadFilenameImageChipVrt(self, location: SpatialPoint, imageId: str, bandNames: List[str]):
        collectionId = self.eeFullCollectionJson.id().replace('/', '_')
        filename = join(
            'c:/vsimem/GEETSE', collectionId, 'X%018.13f_Y%018.13f' % (location.x(), location.y()),
            imageId, imageId + '_' + "-".join(bandNames) + '.vrt'
        )
        if not filename.startswith('/vsimem/') and not exists(dirname(filename)):
            makedirs(dirname(filename))

        return filename

    def createWmsLayer(
            self, eeImage: ee.Image, eeImageRgb: ee.Image, visParams: Dict, layerName: str,
            temporalRange: Optional[QgsDateTimeRange]
    ):

        if self.currentMapCanvas() is None:
            return

        # update/create WMS layer
        with GeeWaitCursor():
            try:
                from geetimeseriesexplorerapp.externals.ee_plugin import Map
                layer = Map.addLayer(eeImageRgb, visParams, layerName, self.currentMapCanvas())
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

        # set collection information
        provider: GeetseEarthEngineRasterDataProvider = layer.dataProvider()
        provider.setInformation(self.eeFullCollectionJson, self.eeFullCollectionInfo)
        showBandInProfile = [self.mBandProperty.cellWidget(row, 4).isChecked()
                             for row in range(self.mBandProperty.rowCount())]
        provider.setImageForProfile(eeImage, showBandInProfile)

        # set temporal properties
        if temporalRange is not None:
            temporalProperties: QgsMapLayerTemporalProperties = layer.temporalProperties()
            temporalProperties.setFixedTemporalRange(temporalRange)
            temporalProperties.setIsActive(True)

        self.setCurrentLayer(layer)

    def createImageChipLayer(
            self, eeImage: ee.Image, bandNames: List[str], layerName: str, imageId: str,
            location: SpatialPoint, visParams: Dict, visBands: List['str'], renderTypeName: str,
            cumulativeCountCut=False, temporalRange: QgsDateTimeRange = None
    ):
        alreadyExists = True
        filenames = list()
        subTasks = list()
        for bandName in bandNames:
            filename = self.downloadFilenameImageChipBandTif(location, imageId, bandName)
            filenames.append(filename)
            subTasks.append(DownloadImageChipBandTask(filename, location, eeImage, bandName))
            alreadyExists &= exists(filename)

        filename = self.downloadFilenameImageChipVrt(location, imageId, bandNames)
        alreadyExists &= exists(filename)

        if alreadyExists:
            self.onImageChipLayerCreated(
                filename, layerName, visParams, visBands, renderTypeName, cumulativeCountCut, temporalRange
            )
            return

        mainTask = DownloadImageChipTask(filename, filenames, location)
        for subTask in subTasks:
            mainTask.addSubTask(subTask, [], QgsTask.ParentDependsOnSubTask)

        mainTask.taskCompleted.connect(
            lambda: self.onImageChipLayerCreated(
                filename, layerName, visParams, visBands, renderTypeName, cumulativeCountCut, temporalRange
            )
        )

        self.currentCreateImageChipTask = mainTask
        self.taskManager.addTask(mainTask)

        # keep refs alive
        self.refs.append(mainTask)
        self.refs.append(subTasks)

    def onImageChipLayerCreated(
            self, filename: str, layerName: str, visParams: Dict, visBands: List['str'], renderTypeName: str,
            cumulativeCountCut=False, temporalRange: QgsDateTimeRange = None
    ):
        layer = QgsRasterLayer(filename, layerName)
        self.cache['onImageChipLayerCreated/' + filename] = layer  # need to hold ref to prevent crashes?

        if cumulativeCountCut:
            self.calculateCumulativeCountCutStretchForImageChip(layer)
            _, _, visParams, visBands = self.eeImage()  # use new min-max values

        # set renderer
        reader = RasterReader(layer)
        bandNumbers = [reader.findBandName(bandName) for bandName in visBands]
        if renderTypeName == 'Multiband color':
            renderer = Utils.multiBandColorRenderer(
                layer.dataProvider(), bandNumbers, visParams['min'], visParams['max']
            )
        elif renderTypeName == 'Singleband pseudocolor':
            ramp: QgsColorRamp = self.mPseudoColorRamp.colorRamp()
            renderer = Utils.singleBandPseudoColorRenderer(
                layer.dataProvider(), bandNumbers[0], visParams['min'], visParams['max'], ramp
            )
        else:
            assert 0
        layer.setRenderer(renderer)

        # set temporal properties
        if temporalRange is not None:
            temporalProperties: QgsMapLayerTemporalProperties = layer.temporalProperties()
            temporalProperties.setFixedTemporalRange(temporalRange)
            temporalProperties.setIsActive(True)

        if self.enmapBox is not None:
            self.enmapBox.currentMapDock().addOrUpdateLayer(layer)
        elif self.qgisIface is not None:
            raise NotImplementedError
        else:
            assert 0


    def pushInfoMissingCollection(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a collection')

    def pushInfoMissingImage(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select an image')

    def pushInfoQueryCut(self, max_: int):
        self.mMessageBar.pushInfo('Query', f'collection query result cut after accumulating over {max_} elements')

    def pushInfoQueryEmpty(self):
        self.mMessageBar.pushInfo('Query', 'collection query result is empty')

    LocationExtent = 0
    MapViewExtent = 1
    GlobalExtent = 2

    MultibandColorRenderer = 0
    SinglebandPseudocolorRenderer = 1


def tofloat(obj, default=0, ndigits=None):
    try:
        value = float(obj)
    except:
        value = default
    if ndigits is not None:
        value = round(value, ndigits)
    return value


@typechecked
class CategoryMaskItem(QTreeWidgetItem):

    def __init__(self, text: str, bandName: str, value: int):
        QTreeWidgetItem.__init__(self, [text])
        self.bandName = bandName
        self.value = value

    def eeMask(self, eeImage: ee.Image) -> ee.Image:
        return eeImage.select(self.bandName).neq(self.value)


@typechecked
class PixelQualityBitmaskItem(QTreeWidgetItem):

    def __init__(self, text: str, bandName: str, firstBit: int, bitCount: int, value: int):
        QTreeWidgetItem.__init__(self, [text])
        self.bandName = bandName
        self.firstBit = firstBit
        self.bitCount = bitCount
        self.value = value

    def eeMask(self, eeImage: ee.Image) -> ee.Image:
        return eeImage.select(self.bandName).rightShift(self.firstBit).bitwiseAnd(2 ** self.bitCount - 1).neq(
            self.value)


class GeeWaitCursor(object):

    def __enter__(self):
        QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))

    def __exit__(self, exc_type, exc_value, tb):
        QApplication.restoreOverrideCursor()
