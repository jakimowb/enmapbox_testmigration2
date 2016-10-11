import os, sys
import six
import importlib
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtGui import *

import enmapbox
dprint = enmapbox.dprint


def jp(*args, **kwds):
    return os.path.join(*args, **kwds)


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



class MimeDataHelper(object):
    """
    Object to check all types and contents of mimeData used in EnMAP-Box context
    """
    def __init__(self, mimeData):
        assert isinstance(mimeData, QMimeData)

        self.mimeData = mimeData


    def hasQgsLayerTree(self):
        return self.mimeData.hasFormat('application/qgis.layertreemodeldata')

    def getQgsLayerTreeLayers(self):
        data = self.mimeData.data('application/qgis.layertreemodeldata')
        layerlist = list()
        doc = QDomDocument()
        doc.setContent(data.data())
        elements = doc.elementsByTagName('layer-tree-layer')
        assert isinstance(elements, QDomNodeList)
        for i in range(elements.count()):
            attributes = elements.item(i).attributes()
            values = dict()

            for a in range(attributes.count()):
                attr = attributes.item(a)
                values[attr.nodeName()] = attr.nodeValue()
            dprint(values)

            if "id" in values.keys() and "name" in values.keys():
                ##see https://github.com/qgis/QGIS/blob/master/src/core/qgsmaplayer.cpp
                ##the last numbers beginning with yyyyMMddhhmmsszzz
                #id = str(values['id'])[-17:]
                #layerlist.append((id, str(values['name'])))
                layerlist.append((str(values['id']), str(values['name'])))

        return layerlist

    def hasUriList(self):
        return self.mimeData.hasFormat('text/uri-list')

    def getUriList(self):
        urls = self.mimeData.urls()
        return urls
    def __repr__(self):
        info = [self.__class__]
        for f in self.mimeData.formats(): info.append(f)
        for u in self.mimeData.urls(): info.append(u)
        return '\n'.join(info)

class IconProvider:
    """
    Provides icons
    """
    EnMAP_Logo = ':/enmapbox/png/icons/enmapbox.png'
    Map_Link_Remove = ':/enmapbox/svg/icons/link_basic.svg'
    Map_Link = ':/enmapbox/svg/icons/link_basic.svg'
    Map_Link_Center = ':/enmapbox/svg/icons/link_center.svg'
    Map_Link_Extent = ':/enmapbox/svg/icons/link_mapextent.svg'
    Map_Link_Scale = ':/enmapbox/svg/icons/link_mapscale.svg'
    Map_Link_Scale_Center = ':/enmapbox/svg/icons/link_mapscale_center.svg'
    Map_Zoom_In = ':/enmapbox/svg/icons/mActionZoomOut.svg'
    Map_Zoom_Out = ':/enmapbox/svg/icons/mActionZoomIn.svg'
    Map_Pan = ':/enmapbox/svg/icons/mActionPan.svg'
    Map_Touch = ':/enmapbox/svg/icons/mActionTouch.svg'
    File_RasterMask = ':/enmapbox/svg/icons/filelist_mask.svg'
    File_RasterRegression = ':/enmapbox/png/icons/filelist_regression.png'
    File_RasterClassification = ':/enmapbox/svg/icons/filelist_classification.svg'
    File_Raster = ':/enmapbox/png/icons/filelist_image.png'
    File_Vector_Point = ':/enmapbox/svg/icons/mIconPointLayer.svg'
    File_Vector_Line = ':/enmapbox/svg/icons/mIconLineLayer.svg'
    File_Vector_Polygon = ':/enmapbox/svg/icons/mIconPolygonLayer.svg'



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



class TreeItem(QObject):
    """
    Item to be places in a TreeView
    """
    def __init__(self, parent, name, data=None, icon=None,
                 tooltip=None, mimeData=None):
        super(TreeItem, self).__init__()
        self._parent = parent
        self.name = name
        self.childs = list()
        self.data = data

        self.itemData = list()

        #decoration role stuff
        self.icon = icon
        self.tooltip = tooltip

        self._mimeData = QMimeData() if mimeData is None else mimeData
        self.actions = []

        if parent:
            assert isinstance(parent, TreeItem)
            parent.appendChild(self)

    def mimeData(self):
        mimeCopy = QMimeData()

        for format in self._mimeData.formats():
            data = self._mimeData.data(format)
            mimeCopy.setData(format, data)

        return mimeCopy


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.removeChildren()

    def addTextChilds(self, infolist):
        """
        Adds simple text-lines as new tree-node childs.
        :param infolist: list of strings. each represents a new item
        :return:
        """
        if not isinstance(infolist, list):
            infolist = list(infolist)
        for line in infolist:
            TreeItem(self, line, data=line, tooltip=line)



    def parent(self):
        return self._parent

    def child(self, row):
        """
         returns a specific child from the internal list of children
        :param row: child/row number
        :return:
        """
        #if row > len(self.childs) - 1:
        #    return None
        return self.childs[row]


    def childCount(self):
        """
        Returns the number of childs
        :return:
        """
        return len(self.childs)

    def childNumber(self):
        """
        Returns the index of the child in its parent's list of children
        :return:
        """
        if self.parent():
            return self.parent().childs.index(self)
        return 0

    def appendChild(self, child):
        """
        Appends a child and sets its parent to this TreeItem
        :param child:
        :return:
        """
        assert isinstance(child, TreeItem)
        child._parent = self
        self.childs.append(child)

    def insertChild(self, i, child):
        """
        Appends a child and sets its parent to this TreeItem
        :param child:
        :return:
        """
        assert isinstance(child, TreeItem)
        child._parent = self
        self.childs.insert(i, child)


    def removeChild(self, child):
        """
        Savely removes child from this TreeItem
        :param child:
        :return:
        """
        assert child in self.childs
        self.childs.remove(child)
        child._parent = None
        return child

    def removeChildren(self, position, count):
        if position < 0 or position + count > self.childCount():
            return False

        to_remove = [self.childs[position + i] for i in range(count)]
        for child in to_remove:
            self.removeChild(child)
            del child
        return True


    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childs):
            return False

        for i in range(count):
            child = TreeItem(self, None, data=None)
            self.insertChild(position+i, child)

        return True

    """
    bool TreeItem::insertColumns(int position, int columns)
    """
    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.insert(position,None)

        for child in self.childs:
            child.insertColumns(position, columns)

    """
    def row(self):
        if self.parent != None:
            return self.parent.childs.index(self)
        return 0
    """

    def columnCount(self):
        #return len(self.infos)
        return len(self.itemData)


    def data(self, column):
        #return self.infos[column]
        return self.itemData[column]

    def setData(self, column, value):
        if column < 0 or column >= len(self.itemData):
            return False
        self.itemData[column] = value

