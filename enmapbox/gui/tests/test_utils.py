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

import unittest,pickle
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from osgeo import gdal, ogr, osr
from enmapbox.gui.sandbox import initQgisEnvironment
QGIS_APP = initQgisEnvironment()


class testclassData(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        self.w = QMainWindow()
        self.cw = QWidget()
        self.cw.setLayout(QVBoxLayout())
        self.w.setCentralWidget(self.cw)
        self.w.show()
        self.menuBar = self.w.menuBar()
        self.menuA = self.menuBar.addMenu('Menu A')

    def tearDown(self):
        self.w.close()


    def test_spatialObjects(self):
        from enmapbox.gui.utils import SpatialPoint, SpatialExtent

        pt1 = SpatialPoint('EPSG:4326', 300,300)
        self.assertIsInstance(pt1, SpatialPoint)
        d = pickle.dumps(pt1)
        pt2 = pickle.loads(d)


        self.assertEquals(pt1, pt2)


    def test_gdalDataset(self):
        from enmapbox.gui.utils import gdalDataset
        from enmapbox.testdata.UrbanGradient import EnMAP
        ds1 = gdalDataset(EnMAP)
        self.assertIsInstance(ds1, gdal.Dataset)
        ds2 = gdalDataset(ds1)
        self.assertEqual(ds1, ds2)


    def test_coordinateTransformations(self):
        from enmapbox.gui.utils import gdalDataset, geo2px, px2geo, SpatialPoint, SpatialExtent
        from enmapbox.testdata.UrbanGradient import EnMAP
        from qgis.core import QgsPoint, QgsCoordinateReferenceSystem
        ds = gdalDataset(EnMAP)
        gt = ds.GetGeoTransform()
        crs = QgsCoordinateReferenceSystem(ds.GetProjection())

        self.assertTrue(crs.isValid())

        geoCoordinate = QgsPoint(gt[0], gt[3])
        pxCoordinate = geo2px(geoCoordinate, gt)

        self.assertEqual(pxCoordinate.x(), 0)
        self.assertEqual(pxCoordinate.y(), 0)
        self.assertAlmostEqual(px2geo(pxCoordinate, gt), geoCoordinate)


        spatialPoint = SpatialPoint(crs, geoCoordinate)
        pxCoordinate = geo2px(spatialPoint, gt)
        self.assertEqual(pxCoordinate.x(), 0)
        self.assertEqual(pxCoordinate.y(), 0)
        self.assertAlmostEqual(px2geo(pxCoordinate, gt), geoCoordinate)

        ext = SpatialExtent.fromLayer(ds)



    def test_appendItemsToMenu(self):
        from enmapbox.gui.utils import appendItemsToMenu

        B = QMenu()
        action = B.addAction('Do something')

        appendItemsToMenu(self.menuA, B)

        self.assertTrue(action in self.menuA.children())

    def test_MimeDataHelper(self):
        class TestClassA(object):

            s = "TEST A"

        class TestClassB(QObject):

            def __init__(self):
                super(TestClassB, self).__init__()
                self.s = 'TEST B A QOBJECT'

        from enmapbox.gui.utils import MimeDataHelper

        oA = TestClassA()
        oB = TestClassB()

        url = 'https://bitbucket.org/hu-geomatics/enmap-box'
        text = 'Lore Ipsum'
        md = QMimeData()
        #md.setUrls([url])
        md.setText(text)

        MimeDataHelper.setObjectReferences(md, [oA, oB])
        mdh = MimeDataHelper(md)
        self.assertTrue(mdh.hasPythonObjects())

        objectList = mdh.pythonObjects()
        self.assertTrue(len(objectList) == 2)
        self.assertIs(objectList[0], oA)
        self.assertIs(objectList[1], oB)


        self.assertTrue(mdh.hasUrls())
        urls = mdh.urls()
        self.assertTrue(len(urls) == 1)
        self.assertTrue(urls[0] == url)

        #todo: check tree mode nodes etc.

if __name__ == "__main__":

    unittest.main()



