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

from qgis.core import *
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsMapLayerStore
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox.exampledata import enmap, landcover_polygons
from enmapbox.gui import *
from enmapbox.testing import TestObjects
from enmapbox.externals.qps.cursorlocationvalue import CursorLocationInfoDock


class CursorLocationTest(EnMAPBoxTestCase):

    def webLayers(self) -> list:

        if os.environ.get('CI') is None:
            layers = [QgsRasterLayer(TestObjects.uriWMS(), 'OSM', 'wms'), \
                      QgsVectorLayer(TestObjects.uriWFS(), 'Berlin', 'WFS')]
        else:
            layers = [TestObjects.createRasterLayer(), TestObjects.createVectorLayer()]
        for l in layers:
            self.assertIsInstance(l, QgsMapLayer)
            self.assertTrue(l.isValid())
        return layers

    def test_layertest(self):

        canvas = QgsMapCanvas()

        # layers = self.webLayers()
        layers = [TestObjects.createRasterLayer(), TestObjects.createVectorLayer()]
        center = SpatialPoint.fromMapLayerCenter(layers[0])
        store = QgsMapLayerStore()
        store.addMapLayers(layers)
        canvas.setLayers(layers)
        cldock = CursorLocationInfoDock()
        self.assertIsInstance(cldock, CursorLocationInfoDock)
        cldock.show()
        cldock.loadCursorLocation(center, canvas)
        point = cldock.cursorLocation()
        self.assertIsInstance(point, SpatialPoint)

        self.showGui(cldock)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
