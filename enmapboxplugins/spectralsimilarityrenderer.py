from copy import deepcopy
from typing import List

import numpy as np
from PyQt5.QtWidgets import QWidget, QToolButton, QCheckBox, \
    QMainWindow, QComboBox, QRadioButton, QLineEdit
from PyQt5.uic import loadUi
from qgis._core import QgsRasterRenderer, QgsRasterInterface, QgsRectangle, QgsRasterBlockFeedback, Qgis, \
    QgsRasterLayer, QgsMultiBandColorRenderer, QgsCoordinateTransform, QgsProject
from qgis._gui import QgsMapCanvas, QgsRasterBandComboBox, QgsDoubleSpinBox
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler, MinMaxScaler

from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class SpectralSimilarityRenderer(QgsRasterRenderer):
    endmember: np.ndarray
    minimumValue: float
    maximumValue: float

    def __init__(self, input: QgsRasterInterface = None, type: str = ''):
        super().__init__(input, type)

    def setEndmembers(self, endmembers: np.ndarray):
        self.endmembers = endmembers

    def setMinimumValue(self, value: float):
        self.minimumValue = value

    def setMaximumValue(self, value: float):
        self.maximumValue = value

    def usesBands(self) -> List[int]:
        return list(range(self.input().bandCount()))

    def block(self, band_nr: int, extent: QgsRectangle, width: int, height: int,
              feedback: QgsRasterBlockFeedback = None):
        # read data
        reader = RasterReader(self.input())
        array = reader.array(width=width, height=height, boundingBox=extent)
        maskArray = np.all(reader.maskArray(array), axis=0)

        # calculate max. similarity over all endmember
        array = np.array(array, dtype=np.float32)
        minRmse = np.full((height, width), np.inf, np.float32)
        for endmember in self.endmembers:
            endmember = np.reshape(endmember, (-1, 1, 1))
            similarity = np.sqrt(np.mean((array - endmember) ** 2, axis=0))
            np.minimum(minRmse, similarity, out=minRmse)

        # scale to 0-255
        scale = self.maximumValue - self.minimumValue
        minRmse = (minRmse - self.minimumValue) * (255 / scale)
        np.clip(minRmse, 0, 255, out=minRmse)
        minRmse = np.array(minRmse, np.uint32)

        # convert back to QGIS raster block
        r = g = b = minRmse

        a = np.zeros((height, width), dtype=np.uint32)
        a[maskArray] = 255
        outarray = (r << 16) + (g << 8) + b + (a << 24)
        return Utils.numpyArrayToQgsRasterBlock(outarray, Qgis.ARGB32_Premultiplied)

    def clone(self) -> QgsRasterRenderer:
        renderer = SpectralSimilarityRenderer()
        renderer.endmembers = deepcopy(self.endmembers)
        renderer.minimumValue = self.minimumValue
        renderer.maximumValue = self.maximumValue
        return renderer


@typechecked
class SpectralSimilarityRendererWidget(QMainWindow):
    mMin: QLineEdit
    mMax: QLineEdit

    mMinMaxUser: QRadioButton
    mMinMaxPercentile: QRadioButton
    mMinMaxMinMax: QRadioButton

    mP1: QgsDoubleSpinBox
    mP2: QgsDoubleSpinBox

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

        self.mP1.setClearValue(self.mP1.value())
        self.mP2.setClearValue(self.mP2.value())
        self.mP1.valueChanged.connect(lambda v1: self.mP2.setValue(max(self.mP2.value(), v1 + 1)))
        self.mP2.valueChanged.connect(lambda v2: self.mP1.setValue(min(self.mP1.value(), v2 - 1)))

        self.mP1.valueChanged.connect(self.onLiveUpdate)
        self.mP2.valueChanged.connect(self.onLiveUpdate)

        self.mOk.clicked.connect(self.onOkClicked)
        self.mCancel.clicked.connect(self.onCancelClicked)
        self.mApply.clicked.connect(self.onApplyClicked)

    def currentRenderer(self) -> SpectralSimilarityRenderer:

        if self.mMinMaxUser.isChecked():
            assert 0


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
        # percentiles = np.percentile(Xt, [2, 98], axis=0)
        scaler2 = MinMaxScaler(feature_range=[0, 255], clip=True)
        scaler2.fit(percentiles)

        # make renderer
        renderer = SpectralSimilarityRenderer()
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
