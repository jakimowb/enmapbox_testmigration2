
import pickle, uuid
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
MDF_SPECTRALLIBRARY = 'application/hub-spectrallibrary'

MDF_URILIST = 'text/uri-list'
MDF_TEXT_HTML = 'text/html'
MDF_TEXT_PLAIN = 'text/plain'

MDF_QGIS_LAYER_STYLE = 'application/qgis.style'

def attributesd2dict(attributes:QDomNamedNodeMap)->str:
    d = {}
    assert isinstance(attributes, QDomNamedNodeMap)
    for i in range(attributes.count()):
        attribute = attributes.item(i)
        d[attribute.nodeName()] = attribute.nodeValue()
    return d


def fromDataSourceList(dataSources):
    from enmapbox.gui.datasources import DataSource
    if not isinstance(dataSources, list):
        dataSources = [dataSources]

    mimeData = QMimeData()

    doc = QDomDocument()
    node = doc.createElement(MDF_DATASOURCETREEMODELDATA_XML)
    doc.appendChild(node)

    for ds in dataSources:
        assert isinstance(ds, DataSource)
        ds.writeXml(node)
    mimeData.setData(MDF_DATASOURCETREEMODELDATA, doc.toByteArray())
    return mimeData

def toDataSourceList(mimeData):
    assert isinstance(mimeData, QMimeData)

    dataSources = []

    if MDF_DATASOURCETREEMODELDATA in mimeData.formats():
        doc = QDomDocument()
        doc.setContent(mimeData.data(MDF_DATASOURCETREEMODELDATA))
        node = doc.firstChildElement(MDF_DATASOURCETREEMODELDATA_XML)
        childs = node.childNodes()

        from enmapbox.gui.datasources import DataSource, DataSourceFactory
        from enmapbox.gui.datasourcemanager import DataSourceManager
        from uuid import UUID
        dsm = DataSourceManager.instance()
        b = isinstance(dsm, DataSourceManager)

        for i in range(childs.count()):
            child = childs.at(i).toElement()

            if child.tagName() == 'enmpabox_datasource':
                attributes = attributesd2dict(child.attributes())
                if isinstance(dsm, DataSourceManager):
                    dataSource = dsm.findSourceFromUUID(UUID(attributes['uuid']))
                    if isinstance(dataSource, DataSource):
                        dataSources.append(dataSource)
                        continue
                dataSources.extend(DataSourceFactory.Factory(attributes['source'], name=attributes['name']))

    return dataSources

def fromLayerList(mapLayers):
    """
    Converts a list of QgsMapLayers into a QMimeData object
    :param mapLayers: [list-of-QgsMapLayers]
    :return: QMimeData
    """
    for lyr in mapLayers:
        assert isinstance(lyr, QgsMapLayer)

    tree = QgsLayerTree()
    mimeData = QMimeData()

    urls = []
    for l in mapLayers:
        tree.addLayer(l)
        urls.append(QUrl.fromLocalFile(l.source()))
    doc = QDomDocument()
    context = QgsReadWriteContext()
    node = doc.createElement(MDF_LAYERTREEMODELDATA_XML)
    doc.appendChild(node)
    for c in tree.children():
        c.writeXml(node, context)

    mimeData.setData(MDF_LAYERTREEMODELDATA, doc.toByteArray())

    return mimeData




def extractMapLayers(mimeData:QMimeData)->list:
    """
    Extracts available QgsMapLayer from QMimeData
    :param mimeData: QMimeData
    :return: [list-of-QgsMapLayers]
    """
    assert isinstance(mimeData, QMimeData)
    newMapLayers = []
    if MDF_LAYERTREEMODELDATA in mimeData.formats():
        doc = QDomDocument()
        doc.setContent(mimeData.data(MDF_LAYERTREEMODELDATA))
        xml = doc.toString()
        node = doc.firstChildElement(MDF_LAYERTREEMODELDATA_XML)
        context = QgsReadWriteContext()
        #context.setPathResolver(QgsProject.instance().pathResolver())
        layerTree = QgsLayerTree.readXml(node, context)
        lt = QgsLayerTreeGroup.readXml(node, context)
        #layerTree.resolveReferences(QgsProject.instance(), True)
        registeredQGISLayers = QgsProject.instance().mapLayers()
        from enmapbox import EnMAPBox
        registeredEnMAPBoxLayers = {}
        if isinstance(EnMAPBox.instance(), EnMAPBox):
            store = EnMAPBox.instance().mapLayerStore()
            registeredEnMAPBoxLayers.update(store.mapLayers())


        attributesLUT= {}
        childs = node.childNodes()

        for i in range(childs.count()):
            child = childs.at(i).toElement()
            if child.tagName() == 'layer-tree-layer':
                attributesLUT[child.attribute('id')] = attributesd2dict(child.attributes())

        for treeLayer in layerTree.findLayers():
            assert isinstance(treeLayer, QgsLayerTreeLayer)

            mapLayer = treeLayer.layer()

            if not isinstance(mapLayer, QgsMapLayer):
                id = treeLayer.layerId()

                if id in registeredEnMAPBoxLayers.keys():
                    mapLayer = registeredEnMAPBoxLayers[id]

                elif id in registeredQGISLayers.keys():
                    mapLayer = registeredQGISLayers[id]

                elif id in attributesLUT.keys():
                    attributes = attributesLUT[id]
                    providerKey = attributes.get('providerKey')
                    if providerKey == 'gdal':
                        mapLayer = QgsRasterLayer(attributes['source'])
                    elif providerKey == 'ogr':
                        mapLayer = QgsVectorLayer(attributes['source'])
                    else:
                        s = ""

                    if isinstance(mapLayer, QgsMapLayer):
                        mapLayer.setName(attributes['name'])

            if isinstance(mapLayer, QgsMapLayer):
                newMapLayers.append(mapLayer)
        s = ""
    elif MDF_DATASOURCETREEMODELDATA in mimeData.formats():
        dsUUIDs = pickle.loads(mimeData.data(MDF_DATASOURCETREEMODELDATA))

        from enmapbox.gui.datasources import DataSource, DataSourceSpatial
        for uuid4 in dsUUIDs:
            assert isinstance(uuid4, uuid.UUID)
            ds = DataSource.fromUUID(uuid4)
            if isinstance(ds, DataSourceSpatial):
                newMapLayers.append(ds.createUnregisteredMapLayer())

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


def textToByteArray(text):
    """
    Converts input into a QByteArray
    :param text: bytes or str
    :return: QByteArray
    """

    if isinstance(text, QDomDocument):
        return textToByteArray(text.toString())
    else:
        data = QByteArray()
        data.append(text)
        return data

def textFromByteArray(data):
    """
    Decodes a QByteArray into a str
    :param data: QByteArray
    :return: str
    """
    assert isinstance(data, QByteArray)
    s = data.data().decode()
    return s

