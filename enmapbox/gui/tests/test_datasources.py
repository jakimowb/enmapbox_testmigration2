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
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *

class testclassData(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):
        pass

    def test_hubflowtypes(self):
        p = r'D:\Repositories\QGIS_Plugins\enmap-box\tmp\classificationSample'
        ds = DataSourceFactory.Factory(p)
        self.assertIsInstance(ds, HubFlowDataSource)

        s = ""

if __name__ == "__main__":

    t = testclassData()
    t.test_hubflowtypes()

    #unittest.main()



