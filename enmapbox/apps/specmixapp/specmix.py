import typing
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from enmapbox.externals.qps.speclib.core import SpectralLibrary, SpectralProfile
from enmapbox.externals.qps.speclib.gui import SpectralLibraryPlotWidget
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

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.mProfiles: typing.List[SpectralProfile] = []
        self.mProfileWeights: typing.Dict[int, float] = dict()
        self.mNormalizedWeights: typing.Dict[int, float] = dict()
        self.mDefaultWeight: float = 1.0
        self.mProfileLimit: int = 100

        self.cnProfile: str = 'Profile'
        self.cnWeight: str = 'Weight'
        self.cnNWeights: str = 'N.Weights'

        self.mColumnNames: typing.List[str] = [self.cnProfile, self.cnWeight]
        self.mColumnToolTips = [
            'Spectral Profile Name',
            'Weights',
            'Normalized Weights (sum = 1.0)'
        ]

    def updateNormalizedWeights(self):
        ids = self.profileIds()
        weights = np.asarray([self.mProfileWeights.get(id, 1) for id in ids])
        nweights = weights / weights.sum()
        self.mNormalizedWeights.clear()
        for i, id in ids:
            self.mNormalizedWeights[id] = float(nweights[i])

    def profileIds(self) -> typing.List[int]:
        return [f.id() for f in self.mProfiles]

    def setProfileLimit(self, limit: int):
        assert limit >= 0
        if limit != self.mProfileLimit:
            self.mProfileLimit = limit
            self.sigProfileLimitChanged.emit(limit)

    def profileLimit(self) -> int:
        return self.mProfileLimit

    def addProfiles(self, profiles: typing.List[SpectralProfile]):
        if not isinstance(profiles, list):
            profiles = [profiles]

        for p in profiles:
            assert isinstance(p, SpectralProfile)

        n = len(profiles)
        if n > 0:
            i = len(self.mProfiles)
            self.beginInsertRows(QModelIndex(), i, i+n-1)
            self.mProfiles.extend(profiles)
            self.endInsertRows()

    def removeProfiles(self, profiles: typing.List[SpectralProfile]):

        for p in profiles:
            assert isinstance(p, SpectralProfile) and p in self.mProfiles
            i = self.mProfiles.index(p)
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mProfiles.pop(i)
            self.endInsertRows()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.mProfiles)

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

        profile: SpectralProfile = self.mProfiles[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return profile.name()
            if index.column() == 1:
                return float(self.mProfileWeights.get(profile.id(), self.mDefaultWeight))

        if role == Qt.EditRole:
            if index.column() == 1:
                return self.mProfileWeights[profile.id()]

    def setData(self, index: QModelIndex, value, role=None):

        profile: SpectralProfile = self.mProfiles[index.row()]
        changed = False
        if index.column() == 1: # set weight
            self.mProfileWeights[profile.id()] = float(value)
            changed = True

        if changed:
            self.dataChanged.emit(index, role=role)


class SpecMixParameterProxyModel(QAbstractProxyModel):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


class SpecMixParameterTableView(QTableView):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)


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
            s = ""
        return w

    def setEditorData(self, editor, index: QModelIndex):

        if index.isValid():
            pass

    def setModelData(self, w, bridge, proxyIndex):
        index = self.sortFilterProxyModel().mapToSource(proxyIndex)
        cname = self.bridgeColumnName(proxyIndex)
        bridge = self.bridge()

        if index.isValid():
            s = ""
        else:
            raise NotImplementedError()


class SpecMixPlotWidget(SpectralLibraryPlotWidget):

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)


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
        self.mSelectedSpeclib : SpectralLibrary = None
        self.mParameterModel = SpecMixParameterModel()
        self.mProxyModel = QSortFilterProxyModel() # SpecMixParameterProxyModel()
        self.mProxyModel.setSourceModel(self.mParameterModel)
        self.tableView.setModel(self.mProxyModel)

        self.mViewDelegate = SpecMixParameterViewDelegate(self.tableView)
        self.mViewDelegate.setItemDelegates(self.tableView)

        self.sbProfileLimit: QSpinBox
        self.sbProfileLimit.setValue(self.mParameterModel.profileLimit())
        self.sbProfileLimit.valueChanged.connect(self.mParameterModel.setProfileLimit)
        self.mParameterModel.sigProfileLimitChanged.connect(self.sbProfileLimit.setValue)

        self.cbSyncWithSelection.toggled.connect(self.updateButtons)

        self.btnAddProfiles.setDefaultAction(self.actionAddSelectedSourceProfiles)
        self.btnRemoveProfiles.setDefaultAction(self.actionRemoveSelectedSourceProfiles)
        self.actionAddSelectedSourceProfiles.triggered.connect(self.addSelectedSourceProfiles)
        self.actionRemoveSelectedSourceProfiles.triggered.connect(self.removeSelectedSourceProfiles)
        self.updateButtons()

    def addSelectedSourceProfiles(self, *args):
        speclib = self.selectedSpeclib()
        if isinstance(speclib, SpectralLibrary):
            profiles = list(speclib.profiles(speclib.selectedFeatureIds()))
            self.mParameterModel.addProfiles(profiles)

    def removeSelectedSourceProfiles(self, *args):

        rows = self.tableView.selectionModel().selectedRows()
        profiles = []
        for idx in rows:

            profiles.append(idx.data(Qt.UserRole))

        self.mParameterModel.removeProfiles(profiles)

    def onSelectedSpeclibChanged(self, index: int):
        lastSpeclib: SpectralLibrary = self.mSelectedSpeclib
        speclib = self.cbSourceLibrary.currentData(role=Qt.UserRole)

        if isinstance(lastSpeclib, SpectralLibrary):
            # unregister signals
            speclib.selectionChanged.disconnect(self.onSourceSpeclibSelectionChanged)

        if isinstance(speclib, SpectralLibrary):
            # register signals
            speclib.selectionChanged.connect(self.onSourceSpeclibSelectionChanged)

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
            existingFIDs = self.mParameterModel.profileIds()

            to_remove = [f for f in existingFIDs if f not in requiredFIDs]
            to_add = [f for f in requiredFIDs if f not in existingFIDs]

            to_remove = [p for p in self.mParameterModel.mProfiles if p.id() in to_remove]
            to_add = list(speclib.profiles(to_add))
            self.mParameterModel.removeProfiles(to_remove)
            self.mParameterModel.addProfiles(to_add)
        else:
            self.mParameterModel.removeProfiles(self.mParameterModel.mProfiles)


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
