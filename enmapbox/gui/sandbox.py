# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    sandbox.py
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
from __future__ import absolute_import, unicode_literals


import os
from qgis.core import *
from PyQt4.QtGui import *
from enmapbox.gui.utils import *

LORE_IPSUM = r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."

"""
def printLogMessage(message, tag, level):
    if level == 1:
        m = message.split('\n')
        if '' in message.split('\n'):
            m = m[0:m.index('')]
        m = '\n'.join(m)
        if not re.search('enmapbox', m):
            return
        print('{}: {}'.format(tag, m))
    elif level == 2:
        print('{}({}): {}'.format( tag, level, message ) )
    s= ""
#from qgis.core import QgsMessageLog
#QgsMessageLog.instance().messageReceived.connect(printLogMessage)
"""

def _sandboxTemplate():
    qgsApp = initQgisEnvironment()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    #do something here

    qgsApp.exec_()
    qgsApp.exitQgis()

def sandboxPureGui(dataSources=None, loadProcessingFramework=False, loadExampleData=False):
    qgsApp = initQgisEnvironment()


    import enmapbox.gui
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = loadProcessingFramework
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()

    if loadExampleData:
        EB.openExampleData(mapWindows=2)

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxProcessingFramework():
    qgsApp = initQgisEnvironment()
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()
    EB.loadExampleData()

    from processing import Processing

    # for k in sorted(Processing.algs()['enmapbox'].keys()): print(k)
    GA = Processing.getAlgorithm('enmapbox:rasterizevectorasclassification')
    Processing.runandload(GA, None)


    # do something here

    qgsApp.exec_()
    qgsApp.exitQgis()


def sandboxUmlaut():
    import enmapbox.gui
    enmapbox.gui.DEBUG = False
    enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = False
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)

    EB.loadExampleData()
    EB.addSource(r'D:\Temp\landsatüddüüä22.vrt')
    #p = r'H:\Sentinel2\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\MTD_MSIL1C.xml'
    #EB.addSources([p])
    s = ""


#for backward compatibility
initQgisEnvironment = initQgisApplication



def sandboxGUI():
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)

    EB.openExampleData(mapWindows=3)
    #EB.addSource(r'R:\WS1718_FE1\Daten\Sitzung_12\MODIS Berlin\MOD13A1.A2015273.h18v03.006.2015307052831.hdf')
    #EB.addSource(r'H:\Sentinel2\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\MTD_MSIL1C.xml')
    #EB.addSource(r'H:\Pleiades\GFOIGroupe13Brazil_SO16018091-2-01_DS_PHR1A_201610071358040_FR1_PX_W056S07_0707_03492\TPP1600447277\VOL_PHR.XML')
    #p = r'H:\Sentinel2\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\S2A_MSIL1C_20170315T101021_N0204_R022_T33UUV_20170315T101214.SAFE\MTD_MSIL1C.xml'
    #EB.addSources([p])
    s = ""



#for backward compatibility
initQgisEnvironment = initQgisApplication



def sandboxQgisBridge():
    fakeQGIS = QgisFake()
    import qgis.utils
    qgis.utils.iface = fakeQGIS

    from enmapbox.gui.enmapboxgui import EnMAPBox
    S = EnMAPBox(fakeQGIS)
    S.run()

    fakeQGIS.ui.show()
    import enmapboxtestdata
    fakeQGIS.addVectorLayer(enmapboxtestdata.landcover)
    fakeQGIS.addRasterLayer(enmapboxtestdata.enmap)

    S.openExampleData(1)

def sandboxDialog():
    qgsApp = initQgisEnvironment()
    w = QDialog()
    w.setWindowTitle('Sandbox')
    w.setFixedSize(QSize(300,400))
    l = QHBoxLayout()

    canvas = QgsMapCanvas(w, 'Canvas')
    l.addWidget(canvas)
    canvas.setAutoFillBackground(True)
    canvas.setCanvasColor(Qt.black)
    canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

    w.setLayout(l)
    qgsApp.setActiveWindow(w)
    w.show()

    qgsApp.exec_()
    qgsApp.exitQgis()



def sandboxTreeNodes():
    from enmapbox.gui.dockmanager import DockManager, DockPanelUI
    from enmapbox.gui.docks import DockArea

    dm = DockManager()
    ui = DockPanelUI()
    ui.connectDockManager(dm)
    rootNode = ui.model.rootNode
    from enmapbox.testdata.HymapBerlinA import HymapBerlinA_image
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode

    if True:
        n1 = TreeNode(rootNode, 'Group Node without value. Column span')
        n2 = TreeNode(n1, 'SubNode', value='SubNode Value')
        n3 = TreeNode(n1, 'Subnode, no value')
        crs = QgsCoordinateReferenceSystem('EPSG:4362')
        nCrs = CRSTreeNode(n1, crs)
        n2 = TreeNode(n1, 'SubGroup', value='SubGroup value')
        n3 = TreeNode(n1, 'SubSubNode, no value')
        n1.removeChildNode(n2)
    else:
        da = DockArea()
        dm.connectDockArea(da)
        dm.createDock('MAP', initSrc=HymapBerlinA_image)

    ui.show()







class QgisFake(QgisInterface):

    def __init__(self, *args):
        super(QgisFake, self).__init__(*args)

        self.canvas = QgsMapCanvas()
        self.canvas.blockSignals(False)
        print(self.canvas)
        self.canvas.setCrsTransformEnabled(True)
        self.canvas.setCanvasColor(Qt.black)
        self.canvas.extentsChanged.connect(self.testSlot)
        self.layerTreeView = QgsLayerTreeView()
        self.rootNode =QgsLayerTreeGroup()
        self.treeModel = QgsLayerTreeModel(self.rootNode)
        self.layerTreeView.setModel(self.treeModel)
        self.bridge = QgsLayerTreeMapCanvasBridge(self.rootNode, self.canvas)
        self.bridge.setAutoSetupOnFirstLayer(True)
        self.ui = QMainWindow()
        mainFrame = QFrame()

        self.ui.setCentralWidget(mainFrame)
        self.ui.setWindowTitle('Fake QGIS')
        l = QHBoxLayout()
        l.addWidget(self.layerTreeView)
        l.addWidget(self.canvas)
        mainFrame.setLayout(l)
        self.ui.setCentralWidget(mainFrame)
        self.lyrs = []
        self.createActions()

    def testSlot(self, *args):
        #print('--canvas changes--')
        s = ""

    def addVectorLayer(self, path, basename=None, providerkey=None):
        if basename is None:
            basename = os.path.basename(path)
        if providerkey is None:
            bn, ext = os.path.splitext(basename)

            providerkey = 'ogr'
        l = QgsVectorLayer(path, basename, providerkey)
        assert l.isValid()
        QgsMapLayerRegistry.instance().addMapLayer(l, True)
        self.rootNode.addLayer(l)
        self.bridge.setCanvasLayers()
        s = ""

    def legendInterface(self):
        QgsLegendInterface
    def addRasterLayer(self, path, baseName=''):
        l = QgsRasterLayer(path, loadDefaultStyleFlag=True)
        self.lyrs.append(l)
        QgsMapLayerRegistry.instance().addMapLayer(l, True)
        self.rootNode.addLayer(l)
        self.bridge.setCanvasLayers()
        return

        cnt = len(self.canvas.layers())

        self.canvas.setLayerSet([QgsMapCanvasLayer(l)])
        l.dataProvider()
        if cnt == 0:
            self.canvas.mapSettings().setDestinationCrs(l.crs())
            self.canvas.setExtent(l.extent())

            spatialExtent = SpatialExtent.fromMapLayer(l)
            #self.canvas.blockSignals(True)
            self.canvas.setDestinationCrs(spatialExtent.crs())
            self.canvas.setExtent(spatialExtent)
            #self.blockSignals(False)
            self.canvas.refresh()

        self.canvas.refresh()

    def createActions(self):
        m = self.ui.menuBar().addAction('Add Vector')
        m = self.ui.menuBar().addAction('Add Raster')

    def mapCanvas(self):
        return self.canvas


def sandboxDataSourceManager():
    from enmapbox.gui.datasourcemanager import DataSourceManager, DataSourcePanelUI
    from enmapbox.gui.docks import DockArea

    dm = DataSourceManager()
    d = QDialog()
    d.setWindowTitle('TestDialog')
    d.setLayout(QVBoxLayout())
    ui = DataSourcePanelUI()
    ui.connectDataSourceManager(dm)
    d.layout().addWidget(ui)
    from enmapboxtestdata import enmap, landcover
    from enmapbox.gui.treeviews import TreeNode, CRSTreeNode
    dm.addSource(r'R:\WS1718_FE1\Daten\Sitzung_12\MODIS Berlin\MOD13A1.A2015273.h18v03.006.2015307052831.hdf')
    dm.addSource(enmap)
    dm.addSource(landcover)
    d.show()
    s = ""


def howToStartEnMAPBoxInPython():

    # 2. start EnMAP-Box GUI
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EB = EnMAPBox(None)
    EB.run()



if __name__ == '__main__':
    import site, sys, os
    if False:
        howToStartEnMAPBoxInPython()
        exit(0)
    else:
        from enmapbox.gui.utils import initQgisApplication
        qgsApp = initQgisApplication()

        if False: sandboxTreeNodes()
        if False: sandboxDataSourceManager()

        if False: sandboxPureGui(loadProcessingFramework=True)

        if False: sandboxProcessingFramework()
        if False: sandboxQgisBridge()
        if True: sandboxGUI()
        if False: sandboxUmlaut()
        if False: sandboxDialog()

        qgsApp.exec_()
        qgsApp.quit()