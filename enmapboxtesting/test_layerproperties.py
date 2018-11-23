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
from enmapboxtesting import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()
from enmapboxtestdata import enmap, hires, library
from enmapbox.gui.mapcanvas import *

from enmapbox.gui.layerproperties import *

class LayerRendererTests(unittest.TestCase):



    def test_defaultRenderer(self):
        #1 band, byte
        ds = TestObjects.inMemoryImage(nb=1, eType=gdal.GDT_Byte)
        lyr = QgsRasterLayer(ds.GetFileList()[0])
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsSingleBandGrayRenderer)

        #1 band, classification
        ds = TestObjects.inMemoryImage(nc=3)
        lyr = QgsRasterLayer(ds.GetFileList()[0])
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsPalettedRasterRenderer)

        #3 bands, byte
        ds = TestObjects.inMemoryImage(nb=3, eType=gdal.GDT_Byte)
        lyr = QgsRasterLayer(ds.GetFileList()[0])
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsMultiBandColorRenderer)


        #10 bands, int
        ds = TestObjects.inMemoryImage(nb=10, eType=gdal.GDT_Int16)
        lyr = QgsRasterLayer(ds.GetFileList()[0])
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsMultiBandColorRenderer)


        s = ""
if __name__ == "__main__":
    unittest.main()



