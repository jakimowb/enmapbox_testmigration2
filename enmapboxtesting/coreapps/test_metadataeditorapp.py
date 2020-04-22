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

import unittest, time, pathlib, site

from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapboxtestdata import landcover_polygons, enmap
from enmapbox import DIR_ENMAPBOX
p = pathlib.Path(DIR_ENMAPBOX) / 'coreapps'
assert p.is_dir()
site.addsitedir(p)
from metadataeditorapp.metadataeditor import *
from enmapbox.gui.utils import *


class TestMDMetadataKeys(EnMAPBoxTestCase):
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

    def test_MDDialog(self):
        from enmapboxtestdata import hires


        layers = [TestObjects.createRasterLayer(nb=30),
                  TestObjects.createVectorLayer(),
                  TestObjects.createRasterLayer(nc=5),
                  QgsRasterLayer(),
                  QgsRasterLayer(hires),
                  QgsRasterLayer(hires)
                  ]

        d = MetadataEditorDialog()
        self.assertIsInstance(d, MetadataEditorDialog)
        d.show()
        QgsProject.instance().addMapLayers(layers)
        self.showGui(d)

if __name__ == "__main__":

    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)

