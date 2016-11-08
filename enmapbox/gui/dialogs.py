from __future__ import absolute_import
import six, sys, os, gc, re, collections, site
import itertools
from qgis.core import *
from qgis.gui import *

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from enmapbox.utils import *
from enmapbox.main import DIR_GUI

def showLayerPropertiesDialog(layer, canvas, parent):
    d = None
    if isinstance(layer, QgsRasterLayer):
        d = RasterLayerProperties(layer, canvas, parent)
    elif isinstance(layer, QgsVectorLayer):
        d = VectorLayerProperties(layer, canvas, parent)
    else:
        assert NotImplementedError()
    d.exec_()


class RasterLayerProperties(QgsOptionsDialogBase):

    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("RasterLayerProperties", parent, fl)

       # self.setupUi(self)

        self.initOptionsBase(False)
        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)



class VectorLayerProperties(QgsOptionsDialogBase):

    def __init__(self, lyr, canvas, parent, fl=Qt.Widget):
        super(RasterLayerProperties, self).__init__("VectorLayerProperties", parent, fl)

        title = "Layer Properties - {}".format(lyr.name())
        self.restoreOptionsBaseUi(title)

class CursorLocationValueWidget(QtGui.QMainWindow,
                                loadUIFormClass(os.path.normpath(jp(DIR_GUI, 'cursorlocationinfo.ui')))):
    def __init__(self, parent=None):
        """Constructor."""
        QWidget.__init__(self, parent)
        #super(CursorLocationValueWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)



    def updateSplitMode(self):
        s = self.size()
        o = Qt.Vertical if s.width() < s.height() else Qt.Horizontal
        self.splitter.setOrientation(o)

    def connectDataSourceManager(self, dsm):
        from enmapbox.datasources import DataSourceManager
        if dsm:

            assert isinstance(dsm, DataSourceManager)
            self.DSM = dsm
            #self.DSM.sigDataSourceAdded.connect(self.linkDataSource)
            #self.DSM.sigDataSourceRemoved.connect(self.unlinkDataSource)
            model = CursorLocationDataSourceModel(self.DSM)
            self.tableViewDataSources.setModel(model)
            #for ds in self.DSM.sources:
            #    self.linkDataSource(ds)
        else:
            #for ds in self.DSM.sources:
            #    self.unlinkDataSource(ds)
            self.tableViewDataSources.setModel(None)
            self.DSM = None

    def resizeEvent(self, event):
        super(CursorLocationValueWidget, self).resizeEvent(event)
        self.updateSplitMode()

    def showLocationValues(self, point, viewExtent, mapUnitsPerPixel, searchExtent):
        results = collections.OrderedDict()
        model = self.tableViewDataSources.model()
        if model is None:
            return

        #request info
        for ds in model.selectedSources():
            #request info
            lyr = ds.createMapLayer()
            dprovider = lyr.dataProvider()

            crs_lyr = dprovider.crs()
            #todo: transform point and viewExtent if necessary

            width = int(viewExtent.width() / mapUnitsPerPixel)
            height = int(viewExtent.height() / mapUnitsPerPixel)

            if isinstance(dprovider, QgsRasterDataProvider):
                result = dprovider.identify(point, QgsRaster.IdentifyFormatValue, viewExtent, width, height)
                if result.isValid():

                    results[str(lyr.name())] = result.results()
            if isinstance(dprovider, QgsVectorDataProvider):


                results = dprovider



        #show info
        info = []
        p = self.graphicsView

        for dsName, res in results.items():
            info.append(dsName)

            for k, v in res.items():
                info.append('{}:{}'.format(k,v))

        self.locationValuesTextEdit.setText('\n'.join(info))


class CursorLocationDataSourceItem():
    columns = ['v','name','uri']

    def __init__(self, dataSource):

        self.src = dataSource
        self.show = True

    def __cmp__(self, other):
        return self.src == other.src




class CursorLocationDataSourceModel(QAbstractTableModel):


    def __init__(self, dsm, parent=None, *args):
        super(QAbstractTableModel, self).__init__()
        from enmapbox.datasources import DataSourceManager, DataSourceSpatial
        from enmapbox.treeviews import TreeNode
        assert isinstance(dsm, DataSourceManager)
        self.DSM = dsm
        self.columnnames = CursorLocationDataSourceItem.columns
        self.cursorLocationDataSourceItems = list()
        for src in self.DSM.sources:
            self.addCLDataSourceItem(src)
        self.DSM.sigDataSourceAdded.connect(self.addCLDataSourceItem)
        self.DSM.sigDataSourceRemoved.connect(self.removeCLDataSourceItem)


    def addCLDataSourceItem(self, src):
        from enmapbox.datasources import DataSourceSpatial
        if isinstance(src, DataSourceSpatial):
            self.cursorLocationDataSourceItems.append(CursorLocationDataSourceItem(src))

    def removeCLDataSourceItem(self, src):
        for clvds in [c for c in self.cursorLocationDataSourceItems if c.src == src]:
            self.cursorLocationDataSourceItems.remove(clvds)

    def selectedCLDataSourceItems(self):
        return [i for i in self.cursorLocationDataSourceItems if i.show]

    def selectedSources(self):
        return [c.src for c in self.selectedCLDataSourceItems()]

    def rowCount(self, parent = QModelIndex()):
        return len(self.cursorLocationDataSourceItems)

    def columnCount(self, parent = QModelIndex()):
        return len(self.columnnames)



    def data(self, index, role = Qt.DisplayRole):
        if role is None or not index.isValid():
            return None
        from enmapbox.datasources import DataSourceSpatial, DataSourceRaster, DataSourceVector
        clds = self.cursorLocationDataSourceItems[index.row()]
        ds = clds.src
        assert isinstance(ds, DataSourceSpatial)
        cn = self.columnnames[index.column()]
        result = None
        if role == Qt.DisplayRole:
            if cn == 'name':
                result = ds.name
            elif cn == 'uri':
                result = ds.uri
        elif role == Qt.CheckStateRole:
            if cn == 'v':

                result = Qt.Checked if clds.show else Qt.Unchecked

        elif role == Qt.ToolTipRole:
            result = '{} : {}'.format(ds.name, ds.uri)
        elif role == Qt.UserRole:
            result = ds
        return result

    def setData(self, index, value, role=None):
        cn = self.columnnames[index.column()]
        if role == Qt.CheckStateRole and cn == 'v':
            self.cursorLocationDataSourceItems[index.row()].show = value == Qt.Checked
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if index.isValid():
            cn = self.columnnames[index.column()]
            if cn == 'v': #relative values can be edited
                flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
            else:
                flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
            return flags
        return None

    def headerData(self, col, orientation, role):
        if Qt is None:
            return None
        cn = self.columnnames[col]
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if cn == 'v':
                return ''
            else:
                return self.columnnames[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None