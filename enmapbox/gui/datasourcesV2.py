
import os
import re
import typing
from osgeo import gdal, ogr, osr
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.core import QgsApplication, QgsDataItemProvider, \
    QgsDataCollectionItem, QgsDataItem, QgsDataProvider, QgsMapLayer, QgsRasterLayer, QgsVectorLayer
from qgis.gui import *
from qgis.gui import QgsBrowserGuiModel, QgsDataItemGuiContext

from enmapbox.gui import SpectralLibrary

class EnMAPBoxRasterCollectionItem(QgsDataCollectionItem):

    def __init__(self, parent:QgsDataItem=None):

        super().__init__(parent, 'Raster Sources', '', '')


        self.mSources = dict()
        QgsProject.instance().layersAdded.connect(self.onLayersAdded)

    def onLayersAdded(self, layers):
        print(f'EnMAPBoxRasterCollectionItem:onLayersAdded added: {layers}')


    def icon(self) -> QIcon:
        return QIcon(':/qps/ui/icons/raster.svg')

    def menus(self, parent:QWidget=None):
        m = QMenu(parent)
        m.addAction('Test1')
        return [m]


    def actions(self, parent:QWidget=None):
        a = QAction('Test Action')
        return [a]

class EnMAPBoxVectorCollectionItem(QgsDataCollectionItem):

    def __init__(self, parent:QgsDataItem=None):

        super().__init__(parent, 'Vector Sources', '', '')

    def icon(self) -> QIcon:
        return QIcon(':/images/themes/default/mIconLineLayer.svg')

    def menus(self, parent:QWidget=None):
        m = QMenu(parent)
        m.addAction('Test1')
        return [m]

    def actions(self, parent:QWidget=None):
        a = QAction('Test Action')
        return [a]


class EnMAPBoxSpectralLibraryCollectionItem(QgsDataCollectionItem):

    def __init__(self, parent: QgsDataItem = None):
        super().__init__(parent, 'Spectral Libraries', '', '')

    def icon(self) -> QIcon:
        return QIcon(':/qps/ui/icons/speclib.svg')


class DummyItem(QgsDataItem):

    def __init__(self, parent:QgsDataItem=None):
        # QgsDataItem (QgsDataItem::Type type, QgsDataItem *parent, const QString &name, const QString &path, const QString &providerKey=QString())
        super().__init__(QgsDataItem.Custom, parent, 'Dummy', 'no path', '')

    def type(self)->QgsDataItem.Type:
        return QgsDataItem.Custom

    def icon(self) -> QIcon:
        return QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg')
    def capabilities(self):
        return QgsDataItem.Fast | QgsDataItem.Fertile

class EnMAPBoxDataItem(QgsDataItem):

    def __init__(self, parent:QgsDataItem=None):
        # QgsDataItem (QgsDataItem::Type type, QgsDataItem *parent, const QString &name, const QString &path, const QString &providerKey=QString())
        super().__init__(QgsDataItem.Custom, parent, 'EnMAP-Box', '', 'EnMAPBox')

        self.mRasters = EnMAPBoxRasterCollectionItem(None)
        self.mVectors = EnMAPBoxVectorCollectionItem(None)
        self.mSpeclibs = EnMAPBoxSpectralLibraryCollectionItem(None)

        #self.mDummy = DummyItem(self)
        #self.addChildItem(self.mDummy, refresh=False)
        #self.addChildItem(self.mSpeclibs, refresh=True)
        #self.addChildItem(self.mRasters, refresh=True)
        QgsProject.instance().layersAdded.connect(self.onLayersAdded)
        self.populate()
        print('populated')

    def onLayersAdded(self, layers):
        print(f'EnMAPBoxDataItem:onLayersAdded added: {layers}')

    def menus(self, parent:QWidget=None):
        m = QMenu(parent)
        m.addAction('Test1')
        return [m]

    def actions(self, parent:QWidget=None):
        a = QAction('Test Action')
        return [a]

    def createChildren(self):
        print('Create Children')
        return [self.mRasters, self.mVectors, self.mSpeclibs]

    #def addChildItem(self, child:QgsDataItem, refresh:bool=False):


    def icon(self) -> QIcon:
        return QIcon(':/enmapbox/gui/ui/icons/enmapbox.svg')

    def type(self)->QgsDataItem.Type:
        return QgsDataItem.Custom

    def capabilities(self):
        return QgsDataItem.Fast | QgsDataItem.Fertile


class EnMAPBoxDataItemProvider(QgsDataItemProvider):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.mItems = []

        QgsProject.instance().layersAdded.connect(self.onLayersAdded)

    def onLayersAdded(self, layers):
        print(f'EnMAPBoxDataItemProvider:onLayersAdded added: {layers}')

    def capabilities(self):
        # return -1
        # return QgsDataProvider.NoDataCapabilities
        return QgsDataProvider.Dir

    def createDataItem(self, path:str, parentItem:QgsDataItem=None):
        print('createDataItem: {}'.format(path))
        if parentItem is None:
            item = EnMAPBoxDataItem(parentItem)
            self.mItems.append(item)
            return item
        else:
            # here we could handle specific source files, e.g. spectral library file formats
            return None

    def createDataItems(self, path:str, parent:QgsDataItem=None):
        print('createDataItems: {}'.format(path))
        return []

    def handlesDirectoryPath(self, path:str) -> bool:
        print('handlesDirectoryPath: {}'.format(path))
        return False

    def name(self):
        return 'EnMAP-Box'

    def populateContextMenu(self, item:QgsDataItem, menu:QMenu,
                            selectedItems:typing.List[QgsDataItem],
                            context:QgsDataItemGuiContext):

        print('Populate context menu')
        s = ""