from copy import deepcopy
from typing import List


import numpy as np
from PyQt5.QtWidgets import QWidget, QToolButton, QCheckBox, \
    QMainWindow, QComboBox
from PyQt5.uic import loadUi
from qgis._core import QgsRasterRenderer, QgsRasterInterface, QgsRectangle, QgsRasterBlockFeedback, Qgis, \
    QgsRasterLayer, QgsMultiBandColorRenderer, QgsCoordinateTransform, QgsProject
from qgis._gui import QgsMapCanvas, QgsRasterBandComboBox, QgsDoubleSpinBox

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import RobustScaler, MinMaxScaler
except ModuleNotFoundError:
    from unittest.mock import Mock
    RobustScaler = MinMaxScaler = PCA = Mock()

from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class DecorrelationStretchRenderer(QgsRasterRenderer):
    pca: PCA
    scaler1: RobustScaler
    scaler2: MinMaxScaler
    bandList: List[int]

    def __init__(self, input: QgsRasterInterface = None, type: str = ''):
        super().__init__(input, type)

    def setTransformer(self, pca: PCA, scaler1: RobustScaler, scaler2: MinMaxScaler):
        self.pca = pca
        self.scaler1 = scaler1
        self.scaler2 = scaler2

    def setBandList(self, bandList: List[int]):
        self.bandList = bandList

    def usesBands(self) -> List[int]:
        return list(self.bandList)

    def block(self, band_nr: int, extent: QgsRectangle, width: int, height: int,
              feedback: QgsRasterBlockFeedback = None):
        # read data
        reader = RasterReader(self.input())
        array = reader.array(width=width, height=height, bandList=self.bandList, boundingBox=extent)
        maskArray = np.all(reader.maskArray(array, self.bandList), axis=0)

        # convert to sklearn sample format
        X = np.transpose([a[maskArray] for a in array])

        # transform data
        XPca = self.pca.transform(X)
        XPcaStretched = self.scaler1.transform(XPca)
        Xt = self.pca.inverse_transform(XPcaStretched)
        XRgb = self.scaler2.transform(Xt)

        # convert back to spatial block
        r = np.zeros((height, width), dtype=np.uint32)
        g = np.zeros((height, width), dtype=np.uint32)
        b = np.zeros((height, width), dtype=np.uint32)
        a = np.zeros((height, width), dtype=np.uint32)
        r[maskArray] = XRgb[:, 0]
        g[maskArray] = XRgb[:, 1]
        b[maskArray] = XRgb[:, 2]
        a[maskArray] = 255

        # convert back to QGIS raster block
        outarray = (r << 16) + (g << 8) + b + (a << 24)
        return Utils.numpyArrayToQgsRasterBlock(outarray, Qgis.ARGB32_Premultiplied)

    def clone(self) -> QgsRasterRenderer:
        renderer = DecorrelationStretchRenderer()
        renderer.pca = deepcopy(self.pca)
        renderer.scaler1 = deepcopy(self.scaler1)
        renderer.scaler2 = deepcopy(self.scaler2)
        renderer.bandList = deepcopy(self.bandList)
        return renderer


@typechecked
class DecorrelationStretchRendererWidget(QMainWindow):
    mRed: QgsRasterBandComboBox
    mGreen: QgsRasterBandComboBox
    mBlue: QgsRasterBandComboBox

    mP1: QgsDoubleSpinBox
    mP2: QgsDoubleSpinBox

    mExtent: QComboBox
    mAccurary: QComboBox

    mLiveUpdate: QCheckBox

    mOk: QToolButton
    mCancel: QToolButton
    mApply: QToolButton

    def __init__(self, layer: QgsRasterLayer, mapCanvas: QgsMapCanvas, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)
        self.layer = layer
        self.mapCanvas = mapCanvas
        self.rendererBackup = layer.renderer().clone()

        self.mRed.setLayer(layer)
        self.mGreen.setLayer(layer)
        self.mBlue.setLayer(layer)

        self.mP1.setClearValue(self.mP1.value())
        self.mP2.setClearValue(self.mP2.value())
        self.mP1.valueChanged.connect(lambda v1: self.mP2.setValue(max(self.mP2.value(), v1 + 1)))
        self.mP2.valueChanged.connect(lambda v2: self.mP1.setValue(min(self.mP1.value(), v2 - 1)))

        if isinstance(self.rendererBackup, DecorrelationStretchRenderer):
            self.mRed.setBand(self.rendererBackup.bandList[0])
            self.mGreen.setBand(self.rendererBackup.bandList[1])
            self.mBlue.setBand(self.rendererBackup.bandList[2])
        elif isinstance(self.rendererBackup, QgsMultiBandColorRenderer):
            self.mRed.setBand(self.rendererBackup.redBand())
            self.mGreen.setBand(self.rendererBackup.greenBand())
            self.mBlue.setBand(self.rendererBackup.blueBand())
        else:
            self.mRed.setLayer(1)
            self.mGreen.setLayer(min(2, layer.bandCount()))
            self.mBlue.setLayer(min(3, layer.bandCount()))

        self.mRed.bandChanged.connect(self.onLiveUpdate)
        self.mGreen.bandChanged.connect(self.onLiveUpdate)
        self.mBlue.bandChanged.connect(self.onLiveUpdate)
        self.mP1.valueChanged.connect(self.onLiveUpdate)
        self.mP2.valueChanged.connect(self.onLiveUpdate)
        self.mExtent.currentIndexChanged.connect(self.onLiveUpdate)
        self.mAccurary.currentIndexChanged.connect(self.onLiveUpdate)

        self.mOk.clicked.connect(self.onOkClicked)
        self.mCancel.clicked.connect(self.onCancelClicked)
        self.mApply.clicked.connect(self.onApplyClicked)

    def currentRenderer(self) -> DecorrelationStretchRenderer:
        bandList = [band.currentBand() for band in [self.mRed, self.mGreen, self.mBlue]]
        quantile_range = self.mP1.value(), self.mP2.value()

        # derive extent
        WholeRasterExtent, CurrentCanvasExtent = 0, 1
        if self.mExtent.currentIndex() == WholeRasterExtent:
            extent = self.layer.extent()
        elif self.mExtent.currentIndex() == CurrentCanvasExtent:
            if self.layer.crs() == self.mapCanvas.mapSettings().destinationCrs():
                transform = QgsCoordinateTransform(
                    self.layer.crs(), self.mapCanvas.mapSettings().destinationCrs(), QgsProject.instance()
                )
                extent: QgsRectangle = transform.transformBoundingBox(self.mapCanvas.extent())
            else:
                extent: QgsRectangle = self.mapCanvas.extent()
            extent.intersect(self.layer.extent())
        else:
            assert 0

        # derive sample size
        nEstimated = 100
        EstimateAccuracy, ActualAccuracy = 0, 1
        if self.mAccurary.currentIndex() == EstimateAccuracy:
            if self.mExtent.currentIndex() == WholeRasterExtent:
                width = min(nEstimated, self.layer.width())
                height = min(nEstimated, self.layer.height())
            elif self.mExtent.currentIndex() == CurrentCanvasExtent:
                width = min(nEstimated, self.mapCanvas.width())
                height = min(nEstimated, self.mapCanvas.height())
            else:
                assert 0
        elif self.mAccurary.currentIndex() == ActualAccuracy:
            width = height = None  # derived by reader
        else:
            assert 0

        # read trainings data
        reader = RasterReader(self.layer)
        array = reader.array(bandList=bandList, width=width, height=height, boundingBox=extent)
        maskArray = np.all(reader.maskArray(array, bandList), axis=0)

        # fit transformers
        X = np.transpose([a[maskArray] for a in array])
        pca = PCA(n_components=3)
        pca.fit(X)
        XPca = pca.transform(X)
        scaler1 = RobustScaler(with_centering=False, quantile_range=quantile_range)
        scaler1.fit(XPca)
        XPcaStretched = scaler1.transform(XPca)
        Xt = pca.inverse_transform(XPcaStretched)
        percentiles = np.percentile(Xt, quantile_range, axis=0)
        #percentiles = np.percentile(Xt, [2, 98], axis=0)
        scaler2 = MinMaxScaler(feature_range=[0, 255], clip=True)
        scaler2.fit(percentiles)

        # make renderer
        renderer = DecorrelationStretchRenderer()
        renderer.setTransformer(pca, scaler1, scaler2)
        renderer.setBandList(bandList)

        return renderer

    def onOkClicked(self):
        self.onApplyClicked()
        self.close()

    def onCancelClicked(self):
        self.layer.setRenderer(self.rendererBackup)
        self.layer.triggerRepaint()
        self.close()

    def onApplyClicked(self):
        self.layer.setRenderer(self.currentRenderer())
        self.layer.triggerRepaint()

    def onLiveUpdate(self):
        if self.mLiveUpdate.isChecked():
            self.onApplyClicked()
