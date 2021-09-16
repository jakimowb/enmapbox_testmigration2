from collections import OrderedDict
from functools import partial
from os.path import splitext, basename
from time import time
from typing import Dict, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QInputDialog, QMenu, QAction, QComboBox, QListWidget
from PyQt5.uic import loadUi
from qgis._core import QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFields, QgsField, QgsCoordinateReferenceSystem

from enmapboxprocessing.parameter.processingparametercodeeditwidget import CodeEditWidget
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.utils import Utils
from processing.gui.wrappers import WidgetWrapper, DIALOG_MODELER, DIALOG_BATCH


class ProcessingParameterRasterMathCodeEdit(QWidget):
    mCode: CodeEditWidget
    mSourcesTree: QTreeWidget
    mInput: QComboBox
    mOutput: QComboBox
    mLandsat8: QListWidget
    mSentinel2: QListWidget

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)

        self.updateSources()
        QgsProject.instance().layersAdded.connect(self.updateSources)

        # connect signals
        self.mSourcesTree.clicked.connect(self.onSourceClicked)
        self.mSourcesTree.doubleClicked.connect(self.onSourceDoubleClicked)
        self.mSourcesTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mSourcesTree.customContextMenuRequested.connect(self.onContextMenuRequested)

        self.mBiggerGui.clicked.connect(
            lambda: self.mCode.setMinimumSize(0, min(self.mCode.size().height() + 100, 1000))
        )
        self.mSmallerGui.clicked.connect(
            lambda: self.mCode.setMinimumSize(0, max(self.mCode.size().height() - 100, 300))
        )

        for name in ['mAdd', 'mSubtract', 'mMultiply', 'mDivide', 'mLeftBracket', 'mRightBracket', 'mLess', 'mGreater',
                     'mEqual', 'mNotEqual', 'mLessEqual', 'mGreaterEqual']:
            obj: QPushButton = getattr(self, name)
            obj.clicked.connect(self.onOperatorClicked)

        for name in ['mNoDataValue', 'mMetadata', 'mMetadataItem', 'mBandName',
                     'mSetNoDataValue', 'mSetMetadata', 'mSetMetadataItem', 'mSetBandName',
                     'mAssign',
                     'mInputArray', 'mInputMask', 'mOutputArray']:
            obj: QPushButton = getattr(self, name)
            obj.clicked.connect(self.onMethodClicked)

        self.mLandsat8.doubleClicked.connect(self.onSensorBandDoubleClicked)
        self.mSentinel2.doubleClicked.connect(self.onSensorBandDoubleClicked)

        self._lastDoubleClickTime = 0.  # required for a workaround

    def onSensorBandDoubleClicked(self):
        list = self.sender()
        text = self.mInput.currentText()
        text += list.currentItem().toolTip()
        y, x = self.mCode.getCursorPosition()
        self.mCode.insert(text)
        x += len(text)
        self.mCode.setCursorPosition(y, x)

    def onSourceClicked(self):
        item = self.mSourcesTree.currentItem()

        if isinstance(item, LayerItem):
            layerItem = item
        elif isinstance(item, BandItem):
            layerItem = item.layerItem
        else:
            return
        text = layerItem.data(0, 0)
        self.mInput.setCurrentText(text)

        texts = [self.mInput.itemText(i) for i in range(self.mInput.count())] + ['']
        if text in texts:
            return

        self.mInput.addItem(text)

    def onSourceDoubleClicked(self):
        self.insertIdentifier()
        self.onSourceClicked()

    def onContextMenuRequested(self, pos):

        item = self.mSourcesTree.currentItem()
        if item is None:
            return

        if isinstance(item, FolderItem):
            return

        menu = QMenu()

        if isinstance(item, LayerItem):
            isMapped = item.data(0, 0) != ''
            if not isMapped:
                action = QAction('Map source to identifier', self)
                action.triggered.connect(self.onContextMapSourceClicked)
                menu.addAction(action)

            action = QAction('Rename identifier', self)
            action.triggered.connect(self.onContextRenameIdentifierClicked)
            action.setEnabled(isMapped)
            menu.addAction(action)

        if isinstance(item, RasterBandItem):
            bandNo = item.data(0, 0)[1:]
            if bandNo.endswith('nm'):
                wavelength = float(bandNo.replace('nm', ''))
                reader = RasterReader(item.layer)
                bandNo = reader.findWavelength(wavelength)
            else:
                bandNo = int(bandNo)
            layerItem = item.layerItem

            action = QAction('Data array', self)
            identifier = layerItem.data(0, 0) + item.data(0, 0)
            action.triggered.connect(partial(self.insertIdentifier, identifier))
            menu.addAction(action)

            action = QAction('Mask array', self)
            identifier = layerItem.data(0, 0) + 'Mask' + item.data(0, 0)
            action.triggered.connect(partial(self.insertIdentifier, identifier))
            menu.addAction(action)

            action = QAction('No data value', self)
            identifier = layerItem.data(0, 0) + f'.noDataValue(bandNo={bandNo})'
            action.triggered.connect(partial(self.insertIdentifier, identifier))

            menu.addAction(action)
            action = QAction('Metadata', self)
            identifier = layerItem.data(0, 0) + f'.metadata(bandNo={bandNo})'
            action.triggered.connect(partial(self.insertIdentifier, identifier))

            menu.addAction(action)
            action = QAction('Metadata item', self)
            identifier = layerItem.data(0, 0) + f".metadataItem(key='', domain='', bandNo={bandNo})"
            action.triggered.connect(partial(self.insertIdentifier, identifier))

            menu.addAction(action)
            identifier = layerItem.data(0, 0) + f".metadataItem(key='', domain='', bandNo={bandNo})"
            action.triggered.connect(partial(self.insertIdentifier, identifier))

            menu.addAction(action)


        menu.exec_(self.mSourcesTree.viewport().mapToGlobal(pos))

    def onContextMapSourceClicked(self):
        item = self.mSourcesTree.selectedItems()[0]
        identifier = Utils.makeIdentifier(splitext(item.layer.name())[0])
        text, ok = QInputDialog.getText(
            self, 'Map source', 'Identifier:', text=identifier
        )
        if ok:
            item.setData(0, 0, text)

    def onContextRenameIdentifierClicked(self):
        item = self.mSourcesTree.selectedItems()[0]
        identifier = item.data(0, 0)
        text, ok = QInputDialog.getText(self, 'Rename identifier', 'Identifier', text=identifier)
        if ok:
            item.setData(0, 0, text)

    def onOperatorClicked(self):
        obj: QPushButton = self.sender()
        y, x = self.mCode.getCursorPosition()
        text = obj.text()
        if text not in '()':
            text = ' ' + text + ' '
        self.mCode.insert(text)
        x += len(text)
        self.mCode.setCursorPosition(y, x)

    def onMethodClicked(self):
        obj: QPushButton = self.sender()
        y, x = self.mCode.getCursorPosition()

        if obj.text() in '=':
            # text = self.mOutput.currentText() + ' = '
            text = ' = '
        elif 'set' in obj.text():
            text = self.mOutput.currentText() + '.' + obj.text() + '()'
        elif obj.objectName() == 'mInputArray':
            if self.mInput.currentText() == '':
                return
            text = self.mInput.currentText()
        elif obj.objectName() == 'mInputMask':
            if self.mInput.currentText() == '':
                return
            text = self.mInput.currentText() + 'Mask'
        elif obj.objectName() == 'mOutputArray':
            text = self.mOutput.currentText()
        else:
            text = self.mInput.currentText() + '.' + obj.text() + '()'

        self.mCode.insert(text)
        x += len(text)
        if '.set' in text:
            x -= 1
        self.mCode.setCursorPosition(y, x)
        self.mCode.setFocus()

    def getSources(self) -> Dict:
        sources = dict()
        for i in range(self.mSourcesTree.topLevelItemCount()):
            item: LayerItem = self.mSourcesTree.topLevelItem(i)
            identifier = item.data(0, 0)
            if identifier != '':
                sources[identifier] = item.registryName

        return sources

    def insertIdentifier(self, identifier: str = None):
        # workaround an issue, where on doubleClicked is triggered twice
        t = time()
        if (t - self._lastDoubleClickTime) < 0.1:
            return
        self._lastDoubleClickTime = t

        item = self.mSourcesTree.currentItem()

        if isinstance(item, FolderItem):
            return

        if isinstance(item, LayerItem):
            layerItem = item
        else:
            layerItem = item.layerItem

        if identifier is None:
            identifier = layerItem.data(0, 0)
            if isinstance(item, BandItem):
                identifier += item.data(0, 0)

        y, x = self.mCode.getCursorPosition()
        self.mCode.insert(identifier)
        x += len(identifier)
        self.mCode.setCursorPosition(y, x)
        self.mCode.setFocus()

    def updateSources(self):
        self.mSourcesTree.clear()

        layers = OrderedDict()

        # remove duplicate sources
        identifiers = list()
        for registryName, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, (QgsRasterLayer, QgsVectorLayer)):
                identifier = (layer.source(), layer.name())
                if identifier in identifiers:
                    continue
                identifiers.append(identifier)
                layers[registryName] = layer
        del identifiers

        rasterIcon = QIcon(':/images/themes/default/mIconRaster.svg')
        vectorIcon = QIcon(':/images/themes/default/mIconVector.svg')

        for registryName, layer in layers.items():

            crs: QgsCoordinateReferenceSystem = layer.crs()
            if not crs.isValid():
                continue
            crsid = f' [{crs.authid()}]'

            font = self.mSourcesTree.font()
            font.setItalic(True)
            identifier = splitext(basename(layer.name()))[0]
            if isinstance(layer, QgsRasterLayer):
                data = layer.name() + crsid
                item = RasterItem([identifier, data])
                item.layer = layer
                item.registryName = registryName
                item.setToolTip(1, layer.source())
                item.setIcon(1, rasterIcon)
                self.mSourcesTree.addTopLevelItems([item])
                layerItem = item

                reader = RasterReader(layer)

                for i in range(reader.bandCount()):
                    bandNo = i + 1
                    data = reader.bandName(bandNo)
                    item = RasterBandItem([f'@{bandNo}', data])
                    item.layerItem = layerItem
                    item.layer = layer
                    item.bandNo = bandNo
                    if reader.isSpectralRasterLayer():
                        item.setToolTip(1, f'{layer.source()} ({round(reader.wavelength(bandNo), 1)} Nanometers)')
                    else:
                        item.setToolTip(1, layer.source())
                    item.setIcon(1, rasterIcon)
                    layerItem.addChild(item)
            elif isinstance(layer, QgsVectorLayer):
                data = layer.name() + crsid
                item = VectorItem([identifier, data])
                item.layer = layer
                item.registryName = registryName
                item.setToolTip(1, layer.source())
                item.setIcon(1, vectorIcon)
                self.mSourcesTree.addTopLevelItems([item])
                root = item
                layerItem = item
                fields: QgsFields = layer.fields()
                i = 0
                for name in fields.names():
                    field: QgsField = fields.field(name)
                    if field.typeName() in ['String', 'Binary']:
                        continue
                    i += 1
                    data = f'{name} ({field.typeName()})'
                    item = VectorBandItem([f'@{Utils.makeIdentifier(name)}', data])
                    item.layerItem = layerItem
                    item.layer = layer
                    item.field = name
                    item.setToolTip(1, layer.source())
                    item.setIcon(1, vectorIcon)
                    root.addChild(item)

    def value(self) -> str:
        # include the layer mapping
        text = ''
        for identifier, registryName in self.getSources().items():
            layer = QgsProject.instance().mapLayer(registryName)
            if isinstance(layer, QgsRasterLayer):
                text += f'# {identifier} := QgsRasterLayer("{layer.source()}")\n'
            if isinstance(layer, QgsVectorLayer):
                text += f'# {identifier} := QgsVectorLayer("{layer.source()}")\n'
        # append the actual code
        text += self.mCode.value()
        return text

class ProcessingParameterRasterMathCodeEditWidgetWrapper(WidgetWrapper):
    # adopted from C:\source\QGIS3-master\python\plugins\processing\algs\gdal\ui\RasterOptionsWidget.py

    widget: ProcessingParameterRasterMathCodeEdit

    def createWidget(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return ProcessingParameterRasterMathCodeEdit()

    def setValue(self, value):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            self.widget.mCode.setText(value)

    def value(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return self.widget.value()


class LayerItem(QTreeWidgetItem):
    registryName: str

class RasterItem(LayerItem):
    layer: QgsRasterLayer

class VectorItem(LayerItem):
    layer: QgsVectorLayer

class BandItem(QTreeWidgetItem):
    layerItem: LayerItem
    pass

class RasterBandItem(BandItem):
    layer: QgsRasterLayer
    bandNo: Union[int, float]  # int for actual bands and float for band by center wavelength

class VectorBandItem(BandItem):
    layer: QgsVectorLayer
    field: str

class FolderItem(QTreeWidgetItem):
    pass

class DerivedRasterBandItem(RasterBandItem):
    pass

