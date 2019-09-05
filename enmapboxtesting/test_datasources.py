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

SHOW_GUI = False
import unittest, tempfile, pathlib
from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()
from enmapbox.gui.utils import *
from enmapbox.gui.datasourcemanager import *
from enmapboxtestdata import enmap, hires, landcover_polygons, library


class standardDataSources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    def setUp(self):

        self.wmsUri = r'crs=EPSG:3857&format&type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=19&zmin=0'
        self.wmsUri = 'referer=OpenStreetMap%20contributors,%20under%20ODbL&type=xyz&url=http://tiles.wmflabs.org/hikebike/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=17&zmin=1'
        self.wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
        pass

    def tearDown(self):
        pass

    def test_rasters(self):
        for uri in [None, type(None), landcover_polygons, self.wfsUri]:
            self.assertTrue(rasterProvider(uri) == None)

        self.assertTrue(None == rasterProvider(self.wfsUri))
        self.assertTrue(DataSourceFactory.isRasterSource(enmap))
        self.assertTrue(rasterProvider(self.wmsUri) == 'wms')
        self.assertTrue(DataSourceFactory.isRasterSource(self.wmsUri))

        for uri in [enmap, self.wmsUri]:
            ds = DataSourceFactory.create(uri)
            self.assertIsInstance(ds, list)
            self.assertTrue(len(ds) == 1)
            for source in ds:
                self.assertIsInstance(source, DataSourceRaster)
                self.assertIsInstance(source.spatialExtent(), SpatialExtent)
                self.assertIsInstance(source.mProvider, str)
                self.assertIsInstance(source.icon(), QIcon)


    def createTestSources(self)->list:
        return [library, self.wfsUri, self.wmsUri, enmap, landcover_polygons]

    def createTestSourceLayers(self)->list:
        return [QgsRasterLayer(self.wmsUri, '', 'wms'), QgsVectorLayer(self.wfsUri, '', 'WFS'),
                QgsRasterLayer(enmap), QgsVectorLayer(landcover_polygons), SpectralLibrary.readFrom(library)
                ]


    def test_netCDF(self):

        path = r'Q:\Processing_BJ\99_OSARIS_Testdata\Loibl-2019-OSARIS-Ala-Archa\Coherences\20151207--20151231-coherence.grd'

        if os.path.isfile(path):
            uri, name, provider = DataSourceFactory.isRasterSource(path)

            dsl = DataSourceFactory.create(uri)

            self.assertIsInstance(dsl, list)
            for ds in dsl:
                self.assertIsInstance(ds, DataSourceRaster)

            s = ""


    def test_hubflowsources(self):

        from hubflow.testdata import enmapClassification, vector, enmap
        from hubflow.core import FlowObject
        hubFlowObjects = [vector(), enmap(), enmapClassification()]
        #hubFlowObjects = [vector()]
        #hubFlowObjects = [enmapClassification()]

        for obj in hubFlowObjects:
            isObj, o = DataSourceFactory.isHubFlowObj(obj)
            self.assertTrue(isObj)
            self.assertIsInstance(o, FlowObject)

            ds = DataSourceFactory.create(obj)
            self.assertIsInstance(ds, list)
            self.assertIsInstance(ds[0], HubFlowDataSource)

        for o in hubFlowObjects:
            node = HubFlowObjectTreeNode(None, None)
            self.assertIsInstance(node, DataSourceTreeNode)
            ds = DataSourceFactory.create(o)[0]
            assert isinstance(ds, HubFlowDataSource)

            n = node.fetchInternals(ds.flowObject())
            self.assertIsInstance(n, TreeNode)
            self.assertTrue(len(n.childNodes()) > 0)
            node.connectDataSource(ds)
            self.assertIsInstance(node.childNodes(), list)
            self.assertTrue(len(node.childNodes()) > 0)
            s = ""

        DSM = DataSourceManager()
        TM = DataSourceManagerTreeModel(None, DSM)

        TV = QTreeView()
        TV.header().setResizeMode(QHeaderView.ResizeToContents)
        TV.setModel(TM)
        TV.show()
        TV.resize(QSize(400,250))

        DSM.addSources(hubFlowObjects)
        self.assertTrue(len(DSM) == len(hubFlowObjects))

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_classifier(self):

        import pickle

        pathClassifier = r''
        if not os.path.isfile(pathClassifier):
            self.fail('missing hub flow classifier')
            return
        f = open(pathClassifier, 'rb')
        classifier = pickle.load(file=f)
        f.close()

        HubFlowObjectTreeNode.fetchInternals(classifier._sklEstimator, None)

        DSM = DataSourceManager()
        TM = DataSourceManagerTreeModel(None, DSM)

        TV = QTreeView()
        TV.header().setResizeMode(QHeaderView.ResizeToContents)
        TV.setModel(TM)
        TV.show()
        TV.resize(QSize(400,250))

        DSM.addSource(classifier)
        self.assertTrue(1 > 0)

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_testSources(self):

        for l in self.createTestSourceLayers():
            self.assertIsInstance(l, QgsMapLayer)
            self.assertTrue(l.isValid())

    def test_vectors(self):
        for uri in [None, type(None), self.wmsUri, enmap]:
            self.assertTrue(vectorProvider(uri) == None)

        self.assertTrue(vectorProvider(self.wfsUri) == 'WFS')
        self.assertTrue(DataSourceFactory.isVectorSource(self.wfsUri))
        self.assertTrue(DataSourceFactory.isVectorSource(landcover_polygons))

        for uri in [self.wfsUri, landcover_polygons]:
            sources = DataSourceFactory.create(uri)
            self.assertIsInstance(sources, list)
            self.assertTrue(len(sources) == 1)
            for source in sources:
                self.assertIsInstance(source, DataSourceVector)
                self.assertIsInstance(source.spatialExtent(), SpatialExtent)
                self.assertIsInstance(source.mProvider, str)

    def test_speclibs(self):

        ds = DataSourceFactory.create(library)
        self.assertIsInstance(ds, list)
        self.assertTrue(len(ds) == 1)
        ds = ds[0]
        self.assertIsInstance(ds, DataSourceSpectralLibrary)

    def test_datasourceversions(self):

        path = tempfile.mktemp(suffix='image.bsq')
        TestObjects.inMemoryImage(nb=2, nl=500, path=path)


        src1 = DataSourceFactory.create(path)[0]


        self.assertIsInstance(src1, DataSourceRaster)
        self.assertTrue(src1.nBands == 2)
        self.assertTrue(src1.nLines == 500)
        TestObjects.inMemoryImage(nb=30, nl=1000, path=path)

        src2 = DataSourceFactory.create(path)[0]

        src3 = DataSourceFactory.create(path)[0]
        self.assertIsInstance(src2, DataSourceRaster)
        self.assertTrue(src2.nBands == 30)
        self.assertTrue(src2.nLines == 1000)
        self.assertTrue(src1.modificationTime() < src2.modificationTime())
        self.assertTrue(src2.isNewVersionOf(src1))
        self.assertFalse(src3.isNewVersionOf(src2))


        DSM = DataSourceManager()

        self.assertIsInstance(DSM, DataSourceManager)
        self.assertTrue(len(DSM) == 0)

        DSM.addSource(src1)
        self.assertTrue(len(DSM) == 1)
        self.assertEqual(DSM.sources()[0], src1)
        DSM.addSource(src2)
        self.assertTrue(len(DSM) == 1)
        self.assertEqual(DSM.sources()[0], src2)


    def test_datasourcemanager_equalsources(self):

        p1 = r'C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\enmapboxtestdata\hires_berlin.bsq'
        p2 = r'C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/enmapboxplugin/enmapboxtestdata/hires_berlin.bsq'

        dsm = DataSourceManager()
        dsm.addSources([p1,p2])
        self.assertTrue(len(dsm) == 1)

        dsm = DataSourceManager()
        dsm.addSources([p2, p1])
        self.assertTrue(len(dsm) == 1)

    def test_datasourcemanager(self):
        reg = QgsProject.instance()
        reg.removeAllMapLayers()
        dsm = DataSourceManager()
        uris = [library, enmap, landcover_polygons, self.wfsUri, self.wmsUri]
        dsm.addSources(uris)

        self.assertTrue((len(dsm) == len(uris)))
        dsm.addSources(uris)
        self.assertTrue((len(dsm) == len(uris)), msg='Redundant sources are not allowed')
        uriList = dsm.uriList()
        self.assertIsInstance(uriList, list)
        self.assertTrue(len(uriList) == len(uris))
        self.assertListEqual(uris, dsm.uriList())

        self.assertTrue(len(dsm.sources('SPATIAL')) == 5)
        self.assertTrue(len(dsm.sources('RASTER')) == 2)
        self.assertTrue(len(dsm.sources('VECTOR')) == 3)
        self.assertTrue(len(dsm.sources('SPECLIB')) == 1)


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
        reg.addMapLayers(lyrs)
        self.assertTrue((len(dsm) == 0))

        dsm.importSourcesFromQGISRegistry()
        l = len(dsm)
        self.assertTrue((l == len(reg.mapLayers())))

        reg.removeAllMapLayers()

        # test doubles input
        l = len(dsm)
        try:

            p1 = str(pathlib.WindowsPath(pathlib.Path(enmap)))
            p2 = str(pathlib.Path(enmap).as_posix())

            dsm.addSources(p1)
            dsm.addSources(p2)

            self.assertTrue(len(dsm) == l, msg='DataSourceManager should not contain the same source multiple times')
        except:
            pass

        s = ""


    def test_datasourcmanagertreemodel(self):
        reg = QgsProject.instance()
        reg.removeAllMapLayers()
        dsm = DataSourceManager()
        TM = DataSourceManagerTreeModel(None, dsm)

        uriList = self.createTestSources()
        for uri in uriList:
            print('Test "{}"'.format(uri))
            ds = DataSourceFactory.create(uri)[0]
            print(ds)
            dsm.addSource(uri)

        self.assertEqual(len(dsm), len(uriList))
        self.assertEqual(TM.rowCount(None), 3, msg='More than 3 RasterSource type nodes. Should be raster, vector, speclibs = 3 only.')

        for grpNode in TM.rootNode().children():
            self.assertIsInstance(grpNode, DataSourceGroupTreeNode)
            for dsNode in grpNode.childNodes():
                self.assertIsInstance(dsNode, DataSourceTreeNode)


        rasterGroupNode = [n for n in TM.rootNode() if n.name() == 'Raster Data'][0]
        n = len(rasterGroupNode.childNodes())
        dsm.addSources(enmap)

        self.assertEqual(n, len(rasterGroupNode.childNodes()))


    def test_enmapbox(self):

        from enmapbox.gui.enmapboxgui import EnMAPBox
        EB = EnMAPBox()
        uriList = self.createTestSources()
        for uri in uriList:
            print('Test "{}"'.format(uri))
            ds = EB.addSource(uri)




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

        return [library, self.wfsUri, self.wmsUri, enmap, landcover_polygons]


    def test_testSources(self):

        reg = QgsProject.instance()

        raster = QgsRasterLayer(enmap)
        self.assertIsInstance(raster, QgsRasterLayer)
        reg.addMapLayer(raster, False)


        sl = SpectralLibrary.readFrom(library)
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
            dsl = DataSourceFactory.create(uri)

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
            ds = DataSourceFactory.create(p)
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
        self.assertIsInstance(M, DataSourceManagerTreeModel)

        self.assertEqual(M.rowCount(None), 0)

        #add 2 rasters
        dsm.addSources([enmap, hires])
        self.assertEqual(M.rowCount(None), 1)

        #add
        dsm.addSource(landcover_polygons)
        self.assertEqual(M.rowCount(None), 2)

        dsm.addSource(library)
        self.assertEqual(M.rowCount(None), 3)

        from enmapbox.gui.mapcanvas import MapCanvas


        for i, grpNode in enumerate(M.rootNode().children()):
            self.assertIsInstance(grpNode, DataSourceGroupTreeNode)
            grpIndex = M.node2index(grpNode)
            self.assertIsInstance(grpIndex, QModelIndex)
            self.assertTrue(grpIndex.isValid())
            self.assertEqual(grpIndex.row(), i)


            rasterSourceNodes = []

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
                self.assertIsInstance(dNode.mDataSource, DataSource)
                self.assertIn(MDF_DATASOURCETREEMODELDATA, formats)

                if isinstance(dNode, RasterDataSourceTreeNode):
                    self.assertIsInstance(dNode.mDataSource, DataSourceRaster)
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)
                    rasterSourceNodes.append(dNode)
                if isinstance(dNode, VectorDataSourceTreeNode):
                    self.assertIsInstance(dNode.mDataSource, DataSourceVector)
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)

                if isinstance(dNode, SpeclibDataSourceTreeNode):
                    self.assertIsInstance(dNode.mDataSource, DataSourceSpectralLibrary)

                    # drop speclib to mapcanvas
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == 1)

                    # drop speclib to spectral library widgets
                    from enmapbox.gui.speclib.spectrallibraries import SpectralLibraryWidget, MIMEDATA_SPECLIB_LINK
                    self.assertTrue(MIMEDATA_SPECLIB_LINK in mimeData.formats())
                    w = SpectralLibraryWidget()
                    w.show()
                    w.plotWidget.dropEvent(createDropEvent(mimeData))
                    self.assertEqual(len(w.speclib()), len(dNode.mDataSource.speclib()))



                if isinstance(dNode, HubFlowObjectTreeNode):
                    pass

            for node in rasterSourceNodes:
                self.assertIsInstance(node, RasterDataSourceTreeNode)
                self.assertIsInstance(node.childNodes(), TreeNode)
                n0 = len(mapCanvas.layers())
                for n, child in enumerate(node.mNodeBands.children()):
                    self.assertIsInstance(child, RasterBandTreeNode)
                    nodeIndex = M.node2index(child)
                    mimeData = M.mimeData([nodeIndex])
                    self.assertIsInstance(mimeData, QMimeData)
                    # drop speclib to mapcanvas
                    mapCanvas.dropEvent(createDropEvent(mimeData))
                    self.assertTrue(len(mapCanvas.layers()) == n0 + n + 1)

                    if n > 3:
                        break




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

        from enmapbox.gui.utils import jp, mkdir
        from enmapbox import DIR_REPO
        from enmapbox.gui.datasources import HubFlowDataSource

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
                ds = DataSourceFactory.create(pathTmp)
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



