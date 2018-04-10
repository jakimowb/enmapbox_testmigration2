# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    layerproperties.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


import collections
import os
import re

from osgeo import gdal, ogr
import numpy as np
from qgis.gui import *
from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.utils import loadUI, SpatialExtent
from enmapbox.gui.widgets.models import *
"""
class RasterLayerProperties(QgsOptionsDialogBase):
    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("RasterLayerProperties", parent, fl)
        # self.setupUi(self)
        self.initOptionsBase(False)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)
"""

def displayBandNames(provider_or_dataset, bands=None):
    results = None
    if isinstance(provider_or_dataset, QgsRasterLayer):
        return displayBandNames(provider_or_dataset.dataProvider())
    elif isinstance(provider_or_dataset, QgsRasterDataProvider):
        if provider_or_dataset.name() == 'gdal':
            ds = gdal.Open(provider_or_dataset.dataSourceUri())
            results = displayBandNames(ds, bands=bands)
        else:
            # same as in QgsRasterRendererWidget::displayBandName
            results = []
            if bands is None:
                bands = range(1, provider_or_dataset.bandCount() + 1)
            for band in bands:
                result = provider_or_dataset.generateBandName(band)
                colorInterp ='{}'.format(provider_or_dataset.colorInterpretationName(band))
                if colorInterp != 'Undefined':
                    result += '({})'.format(colorInterp)
                results.append(result)

    elif isinstance(provider_or_dataset, gdal.Dataset):
        results = []
        if bands is None:
            bands = range(1, provider_or_dataset.RasterCount+1)
        for band in bands:
            b = provider_or_dataset.GetRasterBand(band)
            descr = b.GetDescription()
            if len(descr) == 0:
                descr = 'Band {}'.format(band)
            results.append(descr)

    return results

class MultiBandColorRendererWidget(QgsMultiBandColorRendererWidget):
    @staticmethod
    def create(layer, extent):
        return MultiBandColorRendererWidget(layer, extent)

    def __init__(self, layer, extent):
        super(MultiBandColorRendererWidget, self).__init__(layer, extent)

        self.gridLayoutOld = self.layout().children()[0]
        self.gridLayout = QGridLayout()
        #self.layout().removeItem(self.gridLayout)
        #newGrid = QGridLayout()

        def copyObjects():
            while self.gridLayoutOld.count() > 0:
                w = self.gridLayoutOld.takeAt(0)
                w = w.widget()
                self.gridLayoutOld.removeWidget(c)
                w.setVisible(False)
                setattr(self, w.objectName(), w)


        copyObjects()
        #findObjects(QComboBox)
        #findObjects(QLabel)
        #findObjects(QLineEdit)

        self.mRedBandSlider = QSlider(Qt.Horizontal)
        self.mGreenBandSlider = QSlider(Qt.Horizontal)
        self.mBlueBandSlider = QSlider(Qt.Horizontal)

        self.mComboBoxes = [self.mRedBandComboBox, self.mGreenBandComboBox, self.mBlueBandComboBox]
        self.mSliders = [self.mRedBandSlider, self.mGreenBandSlider, self.mBlueBandSlider]
        nb = self.rasterLayer().dataProvider().bandCount()
        for cbox, slider in zip(self.mComboBoxes, self.mSliders):
            slider.valueChanged.connect(cbox.setCurrentIndex)
            slider.setMinimum(1)
            slider.setMaximum(nb)
            intervals = [1, 2, 5, 10, 25, 50]
            for interval in intervals:
                if nb / interval < 10:
                    break
            slider.setTickInterval(interval)
            slider.setPageStep(interval)
            cbox.currentIndexChanged.connect(self.onBandChanged)


        self.mLayerModel = MapLayerModel(layer)
        self.mBandModel = MapLayerModel(layer)
        if type(self.mRedBandComboBox) == QComboBox:
            self.fixBandNames(self.mRedBandComboBox)
            self.fixBandNames(self.mGreenBandComboBox)
            self.fixBandNames(self.mBlueBandComboBox)
        else:
            s = ""

        self.mBtnBar = QFrame()
        self.mBtnBar.setLayout(QHBoxLayout())
        self.initActionButtons()
        self.mBtnBar.layout().addStretch()
        self.mBtnBar.layout().setContentsMargins(0, 0, 0, 0)
        self.mBtnBar.layout().setSpacing(2)

        #self.gridLayout.deleteLater()
#        self.gridLayout = newGrid
        self.gridLayout.addWidget(self.mBtnBar, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.mRedBandLabel, 1, 0)
        self.gridLayout.addWidget(self.mRedBandSlider, 1, 1)
        self.gridLayout.addWidget(self.mRedBandComboBox, 1, 2)
        self.gridLayout.addWidget(self.mRedMinLineEdit, 1, 3)
        self.gridLayout.addWidget(self.mRedMaxLineEdit, 1, 4)

        self.gridLayout.addWidget(self.mGreenBandLabel, 2, 0)
        self.gridLayout.addWidget(self.mGreenBandSlider, 2, 1)
        self.gridLayout.addWidget(self.mGreenBandComboBox, 2, 2)
        self.gridLayout.addWidget(self.mGreenMinLineEdit, 2, 3)
        self.gridLayout.addWidget(self.mGreenMaxLineEdit, 2, 4)

        self.gridLayout.addWidget(self.mBlueBandLabel, 3, 0)
        self.gridLayout.addWidget(self.mBlueBandSlider, 3, 1)
        self.gridLayout.addWidget(self.mBlueBandComboBox, 3, 2)
        self.gridLayout.addWidget(self.mBlueMinLineEdit, 3, 3)
        self.gridLayout.addWidget(self.mBlueMaxLineEdit, 3, 4)

        self.gridLayout.addWidget(self.mContrastEnhancementAlgorithmLabel, 4, 0, 1, 2)
        self.gridLayout.addWidget(self.mContrastEnhancementAlgorithmComboBox, 4, 2, 1, 2)


        for i in range(self.gridLayout.count()):
            item = self.gridLayout.itemAt(i)
            if isinstance(item, QLayout):
                s = ""
            elif isinstance(item, QWidgetItem):
                item.widget().setVisible(True)
                item.widget().setParent(self)
            else:
                s  =""
        #self.gridLayout.itemAtPosition(1, 0).widget().setVisible(True)
        #for c in self.gridLayout.children():
        #    c.setVisible(True)
        self.layout().removeItem(self.gridLayoutOld)
        self.layout().insertItem(0, self.gridLayout)
        self.layout().addStretch()

        self.mRedBandLabel.setText('R')
        self.mGreenBandLabel.setText('G')
        self.mBlueBandLabel.setText('B')

        self.mDefaultRenderer = layer.renderer()


    def initActionButtons(self):

        from enmapbox.gui.utils import parseWavelength
        wl, wlu = parseWavelength(self.rasterLayer())
        self.wavelengths = wl
        self.wavelengthUnit = wlu

        self.actionSetDefault = QAction('Default')
        self.actionSetTrueColor = QAction('RGB')
        self.actionSetCIR = QAction('nIR')
        self.actionSet453 = QAction('swIR')

        self.actionSetDefault.triggered.connect(lambda: self.setBandSelection('default'))
        self.actionSetTrueColor.triggered.connect(lambda: self.setBandSelection('R,G,B'))
        self.actionSetCIR.triggered.connect(lambda: self.setBandSelection('nIR,R,G'))
        self.actionSet453.triggered.connect(lambda: self.setBandSelection('nIR,swIR,R'))


        def addBtnAction(action):
            btn = QToolButton()
            btn.setDefaultAction(action)
            self.mBtnBar.layout().addWidget(btn)
            self.insertAction(None, action)
            return btn

        self.btnDefault = addBtnAction(self.actionSetDefault)
        self.btnTrueColor = addBtnAction(self.actionSetTrueColor)
        self.btnCIR = addBtnAction(self.actionSetCIR)
        self.btn453 = addBtnAction(self.actionSet453)

        b = self.wavelengths is not None
        for a in [self.actionSetCIR, self.actionSet453, self.actionSetTrueColor]:
            a.setEnabled(b)


    def setBandSelection(self, key):

        from enmapbox.gui.utils import defaultBands, bandClosestToWavelength
        if key == 'default':
            bands = defaultBands(self.rasterLayer())
        else:
            colors = re.split('[ ,;:]', key)

            bands = [bandClosestToWavelength(self.rasterLayer(), c) for c in colors]

        if len(bands) == 3:
            for i, b in enumerate(bands):
                self.mComboBoxes[i].setCurrentIndex(b + 1)
                #self.sliders[i].setValue(b + 1)

    def onBandChanged(self, index):
        myBands = [c.currentIndex() for c in self.mComboBoxes]
        for band, slider in zip(myBands, self.mSliders):
            slider.blockSignals(True)
            slider.setValue(band)
            slider.blockSignals(False)

        #super(MultiBandColorRendererWidget, self).onBandChanged(index)

        self.minMaxWidget().setBands(myBands)
        self.widgetChanged.emit()


    def fixBandNames(self, cb):
        assert isinstance(cb, QComboBox)
        from enmapbox.gui.utils import parseWavelength

        bandNames = displayBandNames(self.rasterLayer())
        for i in range(cb.count()):
            #text = cb.itemText(i)
            if i > 0:
                cb.setItemText(i, bandNames[i - 1])

class MapLayerModel(QgsMapLayerModel):

    def __init__(self, *args, **kwds):
        super(MapLayerModel, self).__init__(*args, **kwds)

    def data(self, index, role):
        assert isinstance(index, QModelIndex)
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            s = ""
        else:

            return super(MapLayerModel, self).data(index, role)



class DEPR_MultiBandColorRendererWidget(QgsRasterRendererWidget, loadUI('multibandcolorrendererwidgetbase.ui')):

    @staticmethod
    def create(layer, extent):
        return MultiBandColorRendererWidget(layer, extent)

    def closeEvent(self, event):
        event.accept()

    def __init__(self, layer, extent):
        super(MultiBandColorRendererWidget,self).__init__(layer, extent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.createValidators()


        self.bandNames = None
        self.bandRanges = dict()

        from enmapbox.gui.utils import parseWavelength
        self.wavelengths, self.wavelengthUnit = parseWavelength(self.rasterLayer().dataProvider())

        if self.rasterLayer() and self.rasterLayer().dataProvider():
            provider = self.rasterLayer().dataProvider()

            self.mMinMaxWidget = QgsRasterMinMaxWidget(layer, self)
            self.mMinMaxWidget.setExtent(extent)
            self.mMinMaxWidget.setMapCanvas(self.mapCanvas())
            self.mMinMaxWidget.load.connect(self.loadMinMax)
            self.mMinMaxWidget.widgetChanged.connect(self.widgetChanged)
            layout = QHBoxLayout()
            self.mMinMaxContainerWidget.setLayout(layout)
            layout.addWidget(self.mMinMaxWidget)

            self.bandNames = displayBandNames(provider)
            assert isinstance(self.mRedBandSlider, QSlider)
            nb = len(self.bandNames)

            self.cBoxes = [self.mRedBandComboBox, self.mGreenBandComboBox, self.mBlueBandComboBox]
            self.sliders = [self.mRedBandSlider, self.mGreenBandSlider, self.mBlueBandSlider]
            self.minEdits = [self.mRedMinLineEdit, self.mGreenMinLineEdit, self.mBlueMinLineEdit]
            self.maxEdits = [self.mRedMaxLineEdit, self.mGreenMaxLineEdit, self.mBlueMaxLineEdit]

            for cbox, slider in zip(self.cBoxes, self.sliders):
                slider.valueChanged.connect(cbox.setCurrentIndex)
                slider.setMinimum(1)
                slider.setMaximum(nb)
                intervals = [1,2,5,10,25,50]
                for interval in intervals:
                    if nb / interval < 10:
                        break
                slider.setTickInterval(interval)
                slider.setPageStep(interval)
                cbox.currentIndexChanged.connect(self.onBandChanged)
                cbox.addItem('Not set',-1)

            self.mContrastEnhancementAlgorithmComboBox.addItem("No enhancement",QgsContrastEnhancement.NoEnhancement)
            self.mContrastEnhancementAlgorithmComboBox.addItem("Stretch to MinMax", QgsContrastEnhancement.StretchToMinimumMaximum)
            self.mContrastEnhancementAlgorithmComboBox.addItem("Stretch and clip to MinMax", QgsContrastEnhancement.StretchAndClipToMinimumMaximum)
            self.mContrastEnhancementAlgorithmComboBox.addItem("Clip to MinMax", QgsContrastEnhancement.ClipToMinimumMaximum)

            for i, bandName in enumerate(self.bandNames):
                self.mRedBandComboBox.addItem(bandName, i+1)
                self.mGreenBandComboBox.addItem(bandName, i+1)
                self.mBlueBandComboBox.addItem(bandName, i+1)

            self.defaultBands = [0,0,0]
            self.setFromRenderer(self.rasterLayer().renderer())
            self.onBandChanged(0)

            for edit in self.minEdits + self.maxEdits:
                edit.textChanged.connect(self.widgetChanged)

            self.initButtons(provider)


        s = ""

    def minMaxWidget(self):
        return self.mMinMaxWidget

    def doComputations(self):
        self.mMinMaxWidget.doComputations()
        s = ""

    def initButtons(self, provider):
        assert isinstance(provider, QgsRasterDataProvider)
        from enmapbox.gui.utils import parseWavelength
        wl, wlu = parseWavelength(provider)
        self.wavelengths = wl
        self.wavelengthUnit = wlu

        self.actionSetDefault.triggered.connect(lambda : self.setBandSelection('default'))
        self.actionSetTrueColor.triggered.connect(lambda : self.setBandSelection('R,G,B'))
        self.actionSetCIR.triggered.connect(lambda : self.setBandSelection('nIR,R,G'))
        self.actionSet453.triggered.connect(lambda : self.setBandSelection('nIR,swIR,R'))

        self.btnDef.setDefaultAction(self.actionSetDefault)
        self.btnTrueColor.setDefaultAction(self.actionSetTrueColor)
        self.btnCIR.setDefaultAction(self.actionSetCIR)
        self.btn453.setDefaultAction(self.actionSet453)

        self.btnBar.setEnabled(self.wavelengths is not None)


    def setBandSelection(self, key):

        from enmapbox.gui.utils import defaultBands, bandClosestToWavelength
        if key == 'default':
            bands = self.defaultBands[:]

        else:
            colors = re.split('[ ,;:]', key)

            bands = [bandClosestToWavelength(self.rasterLayer(), c) for c in colors]

        if len(bands) == 3:
            for i, b in enumerate(bands):
                self.sliders[i].setValue(b + 1)

    def loadMinMax(self, theBandNo, theMin, theMax, theOrigin):
        myMinLineEdit = myMaxLineEdit = None
        for c, cbox in enumerate(self.cBoxes):
            i = cbox.currentIndex()
            b = cbox.itemData(i)
            if b == theBandNo:
                myMinLineEdit = self.minEdits[c]
                myMaxLineEdit = self.maxEdits[c]
        if myMinLineEdit is None:
            return
        if theMin is None or qIsNaN(theMax):
            myMinLineEdit.clear()
        else:
            myMinLineEdit.setText('{}'.format(np.round(theMin, 5)))

        if theMax is None or qIsNaN(theMax):
            myMaxLineEdit.clear()
        else:
            myMaxLineEdit.setText('{}'.format(np.round(theMax, 5)))

    def onBandChanged(self, index):
        myBands = [c.currentIndex() for c in self.cBoxes]
        for band, slider in zip(myBands, self.sliders):
            slider.blockSignals(True)
            slider.setValue(band)
            slider.blockSignals(False)


        self.mMinMaxWidget.setBands(myBands)
        self.widgetChanged.emit()

    def createValidators(self):
        self.mRedMinLineEdit.setValidator(QDoubleValidator(self.mRedMinLineEdit))
        self.mRedMaxLineEdit.setValidator(QDoubleValidator(self.mRedMaxLineEdit))

        self.mGreenMinLineEdit.setValidator(QDoubleValidator(self.mGreenMinLineEdit))
        self.mGreenMaxLineEdit.setValidator(QDoubleValidator(self.mGreenMaxLineEdit))

        self.mGreenMinLineEdit.setValidator(QDoubleValidator(self.mGreenMinLineEdit))
        self.mGreenMaxLineEdit.setValidator(QDoubleValidator(self.mGreenMaxLineEdit))



    def displayBandName(self, band):
        if self.bandNames is None:
            return '<empty>'
        else:
            return self.bandNames[band+1]

    def min(self, index):
        if index == 0: return'{}'.format(self.mRedMinLineEdit.text())
        if index == 1: return'{}'.format(self.mGreenMinLineEdit.text())
        if index == 2: return'{}'.format(self.mBlueMinLineEdit.text())
        return ''

    def max(self, index):
        if index == 0: return'{}'.format(self.mRedMaxLineEdit.text())
        if index == 1: return'{}'.format(self.mGreenMaxLineEdit.text())
        if index == 2: return'{}'.format(self.mBlueMaxLineEdit.text())
        return ''

    def minMax(self, index):
        return self.min(index), self.max(index)


    def _roundedFloatStr(self, value):
        return '{}'.format(np.round(value, 5))

    def setMin(self, value, index):
        t = self._roundedFloatStr(value)
        if index == 0: self.mRedMinLineEdit.setText(t)
        if index == 1: self.mGreenMinLineEdit.setText(t)
        if index == 2: self.mBlueMinLineEdit.setText(t)

    def setMax(self, value, index):
        t = self._roundedFloatStr(value)
        if index == 0: self.mRedMaxLineEdit.setText(t)
        if index == 1: self.mGreenMaxLineEdit.setText(t)
        if index == 2: self.mBlueMaxLineEdit.setText(t)

    def stdDev(self):
        s = ""
    def setStdDev(self, QString):
        s = ""

    def selectedBand(self, index):
        if index == 0: return self.mRedBandComboBox.currentIndex()
        if index == 1: return self.mGreenBandComboBox.currentIndex()
        if index == 2: return self.mBlueBandComboBox.currentIndex()
        return -1

    def setMinMaxValue(self, ce, minEdit, maxEdit ):
        if minEdit is None or maxEdit is None:
            return None

        assert isinstance(minEdit, QLineEdit)
        assert isinstance(maxEdit, QLineEdit)

        if ce is None:
            minEdit.clear()
            maxEdit.clear()
        else:

            assert isinstance(ce, QgsContrastEnhancement)
            assert isinstance(self.mContrastEnhancementAlgorithmComboBox, QComboBox)
            minEdit.setText(self._roundedFloatStr(ce.minimumValue()))
            maxEdit.setText(self._roundedFloatStr(ce.maximumValue()))

            alg = ce.contrastEnhancementAlgorithm()
            algs = [self.mContrastEnhancementAlgorithmComboBox.itemData(i) for i in
                    range(self.mContrastEnhancementAlgorithmComboBox.count())]
            self.mContrastEnhancementAlgorithmComboBox.setCurrentIndex(algs.index(alg))



    def setCustomMinMaxValues(self, r, provider, redBand, greenBand, blueBand):
        if r is None or provider is None:
            return None
        i = self.mContrastEnhancementAlgorithmComboBox.currentIndex()
        if self.mContrastEnhancementAlgorithmComboBox.itemData(i) == QgsContrastEnhancement.NoEnhancement:
            r.setRedContrastEnhancement(None)
            r.setGreenContrastEnhancement(None)
            r.setBlueContrastEnhancement(None)
        else:
            def setEnhancement(cmin, cmax, band):
                if cmin is not None and cmax is not None and band != -1:
                    e = QgsContrastEnhancement(self.rasterLayer().dataProvider().dataType(band))
                    e.setMinimumValue(float(cmin))
                    e.setMaximumValue(float(cmax))
                    return e
                else:
                    return None

            redEnhancement = setEnhancement(self.min(0), self.max(0), redBand)
            greenEnhancement = setEnhancement(self.min(1), self.max(1), greenBand)
            blueEnhancement = setEnhancement(self.min(2), self.max(2), blueBand)

            if redEnhancement:
                redEnhancement.setContrastEnhancementAlgorithm(self.mContrastEnhancementAlgorithmComboBox.itemData(i))
            if redEnhancement:
                greenEnhancement.setContrastEnhancementAlgorithm(self.mContrastEnhancementAlgorithmComboBox.itemData(i))
            if redEnhancement:
                blueEnhancement.setContrastEnhancementAlgorithm(self.mContrastEnhancementAlgorithmComboBox.itemData(i))

            r.setRedContrastEnhancement(redEnhancement)
            r.setGreenContrastEnhancement(greenEnhancement)
            r.setBlueContrastEnhancement(blueEnhancement)

    def renderer(self):
        lyr = self.rasterLayer()
        if not lyr: return None
        dp = lyr.dataProvider()
        if not dp: return None

        redBand = self.mRedBandComboBox.currentIndex()
        greenBand = self.mGreenBandComboBox.currentIndex()
        blueBand = self.mBlueBandComboBox.currentIndex()
        r = QgsMultiBandColorRenderer(dp, redBand, greenBand, blueBand)
        self.setCustomMinMaxValues(r, dp, redBand, greenBand, blueBand)

        return r

    def setFromRenderer(self, r):
        if isinstance(r, QgsMultiBandColorRenderer):
            self.mRedBandComboBox.setCurrentIndex(r.redBand())
            self.mGreenBandComboBox.setCurrentIndex(r.greenBand())
            self.mBlueBandComboBox.setCurrentIndex(r.blueBand())
            self.setMinMaxValue(r.redContrastEnhancement(), self.mRedMinLineEdit, self.mRedMaxLineEdit)
            self.setMinMaxValue(r.greenContrastEnhancement(), self.mGreenMinLineEdit, self.mGreenMaxLineEdit)
            self.setMinMaxValue(r.blueContrastEnhancement(), self.mBlueMinLineEdit, self.mBlueMaxLineEdit)
            self.defaultBands = [r.redBand(), r.greenBand(), r.blueBand()]
        else:
            self.defaultBands = [1,1,1]
            self.mRedBandComboBox.setCurrentIndex(self.mRedBandComboBox.findText('Red'))
            self.mGreenBandComboBox.setCurrentIndex(self.mGreenBandComboBox.findText('Green'))
            self.mBlueBandComboBox.setCurrentIndex(self.mBlueBandComboBox.findText('Blue'))


#class RasterLayerProperties(QDialog,
class RasterLayerProperties(QgsOptionsDialogBase, loadUI('rasterlayerpropertiesdialog.ui')):
    def __init__(self, lyr, canvas, parent=None):
        """Constructor."""
        title = 'RasterLayerProperties'
        super(RasterLayerProperties, self).__init__(title, parent, Qt.Dialog, settings=None)
        #super(RasterLayerProperties, self).__init__(parent, Qt.Dialog)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use auto connect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initOptionsBase(False, title)
        #self.restoreOptionsBaseUi('TITLE')
        self.mRasterLayer = lyr
        self.mRendererWidget = None
        self.canvas = canvas

        self.oldStyle = self.mRasterLayer.styleManager().style(self.mRasterLayer.styleManager().currentStyle())

        self.accepted.connect(self.apply)
        self.rejected.connect(self.onCancel)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        #connect controls

        self.initOptsGeneral()
        self.initOptsStyle()
        self.initOptsTransparency()
        self.initOptsMetadata()


    def initOptsGeneral(self):
        rl = self.mRasterLayer

        assert isinstance(rl, QgsRasterLayer)
        dp = rl.dataProvider()
        name = rl.name()
        if name == '':
            name = os.path.basename(rl.source())

        self.tb_layername.setText(name)
        self.tb_layersource.setText(rl.source())

        self.tb_columns.setText('{}'.format(dp.xSize()))
        self.tb_rows.setText('{}'.format(dp.ySize()))
        self.tb_bands.setText('{}'.format(dp.bandCount()))

        #mapUnits = ['m','km','ft','nmi','yd','mi','deg','ukn']
        #mapUnit = rl.crs().mapUnits()
        #mapUnit = mapUnits[mapUnit] if mapUnit < len(mapUnits) else 'ukn'
        mapUnit = QgsUnitTypes.toString(rl.crs().mapUnits())

        self.tb_pixelsize.setText('{0}{2} x {1}{2}'.format(rl.rasterUnitsPerPixelX(),rl.rasterUnitsPerPixelY(), mapUnit))
        self.tb_nodata.setText('{}'.format(dp.sourceNoDataValue(1)))


        se = SpatialExtent.fromLayer(rl)
        pt2str = lambda xy: '{} ; {}'.format(xy[0], xy[1])
        self.tb_upperLeft.setText(pt2str(se.upperLeft()))
        self.tb_upperRight.setText(pt2str(se.upperRight()))
        self.tb_lowerLeft.setText(pt2str(se.lowerLeft()))
        self.tb_lowerRight.setText(pt2str(se.lowerRight()))

        self.tb_width.setText('{} {}'.format(se.width(), mapUnit))
        self.tb_height.setText('{} {}'.format(se.height(), mapUnit))
        self.tb_center.setText(pt2str((se.center().x(), se.center().y())))

        self.mCrsSelector
        s = ""


    def initOptsStyle(self):
        # insert renderer widgets into registry
        m = OptionListModel()

        for key, value in RASTERRENDERER_FUNC.items():
            m.addOption(Option(value, name=key))
            #self.mRenderTypeComboBox.addItem(key, userData=key)

        self.mRenderTypeComboBox.setModel(m)

        renderer = self.mRasterLayer.renderer()

        if renderer:
            setCurrentComboBoxValue(self.mRenderTypeComboBox, renderer.type())

        self.mRenderTypeComboBox.currentIndexChanged.connect(self.on_mRenderTypeComboBox_currentIndexChanged)

    def initOptsTransparency(self):

        s = ""
    def initOptsMetadata(self):

        s = ""

    @pyqtSlot(int)
    def on_mRenderTypeComboBox_currentIndexChanged(self, index):
        if index < 0:
            return None
        rendererName = self.mRenderTypeComboBox.itemData(index).name()
        self.setRendererWidget(rendererName)
        s = ""


    def onCancel(self):
        #restore style
        if self.oldStyle.xmlData() != self.mRasterLayer.styleManager().style(
                self.mRasterLayer.styleManager().currentStyle()
        ).xmlData():

            s = ""
        self.setResult(QDialog.Rejected)

    def apply(self):
        if self.mRendererWidget:
            self.mRendererWidget.doComputations()
            #self.mRendererWidget.minMaxWidget().doComputations()
            self.mRasterLayer.setRenderer(self.mRendererWidget.renderer())

        self.mRasterLayer.triggerRepaint()
        self.setResult(QDialog.Accepted)

    def syncFromLayer(self):

        if self.mRasterLayer:
            dp = self.mRasterLayer.dataProvider()


    def syncToLayer(self):
        renderer = self.mRasterLayer.renderer()
        if renderer:
            self.setRendererWidget('{}'.format(renderer.type()))

        self.sync()
        self.mRasterLayer.triggerRepaint()

    def setRendererWidget(self, rendererName):
        oldWidget = self.mRendererWidget

        if rendererName in RASTERRENDERER_FUNC.keys():

            extent = self.canvas.extent()
            w = RASTERRENDERER_FUNC[rendererName](self.mRasterLayer, extent)
            w.setMapCanvas(self.canvas)
            self.mRendererStackedWidget.addWidget(w)
            self.mRendererWidget = w

            if self.mRendererWidget != oldWidget:
                self.mRendererStackedWidget.removeWidget(oldWidget)
                del oldWidget

RASTERRENDERER_FUNC = collections.OrderedDict()
RASTERRENDERER_FUNC['multibandcolor (QGIS)'] = QgsMultiBandColorRendererWidget.create
#RASTERRENDERER_FUNC['multibandcolor'] = MultiBandColorRendererWidget.create
RASTERRENDERER_FUNC['multibandcolor (V2)'] = MultiBandColorRendererWidget.create
RASTERRENDERER_FUNC['paletted'] = QgsPalettedRendererWidget.create
RASTERRENDERER_FUNC['singlebandgray'] = QgsSingleBandGrayRendererWidget.create
RASTERRENDERER_FUNC['singlebandpseudocolor'] = QgsSingleBandPseudoColorRendererWidget.create



class VectorLayerProperties(QgsOptionsDialogBase, loadUI('vectorlayerpropertiesdialog.ui')):

    def __init__(self, lyr, canvas, parent=None, fl=Qt.Widget):
        super(VectorLayerProperties, self).__init__("VectorLayerProperties", parent, fl)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)
        self.setupUi(self)
        self.initOptionsBase(False, title)
        self.mRendererDialog = None
        assert isinstance(lyr, QgsVectorLayer)
        assert isinstance(canvas, QgsMapCanvas)
        self.mLayer = lyr
        self.mCanvas = canvas
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.syncToLayer)

        self.pbnQueryBuilder.clicked.connect(self.on_pbnQueryBuilder_clicked)
        self.accepted.connect(self.syncToLayer)

        self.rejected.connect(self.onCancel)
        self.syncFromLayer()

    def onCancel(self):
        pass

    def syncFromLayer(self):
        lyr = self.mLayer
        if isinstance(lyr, QgsVectorLayer):
            self.mLayerOrigNameLineEdit.setText(lyr.name())
            self.txtLayerSource.setText(lyr.publicSource())
            gtype = ['Point','Line','Polygon','Unknown','Undefined'][lyr.geometryType()]
            self.txtGeometryType.setText(gtype)
            self.txtnFeatures.setText('{}'.format(self.mLayer.featureCount()))
            self.txtnFields.setText('{}'.format(self.mLayer.fields().count()))

            self.mCrsSelector.setCrs(lyr.crs())

            self.txtSubsetSQL.setText(self.mLayer.subsetString())
            self.txtSubsetSQL.setEnabled(False)


        self.updateSymbologyPage()

        pass


    def syncToLayer(self):

        if self.mLayer.rendererV2():
            dlg = self.widgetStackRenderers.currentWidget()
            dlg.apply()

        if self.txtSubsetSQL.toPlainText() != self.mLayer.subsetString():
            self.mLayer.setSubsetString(self.txtSubsetSQL.toPlainText())

        self.mLayer.triggerRepaint()
        pass

    def on_pbnQueryBuilder_clicked(self):
        qb = QgsQueryBuilder(self.mLayer, self)
        qb.setSql(self.txtSubsetSQL.toPlainText())

        if qb.exec_():
            self.txtSubsetSQL.setText(qb.sql())

    def updateSymbologyPage(self):
        self.mRendererDialog = None
        if self.mLayer.rendererV2():
            self.mRendererDialog = QgsRendererV2PropertiesDialog(self.mLayer, QgsStyleV2.defaultStyle(), True, self)
            self.mRendererDialog.setDockMode(False)
            self.mRendererDialog.setMapCanvas(self.mCanvas)
          #  self.mRendererDialog.showPanel.connect(self.openPanel)
            #self.mRendererDialog.layerVariablesChanged.connect(self.updateVariableEditor())
            self.mOptsPage_Style.setEnabled(True)
        else:
            self.mOptsPage_Style.setEnabled(False)

        if self.mRendererDialog:
            self.mRendererDialog.layout().setMargin(0)
            self.widgetStackRenderers.addWidget(self.mRendererDialog)
            self.widgetStackRenderers.setCurrentWidget(self.mRendererDialog)
            self.widgetStackRenderers.currentWidget().layout().setMargin(0)

def showLayerPropertiesDialog(layer, canvas, parent=None, modal=True):
    dialog = None

    if isinstance(layer, QgsRasterLayer):
        dialog = RasterLayerProperties(layer, canvas, parent)
        #d.setSettings(QSettings())
    elif isinstance(layer, QgsVectorLayer):
        dialog = VectorLayerProperties(layer, canvas, parent)
    else:
        assert NotImplementedError()

    if modal == True:
        dialog.setModal(True)
    else:
        dialog.setModal(False)

    result = dialog.exec_()
    return result


if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox.gui.utils import initQgisApplication
    qgsApp = initQgisApplication()
    from enmapboxtestdata import enmap as pathL
    from enmapboxtestdata import landcover as pathV
    l = QgsRasterLayer(pathL)
    #v = QgsVectorLayer(pathV,'bn', "ogr", loadDefaultStyleFlag=True)
    v = QgsVectorLayer(pathV)

    QgsProject.instance().addMapLayers([l,v])
    c = QgsMapCanvas()
    c.setLayers([l])
    c.setDestinationCrs(l.crs())
    c.setExtent(l.extent())
    c.refreshAllLayers()

    if True:
        l = QgsRasterLayer(r'F:\Temp\landsat22.bsq')
        w = MultiBandColorRendererWidget.create(l, l.extent())
        w.show()
    elif False:
        pass

    else:
        #QgsRendererV2Registry.instance().renderersList()


        #w = QgsMapLayerStyleManagerWidget(v, c, parent=None)
        #w.show()
        b = QPushButton()
        b.setText('Show Properties')
        b.clicked.connect(lambda: showLayerPropertiesDialog(l, c))
        br = QPushButton()
        br.setText('Refresh')
        br.clicked.connect(lambda : c.refresh())
        lh = QHBoxLayout()
        lh.addWidget(b)
        lh.addWidget(br)
        lv = QVBoxLayout()
        lv.addLayout(lh)
        lv.addWidget(b)
        lv.addWidget(c)
        w = QWidget()
        w.setLayout(lv)
        w.show()
        s = ""
        b.click()



    qgsApp.exec_()
    qgsApp.exitQgis()
