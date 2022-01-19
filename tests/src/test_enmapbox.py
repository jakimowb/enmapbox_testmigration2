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
import os
import pathlib
import unittest
import xmlrunner
from PyQt5.QtWidgets import QApplication, QMenu

import qgis
from enmapbox import DIR_REPO
from enmapbox.gui.datasources.datasources import SpatialDataSource
from enmapbox.gui.dataviews.docks import SpectralLibraryDock, MapDock, Dock
from enmapbox.gui.mapcanvas import MapCanvas
from enmapbox.qgispluginsupport.qps.speclib.core.spectralprofile import SpectralProfile
from enmapbox.qgispluginsupport.qps.speclib.gui.spectrallibrarywidget import SpectralLibraryWidget
from enmapbox.qgispluginsupport.qps.utils import SpatialPoint
from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.gui.enmapboxgui import EnMAPBox
from qgis._core import QgsProcessingParameterDefinition, QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, \
    QgsLayerTree, QgsApplication, QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer

from qgis._gui import QgisInterface


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
        # self.addParameter(ParameterRaster('infile', 'Test Input Image'))
        self.addOutput(QgsProcessingParameterRasterLayer('outfile1', 'Test Output Image'))
        self.addOutput(MyOutputRaster('outfile2', 'Test MyOutput Image'))

    def processAlgorithm(self, progress):
        # map processing framework parameters to that of you algorithm
        infile = self.getParameterValue('infile')
        outfile = self.getOutputValue('outfile')
        outfile2 = self.getOutputValue('outfile2')
        s = ""
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

        from enmapbox.qgispluginsupport.qps.resources import ResourceBrowser

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

    @unittest.skipIf(not (pathlib.Path(DIR_REPO) / 'qgisresources').is_dir(), 'qgisresources dir does not exist')
    def test_findqgisresources(self):
        from enmapbox.qgispluginsupport.qps.resources import findQGISResourceFiles
        results = findQGISResourceFiles()
        print('QGIS Resource files:')
        for p in results:
            print(p)
        self.assertTrue(len(results) > 0)

    def test_instance_pure(self):
        EMB = EnMAPBox(load_other_apps=False, load_core_apps=False)

        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())

        self.showGui([qgis.utils.iface.mainWindow(), EMB.ui])

    def test_instance_all_apps(self):
        EMB = EnMAPBox(load_core_apps=True, load_other_apps=True)
        self.assertIsInstance(EMB, EnMAPBox)
        self.showGui(EMB.ui)

    def test_instance_coreapps(self):
        EMB = EnMAPBox(load_core_apps=True, load_other_apps=False)

        for f in os.scandir(self.createTestOutputDirectory()):
            if os.path.isfile(f.path):
                EMB.addSource(f.path)

        self.showGui(EMB.ui)

    def test_instance_coreapps_and_data(self):

        EMB = EnMAPBox(load_core_apps=True, load_other_apps=False)

        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)
        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(EMB, EnMAPBox.instance())

        EMB.openExampleData(mapWindows=1, testData=True)
        self.assertTrue(len(QgsProject.instance().mapLayers()) > 0)
        canvases = EMB.mapCanvases()
        self.assertTrue(canvases[-1] == EMB.currentMapCanvas())

        self.showGui([EMB.ui])

    def test_Qgis(self):

        from enmapbox.exampledata import enmap, landcover_polygons
        from qgis.utils import iface
        layers = [QgsRasterLayer(enmap), QgsVectorLayer(landcover_polygons)]
        # layers.append(QgsRasterLayer(WMS_OSM, 'osm', 'wms'))
        # layers.append(QgsVectorLayer(WFS_Berlin, 'wfs', 'WFS'))

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

        box = EnMAPBox(load_core_apps=False, load_other_apps=False)
        iface = qgis.utils.iface
        self.assertIsInstance(iface, QgisInterface)
        root = iface.layerTreeView().layerTreeModel().rootGroup()
        self.assertIsInstance(root, QgsLayerTree)

        self.assertTrue(len(box.dataSources()) == 0)

        lyrNew = TestObjects.createVectorLayer()
        QgsProject.instance().addMapLayer(lyrNew, True)
        QgsApplication.processEvents()

        self.assertEqual(len(box.dataSources()), 0)

        nQGIS = len(root.findLayerIds())
        box.dataSourceManager().importQGISLayers()
        QgsApplication.processEvents()
        self.assertEqual(len(box.dataSources()), nQGIS)

        QgsApplication.processEvents()

        self.assertEqual(len(box.dataSources()), nQGIS)
        self.showGui([box, iface.mainWindow()])

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
        self.assertIsInstance(ds1, SpatialDataSource)
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
        # E.removeSource(ds1)
        # self.assertEqual(n1 - 1, len(E.dataSources()))
        # QgsProject.instance().removeMapLayer(ds1.mapLayer())
        # self.assertEqual(n1-1, len(E.dataSources()))

        self.showGui([E.ui, qgis.utils.iface.ui])

    def test_addSources(self):
        E = EnMAPBox()
        E.loadExampleData()
        E.removeSources(E.dataSources())
        self.assertTrue(len(E.dataSources()) == 0)
        from enmapbox.exampledata import enmap, landcover_polygons
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

        # E.loadExampleData()
        # self.assertTrue(len(E.mapCanvases()) == 1)

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
        mapDock = E.createDock('MAP')  # empty map
        self.assertIsInstance(mapDock, MapDock)
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)

        self.assertTrue(len(E.dataSources()) == 0)

        # load
        E.loadExampleData()
        QApplication.processEvents()

        self.assertTrue(len(E.dataSources()) > 0)
        ns = len(E.dataSources('SPATIAL'))
        # self.assertTrue(len(QgsProject.instance().mapLayers()) == 0)

        # add layer to map
        mapDock.addLayers([TestObjects.createRasterLayer()])

        # unload
        E.removeSources()
        self.assertTrue(len(E.dataSources()) == 0)
        self.assertTrue(len(QgsProject.instance().mapLayers()) == 1, msg='Layers created outside EnMAP-Box should '
                                                                         'still exists after closing it')

    def test_speclibDocks(self):
        EMB = EnMAPBox()
        EMB.loadExampleData()
        mapDock = EMB.createDock('MAP')
        self.assertIsInstance(mapDock, MapDock)
        sources = EMB.dataSources('RASTER')

        self.assertIsInstance(sources, list)
        self.assertTrue(len(sources) > 0)
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
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
