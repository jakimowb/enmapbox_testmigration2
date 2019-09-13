
import os, sys, typing, collections, enum
import pickle

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import gdal
from enmapbox.gui import *
from enmapbox.gui.datasources import DataSourceRaster
import numpy as np


class SpectralProfileSource(object):

    @staticmethod
    def fromRasterLayer(lyr:QgsRasterLayer):
        return SpectralProfileSource(lyr.source(), lyr.name(), lyr.providerType())

    @staticmethod
    def fromDataSource(dsr:DataSourceRaster):
        return SpectralProfileSource(dsr.uri(), dsr.name(), dsr.provider())

    def __init__(self, uri:str, name:str, provider:str):
        assert len(uri) > 0
        self.mUri = uri
        self.mName = name
        self.mProvider = provider

        self.mLyr = None
    def setName(self, name:str):
        self.mName = name

    def name(self)->str:
        return self.mName

    def toolTip(self)->str:
        return self.mUri

    def rasterLayer(self)->QgsRasterLayer:
        if not isinstance(self.mLyr, QgsRasterLayer):
            loptions = QgsRasterLayer.LayerOptions(loadDefaultStyle=False)
            self.mLyr = QgsRasterLayer(self.mUri, self.mName, self.mProvider, options=loptions)

        return self.mLyr


    def __hash__(self):
        return hash((self.mUri, self.mProvider))

    def __eq__(self, other):
        if not isinstance(other, SpectralProfileSource):
            return False
        return self.mUri == other.mUri and self.mProvider == other.mProvider


class SpectralProfileTopLayerSource(SpectralProfileSource):

    def __init__(self, *args, **kwds):
        super(SpectralProfileTopLayerSource, self).__init__('<toprasterlayer>', '<top raster layer>', None)

        self.mMapLayerSources = []

    def setMapSources(self, sources:typing.List[SpectralProfileSource]):
        self.mMapLayerSources.clear()
        self.mMapLayerSources.extend(sources)

    def mapSources(self)->typing.List[SpectralProfileSource]:
        return self.mMapLayerSources

    def name(self)->str:
        return '<top raster layer>'

    def toolTip(self)->str:
        return 'Reads Spectral Profiles from the top raster layer of a clicked map canvas.'


class SpectralProfileSrcListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """
    def __init__(self, *args, **kwds):
        super(SpectralProfileSrcListModel, self).__init__(*args, **kwds)

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
        return super(SpectralProfileSrcListModel, self).headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        if not index.isValid():
            return None

        source = self.mSources[index.row()]
        assert isinstance(source, SpectralProfileSource)
        if role == Qt.DisplayRole:
            return source.name()
        elif role == Qt.DecorationRole:
            return QIcon(r':/images/themes/default/mIconRaster.svg')
        elif role == Qt.ToolTipRole:
            return source.toolTip()
        elif role == Qt.UserRole:
            return source
        return None


class SpectralProfileDstListModel(QAbstractListModel):
    """
    A list model that list SpectralLibraries
    """
    def __init__(self, *args, **kwds):
        super(SpectralProfileDstListModel, self).__init__(*args, **kwds)

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
        if isinstance(i, int):
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
        return super(SpectralProfileDstListModel, self).headerData(section, orientation, role)

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
            return QIcon(r':/enmapbox/gui/ui/icons/viewlist_spectrumdock.svg')

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

    def __init__(self, src:SpectralProfileSource, dst: SpectralLibraryWidget, isActive=True,
                 samplingMode: SpectralProfileSamplingMode = SpectralProfileSamplingMode.SingleProfile):
        #assert isinstance(slw, SpectralLibraryWidget)

        self.mSrc = None
        self.mDst = None

        self.setSource(src)
        self.setDestination(dst)
        self.mIsActive = isActive
        self.mSamplingMode = samplingMode
        self.mCurrentProfiles = []

    def currentProfiles(self)->typing.List[SpectralProfile]:
        return [p for p in self.mCurrentProfiles if isinstance(p, SpectralProfile)]

    def destination(self)->SpectralLibraryWidget:
        return self.mDst

    def setDestination(self, slw:SpectralLibraryWidget):
        self.mDst = slw

    def setSource(self, src:SpectralProfileSource):
        self.mSrc = src

    def source(self)->SpectralProfileSource:
        return self.mSrc

    def isActive(self)->bool:
        return self.mIsActive

    def setIsActive(self, b:bool):
        assert isinstance(b, bool)
        self.mIsActive = b

    def setSamplingMode(self, mode:SpectralProfileSamplingMode):
        assert isinstance(mode, SpectralProfileSamplingMode)
        self.mSamplingMode = mode

    def samplingMode(self)->typing.Optional[SpectralProfileSamplingMode]:
        return self.mSamplingMode

    def __eq__(self, other):
        if not isinstance(other, SpectralProfileRelation):
            return False
        return self.mDst is other.mDst and self.mSrc == other.mSrc and self.mSamplingMode == other.mSamplingMode

    def isValid(self)->bool:
        return isinstance(self.destination(), SpectralLibraryWidget) \
               and isinstance(self.source(), SpectralProfileSource) \
               and isinstance(self.samplingMode(), SpectralProfileSamplingMode)


class SpectralProfileRelationWrapper(SpectralProfileRelation):


    def __init__(self, r: SpectralProfileRelation):
        super(SpectralProfileRelationWrapper, self).__init__(r.source(), r.destination(),
                                                             isActive=r.isActive(), samplingMode=r.samplingMode())

        self.mSrcID = id(self.mSrc)
        self.mDstID = id(self.mDst)
        self.mDst = None
        #self.mSrc = None

    def __hash__(self):
        return hash((self.mSrcID, self.mDstID, self.mSamplingMode))


    def unwrap(self, relations:typing.List[SpectralProfileRelation])->SpectralProfileRelation:
        key1 = (self.mSrcID, self.mSamplingMode, self.mDstID)
        for r in relations:
            assert isinstance(r, SpectralProfileRelation)
            key2 = (id(r.mSrc), r.mSamplingMode, id(r.mDst))
            if key1 == key2:
                return r

        return None








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

    sigProgress = pyqtSignal(int)


    def __init__(self, *args, **kwds):
        super(SpectralProfileBridge, self).__init__(*args, **kwds)

        self.mDstModel = SpectralProfileDstListModel()
        self.mSrcModel = SpectralProfileSrcListModel()
        self.mBridgeItems = []


        self.cnSrc = 'Source'
        self.cnDst = 'Destination'
        self.cnSampling = 'Sampling'

        self.mTasks = dict()

    def __getitem__(self, slice):
        return self.mBridgeItems[slice]

    def spectralLibraryModel(self)->SpectralProfileDstListModel:
        return self.mDstModel

    def destinations(self)->typing.List[SpectralLibraryWidget]:
        return self.spectralLibraryModel().spectralLibraryWidgets()

    def dataSourceModel(self)->SpectralProfileSrcListModel:
        return self.mSrcModel

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
        dst = item.destination()

        c = index.column()
        cn = self.columnNames()[index.column()]
        if role == Qt.DisplayRole:
            if cn == self.cnSrc and isinstance(src, SpectralProfileSource):
                return src.name()

            if cn == self.cnSampling:
                return item.mSamplingMode.name

            if cn == self.cnDst and isinstance(dst, SpectralLibraryWidget):
                return dst.windowTitle()

        if role == Qt.CheckStateRole:
            if c == 0:
                return Qt.Checked if item.mIsActive else Qt.Unchecked

        if role == Qt.DecorationRole:
            if cn == self.cnDst and isinstance(dst, SpectralLibraryWidget):
                return QIcon(r':/enmapbox/gui/ui/icons/viewlist_spectrumdock.svg')

            if cn == self.cnSrc and isinstance(src, SpectralProfileSource):
                return QIcon(r':/images/themes/default/mIconRaster.svg')

        if role == Qt.ToolTipRole:
            if cn == self.cnDst and isinstance(dst, SpectralLibraryWidget):
                return dst.windowTitle()

            if cn == self.cnSrc and isinstance(src, SpectralProfileSource):
                return src.toolTip()

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
                item.mDst = value
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

        if isinstance(item.destination(), SpectralLibraryWidget):
            self.addDestination(item.destination())

        if isinstance(item.source(), SpectralProfileSource):
            self.addSource(item.source())



        i = len(self)
        self.beginInsertRows(QModelIndex(), i, i)
        self.mBridgeItems.insert(i, item)
        self.endInsertRows()
        return item


    def removeProfileRelation(self, item:SpectralProfileRelation)->SpectralProfileRelation:

        if item in self.mBridgeItems:

            i = self.mBridgeItems.index(item)
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
        self.mSrcModel.addSource(source)

    def removeSource(self, source:SpectralProfileSource):
        
        self.mSrcModel.removeSource(source)

    def sources(self)->typing.List[SpectralProfileSource]:
        return self.mSrcModel[:]

    def addDestination(self, slw:SpectralLibraryWidget):
        assert isinstance(slw, SpectralLibraryWidget)
        _slw = self.mDstModel.addSpectralLibraryWidget(slw)
        if isinstance(_slw, SpectralLibraryWidget):
            # add a new bridge item by default
            #src = SpectralProfileSource(None, None, None)

            if len(self) > 0:
                src = self[-1].source()
            else:
                src = SpectralProfileTopLayerSource()
            item = SpectralProfileRelation(src, _slw)

            self.addProfileRelation(item)

    def removeDestination(self, slw:SpectralLibraryWidget):
        assert isinstance(slw, SpectralLibraryWidget)
        self.mDstModel.removeSpeclib(slw)

    def activeRelations(self, source=None, destination=None)->typing.List[SpectralProfileRelation]:
        relations = [r for r in self.mBridgeItems if isinstance(r, SpectralProfileRelation) and r.isValid()]

        if source:
            relations = [r for r in relations if r.source() == source]
        if destination:
            relations = [r for r in relations if r.destination() == destination]

        return relations

    def onProfilesLoaded(self, exception, result=None)->typing.List[SpectralProfileRelation]:
        """

        :param qgsTask:
        :param point:
        :param relationWrappers:
        :return: list of updates SpectralProfileRelations
        """

        updatedRelations = []
        if isinstance(exception, Exception):
            print(exception, file=sys.stderr)
        else:
            task, point, relationWrappers = result
            # 1: clear current profiles
            for r in self[:]:
                assert isinstance(r, SpectralProfileRelation)
                r.mCurrentProfiles.clear()

            # 2. set current profiles per relation

            for rw in relationWrappers:
                r = rw.unwrap(self.mBridgeItems)
                if isinstance(r, SpectralProfileRelation):
                    r.mCurrentProfiles.extend(rw.currentProfiles())
                    updatedRelations.append(r)

            # 3. update current profiles
            for dst in self.destinations():
                self.updateCurrentProfiles(dst)

            #self.onRemoveTask(task)

        return updatedRelations

    def updateCurrentProfiles(self, dst:SpectralLibraryWidget):
        if isinstance(dst, SpectralLibraryWidget):
            currentProfiles = []
            for r in self[:]:
                if isinstance(r, SpectralProfileRelation) and r.destination() == dst:
                    currentProfiles.extend(r.currentProfiles())
            dst.setCurrentProfiles(currentProfiles)


    def onRemoveTask(self, tid):
        if tid in self.mTasks.keys():
            del self.mTasks[tid]

    def loadProfiles(self, spatialPoint:SpatialPoint, mapCanvas:QgsMapCanvas=None, runAsync:bool=False):
        """
        Loads profiles from sources and sends them to their destinations
        :param spatialPoint: SpatialPoint
        """

        n = len(self)

        self.sigProgress.emit(0)

        # what is the top raster layer?
        if isinstance(mapCanvas, QgsMapCanvas):
            mapRasterLayerSources = [SpectralProfileSource.fromRasterLayer(l) for l in mapCanvas.layers() if isinstance(l, QgsRasterLayer)]
            for src in self.dataSourceModel():
                if isinstance(src, SpectralProfileTopLayerSource):
                    src.setMapSources(mapRasterLayerSources)


        relations = self.activeRelations()

        if not len(relations) > 0:
            return []

        wrappedRelations = [SpectralProfileRelationWrapper(r) for r in relations]

        #dump = pickle.dumps((spatialPoint, relations))
        if runAsync:
            qgsTask = QgsTask.fromFunction('Load Spectral Profiles', doLoadSpectralProfiles, spatialPoint, wrappedRelations, on_finished=self.onProfilesLoaded)
        else:
            qgsTask = QgsTaskMock()

        tid = id(qgsTask)
        qgsTask.progressChanged.connect(lambda v: self.sigProgress.emit(int(v)))
        qgsTask.taskCompleted.connect(lambda *args, tid=tid: self.onRemoveTask(tid))
        qgsTask.taskTerminated.connect(lambda *args, tid=tid: self.onRemoveTask(tid))

        self.mTasks[tid] = qgsTask


        updatedRelations = []
        if runAsync:
            tm = QgsApplication.taskManager()
            assert isinstance(tm, QgsTaskManager)
            tm.addTask(qgsTask)
        else:
            updatedRelations = self.onProfilesLoaded(None, doLoadSpectralProfiles(qgsTask, spatialPoint, wrappedRelations))

        return updatedRelations



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

        self.progressBar.setVisible(False)

        self.mRunAsync = True
        self.mBridge = SpectralProfileBridge()
        self.mBridge.sigProgress.connect(self.progressBar.setValue)
        self.mProxyModel = QSortFilterProxyModel()
        self.mProxyModel.setSourceModel(self.mBridge)
        self.tableView.setModel(self.mProxyModel)
        self.tableView.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.mViewDelegate = SpectralProfileBridgeViewDelegate(self.tableView)
        self.mViewDelegate.setItemDelegates(self.tableView)

        self.btnAddRelation.setDefaultAction(self.actionAddRelation)
        self.btnRemoveRelation.setDefaultAction(self.actionRemoveRelation)

        self.actionAddRelation.triggered.connect(self.createRelation)
        self.actionRemoveRelation.triggered.connect(self.onRemoveRelations)

        self.onSelectionChanged([],[])


    def setRunAsync(self, b:bool):
        self.mRunAsync = b


    def onSelectionChanged(self, selected:QItemSelection, deselected:QItemSelection):
        self.actionRemoveRelation.setEnabled(len(self.tableView.selectionModel().selectedRows()) > 0)

    def onRemoveRelations(self):
        toRemove = []
        for rowIdx in self.tableView.selectionModel().selectedRows():
            assert isinstance(rowIdx, QModelIndex)
            toRemove.append(self.bridge()[rowIdx.row()])

        for item in toRemove:
            self.bridge().removeProfileRelation(item)


    def createRelation(self):
        src = SpectralProfileTopLayerSource()
        dst = None
        if len(self.bridge().spectralLibraryModel()) > 0:
            dst = self.bridge().spectralLibraryModel()[0]
        if len(self.bridge()) > 0:
            lastItem = self.bridge()[-1]
            assert isinstance(lastItem, SpectralProfileRelation)
            dst = lastItem.destination()
            src = lastItem.source()

        relation = SpectralProfileRelation(src, dst)
        self.bridge().addProfileRelation(relation)


    def bridge(self)->SpectralProfileBridge:

        return self.mBridge

    def loadCurrentMapSpectra(self, spatialPoint:SpatialPoint, mapCanvas:QgsMapCanvas=None, runAsync=None):

        if runAsync is None:
            runAsync = self.mRunAsync

        self.bridge().loadProfiles(spatialPoint, mapCanvas=mapCanvas, runAsync=runAsync)

def doLoadSpectralProfiles(task, spatialPoint, relations:typing.List[SpectralProfileRelationWrapper])->typing.Tuple[SpatialPoint, typing.List[SpectralProfileRelationWrapper]]:
    assert isinstance(task, QgsTask)

    #spatialPoint, sourceSamples = pickle.loads(dump)
    assert isinstance(spatialPoint, SpatialPoint)
    assert isinstance(relations, list)

    task.setProgress(0.0)

    if task.isCanceled():
        return None

    LUT_SRC2R = dict()

    for r in relations:
        assert isinstance(r, SpectralProfileRelationWrapper)
        r.mCurrentProfiles.clear()
        src = r.source()
        if src not in LUT_SRC2R.keys():
            LUT_SRC2R[src] = []
        LUT_SRC2R[src].append(r)

    # load source profiles, source by source
    nSources = len(LUT_SRC2R.keys())
    for iSrc, src in enumerate(LUT_SRC2R.keys()):
        assert isinstance(src, SpectralProfileSource)
        if task.isCanceled():
            return None


        lyr = None


        # create raster source layer
        if isinstance(src, SpectralProfileTopLayerSource):
            # in this case find a layer with a valid center pixel
            for potentialSource in src.mapSources():
                potentialLayer = potentialSource.rasterLayer()
                assert isinstance(potentialLayer, QgsRasterLayer)
                pos2 = spatialPoint.toCrs(potentialLayer.crs())
                dp = potentialLayer.dataProvider()
                assert isinstance(dp, QgsRasterDataProvider)
                value, hasValue = dp.sample(pos2, 1)
                if hasValue:
                    lyr = potentialLayer
                    break
        else:
            lyr = src.rasterLayer()

        if not isinstance(lyr, QgsRasterLayer):
            continue
        # read all required pixel positions

        srcPositions = []
        LUT_Rel2Pos = dict()
        LUT_Pos2Profile = dict()
        for r in LUT_SRC2R[src]:
            assert isinstance(r, SpectralProfileRelationWrapper)
            positions = r.samplingMode().profilePositions(lyr, spatialPoint)
            LUT_Rel2Pos[r] = positions
            for pos in positions:
                if pos not in srcPositions:
                    srcPositions.append(pos)

        # load pixel profiles for each srcPosition
        for pos in srcPositions:
            assert isinstance(pos, SpatialPoint)
            profile = SpectralProfile.fromRasterLayer(lyr, pos)
            LUT_Pos2Profile[pos] = profile

        if task.isCanceled():
            return None

        # add profiles to each relation
        for r in LUT_Rel2Pos.keys():
            assert isinstance(r, SpectralProfileRelation)
            profiles = [LUT_Pos2Profile[pos] for pos in LUT_Rel2Pos[r]]

            # aggregate profiles according to the sample mode
            profiles = r.samplingMode().aggregatePositionProfiles(positions, profiles)
            r.mCurrentProfiles = profiles

        if task.isCanceled():
            return None

        task.setProgress(100 * iSrc+1 / nSources)

    return task, spatialPoint, relations

