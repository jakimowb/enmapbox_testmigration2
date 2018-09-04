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
from qgis import *
from qgis.gui import *
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.utils import initQgisApplication
QGIS_APP = initQgisApplication()
from enmapboxtestdata import enmap, hymap, speclib
from enmapbox.gui.mapcanvas import *



class MapCanvasTests(unittest.TestCase):

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
        self.assertTrue(lyr not in QgsProject.instance().mapLayers().values())
        self.mapCanvas.setLayers([lyr])
        self.assertTrue(lyr in QgsProject.instance().mapLayers().values())
        self.assertTrue(lyr in self.mapCanvas.layers())

        menu = self.mapCanvas.contextMenu()
        self.assertIsInstance(menu, QMenu)
        actions = [a for a in menu.children() if isinstance(a, QAction)]
        self.assertTrue(len(actions) > 2)

        #trigger all context menu actions
        for action in actions:
            info = action.text()
            print('Test QAction {}'.format(info))
            try:
                action.trigger()
            except Exception as ex:
                self.fail('Failed to trigger QAction "{}\n\t{}"'.find(info, ex))

    def test_canvaslinks(self):

        CanvasLink()

    def test_dropEvents(self):

        from enmapboxtestdata import enmap, hymap, landcover, speclib
        from enmapbox.gui.utils import TestObjects
        allFiles = [enmap, hymap, landcover, speclib]
        spatialFiles = [enmap, hymap, landcover]

        from enmapbox.gui.mimedata import MDF_URILIST, MDF_DATASOURCETREEMODELDATA, MDF_SPECTRALLIBRARY, MDF_DOCKTREEMODELDATA
        md = QMimeData()
        md.setUrls([QUrl.fromLocalFile(f) for f in allFiles])

        #drop URLs
        self.mapCanvas.setLayers([])
        self.mapCanvas.dropEvent(TestObjects.createDropEvent(md))
        #self.assertTrue(len(self.mapCanvas.layerPaths()) == len(spatialFiles))
        for p in self.mapCanvas.layerPaths():
            self.assertTrue(p in spatialFiles)

        #drop layertree

        layers = [QgsVectorLayer(landcover), QgsRasterLayer(enmap)]
        md = fromLayerList(layers)

        self.mapCanvas.setLayers([])
        self.mapCanvas.dropEvent(TestObjects.createDropEvent(md))
        self.assertTrue(len(self.mapCanvas.layerPaths()) == 2)
        for p in self.mapCanvas.layerPaths():
            self.assertTrue(p in spatialFiles)


        #drop registered layers
        layers = [QgsVectorLayer(landcover), QgsRasterLayer(enmap)]
        QgsProject.instance().addMapLayers(layers)


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
        QgsProject.instance().addMapLayer(lyr)
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

    #exampleMapLinking()
    unittest.main()



