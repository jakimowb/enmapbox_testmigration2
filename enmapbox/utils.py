import os, sys
import six
import importlib
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
import enmapbox
dprint = enmapbox.dprint



def jp(*args, **kwds):
    return os.path.join(*args, **kwds)

def typecheck(variable, type_):
    if isinstance(type_, list):
        for i in range(len(type_)):
            typecheck(variable[i], type_[i])
    else:
        assert isinstance(variable,type_)

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
        dprint('test QImageProviders')
        required = set(['png','svg'])
        available = set([str(p) for p in QImageReader.supportedImageFormats()])
        missing = required - available
        if len(missing) > 0:
            dprint('Missing QImageFormat support : {}'.format(','.join(list(missing))))
        s = ""



        dprint('test resource file icons')
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
            if t in self.formats:
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
        from enmapbox.treeviews import TreeNodeProvider
        assert self.hasLayerTreeModelData()
        nodes = []
        if self.mimeData.hasFormat(MimeDataHelper.MIME_DOCKTREEMODELDATA):
            self.setContent(MimeDataHelper.MIME_DOCKTREEMODELDATA)
            root = self.doc.documentElement()
            child = root.firstChildElement()
            while not child.isNull():
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


    def mapLayers(self):
        layers = []
        if self.setContent(MimeDataHelper.MIME_LAYERTREEMODELDATA):
            root = self.doc.documentElement()
            child = root.firstChildElement()
            while not child.isNull():
                tagName = str(child.tagName())
                if tagName in ['layer-tree-layer', 'layer-tree-group']:
                    node = QgsLayerTreeNode.readXML(child)
                    s = ""
                else:
                    raise NotImplementedError()
                child = child.nextSibling()


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
        from enmapbox.treeviews import TreeNodeProvider, DataSourceTreeNode
        from enmapbox.datasources import DataSourceFactory
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
            root = self.doc.documentElement()
            nodeList = root.elementsByTagName('layer-tree-layer')
            cp = QgsObjectCustomProperties()
            reg = QgsMapLayerRegistry.instance()
            for i in range(nodeList.count()):
                node = nodeList.item(i).toElement()
                cp.readXml(node)
                name = node.attribute('name')
                lyrid = node.attribute('id')
                lyr = reg.mapLayer(lyrid)
                dataSources.append(DataSourceFactory.Factory(lyr, name=name))

        elif MimeDataHelper.MIME_URILIST in self.formats:
            for uri in self.mimeData.urls():
                dataSources.append(DataSourceFactory.Factory(uri))
        dataSources = [d for d in dataSources if d is not None]
        return dataSources


    def hasMapLayers(self):
        return self.mimeTypeCheck(MimeDataHelper.MIME_LAYERTREEMODELDATA)

