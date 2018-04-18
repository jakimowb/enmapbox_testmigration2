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

import os, sys, importlib, tempfile, re, six, fnmatch, io, pickle, zipfile



from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtXml import *
from PyQt5 import uic
from osgeo import gdal
import numpy as np
import enmapbox.gui

from enmapbox import messageLog
messageLog = messageLog

jp = os.path.join

DIR_ENMAPBOX = os.path.dirname(enmapbox.__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui', 'ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui', 'ui', 'icons'])

DIR_TESTDATA = os.path.join(DIR_ENMAPBOX, 'enmapboxtestdata')

REPLACE_TMP = True  # required for loading *.ui files directly

######### Lookup  tables
METRIC_EXPONENTS = {
    "nm": -9, "um": -6, u"µm": -6, "mm": -3, "cm": -2, "dm": -1, "m": 0, "hm": 2, "km": 3
}
# add synonyms
METRIC_EXPONENTS['nanometers'] = METRIC_EXPONENTS['nm']
METRIC_EXPONENTS['micrometers'] = METRIC_EXPONENTS['um']
METRIC_EXPONENTS['millimeters'] = METRIC_EXPONENTS['mm']
METRIC_EXPONENTS['centimeters'] = METRIC_EXPONENTS['cm']
METRIC_EXPONENTS['decimeters'] = METRIC_EXPONENTS['dm']
METRIC_EXPONENTS['meters'] = METRIC_EXPONENTS['m']
METRIC_EXPONENTS['hectometers'] = METRIC_EXPONENTS['hm']
METRIC_EXPONENTS['kilometers'] = METRIC_EXPONENTS['km']

LUT_WAVELENGTH = dict({'B': 480,
                       'G': 570,
                       'R': 660,
                       'NIR': 850,
                       'SWIR': 1650,
                       'SWIR1': 1650,
                       'SWIR2': 2150
                       })


def mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


class TestObjects():
    @staticmethod
    def inMemoryClassification(n=3, nl=10, ns=20, nb=1):
        from enmapbox.gui.classificationscheme import ClassificationScheme
        scheme = ClassificationScheme()
        scheme.createClasses(n)

        drv = gdal.GetDriverByName('MEM')
        assert isinstance(drv, gdal.Driver)

        ds = drv.Create('', ns, nl, bands=nb, eType=gdal.GDT_Byte)

        step = int(np.ceil(float(nl) / len(scheme)))

        assert isinstance(ds, gdal.Dataset)
        for b in range(1, nb + 1):
            band = ds.GetRasterBand(b)
            array = np.zeros((nl, ns), dtype=np.uint8) - 1
            y0 = 0
            for i, c in enumerate(scheme):
                y1 = min(y0 + step, nl - 1)
                array[y0:y1, :] = c.label()
                y0 += y1 + 1
            band.SetCategoryNames(scheme.classNames())
            band.SetColorTable(scheme.gdalColorTable())
        ds.FlushCache()
        return ds

def initQgisApplication(pythonPlugins=None, PATH_QGIS=None, qgisDebug=False, qgisResourceDir=None):
    """
    Initializes the QGIS Environment
    :return: QgsApplication instance of local QGIS installation
    """
    import site
    if pythonPlugins is None:
        pythonPlugins = []
    assert isinstance(pythonPlugins, list)

    if os.path.exists(os.path.join(DIR_REPO, 'qgisresources')):
        qgisResourceDir = os.path.join(DIR_REPO, 'qgisresources')
    if isinstance(qgisResourceDir, str):
        assert os.path.isdir(qgisResourceDir)
        import importlib, re
        modules = [m for m in os.listdir(qgisResourceDir) if re.search(r'[^_].*\.py', m)]
        modules = [m[0:-3] for m in modules]
        for m in modules:
            mod = importlib.import_module('qgisresources.{}'.format(m))
            if "qInitResources" in dir(mod):
                mod.qInitResources()

    envVar = os.environ.get('QGIS_PLUGINPATH', None)
    if isinstance(envVar, list):
        pythonPlugins.extend(re.split('[;:]', envVar))

    # make plugin paths available to QGIS and Python
    os.environ['QGIS_PLUGINPATH'] = ';'.join(pythonPlugins)
    os.environ['QGIS_DEBUG'] = '1' if qgisDebug else '0'
    for p in pythonPlugins:
        sys.path.append(p)

    if isinstance(QgsApplication.instance(), QgsApplication):

        return QgsApplication.instance()

    else:

        if PATH_QGIS is None:
            # find QGIS Path
            if sys.platform == 'darwin':
                # search for the QGIS.app
                import qgis, re
                assert '.app' in qgis.__file__, 'Can not locate path of QGIS.app'
                PATH_QGIS_APP = re.split(r'\.app[\/]', qgis.__file__)[0] + '.app'
                PATH_QGIS = os.path.join(PATH_QGIS_APP, *['Contents', 'MacOS'])

                if not 'GDAL_DATA' in os.environ.keys():
                    os.environ['GDAL_DATA'] = r'/Library/Frameworks/GDAL.framework/Versions/Current/Resources/gdal'

                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns']))
                QApplication.addLibraryPath(os.path.join(PATH_QGIS_APP, *['Contents', 'PlugIns', 'qgis']))


            else:
                # assume OSGeo4W startup
                PATH_QGIS = os.environ['QGIS_PREFIX_PATH']

        assert os.path.exists(PATH_QGIS)

        qgsApp = QgsApplication([], True)
        qgsApp.setPrefixPath(PATH_QGIS, True)
        qgsApp.initQgis()

        def printQgisLog(msg, tag, level):
            if tag not in ['Processing']:
                if tag in ['Python warning', 'warning']:
                    import re
                    if re.search('(Deprecation|Import)Warning', msg) is not None:
                        return
                    else:
                        return
                print(msg)

        QgsApplication.instance().messageLog().messageReceived.connect(printQgisLog)

        return qgsApp



def settings():
    """
    Returns the QSettings object with EnMAPBox Settings
    :return:
    """
    print('DEPRECATED CALL enmapbox.gui.utils.settings()')
    from enmapbox.gui.settings import qtSettingsObj
    return qtSettingsObj()


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


loadUI = lambda basename: loadUIFormClass(jp(DIR_UIFILES, basename))

# dictionary to store form classes and avoid multiple calls to read <myui>.ui
FORM_CLASSES = dict()



def loadUIFormClass(pathUi, from_imports=False, resourceSuffix=''):
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


    if pathUi not in FORM_CLASSES.keys():
        #parse *.ui xml and replace *.h by qgis.gui
        doc = QDomDocument()

        #remove new-lines. this prevents uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        #to mess up the *.ui xml

        f = open(pathUi, 'r')
        txt = ''.join(f.readlines())
        f.close()
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



        buffer = io.StringIO()  # buffer to store modified XML
        buffer.write(doc.toString())
        buffer.flush()
        buffer.seek(0)


        #make resource file directories available to the python path (sys.path)
        baseDir = os.path.dirname(pathUi)
        tmpDirs = []
        for qrcPath in qrcPathes:
            d = os.path.abspath(os.path.join(baseDir, qrcPath))
            d = os.path.dirname(d)
            if d not in sys.path:
                tmpDirs.append(d)
        sys.path.extend(tmpDirs)

        #load form class
        try:
            FORM_CLASS, _ = uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
        except SyntaxError as ex:
            FORM_CLASS, _ = uic.loadUiType(pathUi, resource_suffix=RC_SUFFIX)

        buffer.close()
        buffer = None
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
        assert isinstance(variable, type_)


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
            # item.setParent(menu)
            sub = menu.addMenu(item.title())
            sub.setIcon(item.icon())
            appendItemsToMenu(sub, item.children()[1:])
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
    except Exception as e:
        if stop_on_error:
            raise Exception('Unable to import package/module "{}"'.format(name))
        return False
    return True


def zipdir(pathDir, pathZip):
    """
    :param pathDir: directory to compress
    :param pathZip: path to new zipfile
    """
    # thx to https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    """
    import zipfile
    assert os.path.isdir(pathDir)
    zipf = zipfile.ZipFile(pathZip, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(pathDir):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    """
    relroot = os.path.abspath(os.path.join(pathDir, os.pardir))
    with zipfile.ZipFile(pathZip, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(pathDir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)


def convertMetricUnit(value, u1, u2):
    """converts value, given in unit u1, to u2"""
    assert u1 in METRIC_EXPONENTS.keys()
    assert u2 in METRIC_EXPONENTS.keys()

    e1 = METRIC_EXPONENTS[u1]
    e2 = METRIC_EXPONENTS[u2]

    return value * 10 ** (e1 - e2)


def defaultBands(dataset):
    """
    Returns a list of 3 default bands
    :param dataset:
    :return:
    """
    if isinstance(dataset, str):
        return defaultBands(gdal.Open(dataset))
    elif isinstance(dataset, QgsRasterDataProvider):
        return defaultBands(dataset.dataSourceUri())
    elif isinstance(dataset, QgsRasterLayer):
        return defaultBands(dataset.source())
    elif isinstance(dataset, gdal.Dataset):

        db = dataset.GetMetadataItem(str('default_bands'), str('ENVI'))
        if db != None:
            db = [int(n) for n in re.findall('\d+')]
            return db
        db = [0, 0, 0]
        cis = [gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand]
        for b in range(dataset.RasterCount):
            band = dataset.GetRasterBand(b + 1)
            assert isinstance(band, gdal.Band)
            ci = band.GetColorInterpretation()
            if ci in cis:
                db[cis.index(ci)] = b
        if db != [0, 0, 0]:
            return db

        rl = QgsRasterLayer(dataset.GetFileList()[0])
        defaultRenderer = rl.renderer()
        if isinstance(defaultRenderer, QgsRasterRenderer):
            db = defaultRenderer.usesBands()
            if len(db) == 0:
                return [0, 1, 2]
            if len(db) > 3:
                db = db[0:3]
            db = [b-1 for b in db]
        return db

    else:
        raise Exception()


def bandClosestToWavelength(dataset, wl, wl_unit='nm'):
    """
    Returns the band index of an image dataset closest to wavelength `wl`.
    :param dataset: str | gdal.Dataset
    :param wl: wavelength to search the closed band for
    :param wl_unit: unit of wavelength. Default = nm
    :return: band index | 0 of wavelength information is not provided
    """
    if isinstance(wl, str):
        assert wl.upper() in LUT_WAVELENGTH.keys(), wl
        return bandClosestToWavelength(dataset, LUT_WAVELENGTH[wl.upper()], wl_unit='nm')
    else:
        try:
            wl = float(wl)
            ds_wl, ds_wlu = parseWavelength(dataset)

            if ds_wl is None or ds_wlu is None:
                return 0


            if ds_wlu != wl_unit:
                wl = convertMetricUnit(wl, wl_unit, ds_wlu)
            return int(np.argmin(np.abs(ds_wl - wl)))
        except:
            pass
    return 0


def parseWavelength(dataset):
    """
    Returns the wavelength + wavelength unit of a dataset
    :param dataset:
    :return: (wl, wl_u) or (None, None), if not existing
    """

    wl = None
    wlu = None

    if isinstance(dataset, str):
        return parseWavelength(gdal.Open(dataset))
    elif isinstance(dataset, QgsRasterDataProvider):
        return parseWavelength(dataset.dataSourceUri())
    elif isinstance(dataset, QgsRasterLayer):
        return parseWavelength(dataset.source())
    elif isinstance(dataset, gdal.Dataset):

        for domain in dataset.GetMetadataDomainList():
            # see http://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html for supported wavelength units

            mdDict = dataset.GetMetadata_Dict(domain)

            for key, values in mdDict.items():
                key = key.lower()
                if re.search('wavelength$', key, re.I):
                    tmp = re.findall('\d*\.\d+|\d+', values)  # find floats
                    if len(tmp) != dataset.RasterCount:
                        tmp = re.findall('\d+', values)  # find integers
                    if len(tmp) == dataset.RasterCount:
                        wl = np.asarray([float(w) for w in tmp])

                if re.search(r'wavelength.units?', key):
                    if re.search('(Micrometers?|um)', values, re.I):
                        wlu = 'um'  # fix with python 3 UTF
                    elif re.search('(Nanometers?|nm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Millimeters?|mm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Centimeters?|cm)', values, re.I):
                        wlu = 'nm'
                    elif re.search('(Meters?|m)', values, re.I):
                        wlu = 'nm'
                    elif re.search('Wavenumber', values, re.I):
                        wlu = '-'
                    elif re.search('GHz', values, re.I):
                        wlu = 'GHz'
                    elif re.search('MHz', values, re.I):
                        wlu = 'MHz'
                    elif re.search('Index', values, re.I):
                        wlu = '-'
                    else:
                        wlu = '-'

        if wl is not None and len(wl) > dataset.RasterCount:
            wl = wl[0:dataset.RasterCount]

    return wl, wlu


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
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
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
    assert isinstance(geo, QgsPointXY)
    # see http://www.gdal.org/gdal_datamodel.html
    px = (geo.x() - gt[0]) / gt[1]  # x pixel
    py = (geo.y() - gt[3]) / gt[5]  # y pixel
    return QPointF(px,py)


def geo2px(geo, gt):
    """
    Returns the pixel position related to a Geo-Coordinate as integer number.
    Floating-point coordinate are casted to integer coordinate, e.g. the pixel coordinate (0.815, 23.42) is returned as (0,23)
    :param geo: Geo-Coordinate as QgsPointXY
    :param gt: GDAL Geo-Transformation tuple, as described in http://www.gdal.org/gdal_datamodel.html
    :return: pixel position as QPpint
    """
    px = geo2pxF(geo, gt)
    return QPoint(int(px.x()), int(px.y()))



def px2geo(px, gt):
    """
    Converts a pixel coordinate into a geo-coordinate
    :param px:
    :param gt:
    :return:
    """
    #see http://www.gdal.org/gdal_datamodel.html
    gx = gt[0] + px.x()*gt[1]+px.y()*gt[2]
    gy = gt[3] + px.x()*gt[4]+px.y()*gt[5]
    return QgsPointXY(gx,gy)


class SpatialPoint(QgsPointXY):
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

    def __hash__(self):
        return hash(str(self))

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
        pt = QgsPointXY(self)

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



def findParent(qObject, parentType, checkInstance=False):
    parent = qObject.parent()
    if checkInstance:
        while parent != None and not isinstance(parent, parentType):
            parent = parent.parent()
    else:
        while parent != None and type(parent) != parentType:
            parent = parent.parent()
    return parent


def createCRSTransform(src, dst):
    assert isinstance(src, QgsCoordinateReferenceSystem)
    assert isinstance(dst, QgsCoordinateReferenceSystem)
    t = QgsCoordinateTransform()
    t.setSourceCrs(src)
    t.setDestinationCrs(dst)
    return t

def saveTransform(geom, crs1, crs2):
    assert isinstance(crs1, QgsCoordinateReferenceSystem)
    assert isinstance(crs2, QgsCoordinateReferenceSystem)

    result = None
    if isinstance(geom, QgsRectangle):
        if geom.isEmpty():
            return None


        transform = QgsCoordinateTransform()
        transform.setSourceCrs(crs1)
        transform.setDestinationCrs(crs2)
        try:
            rect = transform.transformBoundingBox(geom);
            result = SpatialExtent(crs2, rect)
        except:
            messageLog('Can not transform from {} to {} on rectangle {}'.format( \
                crs1.description(), crs2.description(), str(geom)))

    elif isinstance(geom, QgsPointXY):

        transform = QgsCoordinateTransform();
        transform.setSourceCrs(crs1)
        transform.setDestinationCrs(crs2)
        try:
            pt = transform.transform(geom);
            result = SpatialPoint(crs2, pt)
        except:
            messageLog('Can not transform from {} to {} on QgsPointXY {}'.format( \
                crs1.description(), crs2.description(), str(geom)))
    return result

def scaledUnitString(num, infix=' ', suffix='B', div=1000):
    """
    Returns a human-readable file size string.
    thanks to Fred Cirera
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    :param num: number in bytes
    :param suffix: 'B' for bytes by default.
    :param div: divisor of num, 1000 by default.
    :return: the file size string
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < div:
            return "{:3.1f}{}{}{}".format(num, infix, unit, suffix)
        num /= div
    return "{:.1f}{}{}{}".format(num, infix, unit, suffix)


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

    def spatialCenter(self):
        return SpatialPoint(self.crs(), self.center())

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
        return QgsPointXY(*self.upperRight())

    def upperLeftPt(self):
        return QgsPointXY(*self.upperLeft())

    def lowerRightPt(self):
        return QgsPointXY(*self.lowerRight())

    def lowerLeftPt(self):
        return QgsPointXY(*self.lowerLeft())


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


    def __hash__(self):
        return hash(str(self))

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
        return inspect.getmembers(IconProvider, lambda a: not (inspect.isroutine(a)) and a.startswith(':'))

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
        required = set(['png', 'svg'])
        available = set([p for p in QImageReader.supportedImageFormats()])
        missing = required - available

        for name, uri in IconProvider.resourceIconsPaths():
            icon = QIcon(uri)
            w = h = 16
            s = icon.actualSize(QSize(w, h))


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



class QgisInterfaceMockup(QgisInterface):

    @staticmethod
    def create():

        iface = QgisInterfaceMockup()

        import qgis.utils
        #import processing
        #p = processing.classFactory(iface)
        if not isinstance(qgis.utils.iface, QgisInterface):

            import processing
            qgis.utils.iface = iface
            processing.Processing.initialize()

            import pkgutil
            prefix = str(processing.__name__ + '.')
            for importer, modname, ispkg in pkgutil.walk_packages(processing.__path__, prefix=prefix):
                try:
                    module = __import__(modname, fromlist="dummy")
                    if hasattr(module, 'iface'):
                        print(modname)
                        module.iface = iface
                except:
                    pass

        return iface


    def __init__(self, *args, **kwds):
        super(QgisInterfaceMockup, self).__init__(*args, **kwds)

        self.mMapCanvas = QgsMapCanvas()
        self.mMessageBar = QgsMessageBar()



    def iconSize(self, *args, **kwargs):
        return QSize(60,60)

    def mapCanvas(self, *args, **kwargs):
        return self.mMapCanvas

    def mapCanvases(self, *args, **kwargs):
        return [self.mMapCanvas]

    def messageBar(self):

        return self.mMessageBar

if __name__ == '__main__':
    from enmapboxtestdata import enmap

    for b in ['B', 'G', 'R', 'NIR', 'SWIR']:
        print(bandClosestToWavelength(enmap, b))
