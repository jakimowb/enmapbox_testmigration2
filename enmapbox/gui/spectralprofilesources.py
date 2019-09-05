
import os, sys, typing, collections, enum
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from enmapbox.gui import *





class SpectralProfileSourceListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """
    def __init__(self, *args, **kwds):
        super(SpectralProfileSourceListModel, self).__init__(*args, **kwds)

        self.mSources = []

    def __len__(self)->int:
        return len(self.mSources)

    def __iter__(self):
        return iter(self.mSources)

    def __getitem__(self, slice):
        return self.mSources[slice]

    def sources(self)->list:
        return self[:]

    def addSource(self, source)->typing.Any:
        if source not in self.mSources:
            i = len(self)
            self.beginInsertRows(QModelIndex(), i, i)
            self.mSources.insert(i, source)
            self.endInsertRows()
            return source
        return None

    def sourceModelIndex(self, source)->QModelIndex:
        if source in self.mSources:
            i = self.mSources.index(source)
            return self.createIndex(i, 0, self.mSources[i])
        else:
            return QModelIndex()


    def removeSource(self, source)->typing.Any:
        if source in self.mSources:
            i = self.mSources.index(source)
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mSources.remove(source)
            self.endRemoveRows()
            return source
        return None

    def rowCount(self, parent: QModelIndex = None)->int:
        return len(self)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return 'Raster Source'
        return super(SpectralProfileSourceListModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        source = self.mSources[index.row()]

        sourceName = str(source)
        sourceIcon = QIcon()
        if role == Qt.DisplayRole:
            return sourceName
        elif role == Qt.DecorationRole:
            return sourceIcon
        elif role == Qt.UserRole:
            return source
        return None


class SpectralLibraryListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """
    def __init__(self, *args, **kwds):
        super(SpectralLibraryListModel, self).__init__(*args, **kwds)

        self.mSpeclibs = []

    def __len__(self)->int:
        return len(self.mSpeclibs)

    def __iter__(self):
        return iter(self.mSpeclibs)

    def __getitem__(self, slice):
        return self.mSpeclibs[slice]

    def spectralLibraries(self)->typing.List[SpectralLibrary]:
        return self[:]



    def addSpeclib(self, speclib:SpectralLibrary)->SpectralLibrary:
        assert isinstance(speclib, SpectralLibrary)
        i = self.speclibListIndex(speclib)
        if i is None:
            i = len(self)
            self.beginInsertRows(QModelIndex(), i, i)
            self.mSpeclibs.insert(i, speclib)
            self.endInsertRows()
            return speclib
        return None

    def speclibListIndex(self, speclib:SpectralLibrary)->int:
        for i,  sl in enumerate(self):
            if sl is speclib:
                return i
        return None

    def speclibModelIndex(self, speclib: SpectralLibrary) -> QModelIndex:

        i = self.speclibListIndex(speclib)
        if isinstance(i, int):
            return self.createIndex(i, 0, speclib)
        return QModelIndex()

    def removeSpeclib(self, speclib:SpectralLibrary)->SpectralLibrary:
        i = self.speclibListIndex(speclib)
        if i:
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mSpeclibs.remove(speclib)
            self.endRemoveRows()
            return speclib
        return None

    def rowCount(self, parent: QModelIndex = None)->int:
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
        return super(SpectralLibraryListModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        speclib = self.mSpeclibs[index.row()]
        assert isinstance(speclib, SpectralLibrary)

        if role == Qt.DisplayRole:
            return speclib.name()

        elif role == Qt.ToolTipRole:
            return speclib.source()

        elif role == Qt.DecorationRole:
            return QIcon(r':/qps/ui/icons/speclib.svg')

        elif role == Qt.UserRole:
            return speclib

        return None

class SpectralProfileSamplingMode(enum.Enum):

    SingleProfile=1
    Sample3x3=2
    Sample5x5=3

class SpectralProfileBridgeItem(object):

    def __init__(self, speclib:SpectralLibrary, source, isActive=True, samplingMode:SpectralProfileSamplingMode=SpectralProfileSamplingMode.SingleProfile):

        self.mSpeclib = None
        self.mSource = None
        self.mIsActive = True
        self.mSamplingMode = SpectralProfileSamplingMode.SingleProfile

    def __eq__(self, other):
        if not isinstance(other, SpectralProfileBridgeItem):
            return False
        return self.mSpeclib is other.mSpeclib and self.mSource == other.mSource and self.mSamplingMode == other.mSamplingMode



class SpectralProfileBridge(QAbstractTableModel):


    def __init__(self, *args, **kwds):
        super(SpectralProfileBridge, self).__init__(*args, **kwds)

        self.mSpeclibModel = SpectralLibraryListModel()
        self.mSourceModel = SpectralProfileSourceListModel()
        self.mBridgeItems = []


        self.cnSrc = 'Source'
        self.cnDst = 'Speclib'
        self.cnSampling = 'Sampling'

    def __getitem__(self, slice):
        return self.mBridgeItems[slice]

    def spectralLibraryModel(self)->SpectralLibraryListModel:
        return self.mSpeclibModel

    def dataSourceModel(self)->SpectralProfileSourceListModel:
        return self.mSourceModel

    def columnNames(self)->typing.List[str]:
        return [self.cnSrc, self.cnDst, self.cnSampling]


    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames()[section]

        return super(SpectralProfileBridge, self).headerData(section, orientation, role)

    def flags(self, index: QModelIndex):

        if not index.isValid():
            return Qt.NoItemFlags
        col = index.column()

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        if col == 0:
            flags = flags | Qt.ItemIsUserCheckable

        return flags

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        item = self.mBridgeItems[index.row()]
        assert isinstance(item, SpectralProfileBridgeItem)
        c = index.column()
        cn = self.columnNames()[index.column()]
        if role == Qt.DisplayRole:
            if cn == self.cnSrc:
                return item.mSource
            if cn == self.cnSampling:
                return item.mSamplingMode.name
            if cn == self.cnDst and isinstance(item.mSpeclib, SpectralLibrary):
                return item.mSpeclib.name()

        if role == Qt.CheckStateRole:
            if c == 0:
                return Qt.Checked if item.mIsActive else Qt.Unchecked

        if role == Qt.ToolTipRole:
            if cn == self.cnDst and isinstance(self.cnDst, SpectralLibrary):
                return item.mSpeclib.source()
            if cn == self.cnSampling:
                return 'Sampling mode = {}'.format(item.mSamplingMode.name)

        if role == Qt.UserRole:
            if cn == self.cnSrc:
                return item.mSource
            if cn == self.cnDst:
                return item.mSpeclib
            if cn == self.cnSampling:
                return item.mSamplingMode

        return None


    def setData(self, index: QModelIndex, value: typing.Any, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        item = self.mBridgeItems[index.row()]
        assert isinstance(item, SpectralProfileBridgeItem)
        c = index.column()
        cn = self.columnNames()[c]
        changed = False
        if role == Qt.CheckStateRole and c == 0:
                item.mIsActive = value == Qt.Checked
                changed == True

        if role == Qt.EditRole:
            if cn == self.cnSrc:
                item.mSource = value
                changed = True
            if cn == self.cnDst and isinstance(value, SpectralLibrary):
                item.mSpeclib = value
                changed = True
            if cn == self.cnSampling and isinstance(value, SpectralProfileSamplingMode):
                item.mSamplingMode = value
                changed = True

        if changed:
            self.dataChanged.emit(index, index, [role])
        return changed

    def __len__(self):
        return len(self.mBridgeItems)

    def __iter__(self):
        return iter(self.mBridgeItems)

    def rowCount(self, parent: QModelIndex):
        return len(self.mBridgeItems)

    def columnCount(self, parent: QModelIndex = None):
        return len(self.columnNames())

    def addBridgeItem(self, item:SpectralProfileBridgeItem)->SpectralProfileBridgeItem:
        if item not in self.mBridgeItems:
            
            self.addSpeclib(item.mSpeclib)
            self.addSource(item.mSource)
            
            
            i = len(self)
            self.beginInsertRows(QModelIndex(), i, i)
            self.mBridgeItems.insert(i, item)
            self.endInsertRows()
            return item
        return None

    def removeBridgeItem(self, item:SpectralProfileBridgeItem)->SpectralProfileBridgeItem:

        if item in self.mBridgeItems:

            i = self.mBridgeItems.insert(item)
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mBridgeItems.remove(item)
            self.endRemoveRows()

            return item

        return None

    def bridgeItems(self)->typing.List[SpectralProfileBridgeItem]:
        return self.mBridgeItems[:]

    
    def addSource(self, source):
        self.mSourceModel.addSource(source)
        
    def removeSource(self, source):
        
        self.mSourceModel.removeSource(source)
    
    def addSpeclib(self, speclib:SpectralLibrary):
        sl = self.mSpeclibModel.addSpeclib(speclib)
        if isinstance(sl, SpectralLibrary):
            # add a new bridge item by default
            item = SpectralProfileBridgeItem(sl, '<Selected Raster Layer>')
            self.addBridgeItem(item)

    def removeSpeclib(self, speclib:SpectralLibrary):

        self.mSpeclibModel.removeSpeclib(speclib)



class SpectralProfileBridgeViewDelegate(QStyledItemDelegate):
    """

    """
    def __init__(self, tableView:QTableView, parent=None):
        assert isinstance(tableView, QTableView)
        super(SpectralProfileBridgeViewDelegate, self).__init__(parent=parent)
        self.mTableView = tableView


    def sortFilterProxyModel(self)->QSortFilterProxyModel:
        return self.mTableView.model()

    def bridge(self)->SpectralProfileBridge:
        return self.sortFilterProxyModel().sourceModel()

    def setItemDelegates(self, tableView:QTableView):
        bridge = self.bridge()

        for c in [bridge.cnSrc, bridge.cnDst, bridge.cnSampling]:
            i = bridge.columnNames().index(c)
            tableView.setItemDelegateForColumn(i, self)

    def bridgeColumnName(self, index):
        assert index.isValid()
        model = self.bridge()
        return model.columnNames()[index.column()]

    def createEditor(self, parent, option, index):
        cname = self.bridgeColumnName(index)
        bridge = self.bridge()
        pmodel = self.sortFilterProxyModel()

        w = None
        if index.isValid() and isinstance(bridge, SpectralProfileBridge):

            item = bridge.mBridgeItems[pmodel.mapToSource(index).row()]
            assert isinstance(item,SpectralProfileBridgeItem)

            if cname == bridge.cnSrc:
                w = QComboBox(parent=parent)
                w.setModel(bridge.dataSourceModel())
            if cname == bridge.cnDst:
                w = QComboBox(parent=parent)
                w.setModel(bridge.spectralLibraryModel())
            if cname == bridge.cnSampling:
                w = QComboBox(parent=parent)
                for mode in SpectralProfileSamplingMode:
                    assert isinstance(mode, SpectralProfileSamplingMode)
                    w.addItem(mode.name, mode)

        return w

    def checkData(self, index, w, value):
        assert isinstance(index, QModelIndex)
        bridge = self.bridge()
        if index.isValid() and isinstance(bridge, SpectralProfileBridge):
            #  todo: any checks?
            self.commitData.emit(w)

    def setEditorData(self, editor, proxyIndex):

        bridge = self.bridge()
        index = self.sortFilterProxyModel().mapToSource(proxyIndex)


        if index.isValid() and isinstance(bridge, SpectralProfileBridge):
            cname = bridge.columnNames()[index.column()]
            item = bridge[index.row()]
            assert isinstance(item, SpectralProfileBridgeItem)

            if cname == bridge.cnSrc:
                assert isinstance(editor, QComboBox)
                idx = editor.model().sourceModelIndex(item.mSource)
                if idx.isValid():
                    editor.setCurrentIndex(idx.row())


            elif cname == bridge.cnDst:
                assert isinstance(editor, QComboBox)
                idx = editor.model().speclibModelIndex(item.mSpeclib)
                if idx.isValid():
                    editor.setCurrentIndex(idx.row())

            elif cname == bridge.cnSampling:
                assert isinstance(editor, QComboBox)

                for i in range(editor.count()):
                    if editor.itemData(i, role=Qt.UserRole) == item.mSamplingMode:
                        editor.setCurrentIndex(i)



    def setModelData(self, w, bridge, proxyIndex):
        index = self.sortFilterProxyModel().mapToSource(proxyIndex)
        cname = self.bridgeColumnName(proxyIndex)
        bridge = self.bridge()

        if index.isValid() and isinstance(bridge, SpectralProfileBridge):
            if cname == bridge.cnSrc:
                assert isinstance(w, QComboBox)
                bridge.setData(index, w.currentData(Qt.UserRole), Qt.EditRole)

            elif cname == bridge.cnDst:
                assert isinstance(w, QComboBox)
                bridge.setData(index, w.currentData(Qt.UserRole), Qt.EditRole)

            elif cname == bridge.cnSampling:
                assert isinstance(w, QComboBox)
                bridge.setData(index, w.currentData(Qt.UserRole), Qt.EditRole)

            else:
                raise NotImplementedError()




class SpectralProfileSourcePanel(QgsDockWidget, loadUI('spectralprofilesourcepanel.ui')):


    def __init__(self, *args, **kwds):
        super(SpectralProfileSourcePanel, self).__init__(*args, **kwds)
        self.setupUi(self)

