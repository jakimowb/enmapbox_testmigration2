# -*- coding: utf-8 -*-
"""
***************************************************************************
    test_enMAPBox
    ---------------------
    Date                 : Januar 2018
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
# noinspection PyPep8Naming


import unittest, os
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QResource
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBox, EnMAPBoxSplashScreen
from enmapbox.gui.docks import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui import *


class MyOutputRaster(QgsProcessingParameterDefinition):

    def __init__(self, name='', description='', ext='bsq'):
        QgsProcessingParameterDefinition.__init__(self, name, description)
        self.ext = ext

    def getFileFilter(self, alg):
        if self.ext is None:
            return self.tr('ENVI (*.bsq *.bil);;TIFF (*.tif);;All files(*.*)', 'OutputFile')
        else:
            return self.tr('%s files(*.%s)', 'OutputFile') % (self.ext, self.ext)

    def getDefaultFileExtension(self, alg):

        return 'bsq'

class MyGeoAlgorithmus(QgsProcessingAlgorithm):

    def defineCharacteristics(self):
        self.name = 'TestAlgorithm'
        self.group = 'TestGroup'
        #self.addParameter(ParameterRaster('infile', 'Test Input Image'))
        self.addOutput(QgsProcessingParameterRasterLayer('outfile1', 'Test Output Image'))
        self.addOutput(MyOutputRaster('outfile2', 'Test MyOutput Image'))

    def processAlgorithm(self, progress):
        # map processing framework parameters to that of you algorithm
        infile = self.getParameterValue('infile')
        outfile = self.getOutputValue('outfile')
        outfile2 = self.getOutputValue('outfile2')
        s  =""
        # define
        # todo:


    def help(self):
        return True, '<todo: describe test>'



# mini test
from enmapbox.gui.applications import EnMAPBoxApplication
class TestEnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapbBox):
        super(EnMAPBoxApplication, self).__init__(enmapbBox)

        self.name = 'Test'
        self.version = '0.8.15'
        self.licence = 'None'

    def menu(self, appMenu):

        assert isinstance(appMenu, QMenu)
        a = appMenu.addAction('Call dummy action')
        a.triggered.connect(self.dummySlot)

    def processingAlgorithms(self):
        return [MyGeoAlgorithmus()]

    def dummySlot(self, *arg, **kwds):
        print('Dummy Slot called.')

class TestEnMAPBox(EnMAPBoxTestCase):

    def tearDown(self):

        emb = EnMAPBox.instance()
        if isinstance(emb, EnMAPBox):
            emb.close()

        assert EnMAPBox.instance() is None

        QgsProject.instance().removeAllMapLayers()


        super().tearDown()

    def test_resources(self):

        from enmapbox.externals.qps.resources import ResourceBrowser

        b = ResourceBrowser()

        r"F:\miniconda3\envs\qgis_stable\Library\qgis\qtplugins;" \
        r"F:\miniconda3\envs\qgis_stable\Library\plugins;" \
        r"F:\miniconda3\envs\qgis_stable\Library\qtplugins;" \
        r"F:\miniconda3\envs\qgis_stable\Library\plugins;"

        self.showGui(b)
        s = ""

    def test_AboutDialog(self):

        from enmapbox.gui.about import AboutDialog
        d = AboutDialog()
        self.assertIsInstance(d, AboutDialog)
        self.showGui(d)

    def test_instance(self):
        EMB = EnMAPBox()

        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())
        log = QgsApplication.instance().messageLog()

        from enmapbox import messageLog
        #messageLog('EnMAPBox TEST STARTED', Qgis.Info)
        s = ""

        self.showGui([qgis.utils.iface.mainWindow(), EMB.ui])

    def test_instanceWithData(self):

        EMB = EnMAPBox(load_other_apps=False)
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)
        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())
        EMB.loadExampleData()
        self.assertTrue(len(QgsProject.instance().mapLayers()) > 0)
        canvases = EMB.mapCanvases()
        self.assertTrue(canvases[-1] == EMB.currentMapCanvas())

        import qgis.utils
        QgsProject.instance()
        qgis.utils.iface.actionSaveProject().trigger()
        self.showGui([qgis.utils.iface.mainWindow(), EMB.ui])


    def test_Qgis(self):

        from enmapbox import Qgis
        from enmapboxtestdata import enmap, landcover_polygons
        from qgis.utils import iface
        from enmapbox.testing import WMS_OSM, WMS_GMAPS, WFS_Berlin
        layers = []
        layers.append(QgsRasterLayer(enmap))
        layers.append(QgsVectorLayer(landcover_polygons))
        #layers.append(QgsRasterLayer(WMS_OSM, 'osm', 'wms'))
        #layers.append(QgsVectorLayer(WFS_Berlin, 'wfs', 'WFS'))

        for lyr in layers:
            self.assertIsInstance(lyr, QgsMapLayer)
            self.assertTrue(lyr.isValid())

        self.assertIsInstance(iface, QgisInterface)
        QgsProject.instance().addMapLayers(layers)

        for layer in layers:
            self.assertIsInstance(layer, QgsMapLayer)

            iface.mapCanvas().setLayers([layer])
            iface.setActiveLayer(layer)
            self.assertEqual(iface.activeLayer(), layer)

            # todo: test return types
            result1 = Qgis.activeBand(0)
            result2 = Qgis.activeData()
            result3 = Qgis.activeRaster()
            s = ""

        box = EnMAPBox(load_core_apps=False, load_other_apps=False)
        iface = qgis.utils.iface
        self.assertIsInstance(iface, QgisInterface)
        root = iface.layerTreeView().model().rootGroup()
        self.assertIsInstance(root, QgsLayerTree)

        self.assertTrue(len(box.dataSources()) == 0)

        lyrNew = TestObjects.createVectorLayer()
        QgsProject.instance().addMapLayer(lyrNew, True)
        QgsApplication.processEvents()

        self.assertEqual(len(box.dataSources()), 0)

        nQGIS = len(root.findLayerIds())
        box.dataSourceManager().importSourcesFromQGISRegistry()
        QgsApplication.processEvents()
        self.assertEqual(len(box.dataSources()), nQGIS)

        QgsApplication.processEvents()

        self.assertEqual(len(box.dataSources()), nQGIS)

    def test_createDock(self):

        EMB = EnMAPBox()
        for d in ['MAP', 'TEXT', 'SPECLIB', 'MIME']:
            dock = EMB.createDock(d)
            self.assertIsInstance(dock, Dock)
        self.showGui()

    def test_qgis_interactions(self):

        import qgis.utils
        E = EnMAPBox()
        E.loadExampleData()
        QgsApplication.instance().processEvents()

        dsSpatial = E.dataSourceManager().sources('SPATIAL')
        self.assertIsInstance(dsSpatial, list)
        ds1 = dsSpatial[0]
        self.assertIsInstance(ds1, DataSourceSpatial)
        uri = ds1.uri()
        uri2 = ds1.mapLayer().source()
        # remove layers from the QgsProject and see what happens.
        # this should remove the entire dataset
        if False:
            lyr = ds1.createUnregisteredMapLayer()
            QgsProject.instance().addMapLayer(lyr)

            n1 = len(E.dataSources())
            # remove a layer unknown to EnMAP-Box
            QgsProject.instance().removeMapLayer(lyr)
            self.assertEqual(n1, len(E.dataSources()))

            # remove a layer known to an EnMAP-Box map canvas
            lyr = E.mapLayers()[0]
            self.assertIsInstance(lyr, QgsMapLayer)
            QgsProject.instance().removeMapLayer(lyr)
            self.assertEqual(n1, len(E.dataSources()))

        # remove a datasource
        #E.removeSource(ds1)
        #self.assertEqual(n1 - 1, len(E.dataSources()))
        #QgsProject.instance().removeMapLayer(ds1.mapLayer())
        #self.assertEqual(n1-1, len(E.dataSources()))

        self.showGui([E.ui, qgis.utils.iface.ui])



    def test_addSources(self):
        E = EnMAPBox()
        E.loadExampleData()
        E.removeSources(E.dataSources())
        self.assertTrue(len(E.dataSources()) == 0)
        from enmapboxtestdata import enmap, landcover_polygons
        E.addSource(enmap)
        self.assertTrue(len(E.dataSources()) == 1)
        E.addSource(landcover_polygons)
        self.assertTrue(len(E.dataSources()) == 2)

        self.showGui()

    def test_mapCanvas(self):
        E = EnMAPBox()
        self.assertTrue(E.mapCanvas() is None)
        self.assertIsInstance(E.mapCanvas(virtual=True), MapCanvas)
        canvases = E.mapCanvases()
        self.assertIsInstance(canvases, list)
        self.assertTrue(len(canvases) == 0)

        #E.loadExampleData()
        #self.assertTrue(len(E.mapCanvases()) == 1)

        E.createDock('MAP')
        self.assertTrue(len(E.mapCanvases()) == 1)
        for c in E.mapCanvases():
            self.assertIsInstance(c, MapCanvas)

        self.showGui()

    def test_loadExampleData(self):
        E = EnMAPBox()
        E.loadExampleData()
        n = len(E.dataSources())
        self.assertTrue(n > 0)
        self.showGui(E.ui)

    def test_loadAndUnloadData(self):
        E = EnMAPBox()
        mapDock = E.createDock('MAP') # empty map
        self.assertIsInstance(mapDock, MapDock)
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)

        self.assertTrue(len(E.dataSources()) == 0)

        # load
        E.loadExampleData()
        self.assertTrue(len(E.dataSources()) > 0)
        ns = len(E.dataSources('SPATIAL'))
        self.assertTrue(len(QgsProject.instance().mapLayers())  > 0)

        # add layer to map
        mapDock.addLayers([TestObjects.createRasterLayer()])

        # unload
        E.removeSources()
        self.assertTrue(len(E.dataSources()) == 0)
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)

    def test_speclibDocks(self):
        EMB = EnMAPBox()
        EMB.loadExampleData()
        mapDock = EMB.createDock('MAP')
        self.assertIsInstance(mapDock, MapDock)
        sources = EMB.dataSources('RASTER')

        self.assertIsInstance(sources, list)
        self.assertTrue(len(sources) > 0 )
        layers = [QgsRasterLayer(p) for p in sources]
        self.assertTrue(len(layers) > 0)
        mapDock.mapCanvas().setLayers(layers)

        speclibDock = EMB.createDock('SPECLIB')
        self.assertIsInstance(speclibDock, SpectralLibraryDock)
        slw = speclibDock.speclibWidget()
        self.assertIsInstance(slw, SpectralLibraryWidget)
        self.assertTrue(len(slw.speclib()) == 0)
        center = SpatialPoint.fromMapCanvasCenter(mapDock.mapCanvas())


        profiles = SpectralProfile.fromMapCanvas(mapDock.mapCanvas(), center)
        for p in profiles:
            self.assertIsInstance(p, SpectralProfile)


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)