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

from enmapboxtestdata import landcover_polygons, enmap
from metadataeditorapp.metadataeditor import *

from enmapbox.gui.utils import *
SHOW_GUI = True
QGSAPP = initQgisApplication()

class TestMDMetadataKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from enmapbox.testing import initQgisApplication
        cls.qgsApp = initQgisApplication()

    @classmethod
    def tearDownClass(cls):

        cls.qgsApp.quit()

    def setUp(self):
        self.dsR = gdal.Open(enmap)
        self.dsV = ogr.Open(landcover_polygons)

        drv = gdal.GetDriverByName('MEM')
        self.dsRM = drv.CreateCopy('', self.dsR)

        drv = ogr.GetDriverByName('Memory')
        self.dsVM = drv.CopyDataSource(self.dsV, '')

    def createSupportedSources(self)->list:

        from enmapboxtestdata import enmap, landcover_polygons

        sources = []

        p1 = '/vsimem/tmp.enmap'
        to = gdal.TranslateOptions(format='ENVI')
        gdal.Translate(p1, enmap, options=to)
        sources.append(QgsRasterLayer(p1))

        sources.append(QgsVectorLayer(landcover_polygons))
        return sources

    def createNotSupportedSources(self)->list:

        sources = []
        sources.append(__file__)
        return sources

    def tearDown(self):
        pass

    def test_oli(self):



        for majorObject in [self.dsR, self.dsR.GetRasterBand(1), self.dsV]:

            try:
                oli = MDKeyAbstract.object2oli(majorObject)
            except Exception as ex:
                self.fail('Failed to generate OLI from {}'.format(majorObject))

            self.assertIsInstance(oli, str)
            self.assertTrue(regexIsOLI.match(oli)), str(majorObject)

            try:
                obj = MDKeyAbstract.oli2obj(oli, majorObject)
            except Exception as ex:
                self.fail('Failed to get object related to OLI {}'.format(oli))
            #self.assertEqual(majorObject,obj)

        #
        self.assertIsInstance(MDKeyAbstract.oli2obj('gdal.Band_1', self.dsR), gdal.Band)
        self.assertIsInstance(MDKeyAbstract.oli2obj('gdal.Dataset', self.dsR.GetRasterBand(1)), gdal.Dataset)

        self.assertIsInstance(MDKeyAbstract.oli2obj('ogr.Layer_0', self.dsV), ogr.Layer)
        #self.assertIsInstance(MDKeyAbstract.oli2obj('ogr.DataSource', self.dsV.GetLayer(0)), ogr.DataSource)


        #these need to fail
        with self.failUnlessRaises(Exception):
            MDKeyAbstract.oli2obj('gdal.Band_0', self.dsR) #band number >= 1

        with self.failUnlessRaises(Exception):
            MDKeyAbstract.oli2obj('gdal.Band_{}'.format(self.dsR.RasterCount + 1), self.dsR) #band number <= number of bands

        with self.failUnlessRaises(Exception):
            MDKeyAbstract.oli2obj('gdal.Band_1', self.dsV)  # can not get raster band from vector data

        with self.failUnlessRaises(Exception):
            MDKeyAbstract.oli2obj('ogr.Layer_1', self.dsR)  # can not get vector layer from raster data

        with self.failUnlessRaises(Exception):
            MDKeyAbstract.oli2obj('ogr.Layer_1', self.dsR)  # vector layer index < number of layers

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

        for o in [self.dsR, self.dsR.GetRasterBand(1)]:
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

        md = MDKeyDomainString.fromDomain(self.dsR, 'ENVI', 'wavelength_units')
        self.assertIsInstance(md.mOptions, list)
        self.assertTrue(len(md.mOptions) > 0)
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

    def test_metadataTreeModel(self):



        m = MetadataTreeModel()

        ds = ogr.Open(landcover_polygons)
        self.assertIsInstance(ds, ogr.DataSource)

        node = m.parseVectorMD(ds)
        self.assertIsInstance(node, TreeNode)



    def test_sourceDomains(self):
        d = MetadataEditorDialog()
        d.show()
        sources = self.createSupportedSources()
        for uri in sources:
            d.mSourceModel.clear()
            self.assertTrue(len(d.mSourceModel) == 0)
            d.addSources([uri])
            self.assertTrue(len(d.mSourceModel) == 1)



    def test_MetadataTreeViewWidgetDelegates(self):

        tv = QTreeView()
        d = MetadataTreeViewWidgetDelegates(tv)

    def test_MDDialog(self):

        d = MetadataEditorDialog()
        d.show()
        sources = self.createSupportedSources()
        d.addSources(sources)
        d.addSources(self.createNotSupportedSources())
        self.assertTrue(len(d.mSourceModel) == len(sources))

        if SHOW_GUI:
            QGSAPP.exec_()

if __name__ == "__main__":

    unittest.main()

