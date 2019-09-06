
import os, sys, typing, collections, enum
import pickle

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import gdal
from enmapbox.gui import *
import numpy as np


class SpectralProfileSource(object):

    def __init__(self, uri:str, name:str, provider:str):
        self.mUri = uri
        self.mName = name
        self.mProvider = provider

    def setName(self, name:str):
        self.mName = name

    def __eq__(self, other):
        if not isinstance(other, SpectralProfileSource):
            return False
        return self.mUri == other.mUri and self.mProvider == other.mProvider


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

    def addSource(self, source:SpectralProfileSource)->SpectralProfileSource:
        assert isinstance(source, SpectralProfileSource)
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

    def removeSource(self, source:SpectralProfileSource)->SpectralProfileSource:
        assert isinstance(source, SpectralProfileSource)
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
        flags = Qt.ItemIsEnabled |  Qt.ItemIsSelectable
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
        assert isinstance(source, SpectralProfileSource)
        if role == Qt.DisplayRole:
            return source.mName
        elif role == Qt.DecorationRole:
            return QIcon(r':/images/themes/default/mIconRaster.svg')
        elif role == Qt.ToolTipRole:
            return source.mUri
        elif role == Qt.UserRole:
            return source
        return None


class SpectralLibraryWidgetListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """
    def __init__(self, *args, **kwds):
        super(SpectralLibraryWidgetListModel, self).__init__(*args, **kwds)

        self.mSLWs = []

    def __len__(self)->int:
        return len(self.mSLWs)

    def __iter__(self):
        return iter(self.mSLWs)

    def __getitem__(self, slice):
        return self.mSLWs[slice]

    def spectralLibraryWidgets(self)->typing.List[SpectralLibraryWidget]:
        return self[:]



    def addSpectralLibraryWidget(self, slw:SpectralLibraryWidget)->SpectralLibraryWidget:
        assert isinstance(slw, SpectralLibraryWidget)
        i = self.speclibListIndex(slw)
        if i is None:
            i = len(self)
            self.beginInsertRows(QModelIndex(), i, i)
            self.mSLWs.insert(i, slw)
            self.endInsertRows()
            return slw
        return None

    def speclibListIndex(self, speclib:SpectralLibraryWidget)->int:
        for i,  sl in enumerate(self):
            if sl is speclib:
                return i
        return None

    def speclibModelIndex(self, speclib: SpectralLibraryWidget) -> QModelIndex:

        i = self.speclibListIndex(speclib)
        if isinstance(i, int):
            return self.createIndex(i, 0, speclib)
        return QModelIndex()

    def removeSpeclib(self, slw:SpectralLibraryWidget)->SpectralLibraryWidget:
        i = self.speclibListIndex(slw)
        if i:
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mSLWs.remove(slw)
            self.endRemoveRows()
            return slw
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
        return super(SpectralLibraryWidgetListModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        slw = self.mSLWs[index.row()]
        assert isinstance(slw, SpectralLibraryWidget)

        if role == Qt.DisplayRole:
            return slw.windowTitle()

        elif role == Qt.ToolTipRole:
            return slw.windowTitle()

        elif role == Qt.DecorationRole:
            return QIcon(r':/qps/ui/icons/speclib.svg')

        elif role == Qt.UserRole:
            return slw

        return None

class SpectralProfileSamplingMode(enum.Enum):

    SingleProfile=1
    Sample3x3=2
    Sample5x5=3
    Sample3x3Mean=4
    Sample5x5Mean=5


    def profilePositions(self, lyr:QgsRasterLayer, spatialPoint:SpatialPoint)->typing.List[SpatialPoint]:
        """
        Returns the positions to sample from in source CRS
        :param source:
        :param spatialPoint:
        :return:
        """
        assert isinstance(lyr, QgsRasterLayer)
        spatialPoint = spatialPoint.toCrs(lyr.crs())
        dx = lyr.rasterUnitsPerPixelX()
        dy = lyr.rasterUnitsPerPixelY()
        cx = spatialPoint.x()
        cy = spatialPoint.y()
        results = []

        if self == SpectralProfileSamplingMode.SingleProfile:
            results.append(spatialPoint)

        elif self in [SpectralProfileSamplingMode.Sample3x3,
                      SpectralProfileSamplingMode.Sample3x3Mean]:
            for x in np.linspace(cx-dx,cx+dx,3):
                for y in np.linspace(cy+dy, cy-dy, 3):
                    results.append(SpatialPoint(spatialPoint.crs(), x, y))
            s = ""

        elif self in [SpectralProfileSamplingMode.Sample5x5,
                      SpectralProfileSamplingMode.Sample5x5Mean]:
            for x in np.linspace(cx-dx,cx+dx,5):
                for y in np.linspace(cy+dy, cy-dy, 5):
                    results.append(SpatialPoint(spatialPoint.crs(), x, y))
            s = ""
        return results

    def aggregatePositionProfiles(self, positions:typing.List[SpatialPoint], profiles:typing.List[SpectralProfile])->typing.List[SpectralProfile]:
        """
        This functions aggregates the Spectral Profiles extracted for the sampled positions
        :param positions:
        :param profiles:
        :return:
        """

        if len(profiles) == 0:
            return []
        if len(profiles) == 1:
            return profiles

        if self in [SpectralProfileSamplingMode.Sample3x3Mean, SpectralProfileSamplingMode.Sample5x5Mean]:
            xValues = None
            yValues = None

            n = len(profiles)

            for i, p in enumerate(profiles):
                if i == 0:
                    xValues = np.asarray(p.xValues())
                    yValues = np.asarray(p.yValues())
                else:
                    xValues = np.nansum([xValues, np.asarray(p.xValues())], axis=0)
                    yValues = np.nansum([yValues, np.asarray(p.yValues())], axis=0)

            xValues = xValues / n
            yValues = yValues / n

            p = profiles[0]
            p.setValues(xValues, yValues)
            profiles = [p]

        return profiles

class SpectralProfileRelation(object):

    def __init__(self, slw:SpectralLibraryWidget, src, isActive=True, samplingMode:SpectralProfileSamplingMode=SpectralProfileSamplingMode.SingleProfile):
        assert isinstance(slw, SpectralLibraryWidget)

        self.mSlw = slw
        self.mSrc = src
        self.mIsActive = isActive
        self.mSamplingMode = samplingMode

        self.mCurrentProfiles = []

    def currentProfiles(self)->typing.List[SpectralProfile]:
        return self.mCurrentProfiles

    def destination(self)->SpectralLibraryWidget:
        return self.mSlw

    def source(self)->SpectralProfileSource:
        return self.mSrc

    def samplingMode(self)->typing.Optional[SpectralProfileSamplingMode]:
        return self.mSamplingMode

    def __eq__(self, other):
        if not isinstance(other, SpectralProfileRelation):
            return False
        return self.mSlw is other.mSlw and self.mSrc == other.mSrc and self.mSamplingMode == other.mSamplingMode

    def isValid(self)->bool:
        return isinstance(self.destination(), SpectralLibraryWidget) \
               and isinstance(self.source(), SpectralProfileSource) \
               and isinstance(self.samplingMode(), SpectralProfileSamplingMode)


class SpectralProfileSourceSample(object):


    def __init__(self, uri:str, name:str, providerType:str, mode:SpectralProfileSamplingMode):

        self.mUri = uri
        self.mName = name
        self.mProviderType = providerType
        self.mMode = mode

        self.mProfile = []

    def profiles(self)->typing.List[SpectralProfile]:
        return self.mProfiles

    def samplingMode(self)->SpectralProfileSamplingMode:
        return self.mMode

    def source(self)->typing.Tuple[str, str, str]:
        return (self.mUri, self.mName, self.mProviderType)



class SpectralProfileBridge(QAbstractTableModel):

    sigProgress = pyqtSignal(int, int)

    def __init__(self, *args, **kwds):
        super(SpectralProfileBridge, self).__init__(*args, **kwds)

        self.mSpeclibModel = SpectralLibraryWidgetListModel()
        self.mSourceModel = SpectralProfileSourceListModel()
        self.mBridgeItems = []


        self.cnSrc = 'Source'
        self.cnDst = 'Destination'
        self.cnSampling = 'Sampling'

        self.mTasks = dict()

    def __getitem__(self, slice):
        return self.mBridgeItems[slice]

    def spectralLibraryModel(self)->SpectralLibraryWidgetListModel:
        return self.mSpeclibModel

    def dataSourceModel(self)->SpectralProfileSourceListModel:
        return self.mSourceModel

    def columnNames(self)->typing.List[str]:
        return [self.cnSrc, self.cnSampling, self.cnDst]

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
        assert isinstance(item, SpectralProfileRelation)

        src = item.source()
        slw = item.destination()

        c = index.column()
        cn = self.columnNames()[index.column()]
        if role == Qt.DisplayRole:
            if cn == self.cnSrc:
                return src.mName

            if cn == self.cnSampling:
                return item.mSamplingMode.name

            if cn == self.cnDst:
                return slw.windowTitle()

        if role == Qt.CheckStateRole:
            if c == 0:
                return Qt.Checked if item.mIsActive else Qt.Unchecked

        if role == Qt.DecorationRole:
            if cn == self.cnDst:
                return QIcon(r':/qps/ui/icons/speclib.svg')

            if cn == self.cnSrc:
                return QIcon(r':/images/themes/default/mIconRaster.svg')

        if role == Qt.ToolTipRole:
            if cn == self.cnDst:
                return slw.windowTitle()

            if cn == self.cnSrc:
                return src.mUri

            if cn == self.cnSampling:
                return 'Sampling mode = {}'.format(item.samplingMode().name)

        if role == Qt.UserRole:
            if cn == self.cnSrc:
                return item.source()
            if cn == self.cnDst:
                return item.destination()
            if cn == self.cnSampling:
                return item.samplingMode()

        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        item = self.mBridgeItems[index.row()]
        assert isinstance(item, SpectralProfileRelation)
        c = index.column()
        cn = self.columnNames()[c]
        changed = False
        if role == Qt.CheckStateRole and c == 0:
                item.mIsActive = value == Qt.Checked
                changed == True

        if role == Qt.EditRole:
            if cn == self.cnSrc and isinstance(value, SpectralProfileSource):
                item.mSrc = value
                changed = True
            if cn == self.cnDst and isinstance(value, SpectralLibraryWidget):
                item.mSlw = value
                changed = True
            if cn == self.cnSampling and isinstance(value, SpectralProfileSamplingMode):
                item.mSamplingMode = value
                changed = True

        if changed:
            self.dataChanged.emit(index, index, [role])
        return changed

    def __len__(self)->int:
        return len(self.mBridgeItems)

    def __iter__(self)->typing.Iterable[SpectralProfileRelation]:
        return iter(self.mBridgeItems)

    def rowCount(self, parent: QModelIndex):
        return len(self.mBridgeItems)

    def columnCount(self, parent: QModelIndex = None):
        return len(self.columnNames())

    def addProfileRelation(self, item:SpectralProfileRelation)->SpectralProfileRelation:
        assert isinstance(item, SpectralProfileRelation)

        self.addSpectralLibraryWidget(item.destination())
        self.addSource(item.source())



        i = len(self)
        self.beginInsertRows(QModelIndex(), i, i)
        self.mBridgeItems.insert(i, item)
        self.endInsertRows()
        return item


    def removeBridgeItem(self, item:SpectralProfileRelation)->SpectralProfileRelation:

        if item in self.mBridgeItems:

            i = self.mBridgeItems.insert(item)
            self.beginRemoveRows(QModelIndex(), i, i)
            self.mBridgeItems.remove(item)
            self.endRemoveRows()

            return item

        return None

    def bridgeItems(self)->typing.List[SpectralProfileRelation]:
        return self.mBridgeItems[:]

    def addRasterLayer(self, layer:QgsRasterLayer):
        if layer.isValid():
            source = SpectralProfileSource(layer.source(), layer.name(), layer.providerType())
            layer.nameChanged.connect(lambda *args, lyr=layer, src=source : src.setName(lyr.name()))
            self.addSource(source)

    def addSource(self, source:SpectralProfileSource):
        self.mSourceModel.addSource(source)
        
    def removeSource(self, source:SpectralProfileSource):
        
        self.mSourceModel.removeSource(source)
    
    def addSpectralLibraryWidget(self, slw:SpectralLibraryWidget):
        assert isinstance(slw, SpectralLibraryWidget)
        _slw = self.mSpeclibModel.addSpectralLibraryWidget(slw)
        if isinstance(_slw, SpectralLibraryWidget):
            # add a new bridge item by default
            src = SpectralProfileSource(None, None, None)
            item = SpectralProfileRelation(_slw, src)

            self.addProfileRelation(item)

    def removeSpectralLibraryWidget(self, slw:SpectralLibraryWidget):
        assert isinstance(slw, SpectralLibraryWidget)
        self.mSpeclibModel.removeSpeclib(slw)

    def activeRelations(self, source=None, destination=None)->typing.List[SpectralProfileRelation]:
        relations = [r for r in self.mBridgeItems if isinstance(r, SpectralProfileRelation) and r.isValid()]

        if source:
            relations = [r for r in relations if r.source() == source]
        if destination:
            relations = [r for r in relations if r.destination() == destination]

        return relations

    def onProfilesLoaded(self, qgsTask, results):

        s = ""

    def onRemoveTask(self, tid):
        if tid in self.mTasks.keys():
            del self.mTasks[tid]

    def loadProfiles(self, spatialPoint:SpatialPoint, runAsync:bool=False):
        """
        Loads profiles from sources and sends them to their destinations
        :param spatialPoint: SpatialPoint
        """

        n = len(self)

        self.sigProgress.emit(0, n)

        relations = self.activeRelations()
        runAsync = False
        dump = pickle.dumps((spatialPoint, relations))
        if runAsync:
            qgsTask = QgsTask.fromFunction('Load Spectral Profiles', doLoadSpectralProfiles, dump, on_finished=self.onProfilesLoaded)
        else:
            qgsTask = QgsTaskMock()

        tid = id(qgsTask)
        qgsTask.progressChanged.connect(self.onLoadingProgressChanged)
        qgsTask.taskCompleted.connect(lambda *args, tid=tid: self.onRemoveTask(tid))
        qgsTask.taskTerminated.connect(lambda *args, tid=tid: self.onRemoveTask(tid))

        self.mTasks[tid] = qgsTask

        if runAsync:
            tm = QgsApplication.taskManager()
            assert isinstance(tm, QgsTaskManager)
            tm.addTask(qgsTask)
        else:
            return self.onProfilesLoaded(qgsTask, doLoadSpectralProfiles(qgsTask, dump))


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
            assert isinstance(item, SpectralProfileRelation)

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
            assert isinstance(item, SpectralProfileRelation)

            if cname == bridge.cnSrc:
                assert isinstance(editor, QComboBox)
                idx = editor.model().sourceModelIndex(item.source())
                if idx.isValid():
                    editor.setCurrentIndex(idx.row())


            elif cname == bridge.cnDst:
                assert isinstance(editor, QComboBox)
                idx = editor.model().speclibModelIndex(item.destination())
                if idx.isValid():
                    editor.setCurrentIndex(idx.row())

            elif cname == bridge.cnSampling:
                assert isinstance(editor, QComboBox)

                for i in range(editor.count()):
                    if editor.itemData(i, role=Qt.UserRole) == item.samplingMode():
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

        self.mBridge = SpectralProfileBridge()

        self.mProxyModel = QSortFilterProxyModel()
        self.mProxyModel.setSourceModel(self.mBridge)
        self.tableView.setModel(self.mProxyModel)

        self.mViewDelegate = SpectralProfileBridgeViewDelegate(self.tableView)
        self.mViewDelegate.setItemDelegates(self.tableView)

        self.btnAddRelation.setDefaultAction(self.actionAddRelation)
        self.btnRemoveRelation.setDefaultAction(self.actionRemoveRelation)

        self.actionAddRelation.triggered.connect(self.createRelation)

    def createRelation(self):
        src = None
        dst = None
        if len(self.bridge()) > 0:
            lastItem = self.bridge()[-1]
            assert isinstance(lastItem, SpectralProfileRelation)
            dst = lastItem.destination()
            src = lastItem.source()

        relation = SpectralProfileRelation(dst, src)
        self.bridge().addProfileRelation(relation)


    def bridge(self)->SpectralProfileBridge:

        return self.mBridge




def doLoadSpectralProfiles(task, dump):
    assert isinstance(task, QgsTask)

    spatialPoint, sourceSamples = pickle.loads(dump)
    assert isinstance(spatialPoint, SpatialPoint)
    assert isinstance(sourceSamples, list)

    uniqueSrc = dict()

    task.setProgress(0.0)

    srcDefinitions = []
    for srcSample in sourceSamples:
        assert isinstance(srcSample, SpectralProfileSourceSample)
        srcDef = srcSample.source()
        if srcDef not in srcDefinitions:
            srcDefinitions.append(srcDef)

    # load source profiles, source by source
    for srcDef in srcDefinitions:

        # create raster source layer
        uri, name, providerType = srcDef
        loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
        lyr = QgsRasterLayer(uri, name, providerType, options=loptions)

        srcSamples = [s for s in sourceSamples if isinstance(s, SpectralProfileSourceSample) and s.source() == srcDef]

        srcPositions = []
        LUT_R2Pos = dict()
        LUT_Pos2Profile = dict()

        for srcSample in srcSamples:
            assert isinstance(srcSample, SpectralProfileSourceSample)
            positions = srcSample.samplingMode().profilePositions(lyr, spatialPoint)
            LUT_R2Pos[srcSample] = positions
            for pos in positions:
                if pos not in srcPositions:
                    srcPositions.append(pos)

        # load pixel profiles for each srcPosition
        for pos in srcPositions:
            assert isinstance(pos, SpatialPoint)
            profile = SpectralProfile.fromRasterLayer(lyr, pos)
            LUT_Pos2Profile[pos] = profile


        # add profiles to each relation
        for srcSample in sourceSamples:
            assert isinstance(srcSample, SpectralProfileSourceSample)
            profiles = [LUT_Pos2Profile[pos] for pos in LUT_R2Pos[srcSample]]
            # aggregate profiles according to the sample mode
            profiles = srcSample.samplingMode().aggregatePositionProfiles(positions, profiles)
            srcSample.mProfiles = profiles

    return pickle.dumps(sourceSamples)

