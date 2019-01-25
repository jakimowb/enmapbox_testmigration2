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

import unittest, tempfile
from qgis import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *


from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()
SHOW_GUI = True


from enmapboxtestdata import *
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *
from enmapbox.gui.dockmanager import *
from enmapbox.gui.docks import *


class testDataSources(unittest.TestCase):

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


    def test_dockview(self):
        TV = DockTreeView(None)
        self.assertIsInstance(TV, QgsLayerTreeView)

    def test_dockmanager(self):

        DM = DockManager()
        self.assertTrue(len(DM) == 0)
        dock = DM.createDock('MAP')
        self.assertIsInstance(dock, MapDock)

    def test_DockPanelUI(self):

        w = DockPanelUI()
        DM = DockManager()
        self.assertIsInstance(w, DockPanelUI)
        self.assertIsInstance(DM, DockManager)
        w.connectDockManager(DM)
        DM.createDock('MAP')
        DM.createDock('SPECLIB')
        if SHOW_GUI:
            w.show()
            QGIS_APP.exec_()


class testDocks(unittest.TestCase):


    def test_dockLabel(self):
        from pyqtgraph.dockarea.Dock import Dock as pgDock
        dock = pgDock('Test')

        l  =DockLabel(dock, 'testlabel')

    def test_pgDock(self):


        da = DockArea()
        from pyqtgraph.dockarea.Dock import Dock as pgDock
        dock = pgDock('Test')
        da.addDock(dock)
        da.show()
        if SHOW_GUI:
            QGIS_APP.exec_()


    def test_MimeDataDock(self):
        da = DockArea()
        dock = MimeDataDock()
        da.addDock(dock)
        da.show()
        if SHOW_GUI:
            QGIS_APP.exec_()


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


        checkTxt = None
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
        if SHOW_GUI:
            QGIS_APP.exec_()


    def test_SpeclibDock(self):
        da = DockArea()
        dock = SpectralLibraryDock()
        da.addDock(dock)
        da.show()

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_MapDock(self):
        da = DockArea()
        from enmapbox.gui.mapcanvas import MapDock
        dock = MapDock()
        da.addDock(dock)
        da.show()

        if SHOW_GUI:
            QGIS_APP.exec_()

if __name__ == "__main__":

    SHOW_GUI = False
    unittest.main()



