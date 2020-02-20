import sys, os, re
from osgeo import gdal, ogr, osr
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
import numpy as np
from enmapbox import DIR_UIFILES
from enmapbox.gui.utils import parseWavelength, convertMetricUnit, LUT_WAVELENGTH,  loadUi, enmapboxUiPath

import enmapbox

class EnMAPBoxRasterLayerConfigWidget(QgsMapLayerConfigWidget):

    def __init__(self, layer:QgsRasterLayer, canvas:QgsMapCanvas, parent:QWidget=None):

        super(EnMAPBoxRasterLayerConfigWidget, self).__init__(layer, canvas, parent=parent)
        loadUi(enmapboxUiPath('rasterlayerconfigwidget.ui'), self)
        self.mCanvas = canvas
        self.mLayer = layer
        self.mLayer.rendererChanged.connect(self.onRendererChanged)
        assert isinstance(self.cbSingleBand, QgsRasterBandComboBox)

        self.cbSingleBand.setLayer(self.mLayer)
        self.cbMultiBandRed.setLayer(self.mLayer)
        self.cbMultiBandGreen.setLayer(self.mLayer)
        self.cbMultiBandBlue.setLayer(self.mLayer)

        self.cbSingleBand.bandChanged.connect(self.widgetChanged)
        self.cbMultiBandRed.bandChanged.connect(self.widgetChanged)
        self.cbMultiBandGreen.bandChanged.connect(self.widgetChanged)
        self.cbMultiBandBlue.bandChanged.connect(self.widgetChanged)


        assert isinstance(self.sliderSingleBand, QSlider)
        self.sliderSingleBand.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandRed.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandGreen.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandBlue.setRange(1, self.mLayer.bandCount())

        mWL, mWLUnit = parseWavelength(self.mLayer)
        if isinstance(mWL, list):
            mWL = np.asarray(mWL)

        if isinstance(mWLUnit, str) and mWLUnit != 'nm':
            try:
                # convert to nanometers
                mWL = np.asarray([convertMetricUnit(v, mWLUnit, 'nm') for v in mWL])
            except:
                mWL = None
                mWLUnit = None

        self.mWL = mWL
        self.mWLUnit = mWLUnit

        hasWL = self.mWL is not None
        self.gbMultiBandWavelength.setEnabled(hasWL)
        self.gbSingleBandWavelength.setEnabled(hasWL)

        self.btnSetSBBand_B.clicked.connect(lambda : self.setWL(('B',)))
        self.btnSetSBBand_G.clicked.connect(lambda: self.setWL(('G',)))
        self.btnSetSBBand_R.clicked.connect(lambda: self.setWL(('R',)))
        self.btnSetSBBand_NIR.clicked.connect(lambda: self.setWL(('NIR',)))
        self.btnSetSBBand_SWIR.clicked.connect(lambda: self.setWL(('SWIR',)))

        self.btnSetMBBands_RGB.clicked.connect(lambda : self.setWL(('R','G','B')))
        self.btnSetMBBands_NIRRG.clicked.connect(lambda: self.setWL(('NIR', 'R', 'G')))
        self.btnSetMBBands_SWIRNIRR.clicked.connect(lambda: self.setWL(('SWIR', 'NIR', 'R')))


        self.initRenderer()

        self.setPanelTitle('EnMAP-Box Raster Settings')

    def onRendererChanged(self):
        self.initRenderer()

    def initRenderer(self):

        renderer = self.mLayer.renderer()
        w = self.renderBandWidget
        assert isinstance(self.labelRenderType, QLabel)
        assert isinstance(w, QStackedWidget)
        self.labelRenderType.setText(str(renderer.type()))
        if isinstance(renderer, (QgsSingleBandGrayRenderer, QgsSingleBandColorDataRenderer, QgsSingleBandPseudoColorRenderer, QgsPalettedRasterRenderer)):
            w.setCurrentWidget(self.pageSingleBand)
        elif isinstance(renderer, QgsMultiBandColorRenderer):
            w.setCurrentWidget(self.pageMultiBand)
        else:
            w.setCurrentWidget(self.pageUnknown)

    def renderer(self)->QgsRasterRenderer:
        return self.mLayer.renderer()

    def apply(self):
        r = self.renderer()
        newRenderer = None
        if isinstance(r, QgsSingleBandGrayRenderer):
            newRenderer = self.renderer().clone()
            newRenderer.setGrayBand(self.cbSingleBand.currentBand())

        elif isinstance(r, QgsSingleBandPseudoColorRenderer):
            pass
            # there is a bug when using the QgsSingleBandPseudoColorRenderer.setBand()
            # see https://github.com/qgis/QGIS/issues/31568
            #band = self.cbSingleBand.currentBand()
            vMin, vMax = r.shader().minimumValue(), r.shader().maximumValue()
            shader = QgsRasterShader(vMin, vMax)

            f = r.shader().rasterShaderFunction()
            if isinstance(f, QgsColorRampShader):
                shaderFunction = QgsColorRampShader(f)
            else:
                shaderFunction = QgsRasterShaderFunction(f)

            shader.setRasterShaderFunction(shaderFunction)
            newRenderer = QgsSingleBandPseudoColorRenderer(r.input(), self.cbSingleBand.currentBand(), shader)

        elif isinstance(r, QgsPalettedRasterRenderer):
            newRenderer = QgsPalettedRasterRenderer(r.input(), self.cbSingleBand.currentBand(), r.classes())

            #r.setBand(band)
        elif isinstance(r, QgsSingleBandColorDataRenderer):
            newRenderer = QgsSingleBandColorDataRenderer(r.input(), self.cbSingleBand.currentBand())

        elif isinstance(r, QgsMultiBandColorRenderer):
            newRenderer = self.renderer().clone()
            newRenderer.setRedBand(self.cbMultiBandRed.currentBand())
            newRenderer.setGreenBand(self.cbMultiBandGreen.currentBand())
            newRenderer.setBlueBand(self.cbMultiBandBlue.currentBand())

        if isinstance(newRenderer, QgsRasterRenderer):
            self.mLayer.setRenderer(newRenderer)

    def wlBand(self, wlKey:str)->int:
        if isinstance(self.mWL, np.ndarray):
            targetWL = float(LUT_WAVELENGTH[wlKey])
            return int(np.argmin(np.abs(self.mWL - targetWL)))+1
        else:
            return None

    def setWL(self, wlRegions:tuple):
        r = self.renderer().clone()
        if isinstance(r, (QgsSingleBandGrayRenderer, QgsSingleBandPseudoColorRenderer, QgsSingleBandColorDataRenderer)):
            band = self.wlBand(wlRegions[0])
            self.cbSingleBand.setBand(band)
        elif isinstance(r, QgsMultiBandColorRenderer):
            bR = self.wlBand(wlRegions[0])
            bG = self.wlBand(wlRegions[1])
            bB = self.wlBand(wlRegions[2])

            self.cbMultiBandBlue.setBand(bB)
            self.cbMultiBandGreen.setBand(bG)
            self.cbMultiBandRed.setBand(bR)

        pass

    def setDockMode(self, dockMode:bool):
        pass

class EnMAPBoxRasterLayerConfigWidgetFactory(QgsMapLayerConfigWidgetFactory):

    def __init__(self):
        import enmapbox

        super(EnMAPBoxRasterLayerConfigWidgetFactory, self).__init__('EnMAPBox', enmapbox.icon())
        self.setIcon(enmapbox.icon())

        self.setSupportLayerPropertiesDialog(True)
        self.setSupportsStyleDock(True)
        self.setTitle('EnMAP-Box Raster Layer Properties')

    def supportsLayer(self, layer):

        if isinstance(layer, QgsRasterLayer):
            return True

        return False

    def supportLayerPropertiesDialog(self):
        return False

    def supportsStyleDock(self):
        return True


    def createWidget(self, layer, canvas, dockWidget=True, parent=None)->QgsMapLayerConfigWidget:

        w = EnMAPBoxRasterLayerConfigWidget(layer, canvas, parent=parent)
        self._w = w
        return w
