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

import os
import pathlib
import tempfile
import unittest
import time

import numpy as np
import xmlrunner
import json
import pickle

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from osgeo import ogr, gdal

import testdata
from enmapbox.externals.qps.speclib.core import profile_fields
from enmapbox.externals.qps.utils import SpatialExtent
from enmapbox.gui.datasources.datasources import SpatialDataSource, DataSource, RasterDataSource
from enmapbox.gui.datasources.manager import DataSourceManager, DataSourceManagerPanelUI, DataSourceFactory
from qgis.PyQt import sip
from qgis.core import *
from qgis.gui import *
from qgis.core import QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsRasterRenderer
from qgis.gui import QgsMapCanvas

from enmapbox import EnMAPBox

from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.exampledata import enmap, hires, landcover_polygons, library, enmap_srf_library
from enmapbox.gui.datasources import *


class DataSourceTests(EnMAPBoxTestCase):

    def setUp(self):
        eb = EnMAPBox.instance()
        if isinstance(eb, EnMAPBox):
            eb.close()
        QApplication.processEvents()

        self.wmsUri = r'crs=EPSG:3857&format&type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0'
        self.wmsUri = 'referer=OpenStreetMap%20contributors,%20under%20ODbL&type=xyz&url=http://tiles.wmflabs.org/hikebike/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=17&zmin=1'
        self.wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
        pass

    def tearDown(self):
        eb = EnMAPBox.instance()
        if isinstance(eb, EnMAPBox):
            eb.close()
        QApplication.processEvents()

    def test_rasterVersioning(self):

        p = r'N:\thielfab\nb_ml\full_growing_season\metrics\fraction\mosaic\NEWFILE_MLP.vrt'

        if os.path.isfile(p):
            ds1 = DataSourceFactory.create(p)[0]
            self.assertIsInstance(ds1, RasterDataSource)

            lyr = ds1.createUnregisteredMapLayer()
            dp = lyr.dataProvider()
            self.assertIsInstance(dp, QgsRasterDataProvider)
            stats = dp.bandStatistics(1)

            ds2 = DataSourceFactory.create(p)[0]
            self.assertIsInstance(ds1, RasterDataSource)

            self.assertTrue(ds1.isSameSource(ds2))
            self.assertFalse(ds1.isNewVersionOf(ds2))
            self.assertFalse(ds2.isNewVersionOf(ds1))

    def test_subdatasets(self):
        path = r'H:\Processing_BJ\01_Data\Sentinel2\T21LWL\S2B_MSIL1C_20191208T140049_N0208_R067_T21LWL_20191208T153903.SAFE\MTD_MSIL1C.xml'
        dsm = DataSourceManager()
        if os.path.isfile(path):

            ds = gdal.Open(path)
            assert isinstance(ds, gdal.Dataset)
            subs = ds.GetSubDatasets()
            import datetime
            for (name, descr) in subs:
                t0 = datetime.datetime.now()
                lyr = QgsRasterLayer(name)
                self.assertTrue(lyr.isValid())
                dt1 = datetime.datetime.now() - t0
                t0 = datetime.datetime.now()

                ds = DataSourceFactory.create(name)
                dt2 = datetime.datetime.now() - t0

                self.assertIsInstance(ds, list)
                self.assertTrue(len(ds) == 1)
                self.assertIsInstance(ds[0], RasterDataSource)

    def createTestSources(self) -> list:

        # return [library, self.wfsUri, self.wmsUri, enmap, landcover_polygons]
        return [library, enmap, landcover_polygons]

    def createOGCSources(self) -> list:
        # todo: add WCS

        return [self.wfsUri, self.wmsUri]

    def createTestSourceLayers(self) -> list:

        # return [QgsRasterLayer(enmap), QgsVectorLayer(landcover_polygons), SpectralLibrary.readFrom(library)]
        return [TestObjects.createRasterLayer(),
                TestObjects.createVectorLayer(ogr.wkbPoint),
                TestObjects.createVectorLayer(ogr.wkbPolygon),
                TestObjects.createSpectralLibrary(10)]

    def test_testSources(self):

        for l in self.createTestSourceLayers():
            self.assertIsInstance(l, QgsMapLayer)
            self.assertTrue(l.isValid())

    def test_layerSourceUpdate(self):

        path = '/vsimem/image.bsq'
        path = tempfile.mktemp(suffix='image.tif')
        TestObjects.createRasterDataset(nb=5, nl=500, path=path)
        c = QgsMapCanvas()
        c.show()
        lyr = QgsRasterLayer(path)
        r = lyr.renderer()
        self.assertIsInstance(r, QgsRasterRenderer)
        r.setInput(lyr.dataProvider())
        r.setGreenBand(5)

        c.setDestinationCrs(lyr.crs())
        c.setExtent(lyr.extent())
        c.setLayers([lyr])
        c.waitWhileRendering()

        self.assertIsInstance(lyr, QgsRasterLayer)
        self.assertTrue(lyr.isValid())
        self.assertEqual(lyr.bandCount(), 5)
        self.assertEqual(lyr.height(), 500)

        # del lyr

    def test_datasourcemanager_equalsources(self):

        p1 = str(pathlib.Path(hires))
        p2 = pathlib.Path(hires).as_posix()

        dsm = DataSourceManager()
        dsm.addSources([p1, p2])
        self.assertTrue(len(dsm) == 1)

        dsm = DataSourceManager()
        dsm.addSources([p2, p1])
        self.assertTrue(len(dsm) == 1)

    def test_DataSourcePanelUI(self):

        dsm = DataSourceManager()
        panel = DataSourceManagerPanelUI()
        panel.connectDataSourceManager(dsm)
        uris = [library, enmap, landcover_polygons]
        dsm.addSources(uris)
        self.showGui(panel)

    def test_datasourcemanager(self):
        reg = QgsProject.instance()
        reg.removeAllMapLayers()
        dsm = DataSourceManager()
        uris = [enmap_srf_library, enmap, landcover_polygons]
        uris = [pathlib.Path(p).as_posix() for p in uris]
        dsm.addSources(uris)

        self.assertTrue((len(dsm) == len(uris)))
        dsm.addSources(uris)
        self.assertEqual(len(dsm), len(uris), msg='Redundant sources are not allowed')

        self.assertEqual(len(dsm.dataSources('SPATIAL')), 3)
        self.assertEqual(len(dsm.dataSources('RASTER')), 1)
        self.assertEqual(len(dsm.dataSources('VECTOR')), 2)
        self.assertEqual(len(dsm.dataSources('SPECLIB')), 1)
        self.assertEqual(len(dsm.dataSources('FILE')), 0)

        self.assertTrue(len(reg.mapLayers()) == 0)
        lyrs = self.createTestSourceLayers()
        dsm = DataSourceManager()
        for i, l in enumerate(lyrs):
            print('Add {}...'.format(l.source()))
            ds = dsm.addDataSources(l)
            self.assertEqual(len(ds), 1)
            self.assertIsInstance(ds[0], DataSource)
            self.assertEqual(len(dsm), i + 1)
        dsm.addSources(lyrs)
        self.assertTrue(len(dsm) == len(lyrs))

        dsm = DataSourceManager()
        reg.addMapLayers(lyrs)
        self.assertTrue((len(dsm) == 0))

        reg.removeAllMapLayers()

        # test doubled input
        l = len(dsm)
        try:
            p1 = str(pathlib.WindowsPath(pathlib.Path(enmap)))
            p2 = str(pathlib.Path(enmap).as_posix())
            dsm.addSources(p1)
            dsm.addSources(p2)
            self.assertTrue(len(dsm) == l, msg='DataSourceManager should not contain the same source multiple times')
        except:
            pass

        # remove
        dsm = DataSourceManager()
        lyr = TestObjects.createVectorLayer()
        dsm.addSource(lyr)
        self.assertTrue(len(dsm) == 1)
        QgsProject.instance().addMapLayer(lyr)
        self.assertTrue(len(dsm) == 1)

        self.assertFalse(sip.isdeleted(lyr))
        QgsProject.instance().removeMapLayer(lyr)
        self.assertTrue(sip.isdeleted(lyr))
        # self.assertTrue(len(dsm) == 0)

    def test_registryresponse(self):

        from enmapbox.gui.mapcanvas import MapCanvas
        mapCanvas = MapCanvas()
        reg = QgsProject.instance()
        reg.removeAllMapLayers()

        for p in self.createTestSources():
            print(p)
            ds = DataSourceFactory.create(p)
            if isinstance(ds, SpatialDataSource):
                lyr = ds.createUnregisteredMapLayer()
                mapCanvas.setLayers(lyr)

                self.assertTrue(len(mapCanvas.layers()) == 1)

                self.assertTrue(len(reg.mapLayers()) == 1)
                reg.removeAllMapLayers()
                self.assertTrue(len(mapCanvas.layers()) == 0)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
