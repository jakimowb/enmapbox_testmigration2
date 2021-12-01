import webbrowser
from collections import OrderedDict
from math import nan
from os import listdir
from os.path import join, dirname
from time import sleep
from traceback import print_exc
from typing import Optional, Dict, List, Tuple
from unittest.mock import Mock

try:
    import ee
except ModuleNotFoundError:
    ee = Mock()

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QLocale, QDateTime, QDate, pyqtSignal, QModelIndex
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import (QToolButton, QApplication, QComboBox, QLineEdit,
                             QTableWidget, QDateEdit, QSpinBox, QRadioButton, QListWidget, QCheckBox, QTableWidgetItem,
                             QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QTabWidget)
from enmapbox import EnMAPBox
from enmapbox.externals.qps.utils import SpatialPoint
from enmapboxprocessing.utils import Utils
from geetimeseriesexplorerapp.codeeditwidget import CodeEditWidget
from geetimeseriesexplorerapp.externals.ee_plugin.provider import EarthEngineRasterDataProvider
from qgis.PyQt import uic
from qgis._core import QgsRasterLayer, QgsCoordinateReferenceSystem, QgsRasterDataProvider
from qgis._gui import (QgsDockWidget, QgsMessageBar, QgsColorRampButton, QgsMapCanvas, QgsSpinBox, QgsCheckableComboBox)
from typeguard import typechecked


@typechecked
class CollectionInfo():
    def __init__(self, info: dict):
        self.info = info  # ee.Image.getInfo() of first image in collection
        self.properties: Dict = self.info['properties']
        self.propertyNames: List[str] = list(sorted(self.properties))
        self.resolutions = [band['crs_transform'][0] for band in self.info['bands']]
        self.bandNames = [band['id'] for band in self.info['bands']]
        self.bandColors: Dict[str, str] = self.properties.get('bandColors', {})
        # self.resolution = min(
        #    [band['crs_transform'][0] for band in self.imageCollection.first().select(0).getInfo()['bands']]
        # )


@typechecked
class CollectionJson():
    def __init__(self, data: dict):
        self.data = data

    def eo_band(self, bandNo: int) -> Dict:
        return self.data['summaries']['eo:bands'][bandNo - 1]

    def groundSamplingDistance(self) -> float:
        return float(min(self.data['summaries']['gsd']))

    def visualizations(self) -> List[Dict]:
        return self.data['summaries']['gee:visualizations']

    def bandWavelength(self, bandNo: int) -> float:
        try:
            fwhm, units = self.eo_band(bandNo)['gee:wavelength'].split()
            wavelength = self.eo_band(bandNo)['center_wavelength']
            if units == '&mu;m':
                wavelength *= 1000.
            if wavelength > 3000:  # skip thermal bands
                wavelength = nan
        except:
            wavelength = nan

        return wavelength

    def bandDescription(self, bandNo: int) -> str:
        return self.eo_band(bandNo)['description']

    def bandTooltip(self, bandNo: int) -> str:
        eo_band = self.eo_band(bandNo)
        tooltip = eo_band['description']
        if 'gee:wavelength' in eo_band:
            tooltip += ' [' + eo_band['gee:wavelength'].replace('&mu;m', 'µm') + ']'
        return tooltip

    def bandOffset(self, bandNo: int) -> Optional[float]:
        return self.eo_band(bandNo).get('gee:offset')

    def bandScale(self, bandNo: int) -> Optional[float]:
        return self.eo_band(bandNo).get('gee:scale')

    def temporalInterval(self) -> Tuple[QDate, QDate]:
        timestamp, d2 = self.data['extent']['temporal']['interval'][0]
        d1 = QDate(*map(int, timestamp.split('T')[0].split('-')))
        if d2 is None:
            d2 = QDateTime.currentDateTime().date()
        else:
            d2 = QDate(*timestamp.split('T')[0].split('-'))
        return d1, d2


@typechecked
class GeeTimeseriesExplorerDockWidget(QgsDockWidget):
    mMessageBar: QgsMessageBar
    mIconList: QListWidget

    # data catalog
    mCollectionDescription: QPlainTextEdit
    mCollectionPreview: QgsMapCanvas
    mCollectionTitle: QLineEdit
    mCollectionWebsite: QToolButton

    # collection metadata
    mCollectionMetadata: QPlainTextEdit

    # collection editor
    mPredefinedCollection: QComboBox
    mOpenDescription: QToolButton
    mOpenCatalog: QToolButton
    mCode: CodeEditWidget
    mLoadCollection: QToolButton

    # property filter
    mFilterDateStart: QDateEdit
    mFilterDateEnd: QDateEdit
    mFilterProperties: QTableWidget

    # bitmask filter
    mFilterBitmask: QTreeWidget

    # symbology
    mRendererType: QComboBox
    mVisualization: QComboBox
    mRedBand: QComboBox
    mGreenBand: QComboBox
    mBlueBand: QComboBox
    mRedMin: QLineEdit
    mGreenMin: QLineEdit
    mBlueMin: QLineEdit
    mRedMax: QLineEdit
    mGreenMax: QLineEdit
    mBlueMax: QLineEdit

    mPseudoColorBand: QComboBox
    mPseudoColorMin: QLineEdit
    mPseudoColorMax: QLineEdit
    mPseudoColorRamp: QgsColorRampButton

    mCalculatePercentiles: QToolButton
    mPercentileMinMax: QRadioButton
    mPercentileMin: QgsSpinBox
    mPercentileMax: QgsSpinBox

    # image explorer
    mImageExplorerTab: QTabWidget
    mImageViewerProperties: QgsCheckableComboBox
    mLayerName: QLineEdit
    mAppendId: QCheckBox
    mAppendDateRange: QCheckBox
    mAppendBandNames: QCheckBox
    mCreateLayer: QToolButton
    # - image viewer
    mImageExtent: QComboBox
    mQueryAvailableImages: QToolButton
    mAvailableImages: QTableWidget
    mImageId: QLineEdit

    # - compositing and mosaicking
    mCompositeDateStart: QDateEdit
    mCompositeDateEnd: QDateEdit
    mCompositeSeasonStart: QDateEdit
    mCompositeSeasonEnd: QDateEdit
    mReducerRed: QComboBox
    mReducerGreen: QComboBox
    mReducerBlue: QComboBox
    mCompositeExtent: QComboBox

    # additional typing
    eeFullCollectionInfo: Optional[CollectionInfo]

    sigCollectionChanged = pyqtSignal()

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        QgsDockWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.enmapBox = enmapBox
        self.eeInitialized = False
        self._currentCollection: Optional[ee.ImageCollection]
        self.backgroundLayer = QgsRasterLayer(
            'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0',
            'Google Maps', 'wms'
        )
        self.epsg4326 = 'EPSG:4326'
        self.crsEpsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        self.eeFullCollection: Optional[ee.ImageCollection] = None
        self.eeFullCollectionInfo: Optional[CollectionInfo] = None
        self.eeFullCollectionJson: Optional[CollectionJson] = None

        # list
        self.mIconList.setCurrentRow(0)

        # data catalog
        self.initDataCatalog()

        self.mCollectionWebsite.clicked.connect(self.onCollectionWebsiteClicked)
        # self.mWebView.setUrl(QUrl('https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2'))

        # collection editor
        self.initPredefinedCollection()

        self.mPredefinedCollection.currentIndexChanged.connect(self.onPredefinedIndexChanged)
        # self.mOpenDescription.clicked.connect(self.onOpenDescriptionClicked)
        self.mLoadCollection.clicked.connect(self.onLoadCollectionClicked)

        # property filter

        # symbology
        self.mGroupBoxBandRendering.setCollapsed(False)
        self.mGroupBoxMinMax.setCollapsed(False)
        self.mPseudoColorRamp.setColorRampFromName('RdYlGn')
        self.mPercentileMin.setClearValue(self.mPercentileMin.value())
        self.mPercentileMax.setClearValue(self.mPercentileMax.value())

        self.mVisualization.currentIndexChanged.connect(self.onVisualizationChanged)
        self.mCalculatePercentiles.clicked.connect(self.calculateCumulativeCountCutStretch)

        # image explorer
        self.mCreateLayer.clicked.connect(self.onCreateLayerClicked)
        # - image viewer
        self.mQueryAvailableImages.clicked.connect(self.queryAvailableImages)
        self.mAvailableImages.itemSelectionChanged.connect(self.onAvailableImagesSelectionChanged)
        # - compositing and mosaicking
        self.mCompositeSeasonStart.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.mCompositeSeasonEnd.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        names = ['Mean', 'StdDev', 'Variance', 'Kurtosis', 'Skewness', 'First', 'Last', 'Min', 'P5', 'P10', 'P25',
                 'Median', 'P75', 'P90', 'P95', 'Max']
        self.mReducerRed.addItems(names)
        self.mReducerGreen.addItems(names)
        self.mReducerBlue.addItems(names)

    def initDataCatalog(self):
        self.mCollectionWebsite.website = 'https://developers.google.com/earth-engine/datasets'

        self.mLANDSAT_LC08_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LE07_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LT05_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mLANDSAT_LT04_C02_T1_L2.clicked.connect(self.onCollectionClicked)
        self.mCOPERNICUS_S1_GRD.clicked.connect(self.onCollectionClicked)
        self.mCOPERNICUS_S2_SR.clicked.connect(self.onCollectionClicked)
        self.mCOPERNICUS_S3_OLCI.clicked.connect(self.onCollectionClicked)

    def initPredefinedCollection(self):
        self.predefinedCollection = OrderedDict()
        root = join(dirname(__file__), 'predefined')
        self.predefinedCollection['<select predefined collection and/or use code editor>'] = ''
        for name in listdir(root):
            if name.endswith('.py'):
                with open(join(root, name)) as f:
                    text = f.read()
                text = f'# {join(root, name)}\n\n' + text
                self.predefinedCollection[name.replace('.py', '').replace('_', ' ')] = text
        for imageCollectionId, name in [
            ('LANDSAT/LT04/C01/T1_SR', 'USGS Landsat 4 Surface Reflectance Tier 1'),
            ('LANDSAT/LT05/C01/T1_SR', 'USGS Landsat 5 Surface Reflectance Tier 1'),
            ('LANDSAT/LE07/C01/T1_SR', 'USGS Landsat 7 Surface Reflectance Tier 1'),
            ('LANDSAT/LC08/C01/T1_SR', 'USGS Landsat 8 Surface Reflectance Tier 1'),
            ('COPERNICUS/S2_SR', 'Sentinel-2 MSI: MultiSpectral Instrument, Level-2A'),
            ('MODIS/006/MCD43A4', 'MCD43A4.006 MODIS Nadir BRDF-Adjusted Reflectance Daily 500m'),
            ('MODIS/006/MOD09GQ', 'MOD09GQ.006 Terra Surface Reflectance Daily Global 250m'),
            ('MODIS/006/MOD09GA', 'MOD09GA.006 Terra Surface Reflectance Daily Global 1km and 500m'),
            ('MODIS/006/MOD09Q1', 'MOD09Q1.006 Terra Surface Reflectance 8-Day Global 250m'),
            ('MODIS/006/MOD09A1', 'MOD09A1.006 Terra Surface Reflectance 8-Day Global 500m'),
            ('NOAA/CDR/AVHRR/SR/V5', 'NOAA CDR AVHRR: Surface Reflectance, Version 5'),
            ('NOAA/VIIRS/001/VNP09GA', 'VNP09GA: VIIRS Surface Reflectance Daily 500m and 1km')
        ]:
            text = f'import ee\n\n\nimageCollection = ee.ImageCollection("{imageCollectionId}")'
            self.predefinedCollection[name] = text

        self.mPredefinedCollection.addItems(self.predefinedCollection.keys())

    def onVisualizationChanged(self):
        if self.mVisualization.currentIndex() > 0:
            v = self.eeFullCollectionJson.visualizations()[self.mVisualization.currentIndex() - 1]
            vmin = min(v['image_visualization']['band_vis']['min'])
            vmax = min(v['image_visualization']['band_vis']['max'])
            bandNames = v['image_visualization']['band_vis']['bands']
            for bandName, mBand, mMin, mMax in zip(
                    bandNames,
                    (self.mRedBand, self.mGreenBand, self.mBlueBand),
                    (self.mRedMin, self.mGreenMin, self.mBlueMin),
                    (self.mRedMax, self.mGreenMax, self.mBlueMax),
            ):
                mBand.setCurrentText(bandName)
                mMin.setText(str(vmin))
                mMax.setText(str(vmax))

    def onAvailableImagesSelectionChanged(self):
        index: QModelIndex
        for index in self.mAvailableImages.selectedIndexes():
            imageId = self.mAvailableImages.item(index.row(), 0).data(Qt.DisplayRole)
            self.mImageId.setText(imageId)

    def onPredefinedIndexChanged(self, index):
        text = list(self.predefinedCollection.values())[index]
        self.mCode.setText(text)
        self.onLoadCollectionClicked()

    def onOpenCatalogClicked(self):
        webbrowser.open_new('https://developers.google.com/earth-engine/datasets/catalog')

    def onLoadCollectionClicked(self):
        self.eeInitialize()

        namespace = dict(ee=ee)
        code = self.mCode.text()
        exec(code, namespace)

        with GeeWaitCursor():
            try:
                eeCollection = namespace['collection']
                assert isinstance(eeCollection, ee.ImageCollection)
                self.eeFullCollection = eeCollection
                self.eeFullCollectionInfo = CollectionInfo(eeCollection.first().getInfo())
            except Exception as error:
                self.mMessageBar.pushCritical('Error', str(error))
                self.eeFullCollection = None
                self.eeFullCollectionInfo = None
                return

        self.updateFilterProperties()
        self.updateFilterBitmask()
        self.updateBandRendering()
        self.mVisualization.setCurrentIndex(1)
        self.mMessageBar.pushSuccess('Success', 'Image Collection loaded')

        self.sigCollectionChanged.emit()

    def onCreateLayerClicked(self):
        if self.mImageExplorerTab.currentIndex() == 0:
            self.createLayer(self.eeImage(), self.eeVisualizationParameters(), self.imageLayerName())
        if self.mImageExplorerTab.currentIndex() == 1:
            self.createLayer(self.eeComposite(), self.eeVisualizationParameters(), self.compositeLayerName())


    def onCollectionWebsiteClicked(self):
        webbrowser.open_new_tab(self.mCollectionWebsite.website)

    def onCollectionClicked(self):
        mCollection: QToolButton = self.sender()

        # fetch description
        id = mCollection.objectName()[1:]
        website = f'https://developers.google.com/earth-engine/datasets/catalog/{id}'
        jsonUrl = f'https://earthengine-stac.storage.googleapis.com/catalog/{id}.json'

        self.mCollectionWebsite.website = website
        with GeeWaitCursor():
            try:
                import urllib.request, json
                with urllib.request.urlopen(jsonUrl) as url:
                    data = json.loads(url.read().decode())
                self.eeFullCollectionJson = CollectionJson(data)
            except Exception as error:
                self.mMessageBar.pushCritical('Error', str(error))
                self.eeFullCollectionJson = None
                return

        # update GUI and load collection
        self.mCollectionTitle.setText(data['title'])
        self.mCollectionTitle.setCursorPosition(0)
        code = 'collection = ee.ImageCollection("' + data['id'] + '")\n'
        self.mCode.setText(code)
        self.onLoadCollectionClicked()

    def eeInitialize(self):
        if not self.eeInitialized:
            ee.Initialize()
        self.eeInitialized = True

    def updateFilterProperties(self):
        self.mFilterProperties.setRowCount(10)
        operators = [
            '', 'equals', 'less_than', 'greater_than', 'not_equals', 'not_less_than', 'not_greater_than', 'starts_with',
            'ends_with', 'not_starts_with', 'not_ends_with', 'contains', 'not_contains'
        ]
        properties = [''] + self.eeFullCollectionInfo.propertyNames

        for row in range(10):
            w = QComboBox()
            w.addItems(properties)
            self.mFilterProperties.setCellWidget(row, 0, w)
            w = QComboBox()
            w.addItems(operators)
            self.mFilterProperties.setCellWidget(row, 1, w)
            w = QLineEdit()
            self.mFilterProperties.setCellWidget(row, 2, w)

        # also update image viewer properties
        self.mImageViewerProperties.clear()
        self.mImageViewerProperties.addItems(self.eeFullCollectionInfo.propertyNames)

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
        for mBand in [self.mRedBand, self.mBlueBand, self.mGreenBand, self.mPseudoColorBand]:
            mBand.addItems(self.eeFullCollectionInfo.bandNames)
            for i, bandName in enumerate(self.eeFullCollectionInfo.bandNames):
                bandNo = i + 1
                tooltip = self.eeFullCollectionJson.bandTooltip(bandNo)
                mBand.setItemData(i, tooltip, Qt.ToolTipRole)

        self.mVisualization.clear()

        visualizations = [''] + [v['display_name'] for v in self.eeFullCollectionJson.visualizations()]
        self.mVisualization.addItems(visualizations)

    def queryAvailableImages(self):
        eeCollection = self.eeCollection()

        if eeCollection is None:
            self.pushInfoMissingCollection()
            return None

        # filter extent
        if self.mImageExtent.currentIndex() == self.MapViewExtent:
            extent = Utils.transformMapCanvasExtent(self.enmapBox.currentMapCanvas(), self.crsEpsg4326)
            eeExtent = ee.Geometry.Rectangle(
                [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], self.epsg4326, False
            )
            eeCollection = eeCollection.filterBounds(eeExtent)
        elif self.mImageExtent.currentIndex() == self.LocationExtent:
            point = self.enmapBox.currentLocation()
            if point is None:
                point = SpatialPoint.fromMapCanvasCenter(self.enmapBox.currentMapCanvas())
            point = point.toCrs(self.crsEpsg4326)
            eePoint = ee.Geometry.Point(point.x(), point.y())
            eeCollection = eeCollection.filterBounds(eePoint)
        else:
            assert 0

        properties = self.mImageViewerProperties.checkedItems()
        properties = ['system:index', 'system:time_start'] + properties
        with GeeWaitCursor():
            try:
                infos = eeCollection.toList(5000, 0).map(
                    lambda eeImage: [ee.Image(eeImage).get(key)
                                     for key in properties]
                ).getInfo()
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

        # format content to enable correct sorting
        propertyFormat = dict()
        for i, property in enumerate(properties):
            if i < 2:
                continue
            if any([isinstance(row[i], float) for row in infos]):
                n1 = len(str(max([row[i] for row in infos])))
                n2 = max([len(str(row[i]).split('.')[1]) for row in infos if '.' in str(row[i])])
                n = n1 + n2 + 1
                propertyFormat[property] = '{:' + str(n) + '.' + str(n2) + 'f}' #.format(value)
            elif all([isinstance(row[i], int) for row in infos]):
                n = len(str(max([row[i] for row in infos])))
                propertyFormat[property] = '{:' + str(n) + '.0f}'

        # fill table
        self.mAvailableImages.setRowCount(len(infos))
        headerLabels = ['Available Images', 'Acquisition Time'] + properties[2:]
        self.mAvailableImages.setColumnCount(len(headerLabels))
        self.mAvailableImages.setHorizontalHeaderLabels(headerLabels)

        for i, values in enumerate(infos):
            imageId = values[0]
            msec = values[1]
            timestamp = utilsMsecToDateTime(msec).toString('yyyy-MM-ddThh:mm:ss')
            self.mAvailableImages.setItem(i, 0, QTableWidgetItem(imageId))
            self.mAvailableImages.setItem(i, 1, QTableWidgetItem(timestamp))
            for k, value in enumerate(values[2:], 2):
                property = properties[k]
                value = propertyFormat.get(property, '{}').format(value)
                self.mAvailableImages.setItem(i, k, QTableWidgetItem(value))

        self.mAvailableImages.resizeColumnsToContents()

        if len(infos) == 5000:
            self.pushInfoQueryCut()

    def calculateCumulativeCountCutStretch(self):

        print('CALC STATS')

        if self.mImageExplorerTab.currentIndex() == 0:
            eeImage = self.eeImage()
        elif self.mImageExplorerTab.currentIndex() == 1:
            limit = 100  # better limit the collection before calc stats!
            eeImage = self.eeComposite(limit)
        else:
            assert 0

        # calculate percentile stretch and update min-max range
        eeImageRGB = self.eeImageRgb(eeImage)
        extent = Utils.transformMapCanvasExtent(self.enmapBox.currentMapCanvas(), self.crsEpsg4326)
        eeExtent = ee.Geometry.Rectangle(
            [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], self.epsg4326, False
        )
        percentageMin = self.mPercentileMin.value()
        percentageMax = self.mPercentileMax.value()

        with GeeWaitCursor():
            try:
                percentiles = eeImageRGB.reduceRegion(
                    ee.Reducer.percentile([percentageMin, percentageMax]),
                    bestEffort=True, maxPixels=100000, geometry=eeExtent,
                    scale=self.enmapBox.currentMapCanvas().mapUnitsPerPixel()
                ).getInfo()
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

            percentiles = {k: str(v) for k, v in percentiles.items()}
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

    def eeVisualizationParameters(self) -> Dict:

        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            visParams = {
                'bands': [self.mRedBand.currentText(), self.mGreenBand.currentText(), self.mBlueBand.currentText()],
                'min': [tofloat(mMin.text()) for mMin in [self.mRedMin, self.mGreenMin, self.mBlueMin]],
                'max': [tofloat(mMax.text()) for mMax in [self.mRedMax, self.mGreenMax, self.mBlueMax]],
            }
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            ramp = self.mPseudoColorRamp.colorRamp()
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

    def eeCollection(self) -> Optional[ee.ImageCollection]:
        eeCollection = self.eeFullCollection

        if eeCollection is None:
            self.pushInfoMissingCollection()
            return None

        # filter date range
        eeCollection = eeCollection.filterDate(
            self.mFilterDateStart.date().toString('yyyy-MM-dd'),
            self.mFilterDateEnd.date().addDays(1).toString('yyyy-MM-dd')  # GEE end date is exclusive
        )

        # filter metadata
        for row in range(self.mFilterProperties.rowCount()):
            name: QComboBox = self.mFilterProperties.cellWidget(row, 0).currentText()
            operator: QComboBox = self.mFilterProperties.cellWidget(row, 1).currentText()
            value: QLineEdit = self.mFilterProperties.cellWidget(row, 2).text()
            if name == '' or operator == '' or value == '':
                continue

            evalType = type(self.eeFullCollectionInfo.properties[name])
            eeCollection = eeCollection.filterMetadata(name, operator, evalType(value))

        # filter pixel quality
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
                if isinstance(item, (PixelQualityBitmaskItem, CategoryMaskItem)) and item.checkState(0) == Qt.Checked:
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

    def eeComposite(self, limit: int = None) -> Optional[ee.Image]:
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
            extent = Utils.transformMapCanvasExtent(self.enmapBox.currentMapCanvas(), self.crsEpsg4326)
            eeExtent = ee.Geometry.Rectangle(
                [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], self.epsg4326, False
            )
            eeCollection = eeCollection.filterBounds(eeExtent)
            eeCollection = eeCollection.map(lambda eeImage: eeImage.clip(eeExtent))

        if extentIndex == self.LocationExtent:
            point = self.enmapBox.currentLocation()
            if point is None:
                point = SpatialPoint.fromMapCanvasCenter(self.enmapBox.currentMapCanvas())
            point = point.toCrs(self.crsEpsg4326)
            eePoint = ee.Geometry.Point(point.x(), point.y())
            eeCollection = eeCollection.filterBounds(eePoint)

        if extentIndex == self.GlobalExtent:
            pass

        # limit the collection
        if limit is not None:
            eeCollection = eeCollection.limit(limit)

        # composite
        reducers = {
            'Mean': ee.Reducer.mean(), 'StdDev': ee.Reducer.stdDev(), 'Variance': ee.Reducer.variance(),
            'Kurtosis': ee.Reducer.kurtosis(), 'Skewness': ee.Reducer.skew(), 'First': ee.Reducer.firstNonNull(),
            'Last': ee.Reducer.lastNonNull(), 'Min': ee.Reducer.min(), 'P5': ee.Reducer.percentile([5]),
            'P10': ee.Reducer.percentile([10]), 'P25': ee.Reducer.percentile([25]), 'Median': ee.Reducer.median(),
            'P75': ee.Reducer.percentile([75]), 'P90': ee.Reducer.percentile([90]), 'P95': ee.Reducer.percentile([95]),
            'Max': ee.Reducer.max(), 'Count': ee.Reducer.count(),
        }
        self.mCompositeReducer = self.mReducerRed
        reducer = reducers[self.mCompositeReducer.currentText()]
        bandNames = eeCollection.first().bandNames()
        eeImage = eeCollection.reduce(reducer).rename(bandNames)

        return eeImage

    def compositeLayerName(self):
        seperator = ' – '
        items = list()
        items.append(self.mLayerName.text())

        if self.mAppendDateRange.isChecked():
            dateStart, dateEnd = self.compositeDates()
            if dateStart.daysTo(dateEnd) == 1:
                item = dateStart.CompositeDateStart.text()
            else:
                item = dateStart.text() + ' to ' + dateEnd.text()
            items.append(item)

            # append season if not the whole year
            seasonStart = self.mCompositeSeasonStart.date().toString('MM-dd')
            seasonEnd = self.mCompositeSeasonEnd.date().toString('MM-dd')
            if seasonStart != '01-01' or seasonEnd != '12-31':
                item = seasonStart + ' to ' + seasonEnd
                items.append(item)

        if self.mAppendBandNames.isChecked():
            if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
                items.append(self.mRedBand.currentText())
                items.append(self.mGreenBand.currentText())
                items.append(self.mBlueBand.currentText())
            elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
                items.append(self.mPseudoColorBand.currentText())

        name = seperator.join(items)
        return name

    def eeImage(self) -> Optional[ee.Image]:
        eeCollection = self.eeCollection()

        if eeCollection is None:
            return None

        # this block is not required anymore i guess???
        # filter extent
        #if self.mImageExtent.currentIndex() == self.MapViewExtent:
        #    extent = Utils.transformMapCanvasExtent(self.enmapBox.currentMapCanvas(), self.crsEpsg4326)
        #    eeExtent = ee.Geometry.Rectangle(
        #        [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()], self.epsg4326, False
        #    )
        #    eeCollection = eeCollection.filterBounds(eeExtent)
        #elif self.mImageExtent.currentIndex() == self.LocationExtent:
        #    point = self.enmapBox.currentLocation()
        #    if point is None:
        #        point = SpatialPoint.fromMapCanvasCenter(self.enmapBox.currentMapCanvas())
        #    point = point.toCrs(self.crsEpsg4326)
        #    eePoint = ee.Geometry.Point(point.x(), point.y())
        #    eeCollection = eeCollection.filterBounds(eePoint)
        #else:
        #    assert 0

        # selecte image by ID
        imageId = self.mImageId.text()
        if imageId == '':
            self.pushInfoMissingImage()
            return

        eeImage = eeCollection.filter(ee.Filter.eq('system:index', self.mImageId.text())).first()

        return eeImage

    def imageLayerName(self):
        seperator = ' – '
        items = list()
        items.append(self.mLayerName.text())

        if self.mAppendId.isChecked():
            items.append(self.mImageId.text())

        if self.mAppendBandNames.isChecked():
            if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
                items.append(self.mRedBand.currentText())
                items.append(self.mGreenBand.currentText())
                items.append(self.mBlueBand.currentText())
            elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
                items.append(self.mPseudoColorBand.currentText())

        name = seperator.join(items)
        return name

    def eeImageRgb(self, eeImage: ee.Image) -> ee.Image:
        # select bands for visualization
        if self.mRendererType.currentIndex() == self.MultibandColorRenderer:
            eeImageRed = eeImage.select(self.mRedBand.currentText())
            eeImageGreen = eeImage.select(self.mGreenBand.currentText())
            eeImageBlue = eeImage.select(self.mBlueBand.currentText())
            eeImageRgb = ee.Image.rgb(eeImageRed, eeImageGreen, eeImageBlue)
        elif self.mRendererType.currentIndex() == self.SinglebandPseudocolorRenderer:
            eeImageRgb = eeImage.select(self.mPseudoColorBand.currentText()).rename('vis-pseudo')
        else:
            assert 0

        return eeImageRgb

    def createLayer(self, eeImage: Optional[ee.Image], visParams: Dict, layerName: str):

        from geetimeseriesexplorerapp.externals.ee_plugin import Map

        if eeImage is None:
            return

        # update/create WMS layer
        with GeeWaitCursor():
            try:
                layer = Map.addLayer(eeImage, visParams, layerName)
            except Exception as error:
                print_exc()
                self.mMessageBar.pushCritical('Error', str(error))
                return

        # set collection information
        provider: EarthEngineRasterDataProvider = layer.dataProvider()
        provider.setInformation(self.eeFullCollectionJson, self.eeFullCollectionInfo)

    def pushInfoMissingCollection(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select a collection')

    def pushInfoMissingImage(self):
        self.mMessageBar.pushInfo('Missing parameter', 'select an image')

    def pushInfoQueryCut(self):
        self.mMessageBar.pushInfo('Query', 'collection query cut after accumulating over 5000 elements')

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
def utilsMsecToDateTime(msec: int) -> QDateTime:
    return QDateTime(QDate(1970, 1, 1)).addMSecs(int(msec))

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
