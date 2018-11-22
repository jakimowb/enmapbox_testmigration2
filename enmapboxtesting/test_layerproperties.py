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
        ds = TestObjects.inMemoryClassification(nb=1, eType=gdal.GDT_Byte)
        lyr = QgsRasterLayer(ds.GetFileList()[0])

        r = defaultRasterRenderer(lyr)

        self.assertIsInstance(r, QgsSingleBandColorDataRenderer)


if __name__ == "__main__":
    unittest.main()



