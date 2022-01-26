# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest
import xmlrunner
import qgis.utils
from qgis.core import QgsProject
from enmapbox.testing import *
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.datasources.manager import *
from enmapbox.gui.dataviews.dockmanager import *


class Tests(EnMAPBoxTestCase):

    def setUp(self):
        super().setUp()

        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox):
            emb.close()
        QgsProject.instance().removeAllMapLayers()

    def test_modeLayer(self):
        qgis.utils.iface.ui.show()

        def qgisLayers():
            return QgsProject.instance().mapLayers().values()

        emb = EnMAPBox(load_core_apps=False, load_other_apps=False)

        self.assertTrue(len(qgisLayers()) == 0)

        lyr = TestObjects.createRasterLayer()
        lyr.setName('RASTER')
        lyr2 = TestObjects.createVectorLayer()
        lyr2.setName('VECTOR')
        emb.addSource(lyr)
        emb.addSource(lyr2)

        for i, l in enumerate(qgisLayers()):
            print('{}: {}'.format(i, l))

        self.assertTrue(len(qgisLayers()) == 0)

        mapDock1 = emb.createDock('MAP')
        mapDock1.setTitle('MAP1')
        self.assertIsInstance(mapDock1, MapDock)
        mapDock1.mapCanvas().setLayers([lyr, lyr2])
        self.assertTrue(len(qgisLayers()) == 2)

        lyr3 = TestObjects.createVectorLayer()

        mapDock1.mapCanvas().setLayers([lyr3])
        self.assertTrue(len(qgisLayers()) == 3)

        mapDock2 = emb.createDock('MAP')
        self.assertIsInstance(mapDock2, MapDock)
        mapDock2.setTitle('MAP2')

        self.assertTrue(len(qgisLayers()) == 3)

        self.showGui(emb.ui)

    def test_hiddenLayerManagerInBox(self):

        emb = EnMAPBox(load_core_apps=False, load_other_apps=False)

        qgis.utils.iface.ui.show()

        emb.loadExampleData()
        # lyr = TestObjects.createRasterLayer()
        # emb.addSource(lyr)

        self.showGui(emb.ui)

    def test_resources(self):
        from enmapbox.qgispluginsupport.qps.resources import ResourceBrowser
        B = ResourceBrowser()
        B.show()

        self.showGui(B)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
