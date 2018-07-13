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
        for uri in [None, type(None), landcover, self.wfsUri]:
            self.assertTrue(rasterProvider(uri) == None)

        self.assertTrue(None == rasterProvider(self.wfsUri))
        self.assertTrue(DataSourceFactory.isRasterSource(enmap))
        self.assertTrue(rasterProvider(self.wmsUri) == 'wms')
        self.assertTrue(DataSourceFactory.isRasterSource(self.wmsUri))

        for uri in [enmap, self.wmsUri]:
            ds = DataSourceFactory.Factory(uri)
            self.assertIsInstance(ds, list)
            self.assertTrue(len(ds) == 1)
            for source in ds:
                self.assertIsInstance(source, DataSourceRaster)
                self.assertIsInstance(source.spatialExtent(), SpatialExtent)
                self.assertIsInstance(source.mProvider, str)

    def createTestSources(self)->list:
        return [speclib, self.wfsUri, self.wmsUri, enmap, landcover]

    def createTestSourceLayers(self)->list:
        return [QgsRasterLayer(self.wmsUri, '', 'wms'), QgsVectorLayer(self.wfsUri, '', 'WFS'),
                QgsRasterLayer(enmap), QgsVectorLayer(landcover), SpectralLibrary.readFrom(speclib)
                ]

    def test_testSources(self):

        for l in self.createTestSourceLayers():
            self.assertIsInstance(l, QgsMapLayer)
            self.assertTrue(l.isValid())

    def test_vectors(self):
        for uri in [None, type(None), self.wmsUri, enmap]:
            self.assertTrue(vectorProvider(uri) == None)

        self.assertTrue(vectorProvider(self.wfsUri) == 'WFS')
        self.assertTrue(DataSourceFactory.isVectorSource(self.wfsUri))
        self.assertTrue(DataSourceFactory.isVectorSource(landcover))

        for uri in [self.wfsUri, landcover]:
            sources = DataSourceFactory.Factory(uri)
            self.assertIsInstance(sources, list)
            self.assertTrue(len(sources) == 1)
            for source in sources:
                self.assertIsInstance(source, DataSourceVector)
                self.assertIsInstance(source.spatialExtent(), SpatialExtent)
                self.assertIsInstance(source.mProvider, str)

    def test_speclibs(self):

        ds = DataSourceFactory.Factory(speclib)
        self.assertIsInstance(ds, list)
        self.assertTrue(len(ds) == 1)
        ds = ds[0]
        self.assertIsInstance(ds, DataSourceSpectralLibrary)




    def test_datasourcemanager(self):
        reg = QgsProject.instance()
        reg.removeAllMapLayers()
        dsm = DataSourceManager()
        uris = [speclib, enmap, landcover, self.wfsUri, self.wmsUri]
        dsm.addSources(uris)

        self.assertTrue((len(dsm) == len(uris)))
        dsm.addSources(uris)
        self.assertTrue((len(dsm) == len(uris)), msg='Redundant sources are not allowed')

        self.assertListEqual(uris, dsm.getUriList())


        self.assertTrue(len(reg.mapLayers()) == 0)
        lyrs = self.createTestSourceLayers()
        dsm = DataSourceManager()
        for i, l in enumerate(lyrs):
            print('Add {}...'.format(l.source()))
            ds = dsm.addSource(l)
            self.assertTrue(len(ds) == 1)
            self.assertIsInstance(ds[0], DataSource)
            self.assertTrue(len(dsm) == i+1)
        dsm.addSources(lyrs)
        self.assertTrue(len(dsm) == len(lyrs))

        dsm = DataSourceManager()
        dsm.onMapLayerRegistryLayersAdded(lyrs)
        self.assertTrue(len(reg.mapLayers()) == 0)
        self.assertTrue(len(dsm) == len(lyrs), msg='There needs to be one DataSource per added MapLayer')


        dsm.onMapLayerRegistryLayersAdded(lyrs)
        self.assertTrue(len(dsm) == len(lyrs), msg='DataSourceManager contains one DataSource object per source only')

        dsm = DataSourceManager()
        reg.addMapLayers(lyrs)
        self.assertTrue((len(dsm) == len(lyrs)), msg='Layers added to the QgsMapLayerRegistry need to appear in the DataSourceManager')






    def test_datasourcmanagertreemodel(self):
        reg = QgsProject.instance()
        reg.removeAllMapLayers()
        dsm = DataSourceManager()
        TM = DataSourceManagerTreeModel(None, dsm)

        uriList = self.createTestSources()
        for uri in uriList:
            print('Test "{}"'.format(uri))
            ds = DataSourceFactory.Factory(uri)[0]
            print(ds)
            dsm.addSource(uri)

        self.assertEqual(len(dsm), len(uriList))
        self.assertEqual(TM.rowCount(), 3)

        for grpNode in TM.rootGroup().children():
            self.assertIsInstance(grpNode, DataSourceGroupTreeNode)
            for dsNode in grpNode.children():
                self.assertIsInstance(dsNode, DataSourceTreeNode)


            s =""



    def test_enmapbox(self):

        from enmapbox.gui.enmapboxgui import EnMAPBox
        EB = EnMAPBox()
        uriList = self.createTestSources()
        for uri in uriList:
            print('Test "{}"'.format(uri))
            ds = EB.addSource(uri)
        #qApp.exec_()



class standardDataSourceTreeNodes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    def setUp(self):

        self.wmsUri = r'crs=EPSG:3857&format&type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0'
        self.wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
        pass

    def tearDown(self):
        pass

    def createTestSources(self)->list:

        return [speclib, self.wfsUri, self.wmsUri, enmap, landcover]


    def test_testSources(self):

        reg = QgsProject.instance()

        raster = QgsRasterLayer(enmap)
        self.assertIsInstance(raster, QgsRasterLayer)
        reg.addMapLayer(raster, False)


        sl = SpectralLibrary.readFrom(speclib)
        self.assertIsInstance(sl, SpectralLibrary)
        reg.addMapLayer(sl, False)


        wfs = QgsVectorLayer(self.wfsUri, '', 'WFS')
        self.assertIsInstance(wfs, QgsVectorLayer)
        reg.addMapLayer(wfs, False)

        wms = QgsRasterLayer(self.wmsUri, '', 'wms')
        self.assertIsInstance(wms, QgsRasterLayer)
        reg.addMapLayer(wms, False)

    def test_sourceNodes(self):

        for uri in self.createTestSources():
            self.assertIsInstance(uri, str)
            dsl = DataSourceFactory.Factory(uri)

            for dataSource in dsl:
                self.assertIsInstance(dataSource, DataSource)

                node = CreateNodeFromDataSource(dataSource)
                self.assertIsInstance(node, DataSourceTreeNode)


    def test_registryresponse(self):

        from enmapbox.gui.mapcanvas import MapCanvas
        mapCanvas = MapCanvas()
        reg = QgsProject.instance()
        reg.removeAllMapLayers()

        for p in self.createTestSources():
            print(p)
            ds = DataSourceFactory.Factory(p)
            if isinstance(ds, DataSourceSpatial):
                lyr = ds.createUnregisteredMapLayer()
                mapCanvas.setLayers(lyr)

                self.assertTrue(len(mapCanvas.layers()) == 1)

                self.assertTrue(len(reg.mapLayers()) == 1)
                reg.removeAllMapLayers()
                self.assertTrue(len(mapCanvas.layers()) == 0)

    def test_datasourceTreeManagerModel(self):




        dsm = DataSourceManager()
        M = DataSourceManagerTreeModel(None, dsm)

        self.assertEqual(M.rowCount(), 0)

        #add 2 rasters
        dsm.addSources([enmapbox, hymap])
        self.assertEqual(M.rowCount(), 1)

        #add
        dsm.addSource(landcover)
        self.assertEqual(M.rowCount(), 2)

        dsm.addSource(speclib)
        self.assertEqual(M.rowCount(), 3)

        from enmapbox.gui.mapcanvas import MapCanvas


        rootIndex = M.node2index(M.rootGroup())
        for i, grpNode in enumerate(M.rootNode.children()):
            self.assertIsInstance(grpNode, DataSourceGroupTreeNode)
            grpIndex = M.node2index(grpNode)
            self.assertIsInstance(grpIndex, QModelIndex)
            self.assertTrue(grpIndex.isValid())
            self.assertEqual(grpIndex.row(), i)
            for j, dNode in enumerate(grpNode.children()):
                self.assertIsInstance(dNode, DataSourceTreeNode)
                nodeIndex = M.node2index(dNode)
                self.assertIsInstance(nodeIndex, QModelIndex)
                self.assertTrue(nodeIndex.isValid())
                self.assertEqual(nodeIndex.row(), j)

                mapCanvas = MapCanvas()
                #get mime data
                mimeData = M.mimeData([nodeIndex])
                self.assertIsInstance(mimeData, QMimeData)


                from enmapbox.gui.mimedata import extractMapLayers
                l = extractMapLayers(mimeData)
                self.assertIsInstance(l, list)
                self.assertTrue(len(l) == 1)
                self.assertIsInstance(l[0], QgsMapLayer)


                def createDropEvent(mimeData:QMimeData)->QDropEvent:
                    return QDropEvent(QPointF(0, 0), Qt.CopyAction, mimeData, Qt.LeftButton, Qt.NoModifier, QEvent.Drop)

                formats = mimeData.formats()
                self.assertIsInstance(dNode.dataSource, DataSource)
                self.assertIn(MDF_DATASOURCETREEMODELDATA, formats)

                if isinstance(dNode, RasterDataSourceTreeNode):
                    self.assertIsInstance(dNode.dataSource, DataSourceRaster)
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)

                if isinstance(dNode, VectorDataSourceTreeNode):
                    self.assertIsInstance(dNode.dataSource, DataSourceVector)
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)

                if isinstance(dNode, SpeclibDataSourceTreeNode):
                    self.assertIsInstance(dNode.dataSource, DataSourceSpectralLibrary)

                    # drop speclib to mapcanvas
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)

                    # drop speclib to spectral library widgets
                    from enmapbox.gui.spectrallibraries import SpectralLibraryWidget, SpectralLibraryPlotWidget, SpectralLibraryTableView, MIMEDATA_SPECLIB_LINK
                    self.assertTrue(MIMEDATA_SPECLIB_LINK in mimeData.formats())
                    w = SpectralLibraryWidget()
                    w.show()
                    w.plotWidget.dropEvent(createDropEvent(mimeData))
                    self.assertEqual(len(w.speclib()), len(dNode.dataSource.spectralLibrary()))



                if isinstance(dNode, HubFlowObjectTreeNode):
                    pass
        s = ""





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
                pathTmp = jp(dirTmp, 'test.{}.pkl'.format(name))
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



