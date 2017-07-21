# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.sandbox import initQgisEnvironment
from enmapbox.gui.utils import *
QGIS_APP = initQgisEnvironment()


class testclassData(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_spectralProfile(self):
        from enmapbox.gui.spectrallibraries import SpectralProfile
        from enmapbox.testdata.UrbanGradient import EnMAP


        p = SpectralProfile()
        self.assertFalse(p.isValid())

        p  = SpectralProfile.fromRasterSource(EnMAP, QPoint(20,40))
        self.assertIsInstance(p, SpectralProfile)
        self.assertTrue(p.pxCoordinate() == QPoint(20,40))
        self.assertIsInstance(p.geoCoordinate(), SpatialPoint)





if __name__ == "__main__":

    unittest.main()



