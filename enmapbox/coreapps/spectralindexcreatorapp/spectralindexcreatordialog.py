import webbrowser
from os.path import join, splitext, basename
from typing import Dict, Generator, Iterator, Tuple
from collections import OrderedDict

import processing
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QSortFilterProxyModel, QModelIndex
from PyQt5.QtWidgets import QToolButton, QMainWindow, QTableView, QTableWidget, QMessageBox
from PyQt5.uic import loadUi
from processing import getTempDirInTempFolder
from qgis._core import QgsMapLayerProxyModel, QgsRasterLayer
from qgis._gui import QgsRasterBandComboBox, QgsMapLayerComboBox, QgsFilterLineEdit, QgsDoubleSpinBox, QgsMessageBar

from enmapboxplugins.widgets.mapviewcombobox import MapViewComboBox
from enmapboxprocessing.algorithm.createspectralindicesalgorithm import CreateSpectralIndicesAlgorithm
from enmapboxprocessing.rasterreader import RasterReader
from typeguard import typechecked


@typechecked
class SpectralIndexCreatorDialog(QMainWindow):
    mMessageBar: QgsMessageBar
    mLayer: QgsMapLayerComboBox
    mFilter: QgsFilterLineEdit
    mSelectAll: QToolButton
    mSelectNone: QToolButton
    mTable: QTableView
    mTable2: QTableWidget
    mMapView: MapViewComboBox
    mCreate: QToolButton
    mCreate2: QToolButton
    mWebsite: QToolButton

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
        self.mTable2.resizeColumnsToContents()
        for i in range(1, 95):
            self.mTable2.insertRow(self.mTable2.rowCount())
        self.mLayer.setFilters(QgsMapLayerProxyModel.RasterLayer)
        for mConstant in self.mConstants():
            mConstant.setClearValue(mConstant.value())

        self.mLayer.layerChanged.connect(self.onLayerChanged)
        self.mSelectAll.clicked.connect(self.mTable.selectAll)
        self.mSelectNone.clicked.connect(self.mTable.clearSelection)
        self.mCreate.clicked.connect(self.onCreateClicked)
        self.mCreate2.clicked.connect(self.onCreateClicked)
        self.mTable.doubleClicked.connect(self.onCreateClicked)
        self.mTable2.doubleClicked.connect(self.onCreateClicked)
        self.mWebsite.clicked.connect(lambda: webbrowser.open('https://awesome-ee-spectral-indices.readthedocs.io/'))

    def mBands(self) -> Iterator[QgsRasterBandComboBox]:
        for mBand in [self.mA, self.mB, self.mG, self.mR, self.mRE1, self.mRE2, self.mRE3, self.mRE4, self.mN, self.mS1,
                      self.mS2, self.mT1, self.mT2]:
            yield mBand

    def mConstants(self) -> Iterator[QgsDoubleSpinBox]:
        for mConstant in [self.mL, self.mg, self.mC1, self.mC2, self.mcexp, self.mnexp, self.malpha, self.mgamma,
                          self.msla, self.mslb]:
            yield mConstant

    def onLayerChanged(self):
        layer = self.mLayer.currentLayer()
        if layer is None:
            for mBand in self.mBands():
                mBand.setBand(-1)
            return
        reader = RasterReader(layer)
        for mBand in self.mBands():
            name = mBand.objectName()[1:]
            wavelength, fwhm = CreateSpectralIndicesAlgorithm.WavebandMapping[name]
            bandNo = reader.findWavelength(wavelength)
            if bandNo is not None:
                inFwhmRange = abs(wavelength - reader.wavelength(bandNo)) < (fwhm / 2)
                if not inFwhmRange:
                    bandNo = None
            if bandNo is None:
                bandNo = -1
            mBand.setBand(bandNo)

    def iterCurrentBands(self) -> Iterator[Tuple[str, int]]:
        for mBand in self.mBands():
            name = mBand.objectName()[1:]
            bandNo = mBand.currentBand()
            yield name, bandNo

    def onCreateClicked(self):

        # create either predefined or custom indices
        if self.sender() in [self.mCreate, self.mTable]:
            mTables = [self.mTable]
        elif self.sender() in [self.mCreate2, self.mTable2]:
            mTables = [self.mTable2]
        else:
            assert 0

        layer: QgsRasterLayer = self.mLayer.currentLayer()
        if layer is None:
            self.mMessageBar.pushInfo('Missing parameter', 'select a spectral raster layer')
            return

        bandNos = {name: bandNo for name, bandNo in self.iterCurrentBands()}

        # get selected indices
        missingBands = list()
        skippedIndices = list()
        formulas = OrderedDict()
        for mTable in mTables:
            indexes = mTable.selectionModel().selectedRows()
            for index in sorted(indexes):
                QModelIndex()
                short_name = mTable.model().data(mTable.model().index(index.row(), 0))
                formula = mTable.model().data(mTable.model().index(index.row(), 2))
                if short_name is None:
                    continue  # skip empty rows

                # derive bands from formular
                formula_ = formula
                bands = list()
                for name in sorted(CreateSpectralIndicesAlgorithm.WavebandMapping.keys(), key=len, reverse=True):
                    if name in formula_:
                        bands.append(name)
                        formula_ = formula_.replace(name, '')

                # skip if band is missing
                skip = False
                for name in bands:
                    if bandNos[name] == -1:
                        missingBands.append(name)
                        skippedIndices.append(short_name)
                        skip = True

                if skip:
                    continue

                if mTable is self.mTable:
                    formulas[short_name] = short_name
                if mTable is self.mTable2:
                    formulas[short_name] = short_name + ' = ' + formula

        if len(skippedIndices) > 0:
            self.mMessageBar.pushInfo(
                'Missing wavebands', ', '.join(set(missingBands)) + ' skip indices ' + ', '.join(set(skippedIndices))
            )

        if len(formulas) == 0:
            self.mMessageBar.pushInfo('Missing parameter', 'select valid indices')
            return

        # create VRT layer
        source = layer.source()
        if len(formulas) == 1:
            short_name = list(formulas.keys())[0]
            filename = join(getTempDirInTempFolder(), f'{splitext(basename(source))[0]}.{short_name}.vrt')
        else:
            filename = join(getTempDirInTempFolder(), f'{splitext(basename(source))[0]}.indices.vrt')

        alg = CreateSpectralIndicesAlgorithm()
        alg.initAlgorithm()
        parameters = {
            alg.P_RASTER: source,
            alg.P_INDICES: ', '.join(formulas.values()),
            alg.P_OUTPUT_VRT: filename
        }
        for name, bandNo in bandNos.items():
            if bandNo != -1:
                parameters[name] = bandNo

        for mC in self.mConstants():
            name = mC.objectName()[1:]
            value = mC.value()
            if value == mC.clearValue():  # skip defaults
                continue
            parameters[name] = value

        # open result
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()
        processing.run(alg, parameters)
        layer = QgsRasterLayer(filename, basename(filename))
        enmapBox.onDataDropped([layer], self.mMapView.currentMapView())

        if len(formulas) == 1:
            self.mMessageBar.pushSuccess('Success', f'created {basename(layer.source())}')
        else:
            self.mMessageBar.pushSuccess('Success', f'created {basename(layer.source())} ({len(formulas)} indices)')


class TableModel(QAbstractTableModel):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        indices = CreateSpectralIndicesAlgorithm.IndexDatabase
        data = [indices[key] for key in sorted(indices)]
        data = [[v['short_name'], v['long_name'], v['formula'], v['type'], v['reference']]
                for v in data if v['type'] != 'kernel']
        self.indices: Dict = indices
        self._data = data
        self._header = ['Short name', 'Long name', 'Formula', 'Type', 'Reference']

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
