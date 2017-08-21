# -*- coding: utf-8 -*-

"""
***************************************************************************
    enmapbox/gui/utils.py
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from __future__ import absolute_import
import os, sys, importlib, tempfile, re, six, logging, fnmatch, StringIO, pickle
logger = logging.getLogger(__name__)

from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyQt4 import uic
from osgeo import gdal
import numpy as np
import enmapbox.gui
jp = os.path.join

DIR_ENMAPBOX = os.path.dirname(enmapbox.__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui','ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui','ui','icons'])
import enmapboxtestdata
DIR_TESTDATA = os.path.dirname(enmapboxtestdata.__file__)


REPLACE_TMP = True #required for loading *.ui files directly


class TestObjects():
    @staticmethod
    def inMemoryClassification(n=3, nl=10, ns=20, nb=1):
        from enmapbox.gui.classificationscheme import ClassificationScheme
        scheme = ClassificationScheme()
        scheme.createClasses(n)

        drv = gdal.GetDriverByName('MEM')
        assert isinstance(drv, gdal.Driver)

        ds = drv.Create('', ns, nl, bands=nb, eType=gdal.GDT_Byte)

        step = np.ceil(float(nl) / len(scheme))

        assert isinstance(ds, gdal.Dataset)
        for b in range(1,nb+1):
            band = ds.GetRasterBand(b)
            array = np.zeros((nl, ns), dtype=np.uint8)-1
            y0 = 0
            for i, c in enumerate(scheme):
                y1 = min(y0+step, nl-1)
                array[y0:y1,:] = c.label()
                y0 += y1+1
            band.SetCategoryNames(scheme.classNames())
            band.SetColorTable(scheme.gdalColorTable())
        ds.FlushCache()
        return ds



def initQgisApplication(pythonPlugins=None, PATH_QGIS=None):
    """
    Initializes the QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    import site
    if pythonPlugins is None:
        pythonPlugins = []
    assert isinstance(pythonPlugins, list)

    from enmapbox.gui.utils import DIR_REPO
    #pythonPlugins.append(os.path.dirname(DIR_REPO))
    PLUGIN_DIR = os.path.dirname(DIR_REPO)

    if os.path.isdir(PLUGIN_DIR):
        for subDir in os.listdir(PLUGIN_DIR):
            if not subDir.startswith('.'):
                pythonPlugins.append(os.path.join(PLUGIN_DIR, subDir))

    envVar = os.environ.get('QGIS_PLUGINPATH', None)
    if isinstance(envVar, list):
        pythonPlugins.extend(re.split('[;:]', envVar))

    #make plugin paths available to QGIS and Python
    os.environ['QGIS_PLUGINPATH'] = ';'.join(pythonPlugins)
    for p in pythonPlugins:
        sys.path.append(p)

    if isinstance(QgsApplication.instance(), QgsApplication):
        #alread started
        return QgsApplication.instance()
    else:



        if PATH_QGIS is None:
            # find QGIS Path
            if sys.platform == 'darwin':
                #search for the QGIS.app
                import qgis, re
                assert '.app' in qgis.__file__, 'Can not locate path of QGIS.app'
                PATH_QGIS_APP = re.split('\.app[\/]', qgis.__file__)[0]+ '.app'
                PATH_QGIS = os.path.join(PATH_QGIS_APP, *['Contents','MacOS'])

                if not 'GDAL_DATA' in os.environ.keys():
                    os.environ['GDAL_DATA'] = r'/Library/Frameworks/GDAL.framework/Versions/2.1/Resources/gdal'

                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns']))
                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns','qgis']))


            else:
                # assume OSGeo4W startup
                PATH_QGIS = os.environ['QGIS_PREFIX_PATH']

        assert os.path.exists(PATH_QGIS)

        QgsApplication.setGraphicsSystem("raster")
        qgsApp = QgsApplication([], True)
        qgsApp.setPrefixPath(PATH_QGIS, True)
        qgsApp.initQgis()
        return qgsApp

def settings():
    return QSettings('HU-Berlin', 'EnMAP-Box')


def showMessage(message, title, level):
    v = QgsMessageViewer()
    v.setTitle(title)

    v.setMessage(message, QgsMessageOutput.MessageHtml \
                    if message.startswith('<html>')
                    else QgsMessageOutput.MessageText)

    v.showMessage(True)


def file_search(rootdir, pattern, recursive=False, ignoreCase=False):
    assert os.path.isdir(rootdir), "Path is not a directory:{}".format(rootdir)
    regType = type(re.compile('.*'))
    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if isinstance(pattern, regType):
                if pattern.search(file):
                    path = os.path.join(root, file)
                    results.append(path)

            elif (ignoreCase and fnmatch.fnmatch(file.lower(), pattern.lower())) \
                    or fnmatch.fnmatch(file, pattern):

                path = os.path.join(root, file)
                results.append(path)
        if not recursive:
            break
            pass

    return results


def gdalDataset(pathOrDataset, eAccess=gdal.GA_ReadOnly):
    """

    :param pathOrDataset: path or gdal.Dataset
    :return: gdal.Dataset
    """
    if not isinstance(pathOrDataset, gdal.Dataset):
        pathOrDataset = gdal.Open(pathOrDataset, eAccess)
    assert isinstance(pathOrDataset, gdal.Dataset)
    return pathOrDataset



FORM_CLASSES = dict()
loadUI = lambda basename: loadUIFormClass(jp(DIR_UIFILES, basename))


#dictionary to store form classes and avoid multiple calls to read <myui>.ui
FORM_CLASSES = dict()

def loadUIFormClass(pathUi, from_imports=False, resourceSuffix='_py2'):
    """
    Loads Qt UI files (*.ui) while taking care on QgsCustomWidgets.
    Uses PyQt4.uic.loadUiType (see http://pyqt.sourceforge.net/Docs/PyQt4/designer.html#the-uic-module)
    :param pathUi: *.ui file path
    :param from_imports:  is optionally set to use import statements that are relative to '.'. At the moment this only applies to the import of resource modules.
    :param resourceSuffix: is the suffix appended to the basename of any resource file specified in the .ui file to create the name of the Python module generated from the resource file by pyrcc4. The default is '_rc', i.e. if the .ui file specified a resource file called foo.qrc then the corresponding Python module is foo_rc.
    :return: the form class, e.g. to be used in a class definition like MyClassUI(QFrame, loadUi('myclassui.ui'))
    """

    RC_SUFFIX =  resourceSuffix
    assert os.path.exists(pathUi), '*.ui file does not exist: {}'.format(pathUi)

    buffer = StringIO.StringIO() #buffer to store modified XML
    if pathUi not in FORM_CLASSES.keys():
        #parse *.ui xml and replace *.h by qgis.gui
        doc = QDomDocument()

        #remove new-lines. this prevents uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        #to mess up the *.ui xml
        txt = ''.join(open(pathUi).readlines())
        doc.setContent(txt)

        # Replace *.h file references in <customwidget> with <class>Qgs...</class>, e.g.
        #       <header>qgscolorbutton.h</header>
        # by    <header>qgis.gui</header>
        # this is require to compile QgsWidgets on-the-fly
        elem = doc.elementsByTagName('customwidget')
        for child in [elem.item(i) for i in range(elem.count())]:
            child = child.toElement()
            className = str(child.firstChildElement('class').firstChild().nodeValue())
            if className.startswith('Qgs'):
                cHeader = child.firstChildElement('header').firstChild()
                cHeader.setNodeValue('qgis.gui')

        #collect resource file locations
        elem = doc.elementsByTagName('include')
        qrcPathes = []
        for child in [elem.item(i) for i in range(elem.count())]:
            path = child.attributes().item(0).nodeValue()
            if path.endswith('.qrc'):
                qrcPathes.append(path)

        #logger.debug('Load UI file: {}'.format(pathUi))
        buffer.write(doc.toString())
        buffer.flush()
        buffer.seek(0)

        #make resource file directories available to the python path (sys.path)
        baseDir = os.path.dirname(pathUi)
        tmpDirs = []
        for qrcPath in qrcPathes:
            d = os.path.dirname(os.path.join(baseDir, os.path.dirname(qrcPath)))
            if d not in sys.path:
                tmpDirs.append(d)
        sys.path.extend(tmpDirs)

        #load form class
        try:
            FORM_CLASS, _ = uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        except SyntaxError as ex:
            logger.info('{}\n{}:"{}"\ncall instead uic.loadUiType(path,...) directly'.format(pathUi, ex, ex.text))
            FORM_CLASS, _ = uic.loadUiType(pathUi, resource_suffix=RC_SUFFIX)

        FORM_CLASSES[pathUi] = FORM_CLASS

        #remove temporary added directories from python path
        for d in tmpDirs:
            sys.path.remove(d)

    return FORM_CLASSES[pathUi]





def typecheck(variable, type_):
    if isinstance(type_, list):
        for i in range(len(type_)):
            typecheck(variable[i], type_[i])
    else:
        assert isinstance(variable,type_)


from collections import defaultdict
import weakref
class KeepRefs(object):
    __refs__ = defaultdict(list)
    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst

def appendItemsToMenu(menu, itemsToAdd):
    """
    Appends items to QMenu "menu"
    :param menu: the QMenu to be extended
    :param itemsToAdd: QMenu or [list-of-QActions-or-QMenus]
    :return: menu
    """
    assert isinstance(menu, QMenu)
    if isinstance(itemsToAdd, QMenu):
        itemsToAdd = itemsToAdd.children()
    if not isinstance(itemsToAdd, list):
        itemsToAdd = [itemsToAdd]
    for item in itemsToAdd:
        if isinstance(item, QAction):
            item.setParent(menu)
            menu.addAction(item)
            s = ""
        elif isinstance(item, QMenu):
            item.setParent(menu)
            menu.addMenu(menu)
        else:
            s = ""
    return menu

def allSubclasses(cls):
    """
    Returns all subclasses of class 'cls'
    Thx to: http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-class-given-its-name
    :param cls:
    :return:
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in allSubclasses(s)]

class PanelWidgetBase(QgsDockWidget):
    def __init__(self, parent):
        super(PanelWidgetBase, self).__init__(parent)
        self.setupUi(self)


    def _blockSignals(self, widgets, block=True):
        states = dict()
        if isinstance(widgets, dict):
            for w, block in widgets.items():
                states[w] = w.blockSignals(block)
        else:
            for w in widgets:
                states[w] = w.blockSignals(block)
        return states



def check_package(name, package=None, stop_on_error=False):
    try:
        importlib.import_module(name, package)
    except Exception, e:
        if stop_on_error:
            raise Exception('Unable to import package/module "{}"'.format(name))
        return False
    return True


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def getDOMAttributes(elem):
    assert isinstance(elem, QDomElement)
    values = dict()
    attributes = elem.attributes()
    for a in range(attributes.count()):
        attr = attributes.item(a)
        values[attr.nodeName()] = attr.nodeValue()
    return values

def fileSizeString(num, suffix='B', div=1000):
    """
    Returns a human-readable file size string.
    thanks to Fred Cirera
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param num: number in bytes
    :param suffix: 'B' for bytes by default.
    :param div: divisor of num, 1000 by default.
    :return: the file size string
    """
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < div:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= div
    return "{:.1f} {}{}".format(num, unit, suffix)



def geo2pxF(geo, gt):
    """
    Returns the pixel position related to a Geo-Coordinate in floating point precision.
    :param geo: Geo-Coordinate as QgsPoint
    :param gt: GDAL Geo-Transformation tuple, as described in http://www.gdal.org/gdal_datamodel.html
    :return: pixel position as QPointF
    """
    assert isinstance(geo, QgsPoint)
    # see http://www.gdal.org/gdal_datamodel.html
    px = (geo.x() - gt[0]) / gt[1]  # x pixel
    py = (geo.y() - gt[3]) / gt[5]  # y pixel
    return QPointF(px,py)

def geo2px(geo, gt):
    """
    Returns the pixel position related to a Geo-Coordinate as integer number.
    Floating-point coordinate are casted to integer coordinate, e.g. the pixel coordinate (0.815, 23.42) is returned as (0,23)
    :param geo: Geo-Coordinate as QgsPoint
    :param gt: GDAL Geo-Transformation tuple, as described in http://www.gdal.org/gdal_datamodel.html
    :return: pixel position as QPpint
    """
    px = geo2pxF(geo, gt)
    return QPoint(int(px.x()), int(px.y()))

def px2geo(px, gt):
    #see http://www.gdal.org/gdal_datamodel.html
    gx = gt[0] + px.x()*gt[1]+px.y()*gt[2]
    gy = gt[3] + px.x()*gt[4]+px.y()*gt[5]
    return QgsPoint(gx,gy)


class SpatialPoint(QgsPoint):
    """
    Object to keep QgsPoint and QgsCoordinateReferenceSystem together
    """

    @staticmethod
    def fromMapCanvasCenter(mapCanvas):
        assert isinstance(mapCanvas, QgsMapCanvas)
        crs = mapCanvas.mapSettings().destinationCrs()
        return SpatialPoint(crs, mapCanvas.center())

    @staticmethod
    def fromSpatialExtent(spatialExtent):
        assert isinstance(spatialExtent, SpatialExtent)
        crs = spatialExtent.crs()
        return SpatialPoint(crs, spatialExtent.center())

    def __init__(self, crs, *args):
        if not isinstance(crs, QgsCoordinateReferenceSystem):
            crs = QgsCoordinateReferenceSystem(crs)
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(SpatialPoint, self).__init__(*args)
        self.mCrs = crs

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs

    def crs(self):
        return self.mCrs

    def toPixelPosition(self, rasterDataSource, allowOutOfRaster=False):
        """
        Returns the pixel position of this SpatialPoint within the rasterDataSource
        :param rasterDataSource: gdal.Dataset
        :param allowOutOfRaster: set True to return out-of-raster pixel positions, e.g. QPoint(-1,0)
        :return: the pixel position as QPoint
        """
        ds = gdalDataset(rasterDataSource)
        ns, nl = ds.RasterXSize, ds.RasterYSize
        gt = ds.GetGeoTransform()

        pt = self.toCrs(ds.GetProjection())
        if pt is None:
            return None

        px = geo2px(pt, gt)
        if not allowOutOfRaster:
            if px.x() < 0 or px.x() >= ns:
                return None
            if px.y() < 0 or px.y() >= nl:
                return None
        return px

    def toCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        pt = QgsPoint(self)

        if self.mCrs != crs:
            pt = saveTransform(pt, self.mCrs, crs)

        return SpatialPoint(crs, pt) if pt else None

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.crs().toWkt(), self.x(), self.y()), {}

    def __eq__(self, other):
        if not isinstance(other, SpatialPoint):
            return False
        return self.x() == other.x() and \
               self.y() == other.y() and \
               self.crs() == other.crs()

    def __copy__(self):
        return SpatialPoint(self.crs(), self.x(), self.y())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{} {} {}'.format(self.x(), self.y(), self.crs().authid())


def findParent(qObject, parentType, checkInstance = False):
    parent = qObject.parent()
    if checkInstance:
        while parent != None and not isinstance(parent, parentType):
            parent = parent.parent()
    else:
        while parent != None and type(parent) != parentType:
            parent = parent.parent()
    return parent


def saveTransform(geom, crs1, crs2):
    crs1 = QgsCoordinateReferenceSystem(crs1)
    crs2 = QgsCoordinateReferenceSystem(crs2)

    result = None
    if isinstance(geom, QgsRectangle):
        if geom.isEmpty():
            return None


        transform = QgsCoordinateTransform(crs1, crs2);
        try:
            rect = transform.transformBoundingBox(geom);
            result = SpatialExtent(crs2, rect)
        except:
            logger.debug('Can not transform from {} to {} on rectangle {}'.format( \
                crs1.description(), crs2.description(), str(geom)))

    elif isinstance(geom, QgsPoint):

        transform = QgsCoordinateTransform(crs1, crs2);
        try:
            pt = transform.transform(geom);
            result = SpatialPoint(crs2, pt)
        except:
            logger.debug('Can not transform from {} to {} on QgsPoint {}'.format( \
                crs1.description(), crs2.description(), str(geom)))
    return result


class SpatialExtent(QgsRectangle):
    """
    Object to keep QgsRectangle and QgsCoordinateReferenceSystem together
    """
    @staticmethod
    def fromMapCanvas(mapCanvas, fullExtent=False):
        assert isinstance(mapCanvas, QgsMapCanvas)

        if fullExtent:
            extent = mapCanvas.fullExtent()
        else:
            extent = mapCanvas.extent()
        crs = mapCanvas.mapSettings().destinationCrs()
        return SpatialExtent(crs, extent)

    @staticmethod
    def world():
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        ext = QgsRectangle(-180,-90,180,90)
        return SpatialExtent(crs, ext)


    @staticmethod
    def fromRasterSource(pathSrc):
        ds = gdalDataset(pathSrc)
        assert isinstance(ds, gdal.Dataset)
        ns, nl = ds.RasterXSize, ds.RasterYSize
        gt = ds.GetGeoTransform()
        crs = QgsCoordinateReferenceSystem(ds.GetProjection())

        xValues = []
        yValues = []
        for x in [0, ns]:
            for y in [0, nl]:
                px = px2geo(QPoint(x,y), gt)
                xValues.append(px.x())
                yValues.append(px.y())

        return SpatialExtent(crs, min(xValues), min(yValues),
                                  max(xValues), max(yValues))





    @staticmethod
    def fromLayer(mapLayer):
        assert isinstance(mapLayer, QgsMapLayer)
        extent = mapLayer.extent()
        crs = mapLayer.crs()
        return SpatialExtent(crs, extent)

    def __init__(self, crs, *args):
        if not isinstance(crs, QgsCoordinateReferenceSystem):
            crs = QgsCoordinateReferenceSystem(crs)
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(SpatialExtent, self).__init__(*args)
        self.mCrs = crs

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs

    def crs(self):
        return self.mCrs

    def toCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        box = QgsRectangle(self)
        if self.mCrs != crs:
            box = saveTransform(box, self.mCrs, crs)
        return SpatialExtent(crs, box) if box else None

    def combineExtentWith(self, *args):
        if args is None:
            return
        elif isinstance(args[0], SpatialExtent):
            extent2 = args[0].toCrs(self.crs())
            self.combineExtentWith(QgsRectangle(extent2))
        else:
            super(SpatialExtent, self).combineExtentWith(*args)

        return self

    def setCenter(self, centerPoint, crs=None):

        if crs and crs != self.crs():
            trans = QgsCoordinateTransform(crs, self.crs())
            centerPoint = trans.transform(centerPoint)

        delta = centerPoint - self.center()
        self.setXMaximum(self.xMaximum() + delta.x())
        self.setXMinimum(self.xMinimum() + delta.x())
        self.setYMaximum(self.yMaximum() + delta.y())
        self.setYMinimum(self.yMinimum() + delta.y())

        return self

    def __cmp__(self, other):
        if other is None: return 1
        s = ""

    def upperRightPt(self):
        return QgsPoint(*self.upperRight())

    def upperLeftPt(self):
        return QgsPoint(*self.upperLeft())

    def lowerRightPt(self):
        return QgsPoint(*self.lowerRight())

    def lowerLeftPt(self):
        return QgsPoint(*self.lowerLeft())


    def upperRight(self):
        return self.xMaximum(), self.yMaximum()

    def upperLeft(self):
        return self.xMinimum(), self.yMaximum()

    def lowerRight(self):
        return self.xMaximum(), self.yMinimum()

    def lowerLeft(self):
        return self.xMinimum(), self.yMinimum()


    def __eq__(self, other):
        return self.toString() == other.toString()

    def __sub__(self, other):
        raise NotImplementedError()

    def __mul__(self, other):
        raise NotImplementedError()

    def __copy__(self):
        return SpatialExtent(self.crs(), QgsRectangle(self))

    def __reduce_ex__(self, protocol):
        return self.__class__, (self.crs().toWkt(),
                                self.xMinimum(), self.yMinimum(),
                                self.xMaximum(), self.yMaximum()
                                ), {}
    def __str__(self):
        return self.__repr__()

    def __repr__(self):

        return '{} {} {}'.format(self.upperLeft(), self.lowerRight(), self.crs().authid())


class IconProvider:
    """
    Provides icons
    """
    EnMAP_Logo = ':/enmapbox/png/icons/enmapbox.png'
    Map_Link_Remove = ':/enmapbox/png/icons/link_open.png'
    Map_Link = ':/enmapbox/png/icons/link_basic.png'
    Map_Link_Center = ':/enmapbox/png/icons/link_center.png'
    Map_Link_Extent = ':/enmapbox/png/icons/link_mapextent.png'
    Map_Link_Scale = ':/enmapbox/png/icons/link_mapscale.png'
    Map_Link_Scale_Center = ':/enmapbox/png/icons/link_mapscale_center.png'
    Map_Zoom_In = ':/enmapbox/png/icons/mActionZoomOut.png'
    Map_Zoom_Out = ':/enmapbox/png/icons/mActionZoomIn.png'
    Map_Pan = ':/enmapbox/png/icons/mActionPan.png'
    Map_Touch = ':/enmapbox/png/icons/mActionTouch.png'
    File_RasterMask = ':/enmapbox/png/icons/filelist_mask.png'
    File_RasterRegression = ':/enmapbox/png/icons/filelist_regression.png'
    File_RasterClassification = ':/enmapbox/png/icons/filelist_classification.png'
    File_Raster = ':/enmapbox/png/icons/filelist_image.png'
    File_Vector_Point = ':/enmapbox/png/icons/mIconPointLayer.png'
    File_Vector_Line = ':/enmapbox/png/icons/mIconLineLayer.png'
    File_Vector_Polygon = ':/enmapbox/png/icons/mIconPolygonLayer.png'

    Dock = ':/enmapbox/png/icons/viewlist_dock.png'
    MapDock = ':/enmapbox/png/icons/viewlist_mapdock.png'
    SpectralDock = ':/enmapbox/png/icons/viewlist_spectrumdock.png'


    @staticmethod
    def resourceIconsPaths():
        import inspect
        return inspect.getmembers(IconProvider, lambda a: not(inspect.isroutine(a)) and a.startswith(':'))

    @staticmethod
    def icon(path):
        if path is None:
            path = IconProvider.EnMAP_Logo

        assert isinstance(path, str)
        icon = None
        if path in IconProvider.resourceIconsPaths():
            icon = QIcon(path)
        else:
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(path))

        return icon

    @staticmethod
    def test():
        required = set(['png','svg'])
        available = set([str(p) for p in QImageReader.supportedImageFormats()])
        missing = required - available



        for name, uri in IconProvider.resourceIconsPaths():
            icon = QIcon(uri)
            w = h = 16
            s = icon.actualSize(QSize(w,h))

class EnMAPBoxMimeData(QMimeData):

    def __init__(self):
        super(EnMAPBoxMimeData, self).__init__()
        self.mData = None

    def setEnMAPBoxData(self, data):
        self.mData = data

    def enmapBoxData(self):
        return self.mData

    def hasEnMAPBoxData(self):
        return self.mData != None



class MimeDataHelper():
    """
    A class to simplify I/O on QMimeData objects, aiming on Drag & Drop operations.
    """


    from weakref import WeakValueDictionary
    #PYTHON_OBJECTS = WeakValueDictionary()
    PYTHON_OBJECTS = dict()

    MDF_DOCKTREEMODELDATA = 'application/enmapbox.docktreemodeldata'
    MDF_DATASOURCETREEMODELDATA = 'application/enmapbox.datasourcetreemodeldata'
    MDF_LAYERTREEMODELDATA = 'application/qgis.layertreemodeldata'
    MDF_PYTHON_OBJECTS = 'application/enmapbox/objectreference'
    MDF_SPECTRALPROFILE = 'application/enmapbox/spectralprofile'
    MDF_SPECTRALLIBRARY = 'application/enmapbox/spectrallibrary'
    MDF_URILIST = 'text/uri-list'
    MDF_TEXT_HTML = 'text/html'
    MDF_TEXT_PLAIN = 'text/plain'

    @staticmethod
    def storeObjectReferences(mimeData, listOfObjects):
        """
        Saves a reference into QMimeData "mimeData"
        :param mimeData: QMimeData
        :param listOfObjects: any python object or [list-of-python-objects]
        :return: QMimeData
        """
        MimeDataHelper.PYTHON_OBJECTS.clear()
        if not isinstance(listOfObjects, list):
            listOfObjects = [listOfObjects]

        refIds = []
        for o in listOfObjects:
            idStr = str(id(o))
            MimeDataHelper.PYTHON_OBJECTS[idStr] = o
            refIds.append(idStr)

        mimeData.setData(MimeDataHelper.MDF_PYTHON_OBJECTS, ';'.join(refIds))
        return mimeData


    def __init__(self, mimeData):
        assert isinstance(mimeData, QMimeData)
        self.mMimeData = mimeData
        self.mMimeDataFormats = [str(f) for f in self.mMimeData.formats()]
        self.doc = QDomDocument()

    def containsMimeType(self, types):
        """
        Returns True if at least one of the types in "types" is defined.
        :param types: MimeDataFormat Type of [list-of-mime-data-format-types]
        :return: True | False
        """
        if not isinstance(types, list):
            types = [types]
        for t in types:
            if t == MimeDataHelper.MDF_LAYERTREEMODELDATA:
                self.setContent(t)
                root = self.doc.documentElement()
                nodes = root.elementsByTagName('layer-tree-layer')
                if nodes.count() > 0:
                    id = nodes.item(0).toElement().attribute('id')
                    # we can read layer-tree-layer xml format only if is exists in same QgsMapLayerRegistry
                    return  QgsMapLayerRegistry.instance().mapLayer(id) is not None
            elif t in self.mMimeDataFormats:
                return True
        return False

    def setContent(self, format):
        """

        :param format:
        :return:
        """
        r = False
        if format in self.mMimeDataFormats:
            r = self.doc.setContent(self.mMimeData.data(format))
        return r

    def hasPythonObjects(self):
        """
        Returns whether any Python object references are available.
        :return: True or False
        """
        if self.containsMimeType(MimeDataHelper.MDF_PYTHON_OBJECTS):
            refIds = str(self.data(MimeDataHelper.MDF_PYTHON_OBJECTS)).split(';')
            for id in refIds:
                if id in MimeDataHelper.PYTHON_OBJECTS.keys():
                    return True
        return False

    def pythonObjects(self, typeFilter=None):
        """
        Returns the referred python objects.
        :param typeFilter: type or [list-of-types] of python objects to be returned.
        :return: [list-of-python-objects]
        """
        objectList = []

        if typeFilter and not isinstance(typeFilter, list):
            typeFilter = [typeFilter]
        else:
            assert isinstance(typeFilter, list)

        if self.hasPythonObjects():

            for refId in str(self.data(MimeDataHelper.MDF_PYTHON_OBJECTS)).split(';'):
                o = MimeDataHelper.PYTHON_OBJECTS.get(refId)

                if o is not None:
                    objectList.append(o)
        if typeFilter:
            objectList = [o for o in objectList if type(o) in typeFilter]

        return objectList

    def hasLayerTreeModelData(self):
        """
        :return: True, if LayerTreeModelData can be extracted from here
        """
        return self.containsMimeType([
            MimeDataHelper.MDF_DOCKTREEMODELDATA,
            MimeDataHelper.MDF_LAYERTREEMODELDATA])

    def layerTreeModelNodes(self):
        from enmapbox.gui.treeviews import TreeNodeProvider
        assert self.hasLayerTreeModelData()
        nodes = []
        if self.mMimeData.hasFormat(MimeDataHelper.MDF_DOCKTREEMODELDATA):
            self.setContent(MimeDataHelper.MDF_DOCKTREEMODELDATA)
            root = self.doc.documentElement()
            child = root.firstChildElement()
            while not child.isNull():
                child = child.toElement()
                tagName = str(child.tagName())
                if 'dock-tree-node' in tagName:
                    nodes.append(TreeNodeProvider.CreateNodeFromXml(child))
                elif tagName in ['layer-tree-layer', 'layer-tree-group']:
                    nodes.append(QgsLayerTreeNode.readXML(child))
                else:
                    raise NotImplementedError()
                child = child.nextSibling()

        elif self.mMimeData.hasFormat(MimeDataHelper.MDF_DOCKTREEMODELDATA):
            s = ""
        nodes = [n for n in nodes if n is not None]
        return nodes

    def _readMapLayersFromXML(self, root):

        nodeList = root.elementsByTagName('layer-tree-layer')
        reg = QgsMapLayerRegistry.instance()
        layers = []
        for i in range(nodeList.count()):
            node = nodeList.item(i).toElement()
            name = node.attribute('name')
            lyrid = node.attribute('id')
            lyr = reg.mapLayer(lyrid)
            if lyr:
                lyr.setLayerName(name)
                layers.append(lyr)
        return layers

    def hasMapLayers(self):
        """
        :return: True, if the QMimeData contains QgsMapLayer
        """
        return self.containsMimeType([MimeDataHelper.MDF_LAYERTREEMODELDATA])

    def mapLayers(self):
        """
        :return: [list-of-QgsMapLayer]
        """
        layers = []
        if self.setContent(MimeDataHelper.MDF_LAYERTREEMODELDATA):
            layers = self._readMapLayersFromXML(self.doc.documentElement())
        if len(layers) == 0:
            s= ""
        return layers

    def hasUrls(self):
        """
        return self.mMimeData.hasUrls()
        """
        return self.mMimeData.hasUrls()

    def urls(self):
        """
        :return: self.mMimeData.urls()
        """
        return self.mMimeData.urls()

    def data(self, mimeDataKey):
        """
        :param mimeDataKey:
        :return: self.mMimeData.data(mimeDataKey)
        """
        return self.mMimeData.data(mimeDataKey)


    def hasDataSources(self):
        """
        :return: True, if any data can be returned as EnMAPBox DataSource
        """
        return self.containsMimeType([
                MimeDataHelper.MDF_DATASOURCETREEMODELDATA,
                MimeDataHelper.MDF_LAYERTREEMODELDATA,
                MimeDataHelper.MDF_URILIST])


    def dataSources(self):
        """
        :return: [list-of-EnMAPBox DataSources]
        """
        dataSources = []
        from enmapbox.gui.datasources import DataSourceFactory
        if self.setContent(MimeDataHelper.MDF_DATASOURCETREEMODELDATA):
            root = self.doc.documentElement()
            nodeList = root.elementsByTagName('datasource-tree-node')
            cp = QgsObjectCustomProperties()
            for i in range(nodeList.count()):
                node = nodeList.item(i).toElement()
                cp.readXml(node)
                name = node.attribute('name')
                uri = cp.value('uri')
                dataSources.append(DataSourceFactory.Factory(uri, name=name))

        elif MimeDataHelper.MDF_LAYERTREEMODELDATA in self.formats:
            layers = self._readMapLayersFromXML(self.doc.documentElement())
            dataSources = [DataSourceFactory.Factory(l) for l in layers]

        elif MimeDataHelper.MDF_URILIST in self.formats:
            dataSources = [DataSourceFactory.Factory(uri) for uri in self.mimeData.urls()]

        dataSources = list(set([d for d in dataSources if d is not None]))
        return dataSources


