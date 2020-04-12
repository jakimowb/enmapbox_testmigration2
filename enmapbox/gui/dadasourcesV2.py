
import os
import re
import typing
from osgeo import gdal, ogr, osr
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *


class RasterCollectionItem(QgsDataCollectionItem):

    def __init__(self, parent:QgsDataItem=None):

        super().__init__(parent, 'Raster Sources', '', '')

    def icon(self) -> QIcon:
        return QIcon(':/qps/ui/icons/raster.svg')


class EnMAPBoxDataItem(QgsDataItem):

    def __init__(self):
        # QgsDataItem (QgsDataItem::Type type, QgsDataItem *parent, const QString &name, const QString &path, const QString &providerKey=QString())
        super().__init__(QgsDataItem.Custom, None, 'EnMAP-Box', '', 'enmapbox' )

        self.mRasters = RasterCollectionItem(self)

        self.addChildItem(self.mRasters, refresh=True)

        s = ""

    def icon(self) -> QIcon:
        return QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg')

    def type(self):
        return QgsDataType.Custom

    def capabilities(self):
        return QgsDataItem.Fast | QgsDataItem.Fertile

class EnMAPBoxDataItemProvider(QgsDataItemProvider):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def capabilities(self):
        return QgsDataProvider.NoDataCapabilities

    def createDataItem(self, path:str, parent:QgsDataItem=None):
        print('createDataItem: {}'.format(path))
        return EnMAPBoxDataItem()

    def createDataItems(self, path:str, parent:QgsDataItem=None):
        print('createDataItems: {}'.format(path))
        return []

    def handlesDirectoryPath(self, path:str) -> bool:
        print('handlesDirectoryPath: {}'.format(path))
        return False

    def name(self):
        return 'enmapbox'
