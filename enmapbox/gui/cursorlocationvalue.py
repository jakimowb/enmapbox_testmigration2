from __future__ import absolute_import
import six, sys, os, gc, re, collections, site
import itertools
import numpy as np
from qgis.core import *
from qgis.gui import *

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyqtgraph.graphicsItems import *
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


class CursorLocationValueMapTool(QgsMapTool):
    sigLocationIdentified = pyqtSignal(list)

    #sigLocationRequest = pyqtSignal(QgsPoint, QgsRectangle, float, QgsRectangle)
    sigLocationRequest = pyqtSignal(QgsPoint, QgsCoordinateReferenceSystem)
    def __init__(self, canvas):
        self.canvas = canvas
        self.layerType = QgsMapToolIdentify.AllLayers
        self.identifyMode = QgsMapToolIdentify.LayerSelection
        QgsMapToolIdentify.__init__(self, canvas)


    def canvasReleaseEvent(self, mouseEvent):
        x = mouseEvent.x()
        y = mouseEvent.y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x,y)
        crs = self.canvas.mapRenderer().destinationCrs()
        self.sigLocationRequest.emit(point, crs)



class CursorLocationValues(object):


    def __init__(self, uri, crs, coord_geo, name=None):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        assert os.path.exists(uri)
        assert isinstance(coord_geo, QgsPoint)
        self.uri = uri
        self.name = name if name is not None else os.path.basename(uri)
        self.coord_geo = coord_geo
        self.crs = crs

    def labelKey(self, name=True, coord_geo=True):
        k = []
        if name:
            k.append(self.name)
        if coord_geo:
            k.append('({} {})'.format(self.coord_geo.x(), self.coord_geo.y()))

        return ' '.join(k)

    @staticmethod
    def fromVector(name,uri, crs, coord_geo):
        s = ""
        return None

    @staticmethod
    def fromRaster(uri, crs, coord_geo, name=None):
        lyr = QgsRasterLayer(uri)
        dprovider = lyr.dataProvider()
        results = dprovider.identify(coord_geo, QgsRaster.IdentifyFormatValue, QgsRectangle(), 0, 0)
        ns = dprovider.xSize()
        nl = dprovider.ySize()
        ex = dprovider.extent()

        if results.isValid():
            if False:
                r2 = dprovider.identify(coord_geo, QgsRaster.IdentifyFormatValue, ex, ns, nl)
                assert results.results().values() == r2.results().values()
            #calculate pixel coordinate
            xres = ex.width() / ns
            yres = ex.height() / nl
            px_x = np.floor((coord_geo.x() - ex.xMinimum()) / xres).astype(int)
            px_y = np.floor((ex.yMaximum() - coord_geo.y()) / yres).astype(int)
            coord_px = QPoint(px_x, px_y)

            #extract band values
            r = results.results()
            band_x = np.asarray(r.keys(), dtype='float')
            band_y = np.asarray(r.values())
            nb = len(band_x)
            band_units = []
            band_names = []
            band_mask = np.ones(band_x.shape, dtype=np.bool)

            if dprovider.name() == 'gdal':
                import gdal
                ds = gdal.Open(uri)
                for b in range(nb):
                    band = ds.GetRasterBand(b + 1)
                    bandname = band.GetDescription()
                    md = band.GetMetadata_Dict()
                    band_units.append(md.get('wavelength_units', ''))
                    band_mask[b] = band_y[b] != band.GetNoDataValue()
                    band_names.append(bandname)
                    if 'wavelength' in md.keys():
                        band_x[b] = float(md['wavelength'])

            else:
                raise NotImplementedError('QgsRasterProvider {} not supported'.format((dprovider.name())))

            x_as_int = band_x.astype(int)
            if np.all(band_x == x_as_int):
                band_x = x_as_int

            C = CursorLocationRasterValues(uri, crs, coord_geo, coord_px, name=name)
            C.setBandValues(band_x, band_y, band_mask=band_mask,band_names=band_names, band_units=band_units)
            return C
        return None

    @staticmethod
    def fromDataSource(coord_geo, crs, datasource):
        from enmapbox.datasources import DataSourceSpatial, DataSourceRaster, DataSourceVector
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        assert isinstance(coord_geo, QgsPoint)
        if isinstance(datasource, DataSourceRaster):
            return CursorLocationValues.fromRaster(datasource.uri, crs, coord_geo, name=datasource.name)
        if isinstance(datasource, DataSourceVector):
            return CursorLocationValues.fromVector(datasource.uri, crs, coord_geo, name=datasource.name)
        return None




class CursorLocationVectorValues(CursorLocationValues):

    def __init__(self, uri, crs, coord_geo, name=None):
        CursorLocationValues.__init__(self, uri, crs, coord_geo, name=name)


        pass


class CursorLocationRasterValues(CursorLocationValues):

    def __init__(self, uri, crs, coord_geo, coord_px, name=None):
        super(CursorLocationRasterValues, self).__init__(uri, crs, coord_geo, name=name)
        assert isinstance(coord_px, QPoint)
        self.coord_px = coord_px
        self.band = None
        self.nb = None

    def setBandValues(self, x, y, band_mask=None, band_names = None, band_units = None):
        self.nb = len(x)
        assert len(y) == self.nb

        if band_mask is None:
            band_mask = np.ones(x.shape, dtype='bool')
        if band_names is None:
            band_names = ['Band {}'.format(b+1) for b in range(self.nb)]
        if band_units is None:
            band_units = np.asarray([])

        self.band = np.rec.fromarrays((x,y,band_mask,band_names, band_units),
                                      names=['x','y','mask','name','unit'])

    def setRATValues(self):
        raise NotImplementedError()


    def labelKey(self, name=True, coord_geo=True, coord_px = True):
        k = super(CursorLocationRasterValues,self).labelKey(name=name, coord_geo=coord_geo)

        if coord_px:
            k += '({} {})'.format(self.coord_px.x(), self.coord_px.y())

        return k

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
        pi = self.graphicsView.getPlotItem()
        pi.setObjectName('CLP')
        pi.setTitle('Cursor Location ')
        pi.getAxis('left').setLabel('Value')
        pi.getAxis('bottom').setLabel('Band')

        self.plotItem = pi
        self.legend = pi.addLegend()
        self.legend.hide()
        self.gbLegend.clicked.connect(self.showLegend)
        self.profiles = []

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

    #def showLocationValues(self, point, viewExtent, mapUnitsPerPixel, searchExtent):
    def showLegend(self, show):
        if show and len(self.profiles) > 0:
            self.legend.show()
        else:
            self.legend.hide()

    def showLocationValues(self, point, crs):
        values = []
        model = self.tableViewDataSources.model()
        if model is None:
            return

        #request info
        for ds in model.selectedSources():
            values.append(CursorLocationValues.fromDataSource(point, crs, ds))
            #request info

        #show info
        info = []

        pixel_profiles = []
        other_profiles = []
        for p in values:
            if isinstance(p, CursorLocationRasterValues) and p.nb > 1:
                pixel_profiles.append(p)
            else:
                other_profiles.append(p)

        self.tabWidget.setCurrentWidget(self.tabLocationValues)
        pi = self.plotItem
        legend = self.legend

        if not self.cbStackProfiles.isChecked():
            #remove all items from plot
            for name in [label.text for _, label in self.legend.items]:
                self.legend.removeItem(name)

            pi.clear()
            del self.profiles[:]


        if len(pixel_profiles) > 0:
            band_units = set()
            for p in pixel_profiles:
                assert isinstance(p, CursorLocationRasterValues)
                band_units.update(set(p.band[:].unit))
            x_unit = 'band' if len(band_units) > 1 else list(band_units)[0]

            kwargs = {'name':self.cbLegendDataSource.isChecked(),
                      'coord_geo':self.cbLegendGeoLocation.isChecked(),
                      'coord_px':self.cbLegendPixelLocation.isChecked()}
            pi.setLabel('bottom', x_unit)
            for p in pixel_profiles:
                assert isinstance(p, CursorLocationRasterValues)
                if x_unit == 'band':
                    x = np.arange(p.nb)+1
                else:
                    x = p.band[:].x
                y = p.band[:].y
                l = p.labelKey(**kwargs)
                if l == '': l = p.name


                item = pi.plot(x, y, name=l)
                self.profiles.append(item)
        self.showLegend(self.gbLegend.isChecked())


        for p in other_profiles + pixel_profiles:
            info.append(os.path.basename(p.name))
            if isinstance(p, CursorLocationRasterValues):
                for i in range(p.nb):
                    x = p.band[i].x
                    y = p.band[i].y
                    wlu = p.band[i].unit
                    t = '  Band {}: {}'.format(i+1, y)
                    if wlu != '':
                        t += ' @{} {}'.format(y, wlu)
                    info.append(t)
            if isinstance(p, CursorLocationVectorValues):
                pass
        self.locationValuesTextEdit.setText('\n'.join(info))


class CursorLocationDataSourceItem():
    columns = ['name','uri']

    def __init__(self, dataSource):

        self.src = dataSource
        self.show = True

    def __cmp__(self, other):
        return self.src == other.src




class CursorLocationDataSourceModel(QAbstractTableModel):


    def __init__(self, dsm, parent=None, *args):
        super(QAbstractTableModel, self).__init__()
        from enmapbox.datasources import DataSourceManager, DataSourceSpatial

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
            if cn == 'name':
                result = Qt.Checked if clds.show else Qt.Unchecked

        elif role == Qt.ToolTipRole:
            result = '{} : {}'.format(ds.name, ds.uri)
        elif role == Qt.UserRole:
            result = ds
        return result

    def setData(self, index, value, role=None):
        cn = self.columnnames[index.column()]
        if role == Qt.CheckStateRole and cn == 'name':
            self.cursorLocationDataSourceItems[index.row()].show = value == Qt.Checked
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if index.isValid():
            cn = self.columnnames[index.column()]
            if cn == 'name': #relative values can be edited
                flags = Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
            else:
                flags = Qt.ItemIsEnabled
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