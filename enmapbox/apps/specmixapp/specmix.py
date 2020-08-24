import typing
import math
import collections
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import QgsField
from enmapbox.externals.qps.speclib.core import SpectralLibrary, SpectralProfile
from enmapbox.externals.qps.speclib.gui import SpectralLibraryPlotWidget, SpectralProfilePlotDataItem
from enmapbox.externals.qps.utils import loadUi
from enmapbox.gui.spectralprofilesources import SpectralProfileDstListModel

import numpy as np
from . import APP_DIR


class SpectralLibraryListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.mSpectralLibraries: typing.List[SpectralLibrary] = []

    def __len__(self) -> int:
        return len(self.mSpectralLibraries)

    def __iter__(self):
        return iter(self.mSpectralLibraries)

    def __getitem__(self, slice):
        return self.mSpectralLibraries[slice]

    def addSpectralLibraries(self, speclibs: typing.List[SpectralLibrary], i: int= None):
        if not isinstance(speclibs, list):
            speclibs = [speclibs]

        speclibs = [s for s in speclibs if isinstance(s, SpectralLibrary) and s not in self.mSpectralLibraries]
        if len(speclibs) > 0:
            if i is None:
                i = len(self)

            self.beginInsertRows(QModelIndex(), i, i + len(speclibs) - 1)
            for j, s in enumerate(speclibs):
                self.mSpectralLibraries.insert(i + j, s)
            self.endInsertRows()

    def removeSpectralLibraries(self, speclibs: typing.List[SpectralLibrary]):
        if not isinstance(speclibs, list):
            speclibs = [speclibs]
        speclibs = [s for s in speclibs if isinstance(s, SpectralLibrary) and s in self.mSpectralLibraries]

        for s in speclibs:
            i = self.mSpectralLibraries.index(s)
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mSpectralLibraries.pop(i)
            self.endRemoveRows()

    def speclib2idx(self, speclib:SpectralLibrary) -> QModelIndex:
        assert isinstance(speclib, SpectralLibrary)
        assert speclib in self.mSpectralLibraries
        i = self.mSpectralLibraries.index(speclib)
        return self.createIndex(i, 0, speclib)

    def rowCount(self, parent: QModelIndex = None) -> int:
        return len(self)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return 'Spectral Library'

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        speclib = self.mSpectralLibraries[index.row()]
        assert isinstance(speclib, SpectralLibrary)
        if role == Qt.DisplayRole:
            return speclib.name()
        if role == Qt.ToolTipRole:
            return speclib.source()

        if role == Qt.DecorationRole:
            return QIcon(r':/qps/ui/icons/speclib.svg')

        elif role == Qt.UserRole:
            return speclib

        return None



class SpecMixParameterModel(QAbstractTableModel):

    sigProfileLimitChanged = pyqtSignal(int)

    SL_OFID = 'ofid'
    SL_METRIC = 'metric'
    SL_WEIGHT = 'weight'
    SL_NWEIGHT = 'nweight'

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.mSpeclib: SpectralLibrary = SpectralLibrary()
        self.mSpeclib.startEditing()
        self.mSpeclib.deleteAttribute(self.mSpeclib.fields().lookupField('source'))
        self.mSpeclib.addAttribute(QgsField(SpecMixParameterModel.SL_OFID, QVariant.Int, 'int'))
        self.mSpeclib.addAttribute(QgsField(SpecMixParameterModel.SL_METRIC, QVariant.String, 'varchar'))
        self.mSpeclib.addAttribute(QgsField(SpecMixParameterModel.SL_WEIGHT, QVariant.Double, 'double'))
        self.mSpeclib.addAttribute(QgsField(SpecMixParameterModel.SL_NWEIGHT, QVariant.Double, 'double'))
        self.mSpeclib.commitChanges()

        self.mSpeclib.committedFeaturesAdded.connect(self.onFeaturesAdded)
        self.mSpeclib.committedFeaturesRemoved.connect(self.onFeaturesRemoved)
        self.mSpeclib.committedAttributeValuesChanges.connect(self.onAttributeChanged)


        self.mDefaultWeight: float = 1.0
        self.mProfileLimit: int = 100

        self.cnProfile: str = 'Profile'
        self.cnWeight: str = 'Weight'
        self.cnNWeights: str = 'N.Weights'

        self.mColumnNames: typing.List[str] = [self.cnProfile, self.cnWeight, self.cnNWeights]
        self.mColumnToolTips = [
            'Spectral Profile Name',
            'Weights',
            'Normalized Weights (sum = 1.0)'
        ]

    def onAttributeChanged(self, layer_id: str, changed_attribute_values: typing.Dict[int,
                                                                                      typing.Dict[int, typing.Any]]):

        fids = sorted(self.mSpeclib.allFeatureIds())

        row0 = self.rowCount()-1
        row1 = 0
        col0 = self.columnCount()-1
        col1 = 0

        for fid, data in changed_attribute_values.items():
            if fid in fids:
                row = fids.index(fid)
                row0 = min(row0, row)
                row1 = max(row1, row)

        idx1 = self.createIndex(row0, col0)
        idx2 = self.createIndex(row1, col1)
        self.dataChanged.emit(idx1, idx2, [Qt.DisplayRole])

    def onFeaturesAdded(self, layer_id: str, added_features):

        self.beginResetModel()
        self.endResetModel()

    def onFeaturesRemoved(self, layer_id, deleted_fids):
        self.beginResetModel()
        self.endResetModel()

    def speclib(self) -> SpectralLibrary:
        return self.mSpeclib

    def calculateMixedProfiles(self) -> typing.Tuple[SpectralProfile, SpectralProfile]:

        x_values = None
        y_values = None
        x_units = None
        n = 0
        for row in range(self.rowCount()):
            idx = self.createIndex(row, 0)
            profile: SpectralProfile = self.data(idx, Qt.UserRole)
            nweight = self.data(self.createIndex(row, 2), Qt.DisplayRole)
            pxdata = np.asarray(profile.xValues())
            pydata = np.asarray(profile.yValues()) * nweight

            if x_values is None:
                x_values = pxdata
                y_values = pydata
                n += 1
            else:
                if len(pxdata) != len(x_values):
                    continue
                y_values += pydata
                n += 1

        if n == 0:
            return None, None
        else:
            avg = x_values / n

            p1 = SpectralProfile()
            p1.setValues(y=avg, x=x_values, xUnit=x_units)
            p1.setName('Weighted Average')

            p2 = SpectralProfile()
            p2.setName('Deviations')

        return p1, p2



    def updateNormalizedWeights(self):

        iFieldW =  self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_WEIGHT)
        iFieldN =self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_NWEIGHT)
        profiles = list(self.mSpeclib.profiles())
        weights = np.asarray([p.attribute(iFieldW) for p in profiles])

        wsum = weights.sum()
        if len(weights) > 0 and wsum > 0:
            nweights = weights / weights.sum()
            self.mSpeclib.startEditing()
            for i, p in enumerate(profiles):
                self.mSpeclib.changeAttributeValue(p.id(), iFieldN, float(nweights[i]))
            self.mSpeclib.commitChanges()

    def originalFeatureIds(self) -> typing.List[int]:
        return [f.attribute(SpecMixParameterModel.SL_OFID) for f in self.mSpeclib]

    def setProfileLimit(self, limit: int):
        assert limit >= 0
        if limit != self.mProfileLimit:
            self.mProfileLimit = limit
            self.sigProfileLimitChanged.emit(limit)

    def profileLimit(self) -> int:
        return self.mProfileLimit

    def addProfiles(self, profiles: typing.List[SpectralProfile]):

        ofids = self.originalFeatureIds()

        if not isinstance(profiles, list):
            profiles = [profiles]

        for p in profiles:
            assert isinstance(p, SpectralProfile)

        profiles = [p for p in profiles if p.id() not in ofids]

        aName = self.mSpeclib.fields().lookupField('name')
        aOFID = self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_OFID)
        aMetric = self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_METRIC)
        aWeight = self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_WEIGHT)
        aNWeight = self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_NWEIGHT)

        n = len(profiles)
        if n > 0:
            i = len(self.mSpeclib)
            clones = []

            for p in profiles:
                assert isinstance(p, SpectralProfile)
                j = SpectralProfile(fields=self.mSpeclib.fields())
                j.setAttribute('values', p.attribute('values'))
                j.setAttribute(aName, p.name())
                j.setAttribute(aOFID, p.id())
                j.setAttribute(aMetric, '')
                j.setAttribute(aWeight, self.mDefaultWeight)
                j.setAttribute(aNWeight, self.mDefaultWeight)
                clones.append(j)

            self.mSpeclib.startEditing()
            self.mSpeclib.addProfiles(clones)
            self.mSpeclib.commitChanges()
            self.updateNormalizedWeights()


    def removeProfiles(self, ofids: typing.List[int]):
        to_remove = [p.id() for p in self.mSpeclib if p.attribute(SpecMixParameterModel.SL_OFID) in ofids]
        if len(to_remove) > 0:
            self.mSpeclib.startEditing()
            self.mSpeclib.deleteFeatures(to_remove)
            self.mSpeclib.commitChanges()

    def rowCount(self, parent=None, *args, **kwargs):
        return len([i for i in self.mSpeclib.allFeatureIds() if i >= 0])

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.mColumnNames)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 1:
            flags = flags | Qt.ItemIsEditable
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.mColumnNames[section]

        if role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.mColumnToolTips[section]

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=None):

        profile: SpectralProfile = self.mSpeclib[index.row()]
        NULL = QVariant()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return profile.name()
            if index.column() == 1:
                return float(profile.attribute(SpecMixParameterModel.SL_WEIGHT))
            if index.column() == 2:
                return float(profile.attribute(SpecMixParameterModel.SL_NWEIGHT))

        if role == Qt.UserRole:
            return profile

        if role == Qt.EditRole:
            if index.column() == 1:
                return float(profile.attribute(SpecMixParameterModel.SL_WEIGHT))

    def setData(self, index: QModelIndex, value, role=None):

        profile: SpectralProfile = self.mSpeclib[index.row()]
        changed = False
        iFieldW = self.mSpeclib.fields().lookupField(SpecMixParameterModel.SL_WEIGHT)
        idx1 = idx2 = index
        if role == Qt.EditRole:
            if index.column() == 1 and isinstance(value, float): # set weight
                self.mSpeclib.startEditing()
                self.mSpeclib.changeAttributeValue(profile.id(), iFieldW, float(value))
                self.mSpeclib.commitChanges()
                changed = True

        if changed:
            self.dataChanged.emit(idx1, idx2, [role])
            self.updateNormalizedWeights()
        return changed


class SpecMixParameterProxyModel(QAbstractProxyModel):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class SpecMixParameterTableView(QTableView):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class SpecMixSliderWidget(QWidget):

    sigValueChanged = pyqtSignal(float)

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.setLayout(QHBoxLayout())
        self.spinbox: QDoubleSpinBox = QDoubleSpinBox()
        self.spinbox.setMinimum(0)

        self.slider: QSlider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.onSliderValueChanged)
        self.spinbox.valueChanged.connect(self.onSpinboxValueChanged)
        self.layout().addWidget(self.spinbox)
        self.layout().addWidget(self.slider)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(2)

        self.setDecimals(2)
        self.setMinimum(0)
        self.setMaximum(1)
        self.setSingleStep(0.1)

    def onSliderValueChanged(self, value: int):
        v = self.slider2spinboxvalue(value)
        self.spinbox.setValue(v)

    def onSpinboxValueChanged(self, value: float):

        v = self.spinbox2slidervalue(value)
        if v != self.slider.value():
            self.slider.setValue(v)
        self.sigValueChanged.emit(value)


    def setSingleStep(self, value: float):
        self.spinbox.setSingleStep(value)

        m = int(10**self.decimals() * value)

        self.slider.setSingleStep(m)
        self.slider.setPageStep(m*10)

    def setMinimum(self, value: float):
        self.spinbox.setMinimum(value)
        self.slider.setMinimum(self.spinbox2slidervalue(value))

    def spinbox2slidervalue(self, value: float) -> int:
        v = int(round(10**self.decimals()*value))
        return v

    def slider2spinboxvalue(self, value: int) -> float:
        v = value / (10 ** self.decimals())
        return v

    def setMaximum(self, value: float):
        self.spinbox.setMaximum(value)
        self.slider.setMaximum(self.spinbox2slidervalue(value))

    def maximum(self) -> float:
        return self.spinbox.maximum()

    def minimum(self) -> float:
        return self.spinbox.minimum()

    def setDecimals(self, value:int):
        self.spinbox.setDecimals(value)
        self.setSingleStep(self.spinbox.singleStep())

    def decimals(self) -> int:
        return self.spinbox.decimals()

    def setValue(self, value:float):
        self.spinbox.setValue(value)

    def value(self) -> float:
        return self.spinbox.value()

class SpecMixParameterViewDelegate(QStyledItemDelegate):
    """

    """

    def __init__(self, tableView: SpecMixParameterTableView, parent=None):
        assert isinstance(tableView, QTableView)
        super().__init__(parent=parent)
        self.mTableView: SpecMixParameterTableView = tableView

    def sortFilterProxyModel(self) -> QSortFilterProxyModel:
        return self.mTableView.model()

    def model(self) -> SpecMixParameterModel:
        return self.sortFilterProxyModel().sourceModel()

    def setItemDelegates(self, tableView: QTableView):
        model = self.model()

        handled = [model.cnWeight]

        for col in range(self.sortFilterProxyModel().columnCount()):
            name: str = self.sortFilterProxyModel().headerData(col, Qt.Horizontal, Qt.DisplayRole)
            if name in handled:
                self.mTableView.setItemDelegateForColumn(col, self)

    def createEditor(self, parent, option, index):
        w = None
        if index.isValid():
            w = SpecMixSliderWidget(parent)
            w.setDecimals(2)
            w.setMaximum(10)


        return w

    def setEditorData(self, editor, index: QModelIndex):

        if index.isValid():
            if isinstance(editor, SpecMixSliderWidget):
                editor.setValue(index.data())

    def setModelData(self, w: QWidget, model: QAbstractItemModel, index: QModelIndex):

        if index.isValid():
            if isinstance(w, SpecMixSliderWidget):
                value = w.value()
                model.setData(index, value, role=Qt.EditRole)
            s = ""
        else:
            raise NotImplementedError()


class SpecMixPlotWidget(SpectralLibraryPlotWidget):

    def __init__(self, *args, **kwds):


        super().__init__(*args, **kwds)

        self.parameter_model : SpecMixParameterModel = None
        self.mPDI_Avg: SpectralProfilePlotDataItem = SpectralProfilePlotDataItem(SpectralProfile())
        self.mPDI_Dev: SpectralProfilePlotDataItem = SpectralProfilePlotDataItem(SpectralProfile())
        self.mPDI_Avg.mProfile.setId(-9999)
        self.mPDI_Dev.mProfile.setId(-9998)

        self.mPlotOverlayItems.extend([self.mPDI_Dev, self.mPDI_Avg])

    def profileIDsToVisualize(self):

        ids = super().profileIDsToVisualize()
        ids.insert(0, self.mPDI_Avg.mProfile.id())
        ids.insert(0, self.mPDI_Dev.mProfile.id())
        return ids

    def setParameterModel(self, model:SpecMixParameterModel):

        if model == self.parameter_model:
            return

        if isinstance(self.parameter_model, SpecMixParameterModel):
            # unregister signals
            try:
                pass
            finally:
                self.parameter_model = None

        if isinstance(model, SpecMixParameterModel):
            # register signals
            self.parameter_model = model
            self.setSpeclib(model.speclib())
            self.parameter_model.rowsInserted.connect(self.update_mixed_profiles)
            self.parameter_model.rowsRemoved.connect(self.update_mixed_profiles)
            self.parameter_model.dataChanged.connect(self.update_mixed_profiles)

    def update_mixed_profiles(self):

        pWAvg, pStdDev = self.parameter_model.calculateMixedProfiles()

        if isinstance(pWAvg, SpectralProfile):
            self.mPDI_Avg.initProfile(pWAvg)
            self.mPDI_Dev.initProfile(pStdDev)



class SpecMixWidget(QWidget):

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)

        loadUi(APP_DIR / 'specmix.ui', self)

        self.mSpeclibModel: SpectralLibraryListModel = SpectralLibraryListModel()
        self.cbSourceLibrary: QComboBox
        self.cbSourceLibrary.setModel(self.mSpeclibModel)
        self.cbSourceLibrary.setMaxCount(10)
        self.cbSourceLibrary.currentIndexChanged.connect(self.onSelectedSpeclibChanged)

        self.tableView: SpecMixParameterTableView
        self.m_profile_source_library: SpectralLibrary = None

        self.mParameterModel = SpecMixParameterModel()
        self.mProxyModel = QSortFilterProxyModel() # SpecMixParameterProxyModel()
        self.mProxyModel.setSourceModel(self.mParameterModel)
        self.tableView.setModel(self.mProxyModel)
        self.tableView.selectionModel().selectionChanged.connect(self.updateButtons)
        self.mViewDelegate = SpecMixParameterViewDelegate(self.tableView)
        self.mViewDelegate.setItemDelegates(self.tableView)

        self.sbProfileLimit: QSpinBox
        self.sbProfileLimit.setValue(self.mParameterModel.profileLimit())
        self.sbProfileLimit.valueChanged.connect(self.mParameterModel.setProfileLimit)
        self.mParameterModel.sigProfileLimitChanged.connect(self.sbProfileLimit.setValue)

        self.cbSyncWithSelection.toggled.connect(self.onSyncWithSelectionToggled)

        self.btnAddProfiles.setDefaultAction(self.actionAddSelectedSourceProfiles)
        self.btnRemoveProfiles.setDefaultAction(self.actionRemoveSelectedSourceProfiles)
        self.actionAddSelectedSourceProfiles.triggered.connect(self.addSelectedSourceProfiles)
        self.actionRemoveSelectedSourceProfiles.triggered.connect(self.removeSelectedSourceProfiles)

        self.cbShowSourceProfiles.setChecked(True)
        self.cbShowMixedProfiles.setChecked(True)
        self.cbShowDeviations.setChecked(True)


        self.plotWidget: SpecMixPlotWidget
        self.plotWidget.setParameterModel(self.mParameterModel)

        self.updateButtons()

    def onSyncWithSelectionToggled(self, b: bool):
        self.updateButtons()
        if b is True:
            self.syncWithSelectedSourceProfiles()



    def addSelectedSourceProfiles(self, *args):
        speclib = self.selectedSpeclib()
        if isinstance(speclib, SpectralLibrary):
            profiles = list(speclib.profiles(speclib.selectedFeatureIds()))
            self.mParameterModel.addProfiles(profiles)

    def removeSelectedSourceProfiles(self, *args):

        rows = self.tableView.selectionModel().selectedRows()
        ofids = []
        for idx in rows:
            ofids.append(idx.data(Qt.UserRole).attribute(SpecMixParameterModel.SL_OFID))

        self.mParameterModel.removeProfiles(ofids)

    def onSelectedSpeclibChanged(self, index: int):
        lastSpeclib: SpectralLibrary = self.m_profile_source_library
        speclib = self.cbSourceLibrary.currentData(role=Qt.UserRole)

        if isinstance(lastSpeclib, SpectralLibrary):
            # unregister signals
            try:
                lastSpeclib.selectionChanged.disconnect(self.onSourceSpeclibSelectionChanged)
            finally:
                self.m_profile_source_library = None

        if isinstance(speclib, SpectralLibrary):
            # register signals
            speclib.selectionChanged.connect(self.onSourceSpeclibSelectionChanged)
            self.m_profile_source_library = speclib
        self.updateButtons()

    def onSourceSpeclibSelectionChanged(self, selected, deselected, clearAndSelect:bool):
        if self.manualHandling():
            self.updateButtons()
        else:
            self.syncWithSelectedSourceProfiles()

    def syncWithSelectedSourceProfiles(self):

        speclib = self.selectedSpeclib()
        if isinstance(speclib, SpectralLibrary):
            requiredFIDs = speclib.selectedFeatureIds()
            ofids = self.mParameterModel.originalFeatureIds()

            to_remove = [f for f in ofids if f not in requiredFIDs]
            to_add = [f for f in requiredFIDs if f not in ofids]

            to_add = list(speclib.profiles(to_add))
            self.mParameterModel.removeProfiles(to_remove)
            self.mParameterModel.addProfiles(to_add)
        else:
            self.mParameterModel.removeProfiles(self.mParameterModel.mSpeclib)


    def selectedSpeclib(self) -> SpectralLibrary:
        return self.cbSourceLibrary.currentData(role=Qt.UserRole)

    def selectSpeclib(self, speclib: SpectralLibrary):
        self.mSpeclibModel.addSpectralLibraries(speclib)
        m = self.cbSourceLibrary.model()
        for row in range(len(self.mSpeclibModel)):
            idx = m.createIndex(row, 0)
            slib = m.data(idx, role=Qt.UserRole)
            if slib == speclib:
                self.cbSourceLibrary.setCurrentIndex(row)
                break

    def addSpectralLibraries(self, speclibs):
        n = len(self.mSpeclibModel)
        self.mSpeclibModel.addSpectralLibraries(speclibs)

        if n == 0 and len(self.mSpeclibModel) > 0:
            self.selectSpeclib(self.mSpeclibModel[0])

    def manualHandling(self) -> bool:
        return not self.cbSyncWithSelection.isChecked()

    def updateButtons(self, *args):

        if isinstance(self.selectedSpeclib(), SpectralLibrary):
            self.cbSyncWithSelection.setEnabled(True)
            is_manual = self.manualHandling()

            has_selectedSpeclibProfiles = self.selectedSpeclib().selectedFeatureCount() > 0
            has_selectedSourceProfiles = len(self.tableView.selectionModel().selectedRows()) > 0
            self.actionAddSelectedSourceProfiles.setEnabled(is_manual and has_selectedSpeclibProfiles)
            self.actionRemoveSelectedSourceProfiles.setEnabled(is_manual and has_selectedSourceProfiles)
        else:
            self.cbSyncWithSelection.setEnabled(False)
            self.actionAddSelectedSourceProfiles.setEnabled(False)
            self.actionRemoveSelectedSourceProfiles.setEnabled(False)
