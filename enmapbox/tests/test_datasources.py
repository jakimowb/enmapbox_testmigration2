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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.utils import initQgisApplication
from enmapbox.gui.utils import initQgisApplication
from enmapbox.gui.utils import *
QGIS_APP = initQgisApplication()
from enmapbox.gui.datasources import *
from enmapbox.gui.datasourcemanager import *
from enmapboxtestdata import enmap, hymap, landcover, speclib
import numpy as np


class standardDataSources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    def setUp(self):

        self.wmsUri = r'crs=EPSG:3857&format&type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0'
        self.wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
        pass

    def tearDown(self):
        pass

    def test_rasters(self):

        self.assertTrue(DataSourceFactory.isRasterSource(enmap))
        self.assertTrue(rasterProvider(self.wmsUri) == 'wms')
        self.assertTrue(DataSourceFactory.isRasterSource(self.wmsUri))

        for uri in [enmap, self.wmsUri]:
            ds = DataSourceFactory.Factory(uri)
            self.assertIsInstance(ds, list)
            self.assertTrue(len(ds) == 1)
            self.assertIsInstance(ds[0], DataSourceRaster)


    def test_vectors(self):
        self.assertTrue(None == rasterProvider(self.wfsUri))
        self.assertTrue(vectorProvider(self.wfsUri) == 'WFS')
        self.assertTrue(DataSourceFactory.isVectorSource(self.wfsUri))
        self.assertTrue(DataSourceFactory.isVectorSource(landcover))

        for uri in [self.wfsUri, landcover]:
            ds = DataSourceFactory.Factory(uri)
            self.assertIsInstance(ds, list)
            self.assertTrue(len(ds) == 1)
            self.assertIsInstance(ds[0], DataSourceVector)

    def test_speclibs(self):

        ds = DataSourceFactory.Factory(speclib)
        self.assertIsInstance(ds, list)
        self.assertTrue(len(ds) == 1)
        self.assertIsInstance(ds[0], DataSourceSpectralLibrary)

    def test_datasourcemanager(self):

        dsm = DataSourceManager()

        uris = [enmap, landcover, speclib, self.wfsUri, self.wmsUri]
        dsm.addSources(uris)

        self.assertTrue((len(dsm) == len(uris)))
        dsm.addSources(uris)
        self.assertTrue((len(dsm) == len(uris)), msg='Redundant sources')

        self.assertListEqual(uris, dsm.getUriList())


class hubflowTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    def setUp(self):


        pass

    def tearDown(self):
        pass

    def test_hubflowtypes(self):
        """
        Tests to load serialized hubflow objects
        """

        from enmapbox.gui.utils import DIR_REPO, jp, mkdir
        from enmapbox.gui.datasources import HubFlowDataSource
        from hubflow.core import ClassDefinition, Vector, VectorClassification


        dirTmp = jp(DIR_REPO, 'tmp')
        mkdir(dirTmp)

        from hubflow.testdata import outdir
        print(outdir)

        for name in dir(hubflow.testdata):
            obj1 = getattr(hubflow.testdata, name)

            if isinstance(obj1, hubflow.core.FlowObject):
                self.assertIsInstance(obj1, hubflow.core.FlowObject)
                pathTmp = jp(dirTmp, 'test.{}.pkl', name)
                obj1.pickle(pathTmp)
                ds = DataSourceFactory.Factory(pathTmp)
                self.assertTrue(len(ds) == 1), 'Failed to open {}'.format(obj1)
                self.assertIsInstance(ds[0], HubFlowDataSource)
                obj3 = hubflow.core.FlowObject.unpickle(pathTmp)
                obj2 = ds[0].flowObject()
                self.assertIsInstance(obj2, hubflow.core.FlowObject)
                self.assertIsInstance(obj3, hubflow.core.FlowObject)
                #self.assertEqual(obj1, obj2)
                #self.assertEqual(obj1, obj3)



if __name__ == "__main__":

    unittest.main()



