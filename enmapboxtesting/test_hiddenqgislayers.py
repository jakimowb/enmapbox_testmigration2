# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest
from qgis.gui import *
from qgis.core import *
import qgis.utils
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import *
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.datasourcemanager import *
from enmapbox.gui.dockmanager import *


class Tests(EnMAPBoxTestCase):


    def test_modeLayer(self):
        qgis.utils.iface.ui.show()

        def qgisLayers():
            return QgsProject.instance().mapLayers().values()

        emb = EnMAPBox()
        self.assertTrue(len(qgisLayers()) == 0)

        lyr = TestObjects.createRasterLayer()
        lyr.setName('RASTER')
        lyr2 = TestObjects.createVectorLayer()
        lyr2.setName('VECTOR')
        emb.addSource(lyr)
        emb.addSource(lyr2)

        if len(qgisLayers()) != 2:
            for i, l in enumerate(qgisLayers()):
                print('{}: {}'.format(i, l))

        self.assertTrue(len(qgisLayers()) == 2)

        mapDock1 = emb.createDock('MAP')
        mapDock1.setTitle('MAP1')
        self.assertIsInstance(mapDock1, MapDock)
        mapDock1.mapCanvas().setLayers([lyr, lyr2])

        self.assertTrue(len(qgisLayers()) == 4)

        mapDock2 = emb.createDock('MAP')
        self.assertIsInstance(mapDock2, MapDock)
        mapDock2.setTitle('MAP2')

        self.assertTrue(len(qgisLayers()) == 4)

        self.showGui(emb.ui)


    def test_hiddenLayerManagerInBox(self):


        emb = EnMAPBox()

        qgis.utils.iface.ui.show()

        from enmapbox.externals.qps.resources import ResourceBrowser
        emb.loadExampleData()
        #lyr = TestObjects.createRasterLayer()
        #emb.addSource(lyr)

        self.showGui(emb.ui)

    def test_resources(self):
        from enmapbox.externals.qps.resources import ResourceBrowser
        B = ResourceBrowser()
        B.show()

        self.showGui(B)


if __name__ == "__main__":
    unittest.main()



