# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
import tempfile
import xmlrunner
from qgis import *
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsLayerTreeLayer
from qgis.gui import QgsLayerTreeView, QgsMapCanvas
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *

from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from enmapbox.gui import SpectralProfile
from enmapbox import EnMAPBox
from enmapboxtestdata import *
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *
from enmapbox.gui.dockmanager import *
from enmapbox.gui.docks import *
from enmapbox.externals.qps.externals.pyqtgraph.dockarea.Dock import Dock as pgDock


class testDataSources(EnMAPBoxTestCase):

    def test_dataSourceManager(self):

        global signalArgs
        signalArgs = []

        def onSignal(dataSource):
            signalArgs.append(dataSource)

        DSM = DataSourceManager()
        self.assertIsInstance(DSM, DataSourceManager)
        DSM.sigDataSourceAdded.connect(onSignal)

        DSM.addSource(enmap)
        DSM.addSource(landcover_polygons)
        DSM.addSource(library)

        self.assertTrue(len(signalArgs) == 3)
        self.assertIsInstance(signalArgs[0], DataSourceRaster)
        self.assertIsInstance(signalArgs[1], DataSourceVector)
        self.assertIsInstance(signalArgs[2], DataSourceSpectralLibrary)

        types = DSM.sourceTypes()
        self.assertTrue(DataSourceRaster in types)
        self.assertTrue(DataSourceVector in types)
        self.assertTrue(DataSourceSpectralLibrary in types)

        sources = DSM.sources(sourceTypes=[DataSourceRaster])
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)

        sources = DSM.sources(sourceTypes=[DataSourceRaster, DataSourceVector])
        self.assertTrue(len(sources) == 2)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIsInstance(sources[1], DataSourceVector)

        self.assertTrue(len(DSM.sources()) == 3)
        sources = DSM.sources(sourceTypes=DataSourceRaster)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIs(sources[0], signalArgs[0])

        sources = DSM.sources(sourceTypes=DataSourceVector)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceVector)
        self.assertIs(sources[0], signalArgs[1])

        lyrWFS = QgsVectorLayer(TestObjects.uriWFS(), 'WFS', 'WFS')
        if lyrWFS.isValid():
            for o in [lyrWFS, lyrWFS.source()]:
                sources = DSM.addSource(o)
                self.assertTrue(len(sources) == 1)
                self.assertIsInstance(sources[0], DataSourceVector)
                DSM.removeSources(sources)

        lyrWMS = QgsRasterLayer(TestObjects.uriWMS(), 'WMS', 'wms')
        if lyrWMS.isValid():
            for o in [lyrWMS, lyrWMS.source()]:
                sources = DSM.addSource(o)
                self.assertTrue(len(sources) == 1)
                self.assertIsInstance(sources[0], DataSourceRaster)
                DSM.removeSources(sources)

    def test_dockview(self):
        TV = DockTreeView(None)
        self.assertIsInstance(TV, QgsLayerTreeView)

    def test_dockmanager(self):

        lyr = TestObjects.createRasterLayer()

        self.assertTrue(lyr.id() not in QgsProject.instance().mapLayers().keys())

        DM = DockManager()

        self.assertTrue(len(DM) == 0)
        dock = DM.createDock('MAP')
        self.assertIsInstance(dock, MapDock)
        dock.mapCanvas().setLayers([lyr])
        self.assertTrue(lyr.id() in QgsProject.instance().mapLayers().keys())

        DMTM = DockManagerTreeModel(DM)
        self.assertIsInstance(DMTM, DockManagerTreeModel)

        mapNodes = DMTM.mapDockTreeNodes()
        self.assertTrue(len(mapNodes) == 1)
        mapNode = mapNodes[0]
        self.assertIsInstance(mapNode, MapDockTreeNode)
        c = mapNode.mapCanvas()
        self.assertIsInstance(c, QgsMapCanvas)
        self.assertTrue(lyr in c.layers())
        self.assertTrue(lyr.id() in mapNode.findLayerIds())

        ltn = mapNode.findLayer(lyr)
        self.assertIsInstance(ltn, QgsLayerTreeLayer)

        idx = DMTM.node2index(ltn)
        self.assertIsInstance(idx, QModelIndex)
        self.assertTrue(idx.isValid())

        mimeData = DMTM.mimeData([idx])
        self.assertIsInstance(mimeData, QMimeData)

    def test_DockPanelUI(self):

        w = DockPanelUI()
        DM = DockManager()
        dockArea = DockArea()
        DM.connectDockArea(dockArea)
        self.assertIsInstance(w, DockPanelUI)
        self.assertIsInstance(DM, DockManager)
        w.connectDockManager(DM)
        w.show()
        DM.createDock('MAP')
        DM.createDock('SPECLIB')
        # DM.createDock('WEBVIEW')
        self.showGui(w)

    def test_pgDock(self):

        da = DockArea()

        dock = pgDock('Test')
        da.addDock(dock)
        da.show()
        self.showGui(da)

    def test_MimeDataDock(self):
        da = DockArea()
        dock = MimeDataDock()
        da.addDock(dock)
        da.show()
        self.showGui(da)

    def test_TextDock(self):
        da = DockArea()
        dock = TextDock()
        self.assertIsInstance(dock, TextDock)
        tw = dock.textDockWidget()
        self.assertIsInstance(tw, TextDockWidget)

        testText = """
        foo
        bar
        """
        tw.setText(testText)
        self.assertEqual(testText, tw.text())
        pathTxt = os.path.join(tempfile.gettempdir(), 'testfile.txt')
        tw.mFile = pathTxt
        tw.save()

        with open(pathTxt, encoding='utf-8') as f:
            checkTxt = f.read()
        self.assertEqual(checkTxt, testText)
        tw.mFile = None

        tw.setText('')
        self.assertEqual(tw.text(), '')
        tw.loadFile(pathTxt)
        self.assertEqual(checkTxt, tw.text())

        da.addDock(dock)
        da.show()
        self.showGui(da)

    def test_SpeclibDock(self):
        da = DockArea()
        profile = SpectralProfile()
        profile.setName('Test')
        profile.setValues(x=[1, 2, 3, 4, 5], y=[2, 1, 2, 3, 2])
        dock = SpectralLibraryDock()
        dock.speclib().startEditing()
        dock.speclib().addProfiles([profile])
        dock.speclib().commitChanges()
        da.addDock(dock)
        self.assertIsInstance(dock, SpectralLibraryDock)
        self.showGui(da)

    def test_MapDock(self):
        da = DockArea()
        from enmapbox.gui.mapcanvas import MapDock
        dock = MapDock()
        self.assertIsInstance(dock, MapDock)
        da.addDock(dock)
        self.showGui(da)

    def test_dockTreeViewDoubleClicks(self):
        from enmapboxtestdata import enmap, landcover_polygons
        eb = EnMAPBox(load_core_apps=False, load_other_apps=False)

        lyrR = QgsRasterLayer(enmap)
        lyrV = QgsVectorLayer(landcover_polygons)

        mapDock1 = eb.createDock('MAP')
        self.assertIsInstance(mapDock1, MapDock)
        mapDock1.mapCanvas().setLayers([lyrR, lyrV])
        tv = eb.dockTreeView()
        mapDock2 = eb.createDock('MAP')
        self.assertIsInstance(mapDock2, MapDock)
        eb.setCurrentMapCanvas(mapDock2.mapCanvas())
        mapDocks = eb.dockManager().docks(MapDock)

        self.assertIsInstance(tv, DockTreeView)

        self.showGui(eb.ui)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
