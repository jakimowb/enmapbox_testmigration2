

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtXml import *
import re
from qgis.gui import *

MDF_DOCKTREEMODELDATA = 'application/enmapbox.docktreemodeldata'
MDF_DOCKTREEMODELDATA_XML = 'dock_tree_model_data'

MDF_DATASOURCETREEMODELDATA = 'application/enmapbox.datasourcetreemodeldata'
MDF_DATASOURCETREEMODELDATA_XML = 'data_source_tree_model_data'

MDF_LAYERTREEMODELDATA = 'application/qgis.layertreemodeldata'
MDF_LAYERTREEMODELDATA_XML = 'layer_tree_model_data'

MDF_PYTHON_OBJECTS = 'application/enmapbox/objectreference'
MDF_SPECTRALPROFILE = 'application/enmapbox/spectralprofile'
MDF_SPECTRALLIBRARY = 'application/enmapbox/spectrallibrary'
MDF_URILIST = 'text/uri-list'
MDF_TEXT_HTML = 'text/html'
MDF_TEXT_PLAIN = 'text/plain'



def toLayerList(mimeData):
    """
    Extracts a layer-tree-group from a QMimeData
    :param mimeData: QMimeData
    :return: QgsLayerTree
    """
    supported = [MDF_LAYERTREEMODELDATA, MDF_DATASOURCETREEMODELDATA]
    assert isinstance(mimeData, QMimeData)
    newMapLayers = []
    if MDF_LAYERTREEMODELDATA in mimeData.formats():
        doc = QDomDocument()
        doc.setContent(mimeData.data(MDF_LAYERTREEMODELDATA))
        xml = doc.toString()
        node = doc.firstChildElement('layer-tree-group')
        context = QgsReadWriteContext()
        context.setPathResolver(QgsProject.instance().pathResolver())
        layerTree = QgsLayerTree.readXml(node, context)
        #layerTree.resolveReferences(QgsProject.instance(), True)
        registeredLayers = QgsProject.instance().mapLayers()


        LUT= {}
        childs = node.childNodes()
        for i in range(childs.count()):
            child = childs.at(i).toElement()
            if child.tagName() == 'layer-tree-layer':
                LUT[child.attribute('id')] = (child.attribute('providerKey'), child.attribute('source'))

        for treeLayer in layerTree.findLayers():
            assert isinstance(treeLayer, QgsLayerTreeLayer)

            mapLayer = treeLayer.layer()
            if not isinstance(mapLayer, QgsMapLayer):
                id = treeLayer.layerId()
                if id in registeredLayers.keys():
                    mapLayer = registeredLayers[id]
                elif id in LUT.keys():
                    providerKey, source = LUT[id]
                    if providerKey == 'gdal':
                        mapLayer = QgsRasterLayer(source)
                    elif providerKey == 'ogr':
                        mapLayer = QgsVectorLayer(source)
                    else:
                        s = ""

            if isinstance(mapLayer, QgsMapLayer):
                newMapLayers.append(mapLayer)
    elif MDF_URILIST in mimeData.formats():
        from enmapbox.gui.datasources import DataSourceFactory, DataSourceSpatial
        for url in mimeData.urls():
            dataSources = DataSourceFactory.Factory(url)
            for dataSource in dataSources:
                if isinstance(dataSource, DataSourceSpatial):
                    newMapLayers.append(dataSource.createUnregisteredMapLayer())
    else:
        s = ""

    return newMapLayers


def toByteArray(text):
    """
    Converts input into a QByteArray
    :param text: bytes or str
    :return: QByteArray
    """

    if isinstance(text, QDomDocument):
        return toByteArray(text.toString())
    else:
        data = QByteArray()
        data.append(text)
        return data

def fromByteArray(data):
    """
    Decodes a QByteArray into a str
    :param data: QByteArray
    :return: str
    """
    assert isinstance(data, QByteArray)
    s = data.data().decode()
    return s



class MimeDataHelper():
    """
    A class to simplify I/O on QMimeData objects, aiming on Drag & Drop operations.
    """

    from weakref import WeakValueDictionary
    # PYTHON_OBJECTS = WeakValueDictionary()
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
    def setObjectReferences(mimeData, listOfObjects):
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
            idStr = '{}'.format(id(o))
            MimeDataHelper.PYTHON_OBJECTS[idStr] = o
            refIds.append(idStr)
        import pickle
        mimeData.setData(MimeDataHelper.MDF_PYTHON_OBJECTS, QByteArray(pickle.dumps(';'.join(refIds))))
        return mimeData

    def __init__(self, mimeData):
        assert isinstance(mimeData, QMimeData)
        self.mMimeData = mimeData
        self.mMimeDataFormats = [f for f in self.mMimeData.formats()]
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
                    return QgsProject.instance().mapLayer(id) is not None
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
            ba = self.mMimeData.data(format)
            r = self.doc.setContent(ba)
        return r

    def hasPythonObjects(self):
        """
        Returns whether any Python object references are available.
        :return: True or False
        """
        if self.containsMimeType(MimeDataHelper.MDF_PYTHON_OBJECTS):
            refIds = self.data(MimeDataHelper.MDF_PYTHON_OBJECTS).split(';')
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

        if self.hasPythonObjects():

            for refId in self.data(MimeDataHelper.MDF_PYTHON_OBJECTS).split(';'):
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
                tagName = child.tagName()
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
                lyr.setName(name)
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
            s = ""
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
                dataSources.extend(DataSourceFactory.Factory(uri, name=name))
                s = ""

        elif MimeDataHelper.MDF_LAYERTREEMODELDATA in self.mMimeData.formats():
            layers = self._readMapLayersFromXML(self.doc.documentElement())
            for l in layers:
                dataSources.extend(DataSourceFactory.Factory(l))

        elif MimeDataHelper.MDF_URILIST in self.mMimeData.formats():
            for uri in self.mMimeData.urls():
                dataSources.extend(DataSourceFactory.Factory(uri))

        dataSources = list(set([d for d in dataSources if d is not None]))

        return dataSources

