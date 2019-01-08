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
from qgis import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *


from enmapbox.testing import initQgisApplication
QGIS_APP = initQgisApplication()
SHOW_GUI = False


from enmapboxtestdata import *
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *
from enmapbox.gui.docks import *


class testclassData(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        from enmapbox.gui.dockmanager import DockManager, DockArea
        from enmapbox.gui.datasourcemanager import DataSourceManager


        self.dialog = QDialog()
        self.dialog.setLayout(QVBoxLayout())
        self.dockArea = DockArea()
        self.dialog.layout().addWidget(self.dockArea)
        self.dialog.show()
        self.dataSourceManager = DataSourceManager()
        self.dockManager = DockManager()
        self.dockManager.connectDockArea(self.dockArea)
        self.dockManager.connectDataSourceManager(self.dataSourceManager)


    def tearDown(self):
        self.dialog.close()

    def test_dataSourceManager(self):

        global signalArgs
        signalArgs = []
        def onSignal(dataSource):
            signalArgs.append(dataSource)
        self.dataSourceManager.sigDataSourceAdded.connect(onSignal)

        self.dataSourceManager.addSource(enmap)
        self.dataSourceManager.addSource(landcover_polygons)
        self.dataSourceManager.addSource(library)

        self.assertTrue(len(signalArgs) == 3)
        self.assertIsInstance(signalArgs[0], DataSourceRaster)
        self.assertIsInstance(signalArgs[1], DataSourceVector)
        self.assertIsInstance(signalArgs[2], DataSourceSpectralLibrary)

        types = self.dataSourceManager.sourceTypes()
        self.assertTrue(DataSourceRaster in types)
        self.assertTrue(DataSourceVector in types)
        self.assertTrue(DataSourceSpectralLibrary in types)

        sources = self.dataSourceManager.sources(sourceTypes=[DataSourceRaster])
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)

        sources = self.dataSourceManager.sources(sourceTypes=[DataSourceRaster, DataSourceVector])
        self.assertTrue(len(sources) == 2)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIsInstance(sources[1], DataSourceVector)

        self.assertTrue(len(self.dataSourceManager.sources()) == 3)
        sources = self.dataSourceManager.sources(sourceTypes=DataSourceRaster)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIs(sources[0], signalArgs[0])

        sources = self.dataSourceManager.sources(sourceTypes=DataSourceVector)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceVector)
        self.assertIs(sources[0], signalArgs[1])



    def test_dockmanager(self):


        self.assertTrue(len(self.dockManager) == 0)
        dock = self.dockManager.createDock('MAP')
        self.assertIsInstance(dock, MapDock)

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
    suite = unittest.makeSuite(testclassData)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)




