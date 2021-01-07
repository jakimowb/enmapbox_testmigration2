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
from qgis import *
from qgis.gui import *
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsPointXY, QgsProject
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import TestObjects, EnMAPBoxTestCase

from enmapboxtestdata import enmap, hires, landcover_polygons, library
from enmapbox.gui.mapcanvas import *
from enmapbox.testing import TestObjects


class MapCanvasTests(EnMAPBoxTestCase):
    def test_mapCRS(self):

        mc = MapCanvas()

        self.assertFalse(mc.mapSettings().destinationCrs().isValid())
        lyr = TestObjects.createRasterLayer()
        mc.setLayers([lyr])
        self.assertEqual(lyr.crs(), mc.mapSettings().destinationCrs())

    def test_mapDock(self):
        dock = MapDock()
        self.assertIsInstance(dock, MapDock)
        m = dock.contextMenu()
        self.assertIsInstance(m, QMenu)


    def test_mapCanvas(self):
        mapCanvas = MapCanvas()
        lyr = TestObjects.createRasterLayer()
        self.assertTrue(lyr not in QgsProject.instance().mapLayers().values())
        QgsProject.instance().addMapLayer(lyr)
        mapCanvas.setLayers([lyr])
        mapCanvas.setDestinationCrs(lyr.crs())
        mapCanvas.zoomToFullExtent()

        #self.assertTrue(lyr in QgsProject.instance().mapLayers().values())
        self.assertTrue(lyr in mapCanvas.layers())
        menu = QMenu()
        mapCanvas.populateContextMenu(menu, None)
        self.assertIsInstance(menu, QMenu)
        actions = [a for a in menu.children() if isinstance(a, QAction)]
        self.assertTrue(len(actions) > 2)

        #trigger all context menu actions
        if False:
            for action in actions:
                info = action.text()
                print('Test QAction {}'.format(info))
                if info in ['Set CRS...']:
                    print('skipped')
                else:
                    try:
                        action.trigger()
                    except Exception as ex:
                        self.fail('Failed to trigger QAction "{}\n\t{}"'.find(info, ex))

        self.showGui(mapCanvas)

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
            self.assertIsInstance(c, MapCanvas)
            self.assertIsInstance(c.property(KEY_LAST_CLICKED), float)
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


    def test_issue593(self):

        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox(None, load_core_apps=False, load_other_apps=False)

        map1: MapDock = enmapBox.createDock('MAP')
        map2: MapDock = enmapBox.createDock('MAP')
        link = map1.linkWithMapDock(mapDock=map2, linkType=LINK_ON_CENTER)
        self.assertIsInstance(link, CanvasLink)
        self.showGui(enmapBox.ui)

    def test_dropEvents(self):

        mapCanvas = MapCanvas()
        allFiles = [enmap, hires, landcover_polygons, library]
        spatialFiles = [enmap, hires, landcover_polygons]

        from enmapbox.gui.mimedata import MDF_URILIST, MDF_DATASOURCETREEMODELDATA, MDF_SPECTRALLIBRARY, MDF_ENMAPBOX_LAYERTREEMODELDATA
        md = QMimeData()
        md.setUrls([QUrl.fromLocalFile(f) for f in allFiles])

        #drop URLs
        mapCanvas.setLayers([])
        mapCanvas.dropEvent(TestObjects.createDropEvent(md))
        #self.assertTrue(len(self.mapCanvas.layerPaths()) == len(spatialFiles))

        layerPaths = [pathlib.Path(p) for p in mapCanvas.layerPaths()]
        for p in spatialFiles:
            self.assertTrue(pathlib.Path(p) in layerPaths)

        #drop layertree

        layers = [QgsVectorLayer(landcover_polygons), QgsRasterLayer(enmap)]
        md = fromLayerList(layers)

        mapCanvas.setLayers([])
        mapCanvas.dropEvent(TestObjects.createDropEvent(md))
        self.assertTrue(len(mapCanvas.layerPaths()) == 2)
        for p in mapCanvas.layerPaths():
            self.assertTrue(p in spatialFiles)

        #drop registered layers
        layers = [QgsVectorLayer(landcover_polygons), QgsRasterLayer(enmap)]
        QgsProject.instance().addMapLayers(layers)


if __name__ == "__main__":

    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)



