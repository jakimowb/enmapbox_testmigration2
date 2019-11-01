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

class HiddenLayerState(object):

    @staticmethod
    def fromJson(t:str):

        vid, vloc, vname = json.loads(t)


        return HiddenLayerState(vid, vloc, vname)

    def __init__(self, lidEnMAPBox:str, location:str, layerName:str):
        assert isinstance(lidEnMAPBox, str)
        assert isinstance(location, str)
        assert isinstance(layerName, str)
        self.mLayerIDEnMAPBox= lidEnMAPBox
        self.mLocation = location
        self.mLayerName = layerName
        self.mEnMAPBoxLayerRef = returnNone

    def json(self)->str:
        return json.dumps((self.mLayerIDEnMAPBox, self.mLocation, self.mLayerName))

    def __eq__(self, other):
        if isinstance(other, HiddenLayerState):
            return self.mLayerIDEnMAPBox == other.mLayerIDEnMAPBox and \
                self.mLocation == other.mLocation and \
                self.mLayerName == other.mLayerName
        else:
            return False

    def __hash__(self):
        return hash((self.mLayerIDEnMAPBox, self.mLocation, self.mLayerName))

class HiddenQGISLayerManager(QObject):

    def __init__(self, dataSourceManager:DataSourceManager, dockManagerTreeModel:DockManagerTreeModel):
        super(HiddenQGISLayerManager, self).__init__()

        assert isinstance(dataSourceManager, DataSourceManager)
        assert isinstance(dockManagerTreeModel, DockManagerTreeModel)

        self.mDataSourceManager = dataSourceManager
        self.mDockManagerTreeModel = dockManagerTreeModel
        self.mHideGroup = True


        self.mMapLayerStore = QgsMapLayerStore()

        self.mLinkedEnMAPBoxLayer = weakref.WeakSet()

        self.mDataSourceManager.sigDataSourceAdded.connect(self.onDataSourceAdded)
        self.mDataSourceManager.sigDataSourceRemoved.connect(self.sync)

        root = self.mDockManagerTreeModel.rootGroup()
        assert isinstance(root, QgsLayerTree)
        root.addedChildren.connect(self.onDockManagerNodeAdded)
        root.nameChanged.connect(self.onDockManagerNodeNameChanged)
        root.willRemoveChildren.connect(self.onDockManagerNodesWillBeRemoved)

    def dataSourceManager(self)->DataSourceManager:
        return self.mDataSourceManager

    def dockManagerTreeModel(self)->DockManagerTreeModel:
        return self.mDockManagerTreeModel


    def currentQGISLayerStates(self, layerIds:list=None)->typing.List[HiddenLayerState]:

        results = list()

        for lyr in QgsProject.instance().mapLayers().values():
            assert isinstance(lyr, QgsMapLayer)
            state =  lyr.customProperty(HIDDEN_ENMAPBOX_LAYER_STATE)
            if isinstance(state, str):
                state = HiddenLayerState.fromJson(state)
                if isinstance(state, HiddenLayerState):
                    results.append(state)

        if isinstance(layerIds, list):
            results = [s for s in results if s.mLayerIDEnMAPBox in layerIds]

        return results

    def currentEnMAPBoxLayerStates(self, layerIds:list=None)->typing.List[HiddenLayerState]:

        results = list()

        # search in data sources
        for ds in self.dataSourceManager():
            if isinstance(ds, (DataSourceRaster, DataSourceVector)):
                lyr = ds.mapLayer()
                if type(lyr) in [QgsRasterLayer, QgsVectorLayer]:
                    state = HiddenLayerState(lyr.id(), 'EnMAP-Box', lyr.name())
                    state.mEnMAPBoxLayerRef = weakref.ref(lyr)
                    results.append(state)
                else:
                    s = ""

        # search in map layer trees (to find also unchecked map layers = not added to a map canvas)
        for mapNode in self.dockManagerTreeModel().mapDockTreeNodes():
            mapName = mapNode.name()
            for layerTreeLayer in mapNode.findLayers():
                assert isinstance(layerTreeLayer, QgsLayerTreeLayer)
                lyr = layerTreeLayer.layer()
                if type(lyr) in [QgsVectorLayer, QgsRasterLayer]:
                    state = HiddenLayerState(lyr.id(), mapName, lyr.name())
                    state.mEnMAPBoxLayerRef = weakref.ref(lyr)
                    results.append(state)

        if isinstance(layerIds, list):
            results = [s for s in results if s.mLayerIDEnMAPBox in layerIds]

        return results

    def sync(self):

        stateEnMAPBox = self.currentEnMAPBoxLayerStates()
        stateQGIS = self.currentQGISLayerStates()

        toRemove = [s for s in stateQGIS if s not in stateEnMAPBox]
        toAdd = [s for s in stateEnMAPBox if s not in stateQGIS]
        toKeep = [s for s in stateQGIS if s in stateQGIS]

        self.removeHiddenLayers(toRemove)
        self.addHiddenLayers(toAdd)
        self.updateHiddenLayers(toKeep)

    def removeHiddenLayers(self, states:typing.List[HiddenLayerState]):

        if len(states) == 0:
            return

        KEYS = [(s.mLayerIDEnMAPBox, s.mLocation) for s in states]

        qgisLayerIdsToRemove = []
        qgisNodesToRemove = []

        for node in self.qgisLayerTreeRoot().findLayers():
            if isinstance(node, QgsLayerTreeNode):
                jsonString = node.customProperty(HIDDEN_ENMAPBOX_LAYER_STATE)
                if isinstance(jsonString, str):
                    state = HiddenLayerState.fromJson(jsonString)
                    key = (state.mLayerIDEnMAPBox, state.mLocation)
                    if key in KEYS:
                        qgisLayerIdsToRemove.append(node.layer().id())
                        qgisNodesToRemove.append(node)

        for node in qgisNodesToRemove:
            node.parent().removeChildNode(node)

        QgsProject.instance().removeMapLayers(qgisLayerIdsToRemove)


    def onDockManagerNodeNameChanged(self, node:QgsLayerTreeNode, name:str):
        statesToUpdate = []
        if isinstance(node, MapDockTreeNode):
            statesToUpdate = self.currentEnMAPBoxLayerStates(layerIds=node.findLayerIds())
        if type(node) == QgsLayerTreeLayer:
            statesToUpdate = self.currentEnMAPBoxLayerStates(layerIds=node.layer().id())


        statesToUpdate = self.currentQGISLayerStates(layerIds=[s.mLayerIDEnMAPBox for s in statesToUpdate])
        self.updateHiddenLayers(statesToUpdate)


    def onDockManagerNodesWillBeRemoved(self, node:QgsLayerTreeNode, indexFrom:int, indexTo:int):

        KEY_LIST = []



        if isinstance(node, QgsLayerTreeGroup):
            layerIdsToBeRemoved = []


            mapNode = node
            while isinstance(mapNode.parent(), QgsLayerTreeNode) and not isinstance(node, MapDockTreeNode):
                mapNode = mapNode.parent()
            if not isinstance(mapNode, QgsLayerTreeGroup):
                return
            location = mapNode.name()

            layerIds = []

            for n in node.children()[indexFrom:indexTo+1]:
                if isinstance(n, QgsLayerTreeLayer):
                    lyr = n.layer()
                    if isinstance(lyr, QgsMapLayer):
                        layerIds.append(lyr.id())
            enmapBoxStateToBeRemoved = [s for s in self.currentEnMAPBoxLayerStates() if s.mLocation == location and s.mLayerIDEnMAPBox in layerIds]

            self.removeHiddenLayers(enmapBoxStateToBeRemoved)

    def onDataSourceAdded(self, dataSource):
        if isinstance(dataSource, DataSourceSpatial):
            stateEnMAPBox = self.currentEnMAPBoxLayerStates()
            stateQGIS = self.currentQGISLayerStates()

            toAdd = [s for s in stateEnMAPBox if s not in stateQGIS]
            toKeep = [s for s in stateQGIS if s in stateQGIS]


            self.addHiddenLayers(toAdd)


    def onDockManagerNodeAdded(self, node:QgsLayerTreeNode, indexFrom:int, indexTo:int):
        #self.sigMapCanvasAdded.connect(self.updateHiddenQGISLayers)
        if isinstance(node, QgsLayerTreeGroup):

            addedLayerIds = []
            for n in node.children()[indexFrom:indexTo + 1]:
                if isinstance(n, QgsLayerTreeLayer):
                    lyr = n.layer()
                    if type(lyr) in [QgsVectorLayer, QgsRasterLayer]:
                        addedLayerIds.append(lyr.id())

            statesAdded = self.currentEnMAPBoxLayerStates(layerIds=addedLayerIds)
            self.addHiddenLayers(statesAdded)

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
            grp = root.addGroup(HIDDEN_ENMAPBOX_LAYER_GROUP)

        ltv = qgis.utils.iface.layerTreeView()
        index = ltv.model().node2index(grp)
        grp.setItemVisibilityChecked(False)
        grp.setCustomProperty('nodeHidden',  'true' if self.mHideGroup else 'false')
        ltv.setRowHidden(index.row(), index.parent(), self.mHideGroup)
        return grp

    def hiddenLayers(self, enmapboxLayerId:str)->typing.List[QgsMapLayer]:
        """
        Returns the QGIS layers that corresponds to the EnMAP-box layer with enmapboxLayerId
        :param enmapboxLayerId: str
        :return: [list-of-QgsMapLayers]
        """
        assert isinstance(enmapboxLayerId, str)

        results = []
        for lyr in QgsProject.instance().mapLayers().values():
            jsonStr = lyr.customProperty(HIDDEN_ENMAPBOX_LAYER_STATE)
            if isinstance(jsonStr, str) and enmapboxLayerId in jsonStr:
                results.append(lyr)
        return results


    def addHiddenLayers(self, states:typing.List[HiddenLayerState]):
        if len(states) == 0:
            return

        hiddenGroup = self.hiddenLayerGroup()

        newQgisLayers = []
        for state in states:
            enmapBoxLayer = state.mEnMAPBoxLayerRef()
            if isinstance(enmapBoxLayer, QgsMapLayer):

                lyr = enmapBoxLayer.clone()
                assert isinstance(lyr, QgsMapLayer)
                lyr.setName(self.hiddenLayerName(state))
                jsonString = state.json()
                lyr.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_STATE, jsonString)
                if enmapBoxLayer not in self.mLinkedEnMAPBoxLayer:
                    enmapBoxLayer.rendererChanged.connect(lambda s=state: self.updateHiddenLayers([s]))
                    self.mLinkedEnMAPBoxLayer.add(enmapBoxLayer)

                node = hiddenGroup.addLayer(lyr)

                node.setCustomProperty(HIDDEN_ENMAPBOX_LAYER_STATE, jsonString)
                newQgisLayers.append(lyr)

        if len(newQgisLayers) > 0:
            QgsProject.instance().addMapLayers(newQgisLayers, False)
        s = ""


    def hiddenLayerName(self, state:HiddenLayerState):
        lyr = state.mEnMAPBoxLayerRef()
        assert isinstance(lyr, QgsMapLayer)
        name = lyr.name()
        return '[{}] {}'.format(state.mLocation, name)




    def updateAllHiddenLayers(self):
        self.updateHiddenLayers(self.currentQGISLayerStates())

    def updateHiddenLayers(self, states:typing.List[HiddenLayerState]):

        assert isinstance(states, list)
        if len(states) == 0:
            return

        layerIds = [s.mLayerIDEnMAPBox for s in states]
        states = self.currentEnMAPBoxLayerStates(layerIds=layerIds)

        for enmapBoxState in states:

            if isinstance(enmapBoxState, HiddenLayerState):

                lyrEnMAPBox = enmapBoxState.mEnMAPBoxLayerRef()
                if isinstance(lyrEnMAPBox, QgsMapLayer):
                    for lyrQgis in self.hiddenLayers(enmapBoxState.mLayerIDEnMAPBox):
                        lyrQgis.setName(self.hiddenLayerName(enmapBoxState))
                        lyrQgis.setRenderer(lyrEnMAPBox.renderer().clone())
                else:
                    s = ""


            s = ""
