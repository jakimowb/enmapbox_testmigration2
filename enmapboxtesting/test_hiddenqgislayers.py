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

SHOW_GUI = False and os.environ.get('CI') is None
QGIS_APP = initQgisApplication(loadProcessingFramework=False)

from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.datasourcemanager import *
from enmapbox.gui.dockmanager import *

from enmapbox.gui.hiddenqgislayers import *
class Tests(unittest.TestCase):

    def setUp(self) -> None:
        QgsProject.instance().removeAllMapLayers()

        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox):
            emb.close()


        s = ""

    def test_hiddenLayerManager(self):

        dsm = DataSourceManager()

        dockArea = DockArea()
        dm = DockManager()
        dm.connectDockArea(dockArea)
        dtm = DockManagerTreeModel(dm)

        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)

        hlm = HiddenQGISLayerManager(dsm, dtm)
        hlm.mMapLayerStore = QgsMapLayerStore()

        self.assertIsInstance(qgis.utils.iface, QgisInterface)

        self.assertIsInstance(hlm, HiddenQGISLayerManager)

        def qgisLayerNames()->typing.List[str]:
            return sorted([l.name() for l in QgsProject.instance().mapLayers().values()])


        self.assertListEqual(qgisLayerNames(), [] )

        lyr = TestObjects.createRasterLayer()
        lyr.setName('LAYER_1')
        sources = dsm.addSource(lyr)
        self.assertListEqual(qgisLayerNames(), ['[EnMAP-Box] LAYER_1'] )
        self.assertTrue(len(dsm) == 1)

        # add layer to map canvas

        mapDock = dm.createDock('MAP')
        mapDock.setTitle('MAP_1')
        self.assertIsInstance(mapDock, MapDock)
        mapDock.mapCanvas().setLayers([lyr])
        self.assertListEqual(qgisLayerNames(), ['[EnMAP-Box] LAYER_1', '[MAP_1] LAYER_1'])

        mapNode = dtm.mapDockTreeNodes()[0]
        self.assertIsInstance(mapNode, MapDockTreeNode)

        # rename mapDock
        mapDock.setTitle('MAP_1R')
        self.assertListEqual(qgisLayerNames(), ['[EnMAP-Box] LAYER_1', '[MAP_1R] LAYER_1'])

        # make layer invisible
        #mapDock.mapCanvas().setLayers([])
        self.assertTrue(len(mapNode.findLayers()) == 1)
        self.assertListEqual(qgisLayerNames(), ['[EnMAP-Box] LAYER_1', '[MAP_1R] LAYER_1'])

        lyrNodes = mapNode.findLayers()
        for n in lyrNodes:
            mapNode.removeChildNode(n)
        self.assertListEqual(qgisLayerNames(), ['[EnMAP-Box] LAYER_1'])

        # remove sources
        dsm.removeSources(sources)
        self.assertListEqual(qgisLayerNames(), [])

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


        if SHOW_GUI:
            QGIS_APP.exec_()


    def test_hiddenLayerManagerInBox(self):

        qgis.utils.iface.ui.show()

        emb = EnMAPBox()
        lyr = TestObjects.createRasterLayer()
        emb.addSource(lyr)




        if SHOW_GUI:
            QGIS_APP.exec_()

if __name__ == "__main__":
    unittest.main()



