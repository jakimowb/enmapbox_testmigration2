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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


from enmapbox.gui.utils import initQgisApplication
QGIS_APP = initQgisApplication()



from enmapboxtestdata import *
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *



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
        self.dataSourceManager.addSource(landcover)

        self.assertTrue(len(signalArgs) == 2)
        self.assertIsInstance(signalArgs[0], DataSourceRaster)
        self.assertIsInstance(signalArgs[1], DataSourceVector)

        types = self.dataSourceManager.sourceTypes()
        self.assertTrue(DataSourceRaster in types)
        self.assertTrue(DataSourceVector in types)

        sources = self.dataSourceManager.sources(sourceTypes=[DataSourceRaster])
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)

        sources = self.dataSourceManager.sources(sourceTypes=[DataSourceRaster, DataSourceVector])
        self.assertTrue(len(sources) == 2)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIsInstance(sources[1], DataSourceVector)

        self.assertTrue(len(self.dataSourceManager.sources()) == 2)
        sources = self.dataSourceManager.sources(sourceTypes=DataSourceRaster)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceRaster)
        self.assertIs(sources[0], signalArgs[0])

        sources = self.dataSourceManager.sources(sourceTypes=DataSourceVector)
        self.assertTrue(len(sources) == 1)
        self.assertIsInstance(sources[0], DataSourceVector)
        self.assertIs(sources[0], signalArgs[1])

    def test_dockmanager(self):
        pass


if __name__ == "__main__":
    suite = unittest.makeSuite(testclassData)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)




