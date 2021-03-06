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
import xmlrunner
import time

from qgis.core import QgsVectorLayer, QgsRasterLayer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from osgeo import gdal, ogr, osr
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox.gui.utils import *
from enmapbox.gui import *
from enmapbox.exampledata import enmap


class testClassUtils(EnMAPBoxTestCase):

    def test_speclibImports(self):

        from enmapbox.exampledata import enmap, landcover_polygons

        vl = QgsVectorLayer(landcover_polygons)
        rl = QgsRasterLayer(enmap)

        t0 = time.time()
        sl = SpectralLibrary.readFromVector(vl, rl)

        dt = time.time() - t0
        n = len(sl)
        print('Time to read {} profiles: {}sec'.format(n, dt))

        t0 = time.time()
        sl.startEditing()
        sl.addSpeclib(sl)
        dt = time.time() - t0
        print('Time to add {} profiles: {}sec'.format(n, dt))

        s = ""


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
