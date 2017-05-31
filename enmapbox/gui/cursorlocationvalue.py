from __future__ import absolute_import

import os, collections

import numpy as np
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from enmapbox.gui.utils import loadUI, SpatialExtent, SpatialPoint


class CursorLocationValues(object):


    def __init__(self, uri, spatialPoint, name=None):
        assert isinstance(spatialPoint, SpatialPoint)


        self.uri = uri
        self.name = name if name is not None else os.path.basename(uri)
        self.spatialPoint = spatialPoint


    def labelKey(self, name=True, coord_geo=True):
        k = []
        if name:
            k.append(self.name)
        if coord_geo:
            k.append('({} {})'.format(self.coord_geo.x(), self.coord_geo.y()))

        return ' '.join(k)

    @staticmethod
    def fromVector(uri, spatialPoint, name=None):
        assert isinstance(spatialPoint, SpatialPoint)

        lyr = QgsVectorLayer(uri, name, 'ogr')
        dprovider = lyr.dataProvider()
        fsource = dprovider.featureSource()

        pt = spatialPoint.toCrs(lyr.crs())
        rect = SpatialExtent(spatialPoint.crs(),0,0,1,1).setCenter(spatialPoint)
        frequest = QgsFeatureRequest().setFilterRect(rect).setFlags(QgsFeatureRequest.ExactIntersect)

        results = {}
        fieldNames = [dprovider.fields()[f].name() for f in range(dprovider.fields().count())]
        C = CursorLocationVectorValues(uri, pt, fieldNames=fieldNames, name=name)
        for feature in fsource.getFeatures(frequest):
            C.addFeature(feature)

        if len(C) > 0:
            return C
        else:
            return None

    @staticmethod
    def fromRaster(uri, spatialPoint, name=None):
        assert isinstance(spatialPoint, SpatialPoint)
        lyr = QgsRasterLayer(uri)
        dprovider = lyr.dataProvider()


        pt = spatialPoint.toCrs(lyr.crs())

        results = dprovider.identify(pt, QgsRaster.IdentifyFormatValue, QgsRectangle(), 0, 0)
        ns = dprovider.xSize()
        nl = dprovider.ySize()
        ex = dprovider.extent()

        if results.isValid():
            if False:
                r2 = dprovider.identify(pt, QgsRaster.IdentifyFormatValue, ex, ns, nl)
                assert results.results().values() == r2.results().values()
            #calculate pixel coordinate
            xres = ex.width() / ns
            yres = ex.height() / nl
            px_x = np.floor((pt.x() - ex.xMinimum()) / xres).astype(int)
            px_y = np.floor((ex.yMaximum() - pt.y()) / yres).astype(int)
            coord_px = QPoint(px_x, px_y)

            #extract band values
            r = results.results()
            xValues = np.asarray(r.keys(), dtype='float')
            yValues = np.asarray(r.values())
            nb = len(xValues)
            band_units = []
            band_names = []
            band_mask = np.not_equal(yValues, None)

            if dprovider.name() == 'gdal':
                from osgeo import gdal
                ds = gdal.Open(uri)
                for b in range(nb):
                    band = ds.GetRasterBand(b + 1)
                    bandname = band.GetDescription()
                    md = band.GetMetadata_Dict()
                    band_units.append(md.get('wavelength_units', ''))
                    nodata = band.GetNoDataValue()
                    if nodata:
                        band_mask[b] = band_mask[b] * (yValues[b] != nodata)
                    band_names.append(bandname)
                    if 'wavelength' in md.keys():
                        xValues[b] = float(md['wavelength'])

            else:
                raise NotImplementedError('QgsRasterProvider {} not supported'.format((dprovider.name())))

            x_as_int = xValues.astype(int)
            if np.all(xValues == x_as_int):
                xValues = x_as_int

            C = CursorLocationRasterValues(uri, pt, coord_px, name=name)
            C.setValues(xValues, yValues, band_mask=band_mask, band_names=band_names, band_units=band_units)
            return C
        return None

    @staticmethod
    def fromDataSource(spatialPoint, datasource):
        from enmapbox.gui.datasources import DataSourceRaster, DataSourceVector
        assert isinstance(spatialPoint, SpatialPoint)

        if isinstance(datasource, DataSourceRaster):
            return CursorLocationValues.fromRaster(datasource.mUri, spatialPoint, name=datasource.mName)
        if isinstance(datasource, DataSourceVector):
            return CursorLocationValues.fromVector(datasource.mUri, spatialPoint, name=datasource.mName)
        return None



class CursorLocationVectorValues(CursorLocationValues):

    def __init__(self, uri, spatialPoint, fieldNames=None, name=None):
        CursorLocationValues.__init__(self, uri, spatialPoint, name=name)
        self.results = list()
        self.fieldNames = fieldNames

    def addFeature(self, feature):
        assert isinstance(feature, QgsFeature)
        if self.fieldNames is None:
            self.fieldNames = feature
        d = collections.OrderedDict()
        for fieldName in self.fieldNames:
            d[fieldName] = feature.attribute(fieldName)
        self.results.append((feature.id(), d))

    def __len__(self):
        return len(self.results)


class LoadWorker(QObject):
    sigValueLoaded = pyqtSignal(str, dict)
    sigLoadingStarted = pyqtSignal(int)
    sigLoadingFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(LoadWorker, self).__init__(parent)

    def doWork(self, theUris, thePointWkt, theCrsDefinition):

        spatialPoint = QgsGeometry.fromWkt(thePointWkt)
        assert spatialPoint.wkbType() == QgsWKBTypes.Point


        crs = QgsCoordinateReferenceSystem(theCrsDefinition)
        assert isinstance(crs, QgsCoordinateReferenceSystem)

        if len(theUris) > 0:
            self.sigLoadingStarted.emit(len(theUris))

            for uri in theUris:
                values = CursorLocationValues.fromDataSource(spatialPoint, uri)

                #values might be expressed as dict or list
                self.sigValueLoaded.emit(uri, values)

            self.sigLoadingFinished.emit()




class CursorLocationRasterValues(CursorLocationValues):

    def __init__(self, uri, spatialPoint, coord_px, name=None):
        super(CursorLocationRasterValues, self).__init__(uri, spatialPoint, name=name)
        assert isinstance(coord_px, QPoint)
        self.coord_px = coord_px
        self.values = None
        self.nb = None

    def setValues(self, x, y, band_mask=None, band_names = None, band_units = None):
        self.nb = len(x)
        assert len(y) == self.nb

        if band_mask is None:
            band_mask = np.not_equal(y, None)

        if band_names is None:
            band_names = ['Band {}'.format(b+1) for b in range(self.nb)]

        if band_units is None:
            band_units = np.ones((self.nb),object)
            band_units[:] = None

        self.values = np.rec.fromarrays((np.arange(self.nb),x, y, band_mask, band_names, band_units),
                                        names=['bandIndex', 'xValue','yValue','isValid','bandName','bandUnit'])

    def setRATValues(self):
        raise NotImplementedError()


    def labelKey(self, name=True, coord_geo=True, coord_px = True):
        k = super(CursorLocationRasterValues,self).labelKey(name=name, coord_geo=coord_geo)

        #append pixel coordinate
        if coord_px:
            k += '({} {})'.format(self.coord_px.x(), self.coord_px.y())
        return k

class CursorLocationValueWidget(QMainWindow,
                                loadUI('cursorlocationinfo.ui')):
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

    def connectDataSourceManager(self, dsm):
        from enmapbox.gui.datasourcemanager import DataSourceManager
        if dsm:
            assert isinstance(dsm, DataSourceManager)
            self.DSM = dsm
            model = CursorLocationDataSourceModel(self.DSM)
            self.tableViewDataSources.setModel(model)
        else:
            self.tableViewDataSources.setModel(None)
            self.DSM = None


    def showLegend(self, show):
        if show and len(self.profiles) > 0:
            self.legend.show()
        else:
            self.legend.hide()

    def showLocationValues(self, spatialPoint):
        assert isinstance(spatialPoint, SpatialPoint)
        values = []
        model = self.tableViewDataSources.model()
        if model is None:
            return

        #get values
        for ds in model.selectedSources():
            values.append(CursorLocationValues.fromDataSource(spatialPoint, ds))

        pixel_profiles = []

        for p in values:
            if isinstance(p, CursorLocationRasterValues) and p.nb > 1:
                pixel_profiles.append(p)

        #self.tabWidget.setCurrentWidget(self.tabLocationValues)
        pi = self.plotItem
        legend = self.legend

        if not self.cbStackProfiles.isChecked():
            #remove all items from plot
            for name in [label.text for _, label in self.legend.items]:
                self.legend.removeItem(name)
            pi.clear()
            del self.profiles[:]

        from pyqtgraph.parametertree import Parameter

        params = []
        if len(pixel_profiles) > 0:
            band_units = set()
            for p in pixel_profiles:
                assert isinstance(p, CursorLocationRasterValues)
                band_units.update(set(p.values[:].bandUnit))
            x_unit = 'band' if len(band_units) > 1 else list(band_units)[0]

            kwargs = {'name':self.cbLegendDataSource.isChecked(),
                      'coord_geo':self.cbLegendGeoLocation.isChecked(),
                      'coord_px':self.cbLegendPixelLocation.isChecked()}
            pi.setLabel('bottom', x_unit)
            for p in pixel_profiles:
                assert isinstance(p, CursorLocationRasterValues)
                x = p.values[:].xValue
                y = p.values[:].yValue
                isValid = p.values[:].isValid
                if np.any(isValid):
                    i = np.where(isValid)
                    x = x[i]
                    y = y[i]
                    label = p.labelKey(**kwargs)
                    if label == '':
                        label = p.name
                    item = pi.plot(x, y, name=label)
                    self.profiles.append(item)
        self.showLegend(self.gbLegend.isChecked())

        from pyqtgraph.parametertree import Parameter

        #handle single band image values first
        for p in [p for p in values if isinstance(p, CursorLocationRasterValues)]:
            assert isinstance(p, CursorLocationRasterValues)
            datasource = {'name':p.name, 'readonly':True, 'type':'group'}
            childs = []
            childs.append({'name':'x', 'value': p.coord_px.x(), 'type':'int', 'readonly':True})
            childs.append({'name':'y', 'value': p.coord_px.y(), 'type': 'int', 'readonly': True})
            for i in range(p.nb):
                v = p.values[i].yValue
                childs.append({'name':'band {}'.format(i+1), 'value': v, 'type': 'str', 'readonly': True})
            datasource['children'] = childs
            params.append(datasource)

        # handle vector source values second
        for p in [p for p in values if isinstance(p, CursorLocationVectorValues)]:
            assert isinstance(p, CursorLocationVectorValues)
            datasource = {'name':p.name, 'readonly':True, 'type':'group'}
            features = []
            for feature in p.results:
                fid, values = feature
                featureFields = [{'name': fieldName, 'value': fieldValue, 'readonly': True, 'type':'str'} \
                                  for fieldName, fieldValue in values.items()]
                features.append(
                    {'name':'FID {}'.format(fid), 'readonly':True, 'type':'group',
                        'children':featureFields}
                )

            datasource['children'] = features
            params.append(datasource)
            s = ""
        treeRoot = Parameter.create(name='Results', type='group', children= params)
        self.parameterTree.setParameters(treeRoot, showTop=False)


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
        from enmapbox.gui.datasourcemanager import DataSourceManager

        assert isinstance(dsm, DataSourceManager)
        self.DSM = dsm
        self.columnnames = CursorLocationDataSourceItem.columns
        self.cursorLocationDataSourceItems = list()
        for src in self.DSM.sources:
            self.addCLDataSourceItem(src)
        self.DSM.sigDataSourceAdded.connect(self.addCLDataSourceItem)
        self.DSM.sigDataSourceRemoved.connect(self.removeCLDataSourceItem)


    def addCLDataSourceItem(self, src):
        from enmapbox.gui.datasources import DataSourceSpatial
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
        from enmapbox.gui.datasources import DataSourceSpatial
        clds = self.cursorLocationDataSourceItems[index.row()]
        ds = clds.src
        assert isinstance(ds, DataSourceSpatial)
        cn = self.columnnames[index.column()]
        result = None
        if role == Qt.DisplayRole:
            if cn == 'name':
                result = ds.mName
            elif cn == 'uri':
                result = ds.mUri
        elif role == Qt.CheckStateRole:
            if cn == 'name':
                result = Qt.Checked if clds.show else Qt.Unchecked

        elif role == Qt.ToolTipRole:
            result = '{} : {}'.format(ds.mName, ds.mUri)
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
        if col > len(self.columnnames)-1:
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



if __name__ == '__main__':
    #todo: implement example
    import enmapbox.gui.sandbox
    import enmapbox.testdata.UrbanGradient as UG
    dataSources = [UG.EnMAP01_Berlin_Urban_Gradient_2009, UG.LandCov_Layer_Level2_Berlin_Urban_Gradient_2009, UG.LandCov_Vec_polygons_Berlin_Urban_Gradient_2009]
    qgsApp = enmapbox.gui.sandbox.sandboxPureGui(dataSources=dataSources)



    qgsApp.exec_()

    pass