import os, sys
from PyQt4.QtCore import *



#jp = os.path.join
def jp(*args, **kwds):
    return os.path.join(*args, **kwds)

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


class Icons:


    """
    Stores icons resource paths
    """
    Logo_png = ':/enmapbox/png/icons/enmapbox.png'
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



class TreeItem(QObject):
    def __init__(self, parent, name, data=None, icon=None, description=None,
                 infos=None, tooltip=None, tag=None, asChild=False, mimeData=None):
        super(TreeItem, self).__init__()
        self.parent = parent
        self.name = name
        self.childs = list()
        self.data = data
        self.icon = icon
        self.description = description
        self.tooltip = tooltip
        if mimeData is None:
            mimeData = QMimeData
        self.mimeData = mimeData
        self.actions = []

        if infos:
            self.addInfos(infos)

        if asChild and parent is not None:
            parent.appendChild(self)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.removeChilds()

    def addInfos(self, infolist):
        if not isinstance(infolist, list):
            infolist = list(infolist)
        for line in infolist:
            item = TreeItem(self, line, tooltip=line)
            self.appendChild(item)


    def parent(self):
        return self.parent

    def child(self, row):
        if row > len(self.childs) - 1:
            return None
        return self.childs[row]

    def childNumber(self):
        if self.parent:
            return self.parent.childs.index(self)
        return 0

    def appendChild(self, child):
        #assert isinstance(child, TreeItem), str(child)
        self.childs.append(child)


    def removeChilds(self):
        del self.childs[:]



    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childs):
            return False

        for r in range(count):
            self.childs.insert(r, TreeItem(self, 'empty'))



    def row(self):
        if self.parent != None:
            return self.parent.childs.index(self)
        return 0

    def childCount(self):
        return len(self.childs)

    def columnCount(self):
        return len(self.infos)


    def data(self, column):
        return self.infos[column]

    def mimeData(self):
        return self.mimeData