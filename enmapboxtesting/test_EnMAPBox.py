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


import unittest
from enmapboxtesting import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()

SHOW_GUI = True
from enmapbox.gui.utils import *



from enmapboxtestdata import enmap
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.docks import *
from enmapbox.gui.mapcanvas import *
from enmapbox.gui.speclib.spectrallibraries import *

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

    def geoAlgorithms(self):
        return MyGeoAlgorithmus()

    def dummySlot(self, *arg, **kwds):
        print('Dummy Slot called.')




class TestEnMAPBox(unittest.TestCase):

    def setUp(self):
        self.EB = EnMAPBox(None)

    def tearDown(self):
        self.EB.close()
        del self.EB


    def test_instance(self):
        emb = EnMAPBox.instance()
        self.assertIsInstance(emb, EnMAPBox)
        self.assertEqual(emb, self.EB)

    def test_initQGISProcessingFramework(self):
        self.fail()

    def test_addApplication(self):
        myApp = TestEnMAPBoxApp(self.EB)
        self.EB.addApplication(myApp)

    def test_loadCurrentMapSpectra(self):
        self.fail()

    def test_activateMapTool(self):
        self.fail()

    def test_setMapTool(self):
        self.fail()

    def test_initEnMAPBoxApplications(self):
        self.fail()

    def test_exit(self):
        self.fail()

    def test_onLogMessage(self):
        self.fail()

    def test_onDataDropped(self):
        self.fail()

    def test_openExampleData(self):
        self.fail()

    def test_onAddDataSource(self):
        self.fail()

    def test_onDataSourceAdded(self):
        self.fail()

    def test_saveProject(self):
        self.fail()

    def test_restoreProject(self):
        self.fail()

    def test_setCurrentLocation(self):
        self.fail()

    def test_setCurrentSpectra(self):
        self.fail()

    def test_currentSpectra(self):
        self.fail()

    def test_dataSources(self):
        self.fail()

    def test_createDock(self):
        from enmapbox.gui.dockmanager import LUT_DOCKTYPES
        for d in ['MAP','TEXT','SPECLIB', 'MIME']:
            dock = self.EB.createDock(d)
            self.assertIsInstance(dock, Dock)
            self.assertIsInstance(dock, LUT_DOCKTYPES[d])

    def test_removeDock(self):
        self.fail()

    def test_isLinkedWithQGIS(self):
        self.fail()

    def test_addSources(self):
        self.EB.removeSources(self.EB.dataSources())
        self.assertTrue(len(self.EB.dataSources()) == 0)
        self.EB.addSource(enmap)
        self.assertTrue(len(self.EB.dataSources()) == 1)

    def test_removeSources(self):
        self.fail()

    def test_removeSource(self):
        self.fail()

    def test_menu(self):
        self.fail()

    def test_run(self):


        self.EB.run()

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_close(self):
        self.fail()

    def test_initQgisInterface(self):
        self.fail()

    def test_mapCanvas(self):
        self.assertTrue(self.EB.mapCanvas() is None)
        self.assertIsInstance(self.EB.mapCanvas(virtual=True), MapCanvas)
        canvases = self.EB.mapCanvases()
        self.assertIsInstance(canvases, list)
        self.assertTrue(len(canvases) == 0)

        self.EB.loadExampleData()
        self.assertTrue(len(self.EB.mapCanvases()) == 1)

        self.EB.createDock('MAP')
        self.assertTrue(len(self.EB.mapCanvases()) == 2)
        for c in self.EB.mapCanvases():
            self.assertIsInstance(c, MapCanvas)


    def test_loadExampleData(self):
        self.EB.loadExampleData()
        self.assertTrue(len(self.EB.dataSources()) > 0)
        self.EB.removeSources()
        self.assertTrue(len(self.EB.dataSources()) == 0)

    def test_openMessageLog(self):
        self.fail()

    def test_addLayers(self):
        self.fail()

    def test_addLayer(self):
        self.fail()

    def test_removeAllLayers(self):
        self.fail()

    def test_newProject(self):
        self.fail()

    def test_addVectorLayer(self):
        self.fail()

    def test_addRasterLayer(self):
        self.fail()

    def test_activeLayer(self):
        self.fail()

    def test_addToolBarIcon(self):
        self.fail()

    def test_removeToolBarIcon(self):
        self.fail()

    def test_addToolBar(self):
        self.fail()


class TestEnMAPBoxWorkflows(unittest.TestCase):

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
        mapDock.setLayers(layers)

        speclibDock = EMB.createDock('SPECLIB')
        self.assertIsInstance(speclibDock, SpectralLibraryDock)
        slw = speclibDock.speclibWidget
        self.assertIsInstance(slw, SpectralLibraryWidget)
        self.assertTrue(len(slw.speclib()) == 0)
        center = SpatialPoint.fromMapCanvasCenter(mapDock.canvas)


        profiles = SpectralProfile.fromMapCanvas(mapDock.canvas, center)
        for p in profiles:
            self.assertIsInstance(p, SpectralProfile)

        EMB.setCurrentMapSpectraLoading('ALL')
        EMB.loadCurrentMapSpectra(center, mapDock.canvas)
        self.assertEqual(profiles, EMB.currentSpectra())
        for s in EMB.currentSpectra():
            self.assertIsInstance(s, SpectralProfile)

        EMB.setCurrentMapSpectraLoading('TOP')
        EMB.loadCurrentMapSpectra(center, mapDock.canvas)
        self.assertEqual(profiles[0:1], EMB.currentSpectra())

        slw.setAddCurrentSpectraToSpeclibMode(True)
        n = len(slw.speclib())
        slw.setCurrentSpectra(profiles)
        self.assertTrue(len(slw.speclib()) == n+len(profiles))
        self.assertTrue(len(slw.currentSpectra()) == 0)
        EMB.setCurrentSpectra(profiles)
        self.assertTrue(len(slw.speclib()) == n + len(profiles)*2)


        slw.setAddCurrentSpectraToSpeclibMode(False)

        n = len(slw.speclib())
        EMB.setCurrentSpectra(profiles)

        self.assertTrue(len(slw.currentSpectra()) == len(profiles))
        self.assertTrue(len(slw.speclib()) == n)

        EMB.setCurrentSpectra([])
        self.assertTrue(len(slw.currentSpectra()) == 0)
        self.assertTrue(len(slw.speclib()) == n)

        s = ""

if __name__ == '__main__':
    SHOW_GUI = False
    unittest.main()