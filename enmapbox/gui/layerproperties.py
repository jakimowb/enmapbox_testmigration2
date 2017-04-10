from __future__ import absolute_import

import collections
import os
import re

from osgeo import gdal, ogr
import numpy as np
from qgis.gui import *
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from enmapbox.gui.utils import loadUI, SpatialExtent

"""
class RasterLayerProperties(QgsOptionsDialogBase):
    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("RasterLayerProperties", parent, fl)
        # self.setupUi(self)
        self.initOptionsBase(False)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)
"""

METRIC_EXPONENTS = {
    "nm":-9,"um": -6, "mm":-3, "cm":-2, "dm":-1, "m": 0,"hm":2, "km":3
}
#add synonyms
METRIC_EXPONENTS['nanometers'] = METRIC_EXPONENTS['nm']
METRIC_EXPONENTS['micrometers'] = METRIC_EXPONENTS['um']
METRIC_EXPONENTS['millimeters'] = METRIC_EXPONENTS['mm']
METRIC_EXPONENTS['centimeters'] = METRIC_EXPONENTS['cm']
METRIC_EXPONENTS['decimeters'] = METRIC_EXPONENTS['dm']
METRIC_EXPONENTS['meters'] = METRIC_EXPONENTS['m']
METRIC_EXPONENTS['hectometers'] = METRIC_EXPONENTS['hm']
METRIC_EXPONENTS['kilometers'] = METRIC_EXPONENTS['km']

def convertMetricUnit(value, u1, u2):
    """converts value, given in unit u1, to u2"""
    assert u1 in METRIC_EXPONENTS.keys()
    assert u2 in METRIC_EXPONENTS.keys()

    e1 = METRIC_EXPONENTS[u1]
    e2 = METRIC_EXPONENTS[u2]

    return value * 10**(e1-e2)

def displayBandNames(provider_or_dataset, bands=None):
    results = None

    if isinstance(provider_or_dataset, QgsRasterDataProvider):
        if str(provider_or_dataset.name()) == 'gdal':
            ds = gdal.Open(provider_or_dataset.dataSourceUri())
            results = displayBandNames(ds, bands=bands)
        else:
            # same as in QgsRasterRendererWidget::displayBandName
            results = []
            if bands is None:
                bands = range(1, provider_or_dataset.bandCount() + 1)
            for band in bands:
                result = provider_or_dataset.generateBandName(band)
                colorInterp = str(provider_or_dataset.colorInterpretationName(band))
                if colorInterp != 'Undefined':
                    result += '({})'.format(colorInterp)
                results.append(result)

    elif isinstance(provider_or_dataset, gdal.Dataset):
        results = []
        if bands is None:
            bands = range(1, provider_or_dataset.RasterCount+1)
        for band in bands:
            b = provider_or_dataset.GetRasterBand(band)
            results.append(b.GetDescription())

    return results

def parseWavelength(provider):
    wl = None
    wlu = None
    assert isinstance(provider, QgsRasterDataProvider)
    md = [l.split('=') for l in str(provider.metadata()).splitlines() if 'wavelength' in l.lower()]
    #see http://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html for supported wavelength units

    mdDict = {}

    for kv in md:
        key, value = kv
        if key not in mdDict.keys():
            mdDict[key] = list()
        mdDict[key].append(value)

    for key in mdDict.keys():
        values = ';'.join(mdDict[key])
        key = key.lower()
        if re.search('wavelength$', key):
            tmp = re.findall('\d*\.\d+|\d+', values) #find floats
            if len(tmp) != provider.bandCount():
                tmp = re.findall('\d+', values) #find integers
            if len(tmp) == provider.bandCount():
                wl = np.asarray([float(w) for w in tmp])

        if re.search(r'wavelength.units?',key):
            if re.search('(Micrometers?|um)', values, re.I):
                wlu = 'um' #fix with python 3 UTF
            elif re.search('(Nanometers?|nm)', values, re.I):
                wlu = 'nm'
            elif re.search('(Millimeters?|mm)', values, re.I):
                wlu = 'nm'
            elif re.search('(Centimeters?|cm)', values, re.I):
                wlu = 'nm'
            elif re.search('(Meters?|m)', values, re.I):
                wlu = 'nm'
            elif re.search('Wavenumber', values, re.I):
                wlu = '-'
            elif re.search('GHz', values, re.I):
                wlu = 'GHz'
            elif re.search('MHz', values, re.I):
                wlu = 'MHz'
            elif re.search('Index', values, re.I):
                wlu = '-'
            else:
                wlu = '-'

    return wl, wlu


class MultiBandColorRendererWidget(QgsRasterRendererWidget, loadUI('multibandcolorrendererwidgetbase.ui')):

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


        self.wavelengths = None
        self.wavelengthUnit = None
        if self.rasterLayer() and self.rasterLayer().dataProvider():
            provider = self.rasterLayer().dataProvider()

            self.mMinMaxWidget = QgsRasterMinMaxWidget(layer, self)
            self.mMinMaxWidget.setExtent(extent)
            self.mMinMaxWidget.setMapCanvas(self.mapCanvas())
            self.mMinMaxWidget.load.connect(self.loadMinMax)

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

    def initButtons(self, provider):
        assert isinstance(provider, QgsRasterDataProvider)
        wl, wlu = parseWavelength(provider)
        self.wavelengths = wl
        self.wavelengthUnit = wlu

        self.actionSetDefault.triggered.connect(lambda : self.setBandSelection('defaultMB'))
        self.actionSetTrueColor.triggered.connect(lambda : self.setBandSelection('TrueColor'))
        self.actionSetCIR.triggered.connect(lambda : self.setBandSelection('CIR'))
        self.actionSet453.triggered.connect(lambda : self.setBandSelection('453'))

        self.btnDef.setDefaultAction(self.actionSetDefault)
        self.btnTrueColor.setDefaultAction(self.actionSetTrueColor)
        self.btnCIR.setDefaultAction(self.actionSetCIR)
        self.btn453.setDefaultAction(self.actionSet453)

        self.btnBar.setEnabled(self.wavelengths is not None)

    def bandClosestToWavelength(self, wl, wl_unit='nm'):
        if self.wavelengths is None or self.wavelengthUnit is None:
            return 0

        wl = float(wl)
        if self.wavelengthUnit != wl_unit:
            wl = convertMetricUnit(wl, wl_unit, self.wavelengthUnit)

        return np.argmin(np.abs(self.wavelengths - wl))

    def setBandSelection(self, key):

        if key == 'default':
            bands = self.defaultBands[:]

        else:
            if key in ['R', 'G', 'B', 'nIR', 'swIR']:
                colors = [key]
            elif key == 'TrueColor':
                colors = ['R', 'G', 'B']
            elif key == 'CIR':
                colors = ['nIR', 'R', 'G']
            elif key == '453':
                colors = ['nIR', 'swIR', 'R']

            LUT_Wavelenghts = dict({'B': 480,
                                    'G': 570,
                                    'R': 660,
                                    'nIR': 850,
                                    'swIR': 1650,
                                    'swIR1': 1650,
                                    'swIR2': 2150
                                    })

            wls = [LUT_Wavelenghts[c] for c in colors]
            bands = [self.bandClosestToWavelength(wl) for wl in wls]

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
            myMinLineEdit.setText(str(np.round(theMin, 5)))

        if theMax is None or qIsNaN(theMax):
            myMaxLineEdit.clear()
        else:
            myMaxLineEdit.setText(str(np.round(theMax, 5)))

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
        if index == 0: return str(self.mRedMinLineEdit.text())
        if index == 1: return str(self.mGreenMinLineEdit.text())
        if index == 2: return str(self.mBlueMinLineEdit.text())
        return ''

    def max(self, index):
        if index == 0: return str(self.mRedMaxLineEdit.text())
        if index == 1: return str(self.mGreenMaxLineEdit.text())
        if index == 2: return str(self.mBlueMaxLineEdit.text())
        return ''

    def minMax(self, index):
        return self.min(index), self.max(index)


    def _roundedFloatStr(self, value):
        return str(np.round(value, 5))

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
        self.rasterLayer = lyr
        self.renderWidget = None
        self.canvas = canvas

        self.oldStyle = self.rasterLayer.styleManager().style(self.rasterLayer.styleManager().currentStyle())

        self.accepted.connect(self.apply)
        self.rejected.connect(self.onCancel)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        #connect controls

        self.initOptsGeneral()
        self.initOptsStyle()
        self.initOptsTransparency()
        self.initOptsMetadata()


    def initOptsGeneral(self):
        rl = self.rasterLayer

        assert isinstance(rl, QgsRasterLayer)
        dp = rl.dataProvider()
        name = str(rl.name())
        if name == '':
            name = os.path.basename(rl.source())

        self.tb_layername.setText(name)
        self.tb_layersource.setText(rl.source())

        self.tb_columns.setText('{}'.format(dp.xSize()))
        self.tb_rows.setText('{}'.format(dp.ySize()))
        self.tb_bands.setText('{}'.format(dp.bandCount()))

        mapUnits = ['m','km','ft','nmi','yd','mi','deg','ukn']
        mapUnit = rl.crs().mapUnits()
        mapUnit = mapUnits[mapUnit] if mapUnit < len(mapUnits) else 'ukn'

        self.tb_pixelsize.setText('{0}{2}x{1}{2}'.format(rl.rasterUnitsPerPixelX(),rl.rasterUnitsPerPixelY(), mapUnit))
        self.tb_nodata.setText('{}'.format(dp.srcNoDataValue(2)))


        se = SpatialExtent.fromLayer(rl)
        pt2str = lambda xy: '{} {}'.format(xy[0], xy[1])
        self.tb_upperLeft.setText(pt2str(se.upperLeft()))
        self.tb_upperRight.setText(pt2str(se.upperRight()))
        self.tb_lowerLeft.setText(pt2str(se.lowerLeft()))
        self.tb_lowerRight.setText(pt2str(se.lowerRight()))

        self.tb_width.setText('{} {}'.format(se.width(), mapUnit))
        self.tb_height.setText('{} {}'.format(se.height(), mapUnit))
        self.tb_center.setText(pt2str((se.center().x(), se.center().y())))

        s = ""


    def initOptsStyle(self):
        # insert renderer widgets into registry
        for key, value in RASTERRENDERER_FUNC.items():
            self.mRenderTypeComboBox.addItem(key, key)

        pass
        renderer = self.rasterLayer.renderer()

        if renderer:
            idx = self.mRenderTypeComboBox.findText(str(renderer.type()))
            if idx != -1:
                self.mRenderTypeComboBox.setCurrentIndex(idx)
        self.mRenderTypeComboBox.currentIndexChanged.connect(self.on_mRenderTypeComboBox_currentIndexChanged)

    def initOptsTransparency(self):

        s = ""
    def initOptsMetadata(self):

        s = ""

    @pyqtSlot(int)
    def on_mRenderTypeComboBox_currentIndexChanged(self, index):
        if index < 0:
            return None
        rendererName = str(self.mRenderTypeComboBox.itemData(index))
        self.setRendererWidget(rendererName)


    def onCancel(self):
        #restore style
        if self.oldStyle.xmlData() != self.rasterLayer.styleManager().style(
                self.rasterLayer.styleManager().currentStyle()
        ).xmlData():

            s = ""
        self.setResult(QDialog.Rejected)

    def apply(self):
        if self.renderWidget:
            self.rasterLayer.setRenderer(self.renderWidget.renderer())

        self.rasterLayer.triggerRepaint()
        self.setResult(QDialog.Accepted)

    def syncFromLayer(self):

        if self.rasterLayer:
            dp = self.rasterLayer.dataProvider()


    def syncToLayer(self):
        renderer = self.rasterLayer.renderer()
        if renderer:
            self.setRendererWidget(str(renderer.type()))

        self.sync()
        self.rasterLayer.triggerRepaint()

    def setRendererWidget(self, rendererName):
        oldWidget = self.renderWidget

        if rendererName in RASTERRENDERER_FUNC.keys():

            extent = self.canvas.extent()
            w = RASTERRENDERER_FUNC[rendererName](self.rasterLayer, extent)
            w.setMapCanvas(self.canvas)
            self.mRendererStackedWidget.addWidget(w)
            self.renderWidget = w

            if self.renderWidget != oldWidget:
                self.mRendererStackedWidget.removeWidget(oldWidget)
                del oldWidget

RASTERRENDERER_FUNC = collections.OrderedDict()
#RASTERRENDERER_FUNC['multibandcolor'] = QgsMultiBandColorRendererWidget.create
RASTERRENDERER_FUNC['multibandcolor'] = MultiBandColorRendererWidget.create
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
    d = None

    if isinstance(layer, QgsRasterLayer):
        d = RasterLayerProperties(layer, canvas, parent)
        #d.setSettings(QSettings())
    elif isinstance(layer, QgsVectorLayer):
        d = VectorLayerProperties(layer, canvas, parent)
    else:
        assert NotImplementedError()

    if modal == True:
        d.setModal(True)
        return  d.exec_()
    else:
        d.setModal(False)
        return d


if __name__ == '__main__':
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox.gui.utils import DIR_SITEPACKAGES
    site.addsitedir(DIR_SITEPACKAGES)

    #prepare QGIS environment
    if sys.platform == 'darwin':
        PATH_QGS = r'/Applications/QGIS.app/Contents/MacOS'
        os.environ['GDAL_DATA'] = r'/usr/local/Cellar/gdal/1.11.3_1/share'
    else:
        # assume OSGeo4W startup
        PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    assert os.path.exists(PATH_QGS)

    qgsApp = QgsApplication([], True)
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns')
    QApplication.addLibraryPath(r'/Applications/QGIS.app/Contents/PlugIns/qgis')
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()


    pathL = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data\BerlinUrbGrad2009_01_image_products\01_image_products\EnMAP02_Berlin_Urban_Gradient_2009.bsq'
    pathV = r'E:\_EnMAP\Project_EnMAP-Box\SampleData\urbangradient_data\BerlinUrbGrad2009_02_additional_data\02_additional_data\land_cover\LandCov_Vec_polygons_Berlin_Urban_Gradient_2009.shp'
    QgsRendererV2Registry.instance().renderersList()

    l = QgsRasterLayer(pathL)
    v = QgsVectorLayer(pathV,'bn', "ogr", loadDefaultStyleFlag=True)

    QgsMapLayerRegistry.instance().addMapLayers([l,v])
    c = QgsMapCanvas()
    c.setLayerSet([QgsMapCanvasLayer(v)])
    c.setDestinationCrs(l.crs())
    c.setExtent(l.extent())
    c.refreshAllLayers()

    #w = QgsMapLayerStyleManagerWidget(v, c, parent=None)
    #w.show()
    b = QPushButton()
    b.setText('Show Properties')
    b.clicked.connect(lambda: showLayerPropertiesDialog(v, c))
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
    b.click()
    qgsApp.exec_()
    qgsApp.exitQgis()
