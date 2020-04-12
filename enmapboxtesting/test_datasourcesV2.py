import unittest
import os
import re
import typing
import xmlrunner
from osgeo import gdal, ogr, osr
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from enmapbox.testing import EnMAPBoxTestCase

from enmapbox.gui.dadasourcesV2 import *

class MyTestCase(EnMAPBoxTestCase):



    def test_something(self):
        reg = QgsApplication.dataItemProviderRegistry()

        dataProvider = EnMAPBoxDataItemProvider()
        reg.addProvider(dataProvider)

        tv = QTreeView()
        m = QgsBrowserGuiModel()
        #m = QgsBrowserModel()
        m.initialize()
        tv.setModel(m)
        tv.show()

        rasterSources = RasterCollectionItem()
        m
        self.showGui(tv)
        #QApplication.exec_()

    def test_printDataItemProviders(self):

        for p in QgsApplication.dataItemProviderRegistry().providers():
            self.assertIsInstance(p, QgsDataItemProvider)
            print(p.name())

    def test_RasterCollectionItem(self):

        item = RasterCollectionItem()
        self.assertIsInstance(item, QgsDataCollectionItem)

if __name__ == '__main__':
    unittest.main()
