from os.path import basename
from typing import List

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem
from PyQt5.uic import loadUi
from qgis._core import QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFields, QgsField, QgsCoordinateReferenceSystem

from enmapbox import EnMAPBox
from enmapbox.gui.datasources import DataSourceRaster
from enmapboxprocessing.parameter.processingparametercodeeditwidget import CodeEditWidget
from enmapboxprocessing.rasterreader import RasterReader
from processing.gui.wrappers import WidgetWrapper, DIALOG_MODELER, DIALOG_BATCH


class ProcessingParameterRasterMathCodeEdit(QWidget):
    mCode: CodeEditWidget
    mSources: QListWidget

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(__file__.replace('.py', '.ui'), self)

        self.updateSources()
        QgsProject.instance().layersAdded.connect(self.updateSources)
        self.mSources.doubleClicked.connect(self.onDoubleClicked)

    def onDoubleClicked(self, index: QModelIndex):
        self.mCode.insert(f'"{self.labels[index.row()]}"')

    def updateSources(self):
        self.mSources.clear()
        self.identifiers = list()
        self.layers = list()
        self.labels = list()

        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, (QgsRasterLayer, QgsVectorLayer)):
                identifier = (layer.source(), layer.name())
                if identifier in self.identifiers:
                    continue
                self.identifiers.append(identifier)
                self.layers.append(layer)

        rasterIcon = QIcon(':/images/themes/default/mIconRaster.svg')
        vectorIcon = QIcon(':/images/themes/default/mIconVector.svg')
        for identifier, layer in zip(self.identifiers, self.layers):
            crs: QgsCoordinateReferenceSystem = layer.crs()
            if not crs.isValid():
                continue
            crsid = f' [{crs.authid()}]'
            if isinstance(layer, QgsRasterLayer):
                label = identifier[1]
                item = QListWidgetItem(rasterIcon, label + crsid)
                item.setToolTip(layer.source())
                self.mSources.addItem(item)
                self.labels.append(label)
                reader = RasterReader(layer)
                for i in range(reader.bandCount()):
                    bandNo = i + 1
                    label = f'{identifier[1]}@{bandNo}'
                    item = QListWidgetItem(rasterIcon, f'{label} ({reader.bandName(bandNo)})' + crsid)
                    item.setToolTip(layer.source())
                    self.mSources.addItem(item)
                    self.labels.append(label)
            elif isinstance(layer, QgsVectorLayer):
                label = identifier[1]
                item = QListWidgetItem(vectorIcon, label + crsid)
                item.setToolTip(layer.source())
                self.mSources.addItem(item)
                self.labels.append(label)
                fields: QgsFields = layer.fields()
                for name in fields.names():
                    field: QgsField = fields.field(name)
                    if field.typeName() in ['String', 'Binary']:
                        continue
                    label = f'{identifier[1]}@{name}'
                    item = QListWidgetItem(vectorIcon, f'{label} ({field.typeName()})' + crsid)
                    item.setToolTip(layer.source())
                    self.mSources.addItem(item)
                    self.labels.append(label)


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
            self.widget.codeEdit.setText(value)

    def value(self):
        if self.dialogType == DIALOG_MODELER:
            raise NotImplementedError()
        elif self.dialogType == DIALOG_BATCH:
            raise NotImplementedError()
        else:
            return self.widget.codeEdit.value()
