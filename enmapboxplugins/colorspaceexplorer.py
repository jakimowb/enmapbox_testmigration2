from random import randint

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QToolButton, QCheckBox, QMainWindow, QSpinBox, QGridLayout, QLayoutItem
from PyQt5.uic import loadUi
from qgis._core import QgsRasterLayer, QgsMultiBandColorRenderer, QgsContrastEnhancement, QgsRasterMinMaxOrigin
from qgis._gui import QgsMapCanvas, QgsRasterBandComboBox

from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from typeguard import typechecked


@typechecked
class ColorSpaceExplorerWidget(QMainWindow):
    mRed: QgsRasterBandComboBox
    mGreen: QgsRasterBandComboBox
    mBlue: QgsRasterBandComboBox
    mRandomBands: QToolButton
    mRedDelta: QSpinBox
    mGreenDelta: QSpinBox
    mBlueDelta: QSpinBox
    mRandomDelta: QToolButton
    mRandomDeltaMax: QSpinBox

    mPrevious: QToolButton
    mNext: QToolButton
    mPlay: QToolButton
    mFps: QSpinBox

    mGridLayout: QGridLayout

    mLiveUpdate: QCheckBox

    mOk: QToolButton
    mCancel: QToolButton
    mApply: QToolButton

    def __init__(self, layer: QgsRasterLayer, mapCanvas: QgsMapCanvas, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)
        self.layer = layer
        self.mapCanvas = mapCanvas
        assert isinstance(layer.renderer(), QgsMultiBandColorRenderer)
        self.rendererBackup = layer.renderer().clone()

        self.mRed.setLayer(layer)
        self.mGreen.setLayer(layer)
        self.mBlue.setLayer(layer)

        if isinstance(self.rendererBackup, QgsMultiBandColorRenderer):
            self.mRed.setBand(self.rendererBackup.redBand())
            self.mGreen.setBand(self.rendererBackup.greenBand())
            self.mBlue.setBand(self.rendererBackup.blueBand())
        else:
            self.mRed.setLayer(1)
            self.mGreen.setLayer(1)
            self.mBlue.setLayer(1)

        for mDelta in [self.mRedDelta, self.mGreenDelta, self.mBlueDelta]:
            mDelta.setMinimum(-self.layer.bandCount())
            mDelta.setMaximum(self.layer.bandCount())
        self.mRandomDeltaMax.setMaximum(self.layer.bandCount())

        for i in range(1, 17):
            mRgb: QToolButton = getattr(self, f'mRgb_{i}')
            text = mRgb.text()
            tmp = text.split(' ')
            name = ' '.join(tmp[:-1])
            bands = tmp[-1][1:-1].split('-')
            mRgb.setText(name)
            mRgb.bands = bands
            mRgb.clicked.connect(self.onPredefinedRgbClicked)

        self.mRed.bandChanged.connect(self.onLiveUpdate)
        self.mGreen.bandChanged.connect(self.onLiveUpdate)
        self.mBlue.bandChanged.connect(self.onLiveUpdate)

        self.mRandomBands.clicked.connect(self.onRandomBandsClicked)
        self.mNext.clicked.connect(self.onNextClicked)
        self.mPrevious.clicked.connect(self.onPreviousClicked)
        self.mPlay.clicked.connect(self.onPlayClicked)

        self.mRandomBands.clicked.connect(self.onRandomBandsClicked)
        self.mRandomDelta.clicked.connect(self.onRandomDeltaClicked)

        self.mOk.clicked.connect(self.onOkClicked)
        self.mCancel.clicked.connect(self.onCancelClicked)
        self.mApply.clicked.connect(self.onApplyClicked)

    def onPredefinedRgbClicked(self):
        mRgb = self.sender()
        bands = [CreateSpectralIndicesAlgorithm.translateSentinel2Band(band) for band in mRgb.bands]
        r, g, b = [CreateSpectralIndicesAlgorithm.findBroadBand(self.layer, band) for band in bands]
        self.mRed.setBand(r)
        self.mGreen.setBand(g)
        self.mBlue.setBand(b)

    def onRandomBandsClicked(self):
        self.mRed.setBand(randint(1, self.layer.bandCount()))
        self.mGreen.setBand(randint(1, self.layer.bandCount()))
        self.mBlue.setBand(randint(1, self.layer.bandCount()))

    def onRandomDeltaClicked(self):
        v = min(self.mRandomDeltaMax.value(), self.layer.bandCount())
        for mDelta in [self.mRedDelta, self.mGreenDelta, self.mBlueDelta]:
            mDelta.setValue(randint(-v, v))

    def nextBandNo(self, bandNo: int, delta: int, backwards) -> int:
        if backwards:
            delta = -delta
        bandNo += delta
        bandNo = ((bandNo - 1) % self.layer.bandCount()) + 1
        return bandNo

    def onNextClicked(self, *args, backwards=False):
        self.mRed.setBand(self.nextBandNo(self.mRed.currentBand(), self.mRedDelta.value(), backwards))
        self.mGreen.setBand(self.nextBandNo(self.mGreen.currentBand(), self.mGreenDelta.value(), backwards))
        self.mBlue.setBand(self.nextBandNo(self.mBlue.currentBand(), self.mBlueDelta.value(), backwards))

    def onPreviousClicked(self):
        self.onNextClicked(backwards=True)

    def onPlayClicked(self):
        self.onNextClicked()
        self.mapCanvas.waitWhileRendering()
        if self.mPlay.isChecked():
            animationFrameLength = 1000 / self.mFps.value()
            QTimer.singleShot(animationFrameLength, self.onPlayClicked)

    def onOkClicked(self):
        self.onApplyClicked()
        self.close()

    def onCancelClicked(self):
        self.layer.setRenderer(self.rendererBackup)
        self.layer.triggerRepaint()
        self.close()

    def onApplyClicked(self):
        self.layer.renderer().setRedBand(self.mRed.currentBand())
        self.layer.renderer().setGreenBand(self.mGreen.currentBand())
        self.layer.renderer().setBlueBand(self.mBlue.currentBand())
        if hasattr(self.layer, 'setCacheImage'):
            self.layer.setCacheImage(None)

        algorithm = QgsContrastEnhancement.StretchToMinimumMaximum
        limits = QgsRasterMinMaxOrigin.CumulativeCut
        self.layer.setContrastEnhancement(algorithm, limits)  # rest is defined by the layer style
        # self.layer.triggerRepaint()

    def onLiveUpdate(self):
        if self.mLiveUpdate.isChecked():
            self.onApplyClicked()
