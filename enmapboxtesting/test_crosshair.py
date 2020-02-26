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
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from enmapbox.testing import EnMAPBoxTestCase
from enmapboxtestdata import enmap, hires, library
from enmapbox.gui.mapcanvas import *
from enmapbox.gui import CrosshairDialog


class CrosshairTests(EnMAPBoxTestCase):

    def test_crosshair(self):
        import site, sys
        # add site-packages to sys.path as done by enmapboxplugin.py


        lyr = QgsRasterLayer(enmap)
        QgsProject.instance().addMapLayer(lyr)
        refCanvas = MapCanvas()
        refCanvas.setLayers([lyr])
        refCanvas.setExtent(lyr.extent())
        refCanvas.setDestinationCrs(lyr.crs())
        refCanvas.show()
        refCanvas.mCrosshairItem.setVisibility(True)



        self.showGui(refCanvas)

if __name__ == "__main__":
    unittest.main()



