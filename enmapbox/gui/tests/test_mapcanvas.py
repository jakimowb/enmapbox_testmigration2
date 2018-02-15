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
from enmapboxtestdata import enmap, hymap
from enmapbox.gui.mapcanvas import *
QGIS_APP = initQgisEnvironment()


class testclassData(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        self.w = QMainWindow()
        self.cw = QWidget()
        self.cw.setLayout(QVBoxLayout())
        self.w.setCentralWidget(self.cw)
        self.w.show()
        self.mapCanvas = MapCanvas(self.w)


    def tearDown(self):
        self.w.close()

    def test_mapCanvas(self):

        menu = self.mapCanvas.contextMenu()
        lyr = QgsRasterLayer(enmap)
        self.assertTrue(lyr not in QgsMapLayerRegistry.instance().mapLayers().values())
        self.mapCanvas.setLayers(lyr)
        self.assertTrue(lyr in QgsMapLayerRegistry.instance().mapLayers().values())
        self.assertTrue(lyr in self.mapCanvas.layers())

        menu = self.mapCanvas.contextMenu()
        self.assertIsInstance(menu, QMenu)
        actions = [a for a in menu.children() if isinstance(a, QAction)]
        self.assertTrue(len(actions) > 2)

        #trigger all context menu actions
        for action in actions:
            print('Test QAction {}'.format(action.text()))
            action.trigger()



def exampleMapLinking():
    import site, sys
    #add site-packages to sys.path as done by enmapboxplugin.py

    from enmapbox.gui.utils import initQgisApplication
    from enmapboxtestdata import enmap, hymap, landcover
    from enmapbox.gui.mapcanvas import CanvasLinkDialog
    import enmapbox.gui.mapcanvas
    enmapbox.gui.mapcanvas.DEBUG = True
    qgsApp = initQgisApplication()
    import math
    geoFiles = [enmap, hymap, landcover]
    nMaps = 4


    maps = []
    for f in geoFiles:
        map = MapCanvas()
        lyr = QgsRasterLayer(f)
        QgsMapLayerRegistry.instance().addMapLayer(lyr)
        map.setLayers([lyr])
        map.setExtent(lyr.extent())
        map.show()
        maps.append(map)

    d = CanvasLinkDialog()
    d.addCanvas(maps)
    d.setSourceCanvas(maps[0])
    d.show()

    qgsApp.exec_()
    qgsApp.exitQgis()


if __name__ == "__main__":

    exampleMapLinking()
    #+unittest.main()



