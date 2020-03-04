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

import unittest, pathlib, os
from qgis import *
from qgis.gui import *

from qgis.core import *
from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *

from enmapbox.testing import EnMAPBoxTestCase
from enmapbox import EnMAPBox, DIR_TESTDATA

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
        self.assertTrue(mimedata.MDF_QGIS_LAYERTREEMODELDATA in md.formats())

        layers = mimedata.extractMapLayers(md)
        for lyr in layers:
            self.assertIsInstance(lyr, QgsMapLayer)
            self.assertTrue(lyr)


    def file2DropEvent(self, path)->QDropEvent:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        md = QMimeData()
        md.setUrls([QUrl.fromLocalFile(path.as_posix())])
        print('Drop {}'.format(path.name))
        self._mdref = md
        return QDropEvent(QPoint(0, 0), Qt.CopyAction, md, Qt.LeftButton, Qt.NoModifier)

    def test_dropping_files_empty_dockarea(self):
        files = []
        for root, dirs, f in os.walk(DIR_TESTDATA):
            for file in f:
                files.append(pathlib.Path(root) / file)

        # drop on
        EB = EnMAPBox()
        dockManager = EB.dockManager()
        dockArea = dockManager.currentDockArea()
        for path in files:
            dockManager.onDockAreaDragDropEvent(dockArea, self.file2DropEvent(path))
        EB.close()

    def test_dropping_files_speclib_widget(self):
        files = []
        for root, dirs, f in os.walk(DIR_TESTDATA):
            for file in f:
                files.append(pathlib.Path(root) / file)

        # drop on spectral library widget
        from enmapbox.gui.docks import SpectralLibraryDock
        from enmapbox.gui import SpectralLibraryWidget
        from enmapboxtestdata import library
        EB = EnMAPBox()
        sld = EB.createDock('SPECLIB')
        self.assertIsInstance(sld, SpectralLibraryDock)
        w = sld.speclibWidget()
        self.assertIsInstance(w, SpectralLibraryWidget)

        # drop a speclib
        self.assertTrue(len(w.speclib()) == 0)
        w.dropEvent(self.file2DropEvent(library))
        self.assertTrue(len(w.speclib()) > 0)

        # drop ASD file
        asdFile = pathlib.Path(DIR_TESTDATA) / 'asd' / 'txt' / 'ribb00002.asd.txt'
        if asdFile.is_file():
            w.dropEvent(self.file2DropEvent(asdFile))
            s = ""


        # drop random files
        for file in files:
            w.dropEvent(self.file2DropEvent(file))
            QApplication.processEvents()
        EB.close()



if __name__ == "__main__":
    unittest.main()



