import traceback
from typing import Optional, List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidget, QComboBox, QToolButton, QLineEdit, QWidget, QCheckBox, QAbstractSpinBox
from qgis._core import QgsRasterLayer, QgsRasterRange, QgsMapLayer
from qgis._gui import QgsMapCanvas, QgsFilterLineEdit, QgsDateTimeEdit, QgsMapLayerConfigWidgetFactory, \
    QgsMapLayerConfigWidget, QgsRasterLayerProperties

from enmapbox.qgispluginsupport.qps.layerconfigwidgets.core import QpsMapLayerConfigWidget
from enmapbox.qgispluginsupport.qps.utils import loadUi
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils


class RasterBandPropertiesConfigWidget(QpsMapLayerConfigWidget):
    mTable: QTableWidget
    mColumn: QComboBox
    mSetValues: QToolButton
    mRevertValues: QToolButton
    mCode: QLineEdit
    mPreview: QLineEdit

    def __init__(self, layer: QgsRasterLayer, canvas: QgsMapCanvas, parent: QWidget = None):

        super(RasterBandPropertiesConfigWidget, self).__init__(layer, canvas, parent=parent)
        pathUi = __file__.replace('.py', '.ui')
        loadUi(pathUi, self)

        assert isinstance(layer, QgsRasterLayer)
        self.mCanvas = canvas
        self.mLayer = layer

        reader = RasterReader(self.mLayer)

        # init gui
        self.mTable.setRowCount(reader.bandCount())
        self.mOldState = dict()
        for bandNo in reader.bandNumbers():
            row = bandNo - 1

            bandName = reader.userBandName(bandNo)
            if bandName is None:
                bandName = reader.bandName(bandNo)
            w = QgsFilterLineEdit()
            w.setNullValue(bandName)
            w.setText(bandName)
            w.setFrame(False)
            self.mTable.setCellWidget(row, 0, w)
            self.mOldState[(row, 0)] = bandName

            wavelength = reader.wavelength(bandNo)
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

            fwhm = reader.fwhm(bandNo)
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

            isBadBand = reader.badBandMultiplier(bandNo) == 0
            w = QCheckBox()
            w.setChecked(isBadBand)
            self.mTable.setCellWidget(row, 3, w)
            self.mOldState[(row, 3)] = isBadBand

            self.dateTimeFormat = 'yyyy-MM-ddTHH:mm:ss'
            startTime = reader.startTime(bandNo)
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

            endTime = reader.endTime(bandNo)
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

            offset = reader.userBandOffset(bandNo)
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

            scale = reader.userBandScale(bandNo)
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
        reader = RasterReader(self.mLayer)
        items = list()
        if reader.sourceNoDataValue(bandNo) is not None:
            items.append(str(reader.sourceNoDataValue(bandNo)))

        rasterRange: QgsRasterRange
        for rasterRange in reader.userNoDataValues(bandNo):
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

        return rasterRanges

    def onCodeChanged(self):
        code = self.mCode.text()
        reader = RasterReader(self.mLayer)
        try:
            values = list()
            for bandNo in reader.bandNumbers():
                value = eval(code, {'bandNo': bandNo, 'layer': reader.layer, 'reader': reader})
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
        reader = RasterReader(self.mLayer)
        column = self.mColumn.currentIndex()
        for bandNo, value in zip(reader.bandNumbers(), self.mEvalValues):
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
        reader = RasterReader(self.mLayer)
        column = self.mColumn.currentIndex()
        for bandNo, value in zip(reader.bandNumbers(), self.mEvalValues):
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
        reader = RasterReader(self.mLayer)
        hasChanged = False
        for bandNo in reader.bandNumbers():
            row = bandNo - 1

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 0)
            bandName = w.text()
            if bandName != self.mOldState[(row, 0)]:
                reader.setUserBandName(bandName, bandNo)
                hasChanged = True

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 1)
            wavelength = w.text()
            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 2)
            fwhm = w.text()
            if wavelength != self.mOldState[(row, 1)] or fwhm != self.mOldState[(row, 2)]:
                fwhm = None if fwhm == '' else float(fwhm)
                wavelength = None if wavelength == '' else float(wavelength)
                reader.setWavelength(wavelength, bandNo, None, fwhm)
                hasChanged = True

            w: QCheckBox = self.mTable.cellWidget(row, 3)
            isBadBand = w.checkState()
            if isBadBand != self.mOldState[(row, 3)]:
                if isBadBand:
                    reader.setBadBandMultiplier(0, bandNo)
                else:
                    reader.setBadBandMultiplier(1, bandNo)
                hasChanged = True

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
                reader.setTime(startTime, endTime, bandNo)
                hasChanged = True

            w: QgsFilterLineEdit() = self.mTable.cellWidget(row, 6)
            offset = w.text()
            if offset != self.mOldState[(row, 6)]:
                reader.setUserBandOffset(offset, bandNo)
                hasChanged = True

            w: QgsFilterLineEdit() = self.mTable.cellWidget(row, 7)
            scale = w.text()
            if scale != self.mOldState[(row, 7)]:
                reader.setUserBandScale(scale, bandNo)
                hasChanged = True

            w: QgsFilterLineEdit = self.mTable.cellWidget(row, 8)
            noDataValues = w.text()
            if noDataValues != self.mOldState[(row, 8)]:
                noDataValues = self.bandNoDataValuesFromString(noDataValues)
                if noDataValues is not None:
                    reader.setUserNoDataValue(bandNo, noDataValues)
                    hasChanged = True

        if hasChanged:
            RasterReader.flushQgisPam(self.mLayer)

    def icon(self) -> QIcon:
        return QIcon(':/images/themes/default/propertyicons/editmetadata.svg')

    def syncToLayer(self, *args):
        super().syncToLayer(*args)
        pass

    def apply(self):
        pass

    def closeEvent(self, *args, **kwargs):
        pass

    def shouldTriggerLayerRepaint(self):
        return False

    def setDockMode(self, dockMode: bool):
        pass


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
