# -*- coding: utf-8 -*-
"""
***************************************************************************
    hiddenqgislayers.py
    -----------------------------------------------------------------------
    begin                : Nov 2019
    copyright            : (C) 2019 Benjamin Jakimow
    email                : benjamin.jakimow@geo.hu-berlin.de

***************************************************************************
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
                                                                                                                                                 *
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software. If not, see <http://www.gnu.org/licenses/>.
***************************************************************************
"""

import sys, os, typing, re, json, weakref
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsProject, QgsMapLayerStore, QgsLayerTreeGroup, QgsLayerTreeLayer, QgsLayerTree, QgsLayerTreeNode
from qgis.gui import *
from qgis.gui import QgsLayerTreeView
import qgis.utils

from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.mapcanvas import MapCanvas
from enmapbox.gui.dockmanager import DockManager, MapDock, DockManagerTreeModel, MapDockTreeNode
from enmapbox.gui.datasourcemanager import DataSourceManager, DataSourceSpatial, DataSourceRaster, DataSourceVector



HIDDEN_ENMAPBOX_LAYER_GROUP = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_GROUP'
HIDDEN_ENMAPBOX_LAYER_STATE = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_STATE'

#HIDDEN_ENMAPBOX_LAYER_MAPCANVAS = 'ENMAPBOX/HIDDEN_ENMAPBOX_LAYER_MAPCANVAS'

#HIDDEN_ENMAPBOX_LAYER_SOURCE = 'ENMAPBOX/HIDDEN_ENMAPBOX_SOURCE_URI'
def qgisLayerNames() -> typing.List[str]:
    """
    Returns the current QGIS Layer names
    :return:
    """
    return sorted([l.name() for l in QgsProject.instance().mapLayers().values()])

def returnNone():
    return None

class HiddenLayerSource(object):

    def __init__(self, layerIdEnMAPBox:str, layerContext:str):

        assert isinstance(layerIdEnMAPBox, str)
        assert isinstance(layerContext, str)

        self.mLayerContext = layerContext
        self.mLayerIdEnMAPBox= layerIdEnMAPBox
        self.mLayerIdQgis = None

    def setLayerIdQgis(self, layerId:str):
        assert isinstance(self.mLayerIdQgis)
        self.mLayerIdQgis = layerId

    def __eq__(self, other):
        if isinstance(other, HiddenLayerSource):
            return self.mLayerIdEnMAPBox == other.mLayerIdEnMAPBox and \
                   self.mLayerContext == other.mLayerContext
        else:
            return False

    def __hash__(self):
        return hash((self.mLayerIdEnMAPBox, self.mLayerIdQgis))

class HiddenQGISLayerManager(QObject):

    def __init__(self, dataSourceManager:DataSourceManager, dockManagerTreeModel:DockManagerTreeModel):
        super(HiddenQGISLayerManager, self).__init__()

        assert isinstance(dataSourceManager, DataSourceManager)
        assert isinstance(dockManagerTreeModel, DockManagerTreeModel)

        self.mDataSourceManager = dataSourceManager
        self.mDockManagerTreeModel = dockManagerTreeModel
        self.mHideGroup = True

        self.mE2Q = dict()

        self.mMapLayerStore = None

        self.mDataSourceManager.sigDataSourceAdded.connect(self.sync)
        self.mDataSourceManager.sigDataSourceRemoved.connect(self.sync)

        root = self.mDockManagerTreeModel.rootGroup()
        assert isinstance(root, QgsLayerTree)
        root.addedChildren.connect(self.sync)
        root.removedChildren.connect(self.sync)
        root.nameChanged.connect(self.onDockManagerNodeNameChanged)
        #root.willRemoveChildren.connect(self.onDockManagerNodesWillBeRemoved)

    def dataSourceManager(self)->DataSourceManager:
        return self.mDataSourceManager

    def dockManagerTreeModel(self)->DockManagerTreeModel:
        return self.mDockManagerTreeModel

    def qgsHiddenLayerIds(self)->typing.List[str]:
        grp = self.hiddenLayerGroup()
        return grp.findLayerIds()

    def enmapboxLayerRefs(self, layerIds:typing.List[str]):
        """
        Returns for each layerId a (layer references, location name)
        :param layerIds: str
        :type layerIds: str
        :return: dict() with key = id, value = QgsMapLayer
        """
        REFS = dict()
        # search in data sources
        for ds in self.dataSourceManager():
            if isinstance(ds, (DataSourceRaster, DataSourceVector)):
                lyr = ds.mapLayer()
                if type(lyr) in [QgsRasterLayer, QgsVectorLayer]:
                    if lyr.id() in layerIds:
                        REFS[lyr.id()] = (lyr, 'EnMAP-Box')

        # search in map layer trees (to find also unchecked map layers = not added to a map canvas)
        for mapNode in self.dockManagerTreeModel().mapDockTreeNodes():
            mapName = mapNode.name()
            for layerTreeLayer in mapNode.findLayers():
                assert isinstance(layerTreeLayer, QgsLayerTreeLayer)
                lyr = layerTreeLayer.layer()
                if type(lyr) in [QgsVectorLayer, QgsRasterLayer]:
                    if lyr.id() in layerIds:
                        REFS[lyr.id()] = (lyr, mapName)

        return REFS

    def enmapboxLayerIds(self)->typing.List[str]:
        """
        Returns the layer ids of QgsMapLayers in the EnMAP-Box
        :return: list[str]
        :rtype:
        """
        ids = list()

        # search in data sources
        for ds in self.dataSourceManager():
            if isinstance(ds, (DataSourceRaster, DataSourceVector)):
                lyr = ds.mapLayer()
                if type(lyr) in [QgsRasterLayer, QgsVectorLayer]:
                    ids.append(lyr.id())

        # search in map layer trees (to find also unchecked map layers = not added to a map canvas)
        for mapNode in self.dockManagerTreeModel().mapDockTreeNodes():
            mapName = mapNode.name()
            for layerTreeLayer in mapNode.findLayers():
                assert isinstance(layerTreeLayer, QgsLayerTreeLayer)
                lyr = layerTreeLayer.layer()
                if type(lyr) in [QgsVectorLayer, QgsRasterLayer]:
                    ids.append(lyr.id())

        return ids

    def sync(self):
        """
        Synchronizes the QGIS hidden layers with that in the EnMAP-Box
        :return:
        :rtype:
        """
        assert isinstance(self.mMapLayerStore,
                          (QgsMapLayerStore, QgsProject)), 'Set EnMAPBox map layer store before calling this method'

        idsEnMAPBox = self.enmapboxLayerIds()
        idsQGIS = self.qgsHiddenLayerIds()

        lutEIds = list(self.mE2Q.keys())
        lutQIds = list(self.mE2Q.values())

        toAdd = [e for e in idsEnMAPBox if e not in self.mE2Q.keys()]
        toRemove = [e for e in self.mE2Q.keys() if e not in idsEnMAPBox]


        #stateEnMAPBox = self.currentEnMAPBoxLayerStates()
        #stateQGIS = self.currentQGISLayerStates()

        #toRemove = [s for s in stateQGIS if s not in stateEnMAPBox]
        #toAdd = [s for s in stateEnMAPBox if s not in stateQGIS]
        #toKeep = [s for s in stateQGIS if s in stateQGIS]

        self.removeHiddenLayers(toRemove)
        self.addHiddenLayers(toAdd)
        #self.updateHiddenLayers(toKeep)

    def removeHiddenLayers(self, enmapBoxLayerIDs:typing.List[str]):
        if len(enmapBoxLayerIDs) == 0:
            return

        qgisIds = [self.mE2Q.get(e, None) for e in enmapBoxLayerIDs]
        qgisIds = [q for q in qgisIds if isinstance(q, str)]

        for e in enmapBoxLayerIDs:
            self.mE2Q.pop(e)

        nodesToRemove = []
        for node in self.hiddenLayerGroup().findLayers():
            if isinstance(node, QgsLayerTreeNode):
                qgsLyr = node.layer()
                if isinstance(qgsLyr, QgsMapLayer) and qgsLyr.id() in qgisIds:
                    nodesToRemove.append(node)

        for node in nodesToRemove:
            node.parent().removeChildNode(node)

        QgsProject.instance().removeMapLayers(qgisIds)


    def onDockManagerNodeNameChanged(self, node:QgsLayerTreeNode, name:str):
        if isinstance(node, QgsLayerTreeLayer):
            self.updateHiddenLayerName(node.layerId())
        elif isinstance(node, QgsLayerTreeGroup):
            self.updateHiddenLayerName(node.findLayerIds())

    def onDockManagerNodesWillBeRemoved(self, node:QgsLayerTreeNode, indexFrom:int, indexTo:int):

        if isinstance(node, QgsLayerTreeGroup):
            layerIdsToBeRemoved = []
            mapNode = node
            while isinstance(mapNode.parent(), QgsLayerTreeNode) and not isinstance(node, MapDockTreeNode):
                mapNode = mapNode.parent()
            if not isinstance(mapNode, QgsLayerTreeGroup):
                return

            eIds = []
            for n in node.children()[indexFrom:indexTo+1]:
                if isinstance(n, QgsLayerTreeLayer):
                    lyr = n.layer()
                    if isinstance(lyr, QgsMapLayer):
                        eIds.append(lyr.id())
            self.removeHiddenLayers(eIds)

    def setGroupVisibility(self, b:bool):
        self.mHideGroup = b
        self.hiddenLayerGroup() #this updates the group




    def qgisLayerTreeRoot(self)->QgsLayerTreeGroup:
        """
        Returns the root of the QgsLayerTree
        :return: QgsLayerTreeGroup
        """
        ltv = qgis.utils.iface.layerTreeView()
        assert isinstance(ltv, QgsLayerTreeView)
        return ltv.model().rootGroup()

    def hiddenLayerGroup(self)->QgsLayerTreeGroup:
        """
        Returns the hidden QgsLayerTreeGroup in the QGIS Layer Tree
        :return: QgsLayerTreeGroup
        """

        root = self.qgisLayerTreeRoot()
        grp = root.findGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        if not isinstance(grp, QgsLayerTreeGroup):
            print('CREATE HIDDEN_ENMAPBOX_LAYER_GROUP')
            grp = root.addGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        ltv = qgis.utils.iface.layerTreeView()
        index = ltv.model().node2index(grp)
        grp.setItemVisibilityChecked(False)
        grp.setCustomProperty('nodeHidden',  'true' if self.mHideGroup else 'false')
        ltv.setRowHidden(index.row(), index.parent(), self.mHideGroup)
        return grp



    def addHiddenLayers(self, enmapBoxLayerIds:typing.List[str]):
        if len(enmapBoxLayerIds) == 0:
            return

        hiddenGroup = self.hiddenLayerGroup()

        newQgisLayers = []
        REFS = self.enmapboxLayerRefs(enmapBoxLayerIds)

        for layerId in enmapBoxLayerIds:
            if layerId in REFS.keys():
                enmapBoxLayer, location = REFS[layerId]
                lyr = enmapBoxLayer.clone()
                assert isinstance(lyr, QgsMapLayer)
                lyr.setName(self.hiddenLayerName(enmapBoxLayer, location))
                lyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_STATE, enmapBoxLayer.id())
                #node = hiddenGroup.addLayer(lyr)
                newQgisLayers.append(lyr)
                self.mE2Q[enmapBoxLayer.id()] = lyr.id()

        if len(newQgisLayers) > 0:
            QgsProject.instance().addMapLayers(newQgisLayers, False)

    def hiddenLayerName(self, enmapBoxLayer:QgsMapLayer, location:str)->str:
        """
        Returns the name in QGIS
        :param enmapBoxLayer:
        :type enmapBoxLayer:
        :param location:
        :type location:
        :return:
        :rtype:
        """
        return '[{}] {}'.format(location, enmapBoxLayer.name())

    def updateHiddenLayerName(self, enmapBoxLayerIds:typing.List[str]):

        if len(enmapBoxLayerIds) > 0:
            REFS = self.enmapboxLayerRefs(enmapBoxLayerIds)

            for eId, (eLyr, location) in REFS.items():
                qId = self.mE2Q.get(eId)
                if isinstance(qId, str):
                    qLyr = QgsProject.instance().mapLayer(qId)
                    if isinstance(qLyr, QgsMapLayer):
                        qLyr.setName(self.hiddenLayerName(eLyr, location))
