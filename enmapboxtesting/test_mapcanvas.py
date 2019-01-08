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
from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()

import enmapbox.dependencycheck
enmapbox.dependencycheck.installTestdata()

from enmapboxtestdata import enmap, hires, landcover_polygons, library
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

        canvases = []
        for i in range(3):
            c = MapCanvas()
            lyr = QgsRasterLayer(enmap)
            QgsProject.instance().addMapLayer(lyr)
            c.setLayers([lyr])
            c.setDestinationCrs(lyr.crs())
            c.setExtent(lyr.extent())
            center0 = c.center()
            center0.setX(center0.x()+ 10*i)
            c.setCenter(center0)
            canvases.append(c)
        c1, c2, c3 = canvases

        center0 = c1.center()
        CanvasLink(c1,c2, CanvasLink.LINK_ON_CENTER_SCALE)
        CanvasLink(c1,c3, CanvasLink.LINK_ON_CENTER_SCALE)
        CanvasLink.GLOBAL_LINK_LOCK = False
        self.assertTrue(c1.center() == center0)
        self.assertTrue(c2.center() == center0)
        self.assertTrue(c3.center() == center0)

        center1 = QgsPointXY(center0)
        center1.setX(center1.x()+ 200)
        center2 = QgsPointXY(center0)
        center2.setX(center1.x() + 300)
        center3 = QgsPointXY(center0)
        center3.setX(center1.x() + 400)

        c1.extentsChanged.connect(lambda : print('Extent C1 changed'))
        c2.extentsChanged.connect(lambda: print('Extent C1 changed'))
        c3.extentsChanged.connect(lambda: print('Extent C1 changed'))

        c1.setCenter(center1)
        self.assertTrue(c1.center() == center1)
        self.assertTrue(c2.center() == center1)
        self.assertTrue(c3.center() == center1)

        c2.setCenter(center2)
        self.assertTrue(c1.center() == center2)
        self.assertTrue(c2.center() == center2)
        self.assertTrue(c3.center() == center2)

        c3.setCenter(center3)
        self.assertTrue(c1.center() == center3)
        self.assertTrue(c2.center() == center3)
        self.assertTrue(c3.center() == center3)


    def test_dropEvents(self):



        allFiles = [enmap, hires, landcover, library]
        spatialFiles = [enmap, hires, landcover]

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

    from enmapbox.testing import initQgisApplication
    from enmapboxtestdata import enmap, hires, landcover
    from enmapbox.gui.mapcanvas import CanvasLinkDialog
    import enmapbox.gui.mapcanvas
    enmapbox.gui.mapcanvas.DEBUG = True
    qgsApp = initQgisApplication()
    import math
    geoFiles = [enmap, hires, landcover]
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



