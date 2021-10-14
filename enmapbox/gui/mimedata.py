import pickle
import typing
import uuid
from os.path import basename, exists

from enmapboxprocessing.algorithm.importdesisl1balgorithm import ImportDesisL1BAlgorithm
from enmapboxprocessing.algorithm.importdesisl1calgorithm import ImportDesisL1CAlgorithm
from enmapboxprocessing.algorithm.importdesisl2aalgorithm import ImportDesisL2AAlgorithm
from enmapboxprocessing.algorithm.importenmapl1balgorithm import ImportEnmapL1BAlgorithm
from enmapboxprocessing.algorithm.importenmapl1calgorithm import ImportEnmapL1CAlgorithm
from enmapboxprocessing.algorithm.importenmapl2aalgorithm import ImportEnmapL2AAlgorithm
from enmapboxprocessing.algorithm.importlandsatl2algorithm import ImportLandsatL2Algorithm
from enmapboxprocessing.algorithm.importprismal1algorithm import ImportPrismaL1Algorithm
from enmapboxprocessing.algorithm.importprismal2dalgorithm import ImportPrismaL2DAlgorithm
from enmapboxprocessing.algorithm.importsentinel2l2aalgorithm import ImportSentinel2L2AAlgorithm
from processing import AlgorithmDialog
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsProject, QgsReadWriteContext, \
    QgsMimeDataUtils, QgsLayerTree, QgsLayerTreeLayer
from PyQt5.QtCore import *
from PyQt5.QtXml import *

from enmapbox import debugLog
from .datasources.datasources import DataSource

from ..externals.qps.layerproperties import defaultRasterRenderer
from ..externals.qps.speclib.core import is_spectral_library
from ..externals.qps.speclib.core.spectrallibrary import SpectralLibrary

MDF_RASTERBANDS = 'application/enmapbox.rasterbanddata'

MDF_DATASOURCETREEMODELDATA = 'application/enmapbox.datasourcetreemodeldata'
MDF_DATASOURCETREEMODELDATA_XML = 'data_source_tree_model_data'

MDF_ENMAPBOX_LAYERTREEMODELDATA = 'application/enmapbox.layertreemodeldata'
MDF_QGIS_LAYERTREEMODELDATA = 'application/qgis.layertreemodeldata'
MDF_QGIS_LAYERTREEMODELDATA_XML = 'layer_tree_model_data'

MDF_PYTHON_OBJECTS = 'application/enmapbox/objectreference'
MDF_SPECTRALLIBRARY = 'application/hub-spectrallibrary'

MDF_URILIST = 'text/uri-list'
MDF_TEXT_HTML = 'text/html'
MDF_TEXT_PLAIN = 'text/plain'

MDF_QGIS_LAYER_STYLE = 'application/qgis.style'
QGIS_URILIST_MIMETYPE = "application/x-vnd.qgis.qgis.uri"


class AlgorithmDialogWrapper(AlgorithmDialog):
    def __init__(self, *args, **kwargs):
        AlgorithmDialog.__init__(self, *args, **kwargs)
        self.finishedSuccessful = False
        self.finishResult = None

    def finish(self, successful, result, context, feedback, in_place=False):
        super().finish(successful, result, context, feedback, in_place)
        self.finishedSuccessful = successful
        self.finishResult = result
        if successful:
            self.close()


def attributesd2dict(attributes: QDomNamedNodeMap) -> str:
    d = {}
    assert isinstance(attributes, QDomNamedNodeMap)
    for i in range(attributes.count()):
        attribute = attributes.item(i)
        d[attribute.nodeName()] = attribute.nodeValue()
    return d


def fromDataSourceList(dataSources):
    if not isinstance(dataSources, list):
        dataSources = [dataSources]

    from enmapbox.gui.datasources.datasources import DataSource

    uriList = []
    for ds in dataSources:

        assert isinstance(ds, DataSource)
        uriList.extend(ds.dataItem().mimeUris())

    mimeData = QgsMimeDataUtils.encodeUriList(uriList)
    return mimeData


def toDataSourceList(mimeData) -> typing.List[DataSource]:
    assert isinstance(mimeData, QMimeData)

    uriList = QgsMimeDataUtils.decodeUriList(mimeData)
    dataSources = []
    from enmapbox.gui.datasources.manager import DataSourceFactory
    for uri in uriList:
        dataSources.extend(DataSourceFactory.create(uri))
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
    node = doc.createElement(MDF_QGIS_LAYERTREEMODELDATA_XML)
    doc.appendChild(node)
    for c in tree.children():
        c.writeXml(node, context)

    mimeData.setData(MDF_QGIS_LAYERTREEMODELDATA, doc.toByteArray())

    return mimeData


def containsMapLayers(mimeData: QMimeData) -> bool:
    """
    Checks if the mimeData contains any format suitable to describe QgsMapLayers
    :param mimeData:
    :return:
    """
    valid = [MDF_RASTERBANDS, MDF_DATASOURCETREEMODELDATA, MDF_QGIS_LAYERTREEMODELDATA, QGIS_URILIST_MIMETYPE,
             MDF_URILIST]

    for f in valid:
        if f in mimeData.formats():
            return True
    return False


def extractMapLayers(mimeData: QMimeData) -> list:
    """
    Extracts available QgsMapLayer from QMimeData
    :param mimeData: QMimeData
    :return: [list-of-QgsMapLayers]
    """
    assert isinstance(mimeData, QMimeData)

    from enmapbox.gui.datasources.datasources import DataSource
    from enmapbox.gui.datasources.datasources import SpatialDataSource
    from enmapbox.gui.datasources.manager import DataSourceFactory

    newMapLayers = []

    QGIS_LAYERTREE_FORMAT = None
    if MDF_ENMAPBOX_LAYERTREEMODELDATA in mimeData.formats():
        QGIS_LAYERTREE_FORMAT = MDF_ENMAPBOX_LAYERTREEMODELDATA
    elif MDF_QGIS_LAYERTREEMODELDATA in mimeData.formats():
        QGIS_LAYERTREE_FORMAT = MDF_QGIS_LAYERTREEMODELDATA

    if QGIS_LAYERTREE_FORMAT in mimeData.formats():
        doc = QDomDocument()
        doc.setContent(mimeData.data(QGIS_LAYERTREE_FORMAT))
        node = doc.firstChildElement(MDF_QGIS_LAYERTREEMODELDATA_XML)
        context = QgsReadWriteContext()
        # context.setPathResolver(QgsProject.instance().pathResolver())
        layerTree = QgsLayerTree.readXml(node, context)

        attributesLUT = {}
        childs = node.childNodes()

        for i in range(childs.count()):
            child = childs.at(i).toElement()
            if child.tagName() == 'layer-tree-layer':
                attributesLUT[child.attribute('id')] = attributesd2dict(child.attributes())

        for treeLayer in layerTree.findLayers():
            assert isinstance(treeLayer, QgsLayerTreeLayer)
            id = treeLayer.layerId()
            mapLayer = QgsProject.instance().mapLayer(id)

            if isinstance(mapLayer, QgsMapLayer) and QGIS_LAYERTREE_FORMAT == MDF_QGIS_LAYERTREEMODELDATA:
                # clone the layer if it comes from the QGIS Application
                mapLayer = mapLayer.clone()

            if not isinstance(mapLayer, QgsMapLayer) and id in attributesLUT.keys():
                attributes = attributesLUT[id]
                name = attributes.get('name')
                src = attributes['source']
                providerKey = attributes.get('providerKey')

                if providerKey in ['gdal', 'wms']:
                    mapLayer = QgsRasterLayer(src, name, providerKey)

                elif providerKey in ['ogr', 'WFS']:
                    mapLayer = QgsVectorLayer(src, name, providerKey)
                    s = ""

                if isinstance(mapLayer, QgsMapLayer):
                    mapLayer.setName(attributes['name'])

            if isinstance(mapLayer, (QgsRasterLayer, QgsVectorLayer)):
                newMapLayers.append(mapLayer)

    elif MDF_RASTERBANDS in mimeData.formats():
        data = pickle.loads(mimeData.data(MDF_RASTERBANDS))

        for t in data:
            uri, baseName, providerKey, band = t
            lyr = QgsRasterLayer(uri, baseName=baseName, providerType=providerKey)
            lyr.setRenderer(defaultRasterRenderer(lyr, bandIndices=[band]))
            newMapLayers.append(lyr)

    elif MDF_DATASOURCETREEMODELDATA in mimeData.formats():
        # this drop comes from the datasource tree
        dsUUIDs = pickle.loads(mimeData.data(MDF_DATASOURCETREEMODELDATA))

        for uuid4 in dsUUIDs:
            assert isinstance(uuid4, uuid.UUID)
            dataSource = DataSource.fromUUID(uuid4)

            if isinstance(dataSource, SpatialDataSource):
                lyr = dataSource.asMapLayer()
                if isinstance(lyr, QgsRasterLayer):
                    lyr.setRenderer(defaultRasterRenderer(lyr))
                newMapLayers.append(lyr)

    elif MDF_ENMAPBOX_LAYERTREEMODELDATA in mimeData.formats():
        # this drop comes from the dock tree

        s = ""

    elif QGIS_URILIST_MIMETYPE in mimeData.formats():
        for uri in QgsMimeDataUtils.decodeUriList(mimeData):

            dataSources = DataSourceFactory.create(uri)
            for dataSource in dataSources:
                if isinstance(dataSource, SpatialDataSource):
                    lyr = dataSource.asMapLayer()
                    if isinstance(lyr, QgsRasterLayer):
                        lyr.setRenderer(defaultRasterRenderer(lyr))
                    newMapLayers.append(lyr)

    elif MDF_URILIST in mimeData.formats():
        for url in mimeData.urls():
            dataSources = DataSourceFactory.create(url)
            for dataSource in dataSources:
                if isinstance(dataSource, SpatialDataSource):
                    lyr = dataSource.asMapLayer()
                    if isinstance(lyr, QgsRasterLayer):
                        lyr.setRenderer(defaultRasterRenderer(lyr))
                    newMapLayers.append(lyr)
                else:

                    # check if URL is associated with an external product,
                    # if so, the product is created by running the appropriate processing algorithm

                    filename = url.toLocalFile()
                    algs = [
                        ImportDesisL1BAlgorithm(),
                        ImportDesisL1CAlgorithm(),
                        ImportDesisL2AAlgorithm(),
                        ImportEnmapL1BAlgorithm(),
                        ImportEnmapL1CAlgorithm(),
                        ImportEnmapL2AAlgorithm(),
                        ImportLandsatL2Algorithm(),
                        ImportPrismaL1Algorithm(),
                        ImportPrismaL2DAlgorithm(),
                        ImportSentinel2L2AAlgorithm()
                    ]
                    for alg in algs:
                        if alg.isValidFile(url.path()):
                            import enmapbox
                            parameters = alg.defaultParameters(filename)

                            if isinstance(alg, ImportEnmapL1BAlgorithm):
                                alreadyExists = exists(parameters[alg.P_OUTPUT_VNIR_RASTER]) & \
                                                exists(parameters[alg.P_OUTPUT_SWIR_RASTER])
                            else:
                                alreadyExists = exists(parameters[alg.P_OUTPUT_RASTER])

                            if not alreadyExists:
                                eb = enmapbox.EnMAPBox.instance()
                                dialog: AlgorithmDialogWrapper = eb.showProcessingAlgorithmDialog(
                                    alg, parameters, True, True, AlgorithmDialogWrapper, True
                                )
                                if not dialog.finishedSuccessful:
                                    continue
                            if isinstance(alg, ImportEnmapL1BAlgorithm):
                                keys = [alg.P_OUTPUT_VNIR_RASTER, alg.P_OUTPUT_SWIR_RASTER]
                            else:
                                keys = [alg.P_OUTPUT_RASTER]
                            for key in keys:
                                layer = QgsRasterLayer(parameters[key], basename(parameters[key]))
                                newMapLayers.append(layer)

    else:
        s = ""

    info = ['Extract map layers from QMimeData']
    info.append('Formats:' + ','.join(mimeData.formats()))
    info.append(f' {len(newMapLayers)} Map Layers: ' + '\n\t'.join([f'{l}' for l in newMapLayers]))
    debugLog('\n'.join(info))

    return newMapLayers


def extractSpectralLibraries(mimeData: QMimeData) -> list:
    """Reads spectral libraries that may be defined in mimeData"""
    results = []
    slib = SpectralLibrary.readFromMimeData(mimeData)
    if is_spectral_library(slib):
        results.append(slib)

    return results


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
