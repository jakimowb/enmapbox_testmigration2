import os, sys, importlib, re, six, logging, fnmatch
logger = logging.getLogger(__name__)
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyQt4 import uic
import enmapbox.gui
jp = os.path.join

DIR_ENMAPBOX = os.path.dirname(enmapbox.__file__)
DIR_REPO = os.path.dirname(DIR_ENMAPBOX)
DIR_SITEPACKAGES = os.path.join(DIR_REPO, 'site-packages')
DIR_UIFILES = os.path.join(DIR_ENMAPBOX, *['gui','ui'])
DIR_ICONS = os.path.join(DIR_ENMAPBOX, *['gui','ui','icons'])
import enmapbox.testdata
DIR_TESTDATA = os.path.dirname(enmapbox.testdata.__file__)
SETTINGS = QSettings(QSettings.UserScope, 'HU Geomatics', 'EnMAP-Box')

def file_search(rootdir, pattern, recursive=False, ignoreCase=False):
    assert os.path.isdir(rootdir), "Path is not a directory:{}".format(rootdir)

    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if (ignoreCase and fnmatch.fnmatch(file.lower(), pattern.lower())) \
                    or fnmatch.fnmatch(file, pattern):
                results.append(os.path.join(root, file))
        if not recursive:
            break
            pass

    return results


loadUI = lambda basename: loadUIFormClass(jp(DIR_UIFILES, basename))

FORM_CLASSES = dict()

def loadUIFormClass(pathUi, from_imports=False):
    """
    Load UI files and takes care on Qgs custom widgets
    :param pathUi:
    :param from_imports:
    :return:
    """
    RC_SUFFIX =  '_py3' if six.PY3 else '_py2'
    DIR_GUI = os.path.dirname(pathUi)
    assert os.path.exists(pathUi)
    if pathUi not in FORM_CLASSES.keys():
        add_and_remove = DIR_GUI not in sys.path
        if add_and_remove:
            sys.path.append(DIR_GUI)


        #replace for <customwidget> with <class>Qgs...</class>
        #       <header>qgscolorbutton.h</header>
        # by    <header>qgis.gui</header>

        if True:
            tmp = jp(os.path.dirname(pathUi), 'tmp.ui')

            doc = QDomDocument()
            doc.setContent(QFile(pathUi))
            elem = doc.elementsByTagName('customwidget')
            overwrite = False
            for child in [elem.item(i) for i in range(elem.count())]:
                child = child.toElement()
                className = str(child.firstChildElement('class').firstChild().nodeValue())
                if className.startswith('Qgs'):
                    cHeader = child.firstChildElement('header').firstChild()
                    cHeader.setNodeValue('qgis.gui')
                    overwrite=True
            if overwrite:
                s = str(doc.toString())
                file = open(tmp, 'w')
                file.write(s)
                file.close()

                pathUi = tmp
        logger.debug('Load UI file: {}'.format(pathUi))
        FORM_CLASS, _ = uic.loadUiType(pathUi,from_imports=from_imports, resource_suffix=RC_SUFFIX)

        if add_and_remove:
            sys.path.remove(DIR_GUI)
        FORM_CLASSES[pathUi] = FORM_CLASS

    return FORM_CLASSES[pathUi]



def typecheck(variable, type_):
    if isinstance(type_, list):
        for i in range(len(type_)):
            typecheck(variable[i], type_[i])
    else:
        assert isinstance(variable,type_)


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

def add_to_sys_path(paths):
    if not isinstance(paths, list):
        paths = [paths]
    paths = [os.path.normpath(p) for p in paths]
    existing = [os.path.normpath(p) for p in sys.path]
    for p in paths:
        if os.path.isdir(p) and p not in existing:
           #sys.path.insert(0, p)
            sys.path.append(p)
            existing.append(p)



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

class SpatialPoint(QgsPoint):
    """
    Object to keep QgsPoint and QgsCoordinateReferenceSystem together
    """
    def __init__(self, crs, *args):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        super(SpatialPoint, self).__init__(*args)
        self.mCrs = crs

    def setCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        self.mCrs = crs

    def crs(self):
        return self.mCrs

    def toCrs(self, crs):
        assert isinstance(crs, QgsCoordinateReferenceSystem)
        pt = QgsPoint(self)
        if self.mCrs != crs:
            trans = QgsCoordinateTransform(self.mCrs, crs)
            box = trans.transform(pt)
        return SpatialPoint(crs, pt)

    def __copy__(self):
        return SpatialExtent(self.crs(), QgsRectangle(self))

    def __repr__(self):
        return '{} {} {}'.format(self.x(), self.y(), self.crs().authid())

class SpatialExtent(QgsRectangle):
    """
    Object to keep QgsRectangle and QgsCoordinateReferenceSystem together
    """
    @staticmethod
    def fromMapCanvas(mapCanvas):
        assert isinstance(mapCanvas, QgsMapCanvas)
        extent = mapCanvas.extent()
        crs = mapCanvas.mapSettings().destinationCrs()
        return SpatialExtent(crs, extent)

    @staticmethod
    def fromLayer(mapLayer):
        assert isinstance(mapLayer, QgsMapLayer)
        extent = mapLayer.extent()
        crs = mapLayer.crs()
        return SpatialExtent(crs, extent)

    def __init__(self, crs, *args):
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
            trans = QgsCoordinateTransform(self.mCrs, crs)
            box = trans.transformBoundingBox(box)
        return SpatialExtent(crs, box)

    def __copy__(self):
        return SpatialExtent(self.crs(), QgsRectangle(self))

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

    def __eq__(self, other):
        s = ""

    def __sub__(self, other):
        raise NotImplementedError()

    def __mul__(self, other):
        raise NotImplementedError()

    def upperRight(self):
        return self.xMaximum(), self.yMaximum()

    def upperLeft(self):
        return self.xMinimum(), self.yMaximum()

    def lowerRight(self):
        return self.xMaximum(), self.yMinimum()

    def lowerLeft(self):
        return self.xMinimum(), self.yMinimum()


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
            if w != s.width() or h != s.height():
                print((name, uri, s.width(), s.height()))
                s = ""


class MimeDataHelper():

    MIME_DOCKTREEMODELDATA = 'application/enmapbox.docktreemodeldata'
    MIME_DATASOURCETREEMODELDATA = 'application/enmapbox.datasourcetreemodeldata'
    MIME_LAYERTREEMODELDATA = 'application/qgis.layertreemodeldata'
    MIME_URILIST = 'text/uri-list'
    MIME_TEXT_HTML = 'text/html'
    MIME_TEXT_PLAIN = 'text/plain'

    def __init__(self, mimeData):
        assert isinstance(mimeData, QMimeData)
        self.mimeData = mimeData
        self.formats = [str(f) for f in self.mimeData.formats()]
        self.doc = QDomDocument()

    def mimeTypeCheck(self, types):
        if not isinstance(types, list):
            types = [types]
        for t in types:
            if t == MimeDataHelper.MIME_LAYERTREEMODELDATA:
                self.setContent(t)
                root = self.doc.documentElement()
                nodes = root.elementsByTagName('layer-tree-layer')
                if nodes.count() > 0:
                    id = nodes.item(0).toElement().attribute('id')
                    # we can read layer-tree-layer xml format only if we use the same QgsMapLayerRegistry
                    reg = QgsMapLayerRegistry.instance()
                    return reg.mapLayer(id) is not None
            elif t in self.formats:
                return True
        return False

    def setContent(self, format):
        r = False
        if format in self.formats:
            r = self.doc.setContent(self.mimeData.data(format))
        if r:
            print(str(self.doc.toString()))
        return r

    def hasLayerTreeModelData(self):
        return self.mimeTypeCheck([
            MimeDataHelper.MIME_DOCKTREEMODELDATA,
            MimeDataHelper.MIME_LAYERTREEMODELDATA])

    def layerTreeModelNodes(self):
        from enmapbox.gui.treeviews import TreeNodeProvider
        assert self.hasLayerTreeModelData()
        nodes = []
        if self.mimeData.hasFormat(MimeDataHelper.MIME_DOCKTREEMODELDATA):
            self.setContent(MimeDataHelper.MIME_DOCKTREEMODELDATA)
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

        elif self.mimeData.hasFormat(MimeDataHelper.MIME_DOCKTREEMODELDATA):
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
        return self.mimeTypeCheck([MimeDataHelper.MIME_LAYERTREEMODELDATA])

    def mapLayers(self):
        layers = []
        if self.setContent(MimeDataHelper.MIME_LAYERTREEMODELDATA):
            layers = self._readMapLayersFromXML(self.doc.documentElement())
        if len(layers) == 0:
            s= ""
        return layers

    def hasUrls(self):
        return MimeDataHelper.MIME_URILIST in self.formats
    def urls(self):
        return self.mimeData.urls()

    def hasDataSources(self):
        return self.mimeTypeCheck([
                MimeDataHelper.MIME_DATASOURCETREEMODELDATA,
                MimeDataHelper.MIME_LAYERTREEMODELDATA,
                MimeDataHelper.MIME_URILIST])


    def dataSources(self):
        dataSources = []
        from enmapbox.gui.datasources import DataSourceFactory
        if self.setContent(MimeDataHelper.MIME_DATASOURCETREEMODELDATA):
            root = self.doc.documentElement()
            nodeList = root.elementsByTagName('datasource-tree-node')
            cp = QgsObjectCustomProperties()
            for i in range(nodeList.count()):
                node = nodeList.item(i).toElement()
                cp.readXml(node)
                name = node.attribute('name')
                uri = cp.value('uri')
                dataSources.append(DataSourceFactory.Factory(uri, name=name))

        elif MimeDataHelper.MIME_LAYERTREEMODELDATA in self.formats:
            layers = self._readMapLayersFromXML(self.doc.documentElement())
            dataSources = [DataSourceFactory.Factory(l) for l in layers]

        elif MimeDataHelper.MIME_URILIST in self.formats:
            dataSources = [DataSourceFactory.Factory(uri) for uri in self.mimeData.urls()]

        dataSources = list(set([d for d in dataSources if d is not None]))
        return dataSources


