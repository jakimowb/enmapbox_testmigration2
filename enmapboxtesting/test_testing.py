# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import *
QGIS_APP = initQgisApplication()

class Tests(unittest.TestCase):

    def test_inMemoryImage(self):
        self.assertIsInstance(TestObjects.inMemoryImage(), gdal.Dataset)

    def test_inMemoryVector(self):
        ds = TestObjects.createVectorDataSet()
        self.assertIsInstance(ds, ogr.DataSource)
        self.assertTrue(ds.GetLayerCount() == 1)
        self.assertIsInstance(ds.GetLayerByIndex(0), ogr.Layer)
        self.assertTrue(ds.GetLayerByIndex(0).GetFeatureCount() > 0)

    def test_initQgsApplication(self):

        self.assertIsInstance(QGIS_APP, QGuiApplication)

        import qgis.utils
        self.assertIsInstance(qgis.utils.iface, QgisInterface)

if __name__ == "__main__":
    unittest.main()



