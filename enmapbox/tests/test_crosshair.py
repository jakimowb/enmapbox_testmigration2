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
from enmapbox.gui.utils import initQgisApplication
QGIS_APP = initQgisApplication()
from enmapboxtestdata import enmap, hymap, speclib
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.crosshair import *


class CrosshairTests(unittest.TestCase):

    def test_crosshair(self):
        import site, sys
        # add site-packages to sys.path as done by enmapboxplugin.py


        lyr = QgsRasterLayer(enmap)
        QgsProject.instance().addMapLayer(lyr)
        refCanvas = QgsMapCanvas()
        refCanvas.setLayers([lyr])
        refCanvas.setExtent(lyr.extent())
        refCanvas.setDestinationCrs(lyr.crs())
        refCanvas.show()


        style = CrosshairDialog.getCrosshairStyle(mapCanvas=refCanvas)
        self.assertIsInstance(style, CrosshairStyle)

        canvas = QgsMapCanvas()
        canvas.setExtent(QgsRectangle(0, 0, 1, 1))
        i = CrosshairMapCanvasItem(canvas)
        i.setShow(True)
        s = CrosshairStyle()
        s.setShow(True)
        i.setCrosshairStyle(s)
        canvas.show()


if __name__ == "__main__":
    unittest.main()



