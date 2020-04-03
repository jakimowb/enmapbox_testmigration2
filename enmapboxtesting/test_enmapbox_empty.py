# -*- coding: utf-8 -*-
"""
***************************************************************************
    test_enMAPBox
    ---------------------
    Date                 : Januar 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming


import unittest, os
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QResource
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBox

class TestEnMAPBoxEmpty(EnMAPBoxTestCase):

    def test_findqgisresources(self):
        from enmapbox.externals.qps.resources import findQGISResourceFiles
        results = findQGISResourceFiles()
        print('QGIS Resource files:')
        for p in results:
            print(p)
        self.assertTrue(len(results) > 0)

    def test_empty(self):
        enmapbox = EnMAPBox(load_core_apps=False, load_other_apps=False)
        self.assertIsInstance(enmapbox, EnMAPBox)
        enmapbox.ui.show()

        testVector = TestObjects.createVectorLayer()
        enmapbox.addSource(testVector)
        enmapbox.loadExampleData()
        self.showGui(enmapbox.ui)

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)