# -*- coding: utf-8 -*-

"""
***************************************************************************


    Some unit tests to check exampleapp components
    ---------------------
    Date                 : March 2018
    Copyright            : (C) 2018 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import unittest
from qgis.core import *
from osgeo import gdal, ogr
import numpy as np

from enmapboxtestdata import enmap, hymap, landcover
from enmapbox.gui.classificationscheme import ClassificationScheme
from metadataeditorV2.metadatakeys import *
from metadataeditorV2.metadataeditor import *




class TestMDMetadataKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from enmapbox.gui.sandbox import initQgisEnvironment
        cls.qgsApp = initQgisEnvironment()

    @classmethod
    def tearDownClass(cls):

        cls.qgsApp.quit()

    def setUp(self):
        self.dsR = gdal.Open(enmap)
        self.dsV = ogr.Open(landcover)

        drv = gdal.GetDriverByName('MEM')
        self.dsRM = drv.CreateCopy('', self.dsR)

        drv = ogr.GetDriverByName('Memory')
        self.dsVM = drv.CopyDataSource(self.dsV, '')


    def tearDown(self):
        pass

    def test_oli(self):



        for d in [self.dsR, self.dsR.GetRasterBand(1), self.dsV, self.dsV.GetLayer(0)]:
            try:
                oli = MDKeyAbstract.object2oli(d)
            except Exception as ex:
                self.fail('Failed to generate OLI from {}'.format(d))

            self.assertIsInstance(oli, str)
            self.assertTrue(regexIsOLI.match(oli))


            print()


    def test_metadatakeys(self):

        exampleObjects = [self.dsR, self.dsR.GetRasterBand(1), self.dsV, self.dsV.GetLayer(0)]

        for o in exampleObjects:
            try:
                key = MDKeyDescription(o)
                print('{} : {}'.format(key, key.value()))
            except Exception as ex:
                self.fail('Failed to get MDKeyDescription from {}'.format(o))

        for o in exampleObjects:
            try:
                key = MDKeyCoordinateReferenceSystem(o)
                print('{} : {}'.format(key, key.value()))
            except Exception as ex:
                self.fail('Failed to get MDKeyCoordinateReferenceSystem from {}'.format(o))

        for o in [dsR, dsR.GetRasterBand(1)]:
            try:
                key = MDKeyClassification(o)
                print('{} : {}'.format(key, key.value()))
            except Exception as ex:
                self.fail('Failed to get MDKeyClassification from {}'.format(o))

        for o in exampleObjects:
            domains = o.GetMetadataDomainList()
            if isinstance(domains, list):
                for domain in domains:
                    for mdKey in o.GetMetadata(domain).keys():
                        try:
                            key = MDKeyDomainString(o, domain, mdKey)
                        except Exception as ex:
                            self.fail('Failed to get MDKeyDomainString from {} {} {}'.format(o, domain, mdKey))


    def test_MDKeyDomainStrings(self):

        # Domain String keys

        md = MDKeyDomainString.fromDomain(self.dsR, 'ENVI', 'wavelength')

        wl = md.value()
        self.assertEqual(len(wl), self.dsR.RasterCount)

        with self.failUnlessRaises(AssertionError):
            md.setValue(wl[0:1])


        # md.setValue(wl[0:1]) #should fail
        # md.setValue(340)  # should fail

        intList = list(np.ones((len(wl)), dtype=int))
        md.setValue(intList)
        values = md.value()
        self.assertIsInstance(values[0], md.mType)

        dates = np.arange('2005-02', '2005-03', dtype='datetime64[D]')
        md.setListLength(len(dates))
        md.mType = np.datetime64
        md.setValue(dates)

        values = md.value()
        self.assertIsInstance(values[0], np.datetime64)
        md.setValue(dates)

        dates = dates.astype(str)

        md.mType = str
        md.setValue(dates)


    def test_MDKeyClassification(self):
        # Write a new classification scheme
        key = MDKeyClassification(self.dsRM)
        classScheme1 = ClassificationScheme.create(5)
        key.setValue(classScheme1)
        key.writeValueToSource(self.dsRM)
        classScheme2 = ClassificationScheme.fromRasterImage(self.dsRM)
        self.assertEqual(classScheme1, classScheme2)

        key.setValue(ClassificationScheme.create(3))
        key.writeValueToSource(self.dsRM)
        classScheme3 = ClassificationScheme.fromRasterImage(self.dsRM)
        self.assertEqual(len(classScheme3), 3)

        # start the GUI thread
    def test_MDKeyDescription(self):

        # Write a description
        for ds in [self.dsRM, self.dsVM, self.dsRM.GetRasterBand(1), self.dsVM.GetLayer(0)]:
            key = MDKeyDescription(ds)
            oldValue = key.value()
            key.setValue('New Description')
            key.writeValueToSource(ds)
            key.readValueFromSource(ds)
            self.assertEqual(key.value(), 'New Description')


if __name__ == "__main__":
    unittest.main()

