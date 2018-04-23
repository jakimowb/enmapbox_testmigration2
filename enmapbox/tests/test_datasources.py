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


        pass

    def tearDown(self):
        pass

    def test_rasters(self):
        ds = DataSourceFactory.Factory(enmap)
        self.assertIsInstance(ds, list)
        self.assertTrue(len(ds) == 1)
        self.assertIsInstance(ds[0], DataSourceRaster)

    def test_vectors(self):

        ds = DataSourceFactory.Factory(landcover)
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

        ds = DataSourceFactory.Factory(speclib)
        dsm.addSource(ds)
        dsm.addSource(speclib)

        self.assertTrue((len(dsm) == 1))

        ds = DataSourceFactory.Factory(enmap)
        dsm.addSource(ds)
        self.assertTrue((len(dsm) == 2))

        ds = DataSourceFactory.Factory(([enmap, hymap]))
        self.assertEqual(len(ds),2)
        dsm.addSource(ds)
        self.assertEqual(len(ds), 2)

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



