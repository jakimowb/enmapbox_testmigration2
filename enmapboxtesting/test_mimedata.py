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
from qgis.gui import *

from qgis.core import *
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import EnMAPBoxTestCase

from enmapboxtestdata import enmap, hires, library, landcover_polygons
import enmapbox.gui.mimedata as mimedata


class MimeDataTests(EnMAPBoxTestCase):


    def test_conversions(self):
        for t1 in ['normalstring', b'bytestring', r'rawstring']:

            ba = mimedata.textToByteArray(t1)
            self.assertIsInstance(ba, QByteArray)
            t2 = mimedata.textFromByteArray(ba)
            self.assertIsInstance(t2, str)
            self.assertEqual(len(t1), len(t2))
            if isinstance(t1, bytes):
                self.assertEqual(t1.decode(), t2)
            else:
                self.assertEqual(t1, t2)

    def test_datasourcehandling(self):

        from enmapbox.gui.datasources import DataSource, DataSourceRaster, DataSourceTextFile, DataSourceVector, DataSourceFactory
        from enmapbox.gui.datasourcemanager import DataSourceManager


        dataSources = DataSourceFactory.create([enmap, hires, library, landcover_polygons])
        dataSourceUUIDs = [ds.uuid() for ds in dataSources]
        dataSourceObjectIDs = [id(ds) for ds in dataSources]

        md = mimedata.fromDataSourceList(dataSources)

        self.assertIsInstance(md, QMimeData)
        self.assertTrue(mimedata.MDF_DATASOURCETREEMODELDATA in md.formats())

        sources = mimedata.toDataSourceList(md)
        self.assertTrue(len(sources) == len(dataSources))
        assert DataSourceManager.instance() is None
        for src in sources:
            self.assertIsInstance(src, DataSource)
            self.assertTrue(src in dataSources)
            self.assertTrue(src.uuid() not in dataSourceUUIDs)
            self.assertTrue(id(src) not in dataSourceObjectIDs)

        #do the same but with registered DataSources
        dsm = DataSourceManager()
        dsm.addSources(dataSources) #register in DataSourceManager
        sources = mimedata.toDataSourceList(md)
        self.assertTrue(len(sources) == len(dataSources))
        for src in sources:
            self.assertTrue(src in dataSources)
            #as each data source has been registere in the DataSource Manager the same object references should be returned
            self.assertTrue(src.uuid() in dataSourceUUIDs)
            self.assertTrue(id(src) in dataSourceObjectIDs)
        s = ""

    def test_maplayerhandling(self):

        mapLayers = [QgsRasterLayer(enmap), QgsVectorLayer(landcover_polygons)]
        md = mimedata.fromLayerList(mapLayers)

        self.assertIsInstance(md, QMimeData)
        self.assertTrue(mimedata.MDF_LAYERTREEMODELDATA in md.formats())

        layers = mimedata.extractMapLayers(md)
        for lyr in layers:
            self.assertIsInstance(lyr, QgsMapLayer)
            self.assertTrue(lyr)



if __name__ == "__main__":
    unittest.main()



