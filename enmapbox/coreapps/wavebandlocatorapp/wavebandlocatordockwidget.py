from math import nan
from typing import Optional

from PyQt5.QtWidgets import QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QToolButton, QLabel, QTabWidget, \
    QLineEdit
from qgis.PyQt import uic
from qgis._core import QgsRasterLayer, QgsSingleBandGrayRenderer, QgsRectangle, \
    QgsContrastEnhancement, QgsRasterRenderer, QgsMultiBandColorRenderer, QgsSingleBandPseudoColorRenderer, \
    QgsMapLayerProxyModel
from qgis._gui import (QgsDockWidget, QgsRasterBandComboBox, QgsMapLayerComboBox)

from enmapbox import EnMAPBox
from enmapbox.externals.qps.utils import SpatialExtent
from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class WavebandLocatorDockWidget(QgsDockWidget):
    mInfo: QLabel
    mLayer: QgsMapLayerComboBox
    mRefresh: QToolButton
    mRenderer: QTabWidget

    mGrayBand: QgsRasterBandComboBox
    mGrayMin: QLineEdit
    mGrayMax: QLineEdit
    mGraySlider: QSlider
    mGrayWavelength: QSpinBox

    mMinMaxUser: QCheckBox
    mMinMaxPercentile: QCheckBox
    mP1: QDoubleSpinBox
    mP2: QDoubleSpinBox
    mExtent: QComboBox
    mAccuracy: QComboBox
    mApply: QToolButton

    def __init__(self, enmapBox: EnMAPBox, parent=None):
        QgsDockWidget.__init__(self, parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)
        self.enmapBox = enmapBox
        self.defaultRenderer: Optional[QgsRasterRenderer] = None
        self.mLayer.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.cache = dict()

        self.visibilityChanged.connect(self.onPanelVisibilityChanged)

        # self.enmapBox.currentLayerChanged.connect(self.mLayer.setLayer)  # do we want this?
        self.mLayer.layerChanged.connect(self.onCurrentLayerChanged)
        self.mRefresh.clicked.connect(self.onCurrentLayerChanged)

        self.mRenderer.currentChanged.connect(self.onRendererTabChanged)

        # gray renderer
        self.mGrayMin.textChanged.connect(self.updateRenderer)
        self.mGrayMax.textChanged.connect(self.updateRenderer)
        self.mGraySlider.valueChanged.connect(self.mGrayBand.setBand)
        self.mGrayBand.bandChanged.connect(self.mGraySlider.setValue)
        self.mGrayBand.bandChanged.connect(self.onBandChanged)

        # min / max value settings
        self.mP1.valueChanged.connect(self.updateMinMax)
        self.mP2.valueChanged.connect(self.updateMinMax)
        self.mExtent.currentIndexChanged.connect(self.onBandChanged)
        self.mAccuracy.currentIndexChanged.connect(self.onBandChanged)
        self.mApply.clicked.connect(self.updateMinMax)

        self.initGui()
        self.disableGui()

    def initGui(self):
        for sname in CreateSpectralIndicesAlgorithm.ShortNames:
            lname = CreateSpectralIndicesAlgorithm.LongNameMapping[sname]
            wavelength, fwhm = CreateSpectralIndicesAlgorithm.WavebandMapping[sname]
            mWaveband: QToolButton = getattr(self, 'mGrayWaveband' + sname)
            mWaveband.setToolTip(f'{lname} at {wavelength} Nanometers')
            mWaveband.clicked.connect(self.onWavebandClicked)

    def updateGui(self):
        layer: QgsRasterLayer = self.mLayer.currentLayer()

        # set waveband enabled state
        for sname in CreateSpectralIndicesAlgorithm.ShortNames:

            # let's cache the broad band matching, because it takes a second
            cacheKey = layer.source(), sname
            if not cacheKey in self.cache:
                isWaveband = CreateSpectralIndicesAlgorithm.findBroadBand(layer, sname, strict=True) is not None
                self.cache[cacheKey] = isWaveband
            isWaveband = self.cache[cacheKey]

            mWaveband: QToolButton = getattr(self, 'mGrayWaveband' + sname)
            mWaveband.setVisible(isWaveband)

    def onPanelVisibilityChanged(self):
        self.onCurrentLayerChanged()  # trigger GUI initialization

    def onWavebandClicked(self):
        mWaveband: QToolButton = self.sender()
        bandName, sname = mWaveband.objectName().split('Waveband')
        mBand: QgsRasterBandComboBox = getattr(self, bandName + 'Band')
        wavelength, fwhm = CreateSpectralIndicesAlgorithm.WavebandMapping[sname]
        reader = RasterReader(self.mLayer.currentLayer())
        bandNo = reader.findWavelength(wavelength)
        mBand.setBand(bandNo)

    def onCurrentLayerChanged(self):

        if self.isHidden():  # do nothing if panel is hidden
            return

        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if not isinstance(layer, QgsRasterLayer):
            self.disableGui()
            return
        else:
            self.enableGui()

        self.defaultRenderer = layer.renderer().clone()

        self.mRenderer.blockSignals(True)
        renderer = layer.renderer()
        if isinstance(renderer, QgsMultiBandColorRenderer):
            self.mRenderer.setCurrentIndex(0)
        elif isinstance(renderer, QgsSingleBandGrayRenderer):
            self.mRenderer.setCurrentIndex(1)
        elif isinstance(renderer, QgsSingleBandPseudoColorRenderer):
            self.mRenderer.setCurrentIndex(2)
        else:
            self.mRenderer.setCurrentIndex(3)
        self.mRenderer.blockSignals(False)

        self.onRendererTabChanged()

        self.enableGui()
        self.updateGui()

    def onRendererTabChanged(self):
        layer: QgsRasterLayer = self.mLayer.currentLayer()

        if layer is None:
            return

        if self.mRenderer.currentIndex() == 0:  # RGB
            pass
        elif self.mRenderer.currentIndex() == 1:  # Gray
            self.mGrayBand.setLayer(layer)
            self.mGraySlider.setRange(1, layer.bandCount())

            renderer: QgsSingleBandGrayRenderer = layer.renderer()
            if not isinstance(layer.renderer(), QgsSingleBandGrayRenderer):
                renderer = Utils.singleBandGrayRenderer(layer.dataProvider(), 1, nan, nan)
                layer.setRenderer(renderer)
            ce: QgsContrastEnhancement = renderer.contrastEnhancement()
            self.mGrayMin.blockSignals(True)
            self.mGrayMax.blockSignals(True)
            self.mGrayMin.setText(str(ce.minimumValue()))
            self.mGrayMax.setText(str(ce.maximumValue()))
            self.mGrayMin.blockSignals(False)
            self.mGrayMax.blockSignals(False)

            self.mGrayBand.setBand(renderer.grayBand())
        elif self.mRenderer.currentIndex() == 2:  # Pseudocolor
            pass
        elif self.mRenderer.currentIndex() == 3:  # default
            layer.setRenderer(self.defaultRenderer.clone())
        else:
            assert 0

        if self.mRenderer.currentIndex() == 3:  # default
            self.mGroupBox.hide()
        else:
            self.mGroupBox.show()

        self.updateMinMax()
        self.updateRenderer()

    def onBandChanged(self):
        mBand: QgsRasterBandComboBox = self.sender()
        mWavelength: QSpinBox = {'mGrayBand': self.mGrayWavelength}[mBand.objectName()]

        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if layer is None:
            return

        bandNo = mBand.currentBand()

        # Check if renderer type was changed externally.
        # If so, create a new renderer with correct type.
        if self.mRenderer.currentIndex() == 0:  # RGB
            pass
        elif self.mRenderer.currentIndex() == 1:  # Gray
            if not isinstance(layer.renderer(), QgsSingleBandGrayRenderer):
                renderer = Utils.singleBandGrayRenderer(layer.dataProvider(), bandNo, nan, nan)
                layer.setRenderer(renderer)
        elif self.mRenderer.currentIndex() == 2:  # Pseudocolor
            pass
        elif self.mRenderer.currentIndex() == 3:  # default
            pass
        else:
            assert 0

        # update wavelength info
        wavelength = RasterReader(layer).wavelength(bandNo)
        if wavelength is None:
            mWavelength.hide()
        else:
            mWavelength.show()
            mWavelength.setValue(int(wavelength))

        self.updateMinMax()
        self.updateRenderer()

    def updateMinMax(self):
        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if layer is None:
            return

        def setCumulativeCut(bandNo: int, mBandMin: QLineEdit, mBandMax: QLineEdit):
            vmin, vmax = layer.dataProvider().cumulativeCut(
                bandNo, self.mP1.value() / 100., self.mP2.value() / 100., self.currentExtent(),
                self.currentSampleSize()
            )
            mBandMin.setText(str(vmin))
            mBandMax.setText(str(vmax))

        if self.mRenderer.currentIndex() == 0:  # RGB
            pass
        elif self.mRenderer.currentIndex() == 1:  # Gray
            if self.mMinMaxPercentile.isChecked():
                setCumulativeCut(self.mGrayBand.currentBand(), self.mGrayMin, self.mGrayMax)
        elif self.mRenderer.currentIndex() == 2:  # Pseudocolor
            pass
        elif self.mRenderer.currentIndex() == 3:  # default
            pass
        else:
            assert 0

    def updateRenderer(self):
        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if layer is None:
            return

        if self.mRenderer.currentIndex() == 0:  # RGB
            pass
        elif self.mRenderer.currentIndex() == 1:  # Gray
            bandNo = self.mGrayBand.currentBand()
            renderer: QgsSingleBandGrayRenderer = layer.renderer()
            renderer.setGrayBand(bandNo)
            ce = renderer.contrastEnhancement()
            ce.setMinimumValue(tofloat(self.mGrayMin.text()))
            ce.setMaximumValue(tofloat(self.mGrayMax.text()))
        elif self.mRenderer.currentIndex() == 2:  # Pseudocolor
            pass
        elif self.mRenderer.currentIndex() == 3:  # default
            pass
        else:
            assert 0

        layer.triggerRepaint()

    def currentExtent(self) -> QgsRectangle:

        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if self.mExtent.currentText() == 'Whole raster':
            return layer.extent()
        elif self.mExtent.currentText() == 'Current canvas':
            mapCanvas = self.enmapBox.currentMapCanvas()
            return SpatialExtent(mapCanvas.crs(), mapCanvas.extent()).toCrs(layer.crs())
        else:
            assert 0

    def currentSampleSize(self) -> int:
        if self.mAccuracy.currentText() == 'Estimated (faster)':
            return int(QgsRasterLayer.SAMPLE_SIZE)
        elif self.mAccuracy.currentText() == 'Actual (slower)':
            return 0
        else:
            assert 0

    def disableGui(self):
        self.mInfo.show()
        self.mRenderer.hide()
        self.mGroupBox.hide()

    def enableGui(self):
        self.mInfo.hide()
        self.mRenderer.show()
        self.mGroupBox.show()


# utils
def tofloat(text: str) -> float:
    try:
        return float(text)
    except:
        return nan
