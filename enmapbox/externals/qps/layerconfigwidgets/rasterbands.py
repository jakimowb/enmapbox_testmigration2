"""
***************************************************************************
    layerconfigwidget/rasterbands.py
        - A QgsMapLayerConfigWidget to select and change bands of QgsRasterRenderers
    -----------------------------------------------------------------------
    begin                : 2020-02-24
    copyright            : (C) 2020 Benjamin Jakimow
    email                : benjamin.jakimow@geo.hu-berlin.de

***************************************************************************
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
                                                                                                                                                 *
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software. If not, see <http://www.gnu.org/licenses/>.
***************************************************************************
"""
import traceback
import typing
import pathlib
from typing import List, Optional

from PyQt5.QtWidgets import QGroupBox, QToolButton, QPushButton, QTableWidget, QCheckBox, QAbstractSpinBox, QComboBox, \
    QTextEdit, QLineEdit
from qgis._core import QgsRasterRange, QgsProject
from qgis._gui import QgsFilterLineEdit, QgsDateTimeEdit

from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from qgis.gui import QgsRasterLayerProperties

from qgis.core import QgsHillshadeRenderer
from qgis.core import QgsRasterDataProvider, QgsRasterLayer, QgsMapLayer, \
    QgsRasterRenderer, \
    QgsSingleBandGrayRenderer, \
    QgsSingleBandColorDataRenderer, \
    QgsSingleBandPseudoColorRenderer, \
    QgsMultiBandColorRenderer, \
    QgsPalettedRasterRenderer, \
    QgsColorRampShader, QgsRasterShaderFunction, QgsRasterShader, \
    QgsApplication

from qgis.gui import QgsMapCanvas, QgsMapLayerConfigWidget, QgsMapLayerConfigWidgetFactory, QgsRasterBandComboBox

from qgis.PyQt.QtWidgets import QSlider, QWidget, QStackedWidget, QLabel
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
import numpy as np
from ..layerconfigwidgets.core import QpsMapLayerConfigWidget
from ..simplewidgets import FlowLayout
from ..utils import loadUi, parseWavelength, UnitLookup, parseFWHM, LUT_WAVELENGTH, WAVELENGTH_DESCRIPTION


class RasterBandComboBox(QgsRasterBandComboBox):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mWL = self.mWLU = self.mFWHM = None

    def setLayer(self, layer):
        """
        Re-Implements void QgsRasterBandComboBox::setLayer( QgsMapLayer *layer ) with own band-name logic
        :param layer: 
        :type layer: qgis._core.QgsRasterLayer
        :return: 
        :rtype: None
        """
        super().setLayer(layer)

        if not (isinstance(layer, QgsRasterLayer) and layer.isValid()):
            return

        WL, WLU = parseWavelength(layer)
        FWHM = parseFWHM(layer)

        offset = 1 if self.isShowingNotSetOption() else 0
        for b in range(layer.bandCount()):
            idx = b + offset
            bandName = self.itemText(idx)
            tooltip = bandName
            if WLU and WLU not in bandName:
                bandName += ' [{} {}]'.format(WL[b], WLU)
                tooltip += ' {} {}'.format(WL[b], WLU)
                if isinstance(FWHM, np.ndarray):
                    tooltip += ' {}'.format(FWHM[b])

            self.setItemText(idx, bandName)
            self.setItemData(idx, tooltip, Qt.ToolTipRole)


class BandCombination(object):
    """
    Describes a band combination
    """

    def __init__(self,
                 band_keys: typing.Union[str, tuple],
                 name: str = None,
                 tooltip: str = None,
                 icon: QIcon = None):

        if isinstance(band_keys, str):
            band_keys = (band_keys,)
        assert isinstance(band_keys, tuple)
        assert len(band_keys) > 0
        for b in band_keys:
            assert b in LUT_WAVELENGTH.keys(), f'Unknown wavelength key: {b}'

        self.mBand_keys = band_keys
        self.mName = name
        self.mTooltip = tooltip
        self.mIcon = QIcon(icon)

    def bandKeys(self) -> tuple:
        return self.mBand_keys

    def icon(self) -> QIcon:
        return self.mIcon

    def name(self) -> str:
        if self.mName is None:
            return '-'.join(self.mBand_keys)
        else:
            return self.mName

    def tooltip(self, wl_nm) -> str:
        tt = self.mTooltip if self.mTooltip else ''
        if len(self.mBand_keys) == 1:
            return 'Selects the band closest to\n{}'.format(WAVELENGTH_DESCRIPTION[self.mBand_keys[0]])
        else:
            tt += '\nSelects the bands closest to:'
            for i, b in enumerate(self.mBand_keys):
                tt += '\n' + WAVELENGTH_DESCRIPTION[b]
        return tt.strip()

    def nBands(self) -> int:
        return len(self.mBand_keys)


BAND_COMBINATIONS: typing.List[BandCombination] = []
# single-band renders
BAND_COMBINATIONS += [BandCombination(b) for b in LUT_WAVELENGTH.keys()]
# 3-band renderers (Order: R-G-B color channel)
BAND_COMBINATIONS += [
    BandCombination(('R', 'G', 'B'), name='True Color'),
    BandCombination(('NIR', 'R', 'G'), name='Colored IR'),
    BandCombination(('SWIR', 'NIR', 'R')),
    BandCombination(('NIR', 'SWIR', 'R'))
]


RENDER_TYPE2NAME = {
    'multibandcolor': 'Multiband color',
    'paletted': 'Paletted/Unique values',
    'contour': 'Contours',
    'hillshade': 'Hillshade',
    'singlebandpseudocolor': 'Singleband pseudocolor',
    'singlebandgray': 'Singleband gray',
}

class RasterBandConfigWidget(QpsMapLayerConfigWidget):

    def __init__(self, layer: QgsRasterLayer, canvas: QgsMapCanvas, parent: QWidget = None):

        super(RasterBandConfigWidget, self).__init__(layer, canvas, parent=parent)
        pathUi = pathlib.Path(__file__).parents[1] / 'ui' / 'rasterbandconfigwidget.ui'
        loadUi(pathUi, self)

        assert isinstance(layer, QgsRasterLayer)
        self.mCanvas = canvas
        self.mLayer = layer
        self.mLayer.rendererChanged.connect(self.syncToLayer)
        assert isinstance(self.cbSingleBand, QgsRasterBandComboBox)

        self.cbSingleBand.setLayer(self.mLayer)
        self.cbMultiBandRed.setLayer(self.mLayer)
        self.cbMultiBandGreen.setLayer(self.mLayer)
        self.cbMultiBandBlue.setLayer(self.mLayer)

        self.cbSingleBand.bandChanged.connect(self.onWidgetChanged)
        self.cbMultiBandRed.bandChanged.connect(self.onWidgetChanged)
        self.cbMultiBandGreen.bandChanged.connect(self.onWidgetChanged)
        self.cbMultiBandBlue.bandChanged.connect(self.onWidgetChanged)

        assert isinstance(self.sliderSingleBand, QSlider)
        self.sliderSingleBand.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandRed.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandGreen.setRange(1, self.mLayer.bandCount())
        self.sliderMultiBandBlue.setRange(1, self.mLayer.bandCount())

        mWL, mWLUnit = parseWavelength(self.mLayer)
        if isinstance(mWL, list):
            mWL = np.asarray(mWL)

        if UnitLookup.isMetricUnit(mWLUnit):
            mWLUnit = UnitLookup.baseUnit(mWLUnit)
            # convert internally to nanometers
            if mWLUnit != 'nm':
                try:
                    mWL = UnitLookup.convertMetricUnit(mWL, mWLUnit, 'nm')
                    mWLUnit = 'nm'
                except:
                    mWL = None
                    mWLUnit = None

        self.mWL = mWL
        self.mWLUnit = mWLUnit

        hasWL = UnitLookup.isMetricUnit(self.mWLUnit)
        self.gbMultiBandWavelength.setEnabled(hasWL)
        self.gbSingleBandWavelength.setEnabled(hasWL)

        def createButton(bc: BandCombination) -> QPushButton:
            btn = QPushButton()
            # btn.setAutoRaise(False)
            btn.setText(bc.name())
            btn.setIcon(bc.icon())
            btn.setToolTip(bc.tooltip(self.mWL))
            btn.clicked.connect(lambda *args, b=bc: self.setWL(b.bandKeys()))
            return btn

        lSingle = FlowLayout()
        lMulti = FlowLayout()

        for bc in BAND_COMBINATIONS:
            if bc.nBands() == 1:
                lSingle.addWidget(createButton(bc))

            if bc.nBands() == 3:
                lMulti.addWidget(createButton(bc))

        self.gbSingleBandWavelength.setLayout(lSingle)
        assert self.gbSingleBandWavelength.layout() == lSingle
        self.gbMultiBandWavelength.setLayout(lMulti)
        lSingle.setContentsMargins(0, 0, 0, 0)
        lSingle.setSpacing(0)
        lSingle.setContentsMargins(0, 0, 0, 0)
        lSingle.setSpacing(0)

        self._ref_multi = lMulti
        self._ref_single = lSingle

        self.syncToLayer()

        self.setPanelTitle('Band Selection')

    def onWidgetChanged(self, *args):
        self.apply()
        # self.widgetChanged.emit()

    def icon(self) -> QIcon:
        return QIcon(':/qps/ui/icons/rasterband_select.svg')

    def syncToLayer(self, *args):
        super().syncToLayer(*args)
        renderer = self.mLayer.renderer().clone()
        self.setRenderer(renderer)

    def renderer(self) -> QgsRasterRenderer:
        oldRenderer = self.mLayer.renderer()
        newRenderer = None
        if isinstance(oldRenderer, QgsSingleBandGrayRenderer):
            newRenderer = oldRenderer.clone()
            newRenderer.setGrayBand(self.cbSingleBand.currentBand())

        elif isinstance(oldRenderer, QgsSingleBandPseudoColorRenderer):
            # there is a bug when using the QgsSingleBandPseudoColorRenderer.setBand()
            # see https://github.com/qgis/QGIS/issues/31568
            # band = self.cbSingleBand.currentBand()
            vMin, vMax = oldRenderer.shader().minimumValue(), oldRenderer.shader().maximumValue()
            shader = QgsRasterShader(vMin, vMax)

            f = oldRenderer.shader().rasterShaderFunction()
            if isinstance(f, QgsColorRampShader):
                shaderFunction = QgsColorRampShader(f)
            else:
                shaderFunction = QgsRasterShaderFunction(f)

            shader.setRasterShaderFunction(shaderFunction)
            newRenderer = QgsSingleBandPseudoColorRenderer(oldRenderer.input(), self.cbSingleBand.currentBand(), shader)

        elif isinstance(oldRenderer, QgsPalettedRasterRenderer):
            newRenderer = QgsPalettedRasterRenderer(oldRenderer.input(), self.cbSingleBand.currentBand(),
                                                    oldRenderer.classes())

            # r.setBand(band)
        elif isinstance(oldRenderer, QgsSingleBandColorDataRenderer):
            newRenderer = QgsSingleBandColorDataRenderer(oldRenderer.input(), self.cbSingleBand.currentBand())

        elif isinstance(oldRenderer, QgsMultiBandColorRenderer):
            newRenderer = oldRenderer.clone()
            newRenderer.setInput(oldRenderer.input())
            if isinstance(newRenderer, QgsMultiBandColorRenderer):
                newRenderer.setRedBand(self.cbMultiBandRed.currentBand())
                newRenderer.setGreenBand(self.cbMultiBandGreen.currentBand())
                newRenderer.setBlueBand(self.cbMultiBandBlue.currentBand())
        return newRenderer

    def rendererName(self, renderer: typing.Union[str, QgsRasterRenderer]) -> str:
        if isinstance(renderer, QgsRasterRenderer):
            renderer = renderer.type()
        return RENDER_TYPE2NAME.get(renderer, renderer)
        assert isinstance(renderer, str)

    def setRenderer(self, renderer: QgsRasterRenderer):
        if not isinstance(renderer, QgsRasterRenderer):
            return

        w = self.renderBandWidget
        assert isinstance(self.labelRenderType, QLabel)
        assert isinstance(w, QStackedWidget)

        self.labelRenderType.setText(self.rendererName(renderer))
        if isinstance(renderer, (
                QgsSingleBandGrayRenderer,
                QgsSingleBandColorDataRenderer,
                QgsSingleBandPseudoColorRenderer,
                QgsPalettedRasterRenderer)):
            w.setCurrentWidget(self.pageSingleBand)

            if isinstance(renderer, QgsSingleBandGrayRenderer):
                self.cbSingleBand.setBand(renderer.grayBand())

            elif isinstance(renderer, QgsSingleBandPseudoColorRenderer):
                self.cbSingleBand.setBand(renderer.band())

            elif isinstance(renderer, QgsPalettedRasterRenderer):
                self.cbSingleBand.setBand(renderer.band())

            elif isinstance(renderer, QgsSingleBandColorDataRenderer):
                self.cbSingleBand.setBand(renderer.usesBands()[0])

        elif isinstance(renderer, QgsMultiBandColorRenderer):
            w.setCurrentWidget(self.pageMultiBand)
            self.cbMultiBandRed.setBand(renderer.redBand())
            self.cbMultiBandGreen.setBand(renderer.greenBand())
            self.cbMultiBandBlue.setBand(renderer.blueBand())

        else:
            w.setCurrentWidget(self.pageUnknown)

    def shouldTriggerLayerRepaint(self) -> bool:
        return True

    def apply(self):
        newRenderer = self.renderer()

        if isinstance(newRenderer, QgsRasterRenderer) and isinstance(self.mLayer, QgsRasterLayer):
            newRenderer.setInput(self.mLayer.dataProvider())
            self.mLayer.setRenderer(newRenderer)
            # self.mLayer.emitStyleChanged()
            self.widgetChanged.emit()

    def wlBand(self, wlKey: str) -> int:
        """
        Returns the band number for a wavelength
        :param wlKey:
        :type wlKey:
        :return:
        :rtype:
        """
        from ..utils import LUT_WAVELENGTH
        if isinstance(self.mWL, np.ndarray):
            targetWL = float(LUT_WAVELENGTH[wlKey])
            return int(np.argmin(np.abs(self.mWL - targetWL))) + 1
        else:
            return None

    def setWL(self, wlRegions: tuple):
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

        self.widgetChanged.emit()

    def setDockMode(self, dockMode: bool):
        pass


class RasterBandPropertiesConfigWidget(QpsMapLayerConfigWidget):

    mTable: QTableWidget
    mColumn: QComboBox
    mSetValues: QToolButton
    mRevertValues: QToolButton
    mCode: QLineEdit
    mPreview: QLineEdit

    def __init__(self, layer: QgsRasterLayer, canvas: QgsMapCanvas, parent: QWidget = None):

        super(RasterBandPropertiesConfigWidget, self).__init__(layer, canvas, parent=parent)
        pathUi = pathlib.Path(__file__).parents[1] / 'ui' / 'rasterbandpropertiesconfigwidget.ui'
        loadUi(pathUi, self)

        assert isinstance(layer, QgsRasterLayer)
        self.mCanvas = canvas
        self.mReader = RasterReader(layer)

        # init gui
        self.mTable.setRowCount(self.mReader.bandCount())
        self.mOldState = dict()
        for bandNo in self.mReader.bandNumbers():
            row = bandNo - 1

            bandName = self.mReader.userBandName(bandNo)
            if bandName is None:
                bandName = self.mReader.bandName(bandNo)
            w = QgsFilterLineEdit()
            w.setNullValue(bandName)
            w.setText(bandName)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 0, w)
            self.mOldState[(row, 0)] = bandName

            wavelength = self.mReader.wavelength(bandNo)
            if wavelength is None:
                wavelength = ''
            else:
                wavelength = str(round(wavelength, 3))
            w = QgsFilterLineEdit()
            w.setNullValue(wavelength)
            w.setText(wavelength)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 1, w)
            self.mOldState[(row, 1)] = wavelength

            fwhm = self.mReader.fwhm(bandNo)
            if fwhm is None:
                fwhm = ''
            else:
                fwhm = str(round(fwhm, 3))
            w = QgsFilterLineEdit()
            w.setNullValue(fwhm)
            w.setText(fwhm)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 2, w)
            self.mOldState[(row, 2)] = fwhm

            isBadBand = self.mReader.badBandMultiplier(bandNo) == 0
            w = QCheckBox()
            w.setChecked(isBadBand)
            self.mTable.setCellWidget(row, 3, w)
            self.mOldState[(row, 3)] = isBadBand

            self.dateTimeFormat = 'yyyy-MM-ddTHH:mm:ss'
            startTime = self.mReader.startTime(bandNo)
            w = QgsDateTimeEdit()
            w.setDisplayFormat(self.dateTimeFormat)
            w.setFrame(False)
            w.setNullRepresentation('')
            w.setCalendarPopup(False)
            w.setButtonSymbols(QAbstractSpinBox.NoButtons)
            if startTime is None:
                w.clear()
            else:
                w.setDateTime(startTime)
            self.mTable.setCellWidget(row, 4, w)
            self.mOldState[(row, 4)] = startTime

            endTime = self.mReader.endTime(bandNo)
            w = QgsDateTimeEdit()
            w.setDisplayFormat(self.dateTimeFormat)
            w.setFrame(False)
            w.setNullRepresentation('')
            w.setCalendarPopup(False)
            w.setButtonSymbols(QAbstractSpinBox.NoButtons)
            if endTime is None:
                w.clear()
            else:
                w.setDateTime(endTime)
            self.mTable.setCellWidget(row, 5, w)
            self.mOldState[(row, 5)] = endTime

            offset = self.mReader.userBandOffset(bandNo)
            if offset is None:
                offset = ''
            else:
                offset = str(offset)
            w = QgsFilterLineEdit()
            w.setNullValue(offset)
            w.setText(offset)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 6, w)
            self.mOldState[(row, 6)] = offset

            scale = self.mReader.userBandScale(bandNo)
            if scale is None:
                scale = ''
            else:
                scale = str(scale)
            w = QgsFilterLineEdit()
            w.setNullValue(scale)
            w.setText(scale)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 7, w)
            self.mOldState[(row, 7)] = scale

            noDataValues = self.bandNoDataValuesToString(bandNo)  # e.g. '-9999, [0, 1.5], [0, 1.5), (0, 1.5], (0, 1.5)'
            w = QgsFilterLineEdit()
            w.setNullValue(noDataValues)
            w.setText(noDataValues)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 8, w)
            self.mOldState[(row, 8)] = noDataValues

        self.mTable.resizeColumnToContents(0)
        self.setPanelTitle('Band Properties')

        # connect signals
        self.mCode.textChanged.connect(self.onCodeChanged)
        self.mSetValues.clicked.connect(self.onSetValuesClicked)
        self.mRevertValues.clicked.connect(self.onRevertValuesClicked)
        self.parent().accepted.connect(self.onAccepted)

    def bandNoDataValuesToString(self, bandNo: int) -> str:
        items = list()
        if self.mReader.sourceNoDataValue(bandNo) is not None:
            items.append(str(self.mReader.sourceNoDataValue(bandNo)))

        rasterRange: QgsRasterRange
        for rasterRange in self.mReader.userNoDataValues(bandNo):
            if rasterRange.min() == rasterRange.max() and rasterRange.bounds() == QgsRasterRange.IncludeMinAndMax:
                items.append(f'{rasterRange.min()}')
            else:
                p1, p2 = ['[]', '(]', '[)', '()'][rasterRange.bounds()]
                items.append(f'{p1}{rasterRange.min()}, {rasterRange.max()}{p2}')

        return ', '.join(items)

    def bandNoDataValuesFromString(self, text: str) -> Optional[List[QgsRasterRange]]:
        # e.g.  '-9999, [0, 1.5], [0, 1.5), (0, 1.5], (0, 1.5)'
        try:
            rasterRanges = list()
            for s in text.split(','):
                s = s.strip()
                if ',' in s:
                    p1, p2 = s[0], s[-1]
                    vmin, vmax = s[1:-1].split(',')
                    bounds = ['[]', '(]', '[)', '()'].index(p1 + p2)
                    rasterRanges.append(QgsRasterRange(float(vmin), float(vmax), bounds))
        except Exception as error:
            traceback.print_exc()
            return None

    def onCodeChanged(self):
        code = self.mCode.text()
        try:
            values = list()
            for bandNo in self.mReader.bandNumbers():
                value = eval(code, {'bandNo': bandNo, 'layer': self.mReader.layer, 'reader': self.mReader})
                values.append(value)
        except Exception as error:
            self.mPreview.setText(str(error))
            self.mSetValues.setEnabled(False)
            self.mEvalValues = None
            return

        self.mSetValues.setEnabled(True)
        self.mPreview.setText(str(values))
        self.mEvalValues = values

    def onSetValuesClicked(self):
        column = self.mColumn.currentIndex()
        for bandNo, value in zip(self.mReader.bandNumbers(), self.mEvalValues):
            row = bandNo - 1

            widget = self.mTable.cellWidget(row, column)
            if isinstance(widget, QgsFilterLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QgsDateTimeEdit):
                widget.setDateTime(Utils.parseDateTime(value))
            else:
                raise NotImplementedError(f'unexpected attribute type: {type(widget)}')

    def onRevertValuesClicked(self):
        column = self.mColumn.currentIndex()
        for bandNo, value in zip(self.mReader.bandNumbers(), self.mEvalValues):
            row = bandNo - 1
            widget = self.mTable.cellWidget(row, column)
            value = self.mOldState[(row, column)]
            if isinstance(widget, QgsFilterLineEdit):
                widget.setText(value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value)
            elif isinstance(widget, QgsDateTimeEdit):
                widget.setDateTime(value)
            else:
                raise NotImplementedError(f'unexpected attribute type: {type(widget)}')

    def onAccepted(self):
        for bandNo in self.mReader.bandNumbers():
            row = bandNo - 1

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 0)
            bandName = w.text()
            if bandName != self.mOldState[(row, 0)]:
                self.mReader.setUserBandName(bandName, bandNo)

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 1)
            wavelength = w.text()
            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 2)
            fwhm = w.text()
            if wavelength != self.mOldState[(row, 1)] or fwhm != self.mOldState[(row, 2)]:
                self.mReader.setWavelength(float(wavelength), bandNo, None, float(fwhm))

            w: QCheckBox = self.mTable.cellWidget(row, 3)
            isBadBand = w.checkState()
            if isBadBand != self.mOldState[(row, 3)]:
                if isBadBand:
                    self.mReader.setBadBandMultiplier(0, bandNo)
                else:
                    self.mReader.setBadBandMultiplier(1, bandNo)

            w: QgsDateTimeEdit = self.mTable.cellWidget(row, 4)
            if w.isNull():
                startTime = None
            else:
                startTime = w.dateTime()
            w: QgsDateTimeEdit = self.mTable.cellWidget(row, 5)
            if w.isNull():
                endTime = None
            else:
                endTime = w.dateTime()
            if startTime != self.mOldState[(row, 4)] or startTime != self.mOldState[(row, 5)]:
                self.mReader.setTime(startTime, endTime, bandNo)

            w: QgsFilterLineEdit() = self.mTable.cellWidget(row, 6)
            offset = w.text()
            if offset != self.mOldState[(row, 6)]:
                self.mReader.setUserBandOffset(offset, bandNo)

            w: QgsFilterLineEdit() = self.mTable.cellWidget(row, 7)
            scale = w.text()
            if scale != self.mOldState[(row, 7)]:
                self.mReader.setUserBandScale(scale, bandNo)

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 8)
            noDataValues = w.text()
            if noDataValues != self.mOldState[(row, 8)]:
                noDataValues = self.bandNoDataValuesFromString(noDataValues)
                if noDataValues is not None:
                    self.mReader.setUserNoDataValue(bandNo, noDataValues)

    def icon(self) -> QIcon:
        return QIcon(':/images/themes/default/propertyicons/editmetadata.svg')

    def syncToLayer(self, *args):
        super().syncToLayer(*args)
        print('syncToLayer')

    def apply(self):
        print('apply')

    def closeEvent(self, *args, **kwargs):
        print('closeEvent')

    def shouldTriggerLayerRepaint(self):
        return False

    def setDockMode(self, dockMode: bool):
        pass


class RasterBandConfigWidgetFactory(QgsMapLayerConfigWidgetFactory):

    def __init__(self):
        super(RasterBandConfigWidgetFactory, self).__init__('Raster Band',
                                                            QIcon(':/qps/ui/icons/rasterband_select.svg'))
        s = ""

    def supportsLayer(self, layer):
        if isinstance(layer, QgsRasterLayer):
            return True

        return False

    def layerPropertiesPagePositionHint(self) -> str:
        return 'mOptsPage_Transparency'

    def supportLayerPropertiesDialog(self):
        return True

    def supportsStyleDock(self):
        return True

    def icon(self) -> QIcon:
        return QIcon(':/qps/ui/icons/rasterband_select.svg')

    def title(self) -> str:
        return 'Raster Band'

    def createWidget(self, layer: QgsMapLayer, canvas: QgsMapCanvas, dockWidget: bool = True,
                     parent=None) -> QgsMapLayerConfigWidget:
        w = RasterBandConfigWidget(layer, canvas, parent=parent)
        if isinstance(parent, QgsRasterLayerProperties):
            w.widgetChanged.connect(parent.syncToLayer)
        w.setWindowTitle(self.title())
        w.setWindowIcon(self.icon())
        return w


class RasterBandPropertiesConfigWidgetFactory(QgsMapLayerConfigWidgetFactory):

    def __init__(self):
        super(RasterBandPropertiesConfigWidgetFactory, self).__init__(self.title(), self.icon())

    def supportsLayer(self, layer):
        if isinstance(layer, QgsRasterLayer):
            return True

        return False

    def layerPropertiesPagePositionHint(self) -> str:
        return 'mOptsPage_Legend'

    def supportLayerPropertiesDialog(self):
        return True

    def supportsStyleDock(self):
        return True

    def icon(self) -> QIcon:
        return QIcon(':/images/themes/default/propertyicons/editmetadata.svg')

    def title(self) -> str:
        return 'Band Properties'

    def createWidget(self, layer: QgsMapLayer, canvas: QgsMapCanvas, dockWidget: bool = True,
                     parent=None) -> QgsMapLayerConfigWidget:
        w = RasterBandPropertiesConfigWidget(layer, canvas, parent=parent)
        if isinstance(parent, QgsRasterLayerProperties):
            w.widgetChanged.connect(parent.syncToLayer)
        w.setWindowTitle(self.title())
        w.setWindowIcon(self.icon())
        return w
