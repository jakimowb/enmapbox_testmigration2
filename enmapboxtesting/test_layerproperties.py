# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapboxtestdata import enmap, hires, library
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.maplayers import *
class LayerRendererTests(EnMAPBoxTestCase):

    def test_EnMAPBoxRasterLayerConfigWidget(self):



        #lyr1 = TestObjects.createRasterLayer(nb=5)
        #lyr2 = TestObjects.createRasterLayer(nb=1)
        from enmapboxtestdata import enmap as pathEnMAP
        from enmapboxtestdata import hires as pathHyMap

        lyr1 = QgsRasterLayer(pathEnMAP, 'EnMAP')
        lyr2 = QgsRasterLayer(pathHyMap, 'HyMAP')
        lyr3 = QgsRasterLayer(pathHyMap, 'HyMAP single pseudo')
        layers = [lyr1, lyr2, lyr3]
        QgsProject.instance().addMapLayers(layers)


        canvas = QgsMapCanvas()
        canvas.setLayers(layers)
        canvas.setDestinationCrs(layers[0].crs())
        canvas.setExtent(canvas.fullExtent())

        shader = QgsRasterShader(0, 255)
        r = QgsSingleBandPseudoColorRenderer(lyr3.dataProvider(), 1, shader)
        r.createShader()
        lyr3.setRenderer(r)
        w = EnMAPBoxRasterLayerConfigWidget(lyr3, canvas)
        w.widgetChanged.connect(w.apply)
        w.show()

        w = None
        def onChanged(layer):
            if isinstance(layer, QgsRasterLayer):
                w = EnMAPBoxRasterLayerConfigWidget(layer, canvas)
                w.widgetChanged.connect(w.apply)
                w.show()
                s = ""

        cb = QgsMapLayerComboBox()
        cb.layerChanged.connect(onChanged)
        cb.show()

        self.showGui(cb)

    def test_defaultRenderer(self):
        #1 band, byte
        ds = lyr = TestObjects.createRasterLayer(nb=1, eType=gdal.GDT_Byte)
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsSingleBandGrayRenderer)

        #1 band, classification
        lyr = TestObjects.createRasterLayer(nc=3)
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsPalettedRasterRenderer)

        #3 bands, byte
        lyr = TestObjects.createRasterLayer(nb=3, eType=gdal.GDT_Byte)
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsMultiBandColorRenderer)

        #10 bands, int
        lyr = TestObjects.createRasterLayer(nb=10, eType=gdal.GDT_Int16)
        r = defaultRasterRenderer(lyr)
        self.assertIsInstance(r, QgsMultiBandColorRenderer)

if __name__ == "__main__":
    unittest.main()



