import json
import pickle

from qgis._core import QgsDataItem, QgsLayerItem, QgsCoordinateReferenceSystem, QgsMapLayer, QgsUnitTypes, \
    QgsMapLayerType, QgsVectorLayer, QgsRasterLayer, Qgis

from enmapbox import messageLog, debugLog
from ...externals.qps.models import TreeNode, PyObjectTreeNode
from ...externals.qps.utils import SpatialExtent, parseWavelength
from ...externals.qps.speclib.core import is_spectral_library
from .metadata import CRSLayerTreeNode, RasterBandTreeNode, DataSourceSizesTreeNode

from qgis.core import QgsDataItem, QgsLayerItem, QgsMapLayer, QgsRasterLayer



def dataItemToLayer(dataItem: QgsDataItem) -> QgsMapLayer:
    lyr = None
    if isinstance(dataItem, QgsLayerItem):

        if dataItem.mapLayerType() == QgsMapLayerType.VectorLayer:
            lyr = QgsVectorLayer(dataItem.path(), dataItem.name(), dataItem.providerKey())
            lyr.loadDefaultStyle()
        elif dataItem.mapLayerType() == QgsMapLayerType.RasterLayer:
            lyr = QgsRasterLayer(dataItem.path(), dataItem.name(), dataItem.providerKey())
            lyr.loadDefaultStyle()
    return lyr

class DataSource(TreeNode):

    def __init__(self, dataItem: QgsDataItem, **kwds):
        assert isinstance(dataItem, QgsDataItem)

        super().__init__(dataItem.name(), icon=dataItem.icon(), toolTip=dataItem.path(), **kwds)

        self.mDataItem: QgsDataItem = dataItem

        self.mNodeSize: DataSourceSizesTreeNode = DataSourceSizesTreeNode()
        self.mNodePath: TreeNode = TreeNode('Path')
        self.appendChildNodes([self.mNodePath, self.mNodeSize])

    def __hash__(self):
        return hash((self.mDataItem.path(), self.mDataItem.type(), self.mDataItem.providerKey()))

    def __eq__(self, other):
        if not isinstance(other, DataSource):
            return False
        return self.__hash__() == other.__hash__()

    def source(self) -> str:
        return self.mDataItem.path()

    def dataItem(self) -> QgsDataItem:
        return self.mDataItem

    def updateNodes(self, **kwds) -> dict:
        """
        Creates and updates notes according to the data source.
        """
        dataItem: QgsDataItem = self.dataItem()
        self.setName(dataItem.name())
        self.setToolTip(dataItem.toolTip())
        self.setIcon(dataItem.icon())

        self.mNodePath.setValue(dataItem.path())
        data = dict()
        data.update(self.mNodeSize.updateNodes(self.dataItem()))
        return data


class SpatialDataSource(DataSource):

    def __init__(self, dataItem: QgsLayerItem):

        super().__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)

        self.nodeExtXmu: TreeNode = TreeNode('Width')
        self.nodeExtYmu: TreeNode = TreeNode('Height')
        self.nodeCRS: CRSLayerTreeNode = CRSLayerTreeNode(QgsCoordinateReferenceSystem())
        self.mNodeSize.appendChildNodes([self.nodeExtXmu, self.nodeExtYmu])
        self.appendChildNodes(self.nodeCRS)

    def asMapLayer(self) -> QgsMapLayer:
        return dataItemToLayer(self.dataItem())

    def dataItem(self) -> QgsLayerItem:
        return self.mDataItem

    def updateNodes(self) -> dict:
        data = super().updateNodes()

        ext = data.get('spatial_extent', None)
        if isinstance(ext, SpatialExtent):
            mu = QgsUnitTypes.toString(ext.crs().mapUnits())
            self.nodeCRS.setCrs(ext.crs())
            self.nodeExtXmu.setValue('{} {}'.format(ext.width(), mu))
            self.nodeExtYmu.setValue('{} {}'.format(ext.height(), mu))
        else:
            self.nodeCRS.setCrs(QgsCoordinateReferenceSystem())
            self.nodeExtXmu.setValue(None)
            self.nodeExtYmu.setValue(None)
        return data


class VectorDataSource(SpatialDataSource):

    def __init__(self, dataItem: QgsLayerItem):
        super().__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.mapLayerType() == QgsMapLayerType.VectorLayer
        self.mIsSpectralLibrary: bool = False

        self.updateNodes()

    def updateNodes(self) -> dict:

        data = super(VectorDataSource, self).updateNodes()
        lyr = data.get('map_layer', None)
        self.mIsSpectralLibrary = is_spectral_library(lyr)

    def isSpectralLibrary(self):
        self.mIsSpectralLibrary

class RasterDataSource(SpatialDataSource):

    def __init__(self, dataItem: QgsLayerItem):
        super(RasterDataSource, self).__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.mapLayerType() == QgsMapLayerType.RasterLayer

        self.mNodeBands: TreeNode = TreeNode('Bands', toolTip='Number of Raster Bands')
        self.appendChildNodes(self.mNodeBands)

        self.mWavelengthUnits = None
        self.mWavelength = None

        self.updateNodes()

    def updateNodes(self) -> dict:
        data = super().updateNodes()

        self.mNodeBands.removeAllChildNodes()

        lyr = data.get('map_layer', None)
        if isinstance(lyr, QgsRasterLayer):
            self.mNodeBands.setValue(lyr.bandCount())
            self.mWavelength, self.mWavelengthUnits = parseWavelength(lyr)
            bandNodes = []
            for b in range(lyr.bandCount()):
                bandName = lyr.bandName(b + 1)
                bandNode = RasterBandTreeNode(lyr, b, name=str(b + 1), value=bandName)
                bandNodes.append(bandNode)
            self.mNodeBands.appendChildNodes(bandNodes)


class ModelDataSource(DataSource):

    def __init__(self, dataItem: QgsDataItem):
        super().__init__(dataItem)
        assert dataItem.providerKey() == 'special:pkl'

        self.mPklObject: object = None
        self.mObjectNode: PyObjectTreeNode = None
        self.updateNodes()

    def updateNodes(self, **kwds) -> dict:
        data = super().updateNodes(**kwds)

        if isinstance(self.mObjectNode, PyObjectTreeNode):
            self.removeChildNodes([self.mObjectNode])

        source = self.source()
        error = None
        try:
            if source.endswith('.pkl'):
                with open(source, 'rb') as f:
                    pkl_obj = pickle.load(f)
            elif source.endswith('.json'):
                with open(source, 'r', encoding='utf-8') as f:
                    pkl_obj = json.load(f)
        except pickle.UnpicklingError as ex1:
            error = f'{self}:: UnpicklingError: Unable to unpickle {source}:\nReason:{ex1}'
        except Exception as ex:
            error = f'{self}:: Unable to load {source}: {ex}'

        if error:
            if source.endswith('.pkl'):
                # in case of *.pkl it is very likely that we should be able to open them with pickle.load
                messageLog(error, level=Qgis.Warning)
            else:
                debugLog(error)
        self.mPklObject = pkl_obj

        if isinstance(pkl_obj, object):
            self.mObjectNode = PyObjectTreeNode(obj=self.mPklObject)
            self.appendChildNodes([self.mObjectNode])


class FileDataSource(DataSource):

    def __init__(self, dataItem: QgsLayerItem):
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.type() == QgsLayerItem.NoType
        assert dataItem.providerKey() == 'speclia:file'
        super(FileDataSource, self).__init__(dataItem)