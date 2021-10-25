import json
import pickle
import warnings

from PyQt5.QtGui import QIcon
from qgis.core import QgsDataItem, QgsLayerItem, QgsCoordinateReferenceSystem, QgsMapLayer, QgsUnitTypes, \
    QgsMapLayerType, QgsVectorLayer, QgsRasterLayer, Qgis, QgsWkbTypes, QgsField

from enmapbox import messageLog, debugLog
from ...externals.qps.classification.classificationscheme import ClassificationScheme
from ...externals.qps.models import TreeNode, PyObjectTreeNode
from ...externals.qps.utils import SpatialExtent, parseWavelength, iconForFieldType
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
    MD_LAYER = 'map_layer'
    MD_MAPUNIT = 'map_unit'
    MD_EXTENT = 'spatial_extent'
    MD_CRS = 'crs'

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

    def uri(self) -> str:
        warnings.warn('Use source()->str', DeprecationWarning)
        return self.source()

    def dataItem(self) -> QgsDataItem:
        return self.mDataItem

    def updateNodes(self, **kwds) -> dict:
        """
        Creates and updates notes according to the data source.
        Returns dictionary with collected metadata
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

    def mapLayer(self) -> QgsMapLayer:
        warnings.warn(DeprecationWarning('Use .asMapLayer() instead'))
        return self.asMapLayer()

    def dataItem(self) -> QgsLayerItem:
        return self.mDataItem

    def updateNodes(self) -> dict:
        MD = super().updateNodes()

        ext = MD.get(DataSource.MD_EXTENT, None)
        if isinstance(ext, SpatialExtent):
            mu = QgsUnitTypes.toString(ext.crs().mapUnits())
            self.nodeCRS.setCrs(ext.crs())
            self.nodeExtXmu.setValue('{} {}'.format(ext.width(), mu))
            self.nodeExtYmu.setValue('{} {}'.format(ext.height(), mu))
        else:
            self.nodeCRS.setCrs(QgsCoordinateReferenceSystem())
            self.nodeExtXmu.setValue(None)
            self.nodeExtYmu.setValue(None)
        return MD


class VectorDataSource(SpatialDataSource):

    def __init__(self, dataItem: QgsLayerItem):
        super().__init__(dataItem)
        assert isinstance(dataItem, QgsLayerItem)
        assert dataItem.mapLayerType() == QgsMapLayerType.VectorLayer
        self.mIsSpectralLibrary: bool = False
        self.mWKBType = None
        self.mGeometryType = None

        self.nodeFeatures: TreeNode = TreeNode('Features', values=[0])
        self.nodeGeomType = TreeNode('Geometry Type')
        self.nodeWKBType = TreeNode('WKB Type')

        self.nodeFields: TreeNode = TreeNode('Fields',
                                             toolTip='Attribute fields related to each feature',
                                             values=[0])

        self.nodeFeatures.appendChildNodes([self.nodeGeomType, self.nodeWKBType])
        self.appendChildNodes([self.nodeFeatures, self.nodeFields])

        self.updateNodes()

    def wkbType(self) -> QgsWkbTypes.Type:
        return self.mWKBType

    def geometryType(self) -> QgsWkbTypes.GeometryType:
        return self.mGeometryType

    def updateNodes(self) -> dict:

        MD = super(VectorDataSource, self).updateNodes()
        lyr = MD.get('map_layer', None)

        self.mIsSpectralLibrary = is_spectral_library(lyr)

        if isinstance(lyr, QgsVectorLayer):
            self.mWKBType = lyr.wkbType()
            self.mGeometryType = lyr.geometryType()

            wkbTypeName = QgsWkbTypes.displayString(int(self.mWKBType))
            geomTypeName = ['Point', 'Line', 'Polygon', 'Unknown', 'Null'][lyr.geometryType()]
            self.nodeWKBType.setValue(wkbTypeName)
            self.nodeGeomType.setValue(geomTypeName)

            nFeat = lyr.featureCount()
            nFields = lyr.fields().count()
            self.nodeFields.setValue(nFields)

            if self.isSpectralLibrary():
                self.setIcon(QIcon(r':/qps/ui/icons/speclib.svg'))
            else:
                self.setIcon(self.dataItem().icon())

            self.nodeFeatures.setValue(nFeat)
            self.nodeFields.removeAllChildNodes()
            field_nodes = []
            for i, f in enumerate(lyr.fields()):
                f: QgsField
                n = TreeNode(f.name())
                l = f.length()
                if l > 0:
                    n.setValue('{} {}'.format(f.typeName(), l))
                else:
                    n.setValue(f.typeName())
                n.setIcon(iconForFieldType(f))
                field_nodes.append(n)

            self.nodeFields.setValue(len(field_nodes))
            self.nodeFields.appendChildNodes(field_nodes)

    def isSpectralLibrary(self) -> bool:
        return self.mIsSpectralLibrary


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
        MD = super().updateNodes()

        self.mNodeBands.removeAllChildNodes()

        lyr = MD.get(DataSource.MD_LAYER, None)
        if isinstance(lyr, QgsRasterLayer):
            self.mNodeBands.setValue(lyr.bandCount())
            self.mWavelength, self.mWavelengthUnits = parseWavelength(lyr)
            bandNodes = []
            for b in range(lyr.bandCount()):
                bandName = lyr.bandName(b + 1)
                bandNode = RasterBandTreeNode(lyr, b, name=str(b + 1), value=bandName)
                bandNodes.append(bandNode)
            self.mNodeBands.appendChildNodes(bandNodes)

            hasClassInfo = isinstance(ClassificationScheme.fromMapLayer(lyr), ClassificationScheme)

            nBands = lyr.bandCount()
            dataType = None
            if nBands > 0:
                dataType = lyr.dataProvider().dataType(1)

            # show more specialized raster icons
            if hasClassInfo is True:
                icon = QIcon(':/enmapbox/gui/ui/icons/filelist_classification.svg')
            elif dataType in [Qgis.Byte] and nBands == 1:
                icon = QIcon(':/enmapbox/gui/ui/icons/filelist_mask.svg')
            elif nBands == 1:
                icon = QIcon(':/enmapbox/gui/ui/icons/filelist_regression.svg')
            else:
                icon = QIcon(':/enmapbox/gui/ui/icons/filelist_image.svg')
            self.setIcon(icon)


class ModelDataSource(DataSource):

    def __init__(self, dataItem: QgsDataItem):
        super().__init__(dataItem)
        assert dataItem.providerKey() == 'special:pkl'

        self.mPklObject: object = None
        self.mObjectNode: PyObjectTreeNode = None
        self.updateNodes()

    def updateNodes(self, **kwds) -> dict:
        MD = super().updateNodes(**kwds)

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
            self.mObjectNode = PyObjectTreeNode(obj=self.mPklObject, name='Content')
            self.appendChildNodes([self.mObjectNode])


class FileDataSource(DataSource):

    def __init__(self, dataItem: QgsDataItem):
        assert isinstance(dataItem, QgsDataItem)
        # assert dataItem.type() == QgsDataItem.NoType
        assert dataItem.providerKey() == 'special:file'
        super(FileDataSource, self).__init__(dataItem)


class DataSourceTypes(object):
    """
    Enumeration that defines the standard data source types.
    """
    Raster = 'RASTER'
    Vector = 'VECTOR'
    SpectralLibrary = 'SPECLIB'
    Spatial = 'SPATIAL'
    Model = 'MODEL'
    File = 'FILE'


LUT_DATASOURCETYPES = {DataSourceTypes.Raster: RasterDataSource,
                       DataSourceTypes.Vector: VectorDataSource,
                       DataSourceTypes.Spatial: SpatialDataSource,
                       DataSourceTypes.SpectralLibrary: VectorDataSource,
                       DataSourceTypes.Model: ModelDataSource,
                       DataSourceTypes.File: FileDataSource,
                       }

for cls in set(LUT_DATASOURCETYPES.values()):
    LUT_DATASOURCETYPES[cls] = cls
