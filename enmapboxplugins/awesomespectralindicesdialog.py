from os.path import join, splitext, basename
from typing import Dict

import processing
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QSortFilterProxyModel
from PyQt5.QtWidgets import QToolButton, QMainWindow, QTableView
from PyQt5.uic import loadUi
from processing import getTempDirInTempFolder
from qgis._core import QgsMapLayerProxyModel, QgsRasterLayer
from qgis._gui import QgsRasterBandComboBox, QgsMapLayerComboBox, QgsFilterLineEdit, QgsDoubleSpinBox

from enmapboxplugins.widgets.mapviewcombobox import MapViewComboBox
from enmapboxprocessing.algorithm.awesomespectralindexalgorithm import AwesomeSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class AwesomeSpectralIndicesDialog(QMainWindow):
    mLayer: QgsMapLayerComboBox
    mFilter: QgsFilterLineEdit
    mSelectAll: QToolButton
    mSelectNone: QToolButton
    mTable: QTableView
    mMapView: MapViewComboBox
    mAdd: QToolButton

    mA: QgsRasterBandComboBox
    mB: QgsRasterBandComboBox
    mG: QgsRasterBandComboBox
    mR: QgsRasterBandComboBox
    mRE1: QgsRasterBandComboBox
    mRE2: QgsRasterBandComboBox
    mRE3: QgsRasterBandComboBox
    mRE4: QgsRasterBandComboBox
    mN: QgsRasterBandComboBox
    mS1: QgsRasterBandComboBox
    mS2: QgsRasterBandComboBox
    mT1: QgsRasterBandComboBox
    mT2: QgsRasterBandComboBox

    mL: QgsDoubleSpinBox
    mg: QgsDoubleSpinBox
    mC1: QgsDoubleSpinBox
    mC2: QgsDoubleSpinBox
    mcexp: QgsDoubleSpinBox
    mnexp: QgsDoubleSpinBox
    malpha: QgsDoubleSpinBox
    mgamma: QgsDoubleSpinBox
    msla: QgsDoubleSpinBox
    mslb: QgsDoubleSpinBox

    def __init__(self, *args, **kwds):
        QMainWindow.__init__(self, *args, **kwds)
        loadUi(__file__.replace('.py', '.ui'), self)

        self.model = TableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        self.mTable.setModel(self.proxy_model)
        self.mFilter.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.mTable.resizeColumnsToContents()
        self.mLayer.setFilters(QgsMapLayerProxyModel.RasterLayer)

        self.mLayer.layerChanged.connect(self.onLayerChanged)
        self.mSelectAll.clicked.connect(self.mTable.selectAll)
        self.mSelectNone.clicked.connect(self.mTable.clearSelection)
        self.mAdd.clicked.connect(self.onAddClicked)
        self.mTable.doubleClicked.connect(self.onAddClicked)

    def onLayerChanged(self):
        layer = self.mLayer.currentLayer()
        if layer is None:
            for mBand in [self.mA, self.mB, self.mG, self.mR, self.mRE1, self.mRE2, self.mRE3, self.mRE4, self.mN,
                          self.mS1, self.mS2, self.mT1, self.mT2]:
                mBand.setBand(-1)
            return
        reader = RasterReader(layer)
        for mBand in [self.mA, self.mB, self.mG, self.mR, self.mRE1, self.mRE2, self.mRE3, self.mRE4, self.mN, self.mS1,
                      self.mS2, self.mT1, self.mT2]:
            name = mBand.objectName()[1:]
            wavelength, fwhm = AwesomeSpectralIndicesAlgorithm.WavebandMapping[name]
            bandNo = reader.findWavelength(wavelength)
            if bandNo is not None:
                inFwhmRange = abs(wavelength - reader.wavelength(bandNo)) < (fwhm / 2)
                if not inFwhmRange:
                    bandNo = None
            if bandNo is None:
                bandNo = -1
            mBand.setBand(bandNo)

    def onAddClicked(self):
        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if layer is None:
            return

        # get selected bands
        bandNos = dict()
        for mBand in [self.mA, self.mB, self.mG, self.mR, self.mRE1, self.mRE2, self.mRE3, self.mRE4, self.mN, self.mS1,
                      self.mS2, self.mT1, self.mT2]:
            name = mBand.objectName()[1:]
            bandNos[name] = mBand.currentBand()

        # get selected indices
        indexes = self.mTable.selectionModel().selectedRows()
        short_names = list()
        for index in sorted(indexes):
            short_name = self.mTable.model().data(index)
            skip = False
            for name in self.model.indices[short_name]['bands']:
                if name not in bandNos:
                    continue  # ignore constants
                if bandNos[name] == -1:
                    skip = True  # missing band, skip index
            if skip:
                print(f'skip index: {short_name}')
            else:
                short_names.append(short_name)

        # create VRT layer
        if len(short_names) == 0:
            return
        if len(short_names) == 1:
            short_name = short_names[0]
            source = layer.source()
            filename = join(getTempDirInTempFolder(), f'{splitext(basename(source))[0]}.{short_name}.vrt')
            alg = AwesomeSpectralIndicesAlgorithm()
            alg.initAlgorithm()
            parameters = {
                alg.P_RASTER: source,
                alg.P_INDEX: short_name,
                alg.P_OUTPUT_VRT: filename
            }
        else:
            assert 0

        # open result
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()
        processing.run(alg, parameters)
        layer = QgsRasterLayer(filename, basename(filename))
        enmapBox.onDataDropped([layer], self.mMapView.currentMapView())


class TableModel(QAbstractTableModel):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        indices = AwesomeSpectralIndicesAlgorithm.loadIndices()['SpectralIndices']
        data = [indices[key] for key in sorted(indices)]
        data = [[v['short_name'], v['long_name'], v['type'], v['formula'], v['reference']]
                for v in data if v['type'] != 'kernel']
        self.indices: Dict = indices
        self._data = data
        self._header = ['Short name', 'Long name', 'Type', 'Formula', 'Reference']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (role != Qt.DisplayRole):
            return QVariant()

        if (orientation == Qt.Horizontal):
            return self._header[section]

        return section + 1
