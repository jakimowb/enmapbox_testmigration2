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
from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()

SHOW_GUI = False


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



class TestEnMAPBoxSplashScreen(unittest.TestCase):

    def test_splashScreen(self):

        import time
        import enmapbox
        w = QWidget()
        enmapbox.initEnMAPBoxResources()
        splash = EnMAPBoxSplashScreen(parent=w)
        self.assertIsInstance(splash, EnMAPBoxSplashScreen)
        i = 0
        splash.showMessage('Message {} {}'.format(i, str(time.time())))
        def onTimeOut(*args):
            nonlocal i
            splash.showMessage('Message {} {}'.format(i, str(time.time())))
            i += 1
        self.assertEqual(splash.size(), QSize(600,287))
        timer = QTimer()
        timer.startTimer(500)
        timer.timeout.connect(onTimeOut)

        if SHOW_GUI:
            w.show()
            splash.show()
            QGIS_APP.processEvents()
            QGIS_APP.exec_()



class TestEnMAPBox(unittest.TestCase):

    def setUp(self):

        self.E = EnMAPBox(None)

    def tearDown(self):
        self.E.close()
        self.E = None

    def test_instance(self):


        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(self.E, EnMAPBox.instance())

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_createDock(self):

        for d in ['MAP', 'TEXT', 'SPECLIB', 'MIME']:
            dock = self.E.createDock(d)
            self.assertIsInstance(dock, Dock)


    def test_addSources(self):
        E = self.E
        E.loadExampleData()
        E.removeSources(E.dataSources())
        self.assertTrue(len(E.dataSources()) == 0)
        from enmapboxtestdata import enmap
        E.addSource(enmap)
        self.assertTrue(len(E.dataSources()) == 1)

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_mapCanvas(self):
        E = self.E
        self.assertTrue(E.mapCanvas() is None)
        self.assertIsInstance(E.mapCanvas(virtual=True), MapCanvas)
        canvases = E.mapCanvases()
        self.assertIsInstance(canvases, list)
        self.assertTrue(len(canvases) == 0)

        E.loadExampleData()
        self.assertTrue(len(E.mapCanvases()) == 1)

        E.createDock('MAP')
        self.assertTrue(len(E.mapCanvases()) == 2)
        for c in E.mapCanvases():
            self.assertIsInstance(c, MapCanvas)


    def test_loadExampleData(self):
        E = self.E
        E.loadExampleData()
        self.assertTrue(len(E.dataSources()) > 0)
        E.removeSources()
        self.assertTrue(len(E.dataSources()) == 0)

        if SHOW_GUI:
            QGIS_APP.exec_()






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
        slw = speclibDock.speclibWidget()
        self.assertIsInstance(slw, SpectralLibraryWidget)
        self.assertTrue(len(slw.speclib()) == 0)
        center = SpatialPoint.fromMapCanvasCenter(mapDock.mapCanvas())


        profiles = SpectralProfile.fromMapCanvas(mapDock.mapCanvas(), center)
        for p in profiles:
            self.assertIsInstance(p, SpectralProfile)

        EMB.setCurrentMapSpectraLoading('ALL')
        EMB.loadCurrentMapSpectra(center, mapDock.mapCanvas())
        self.assertEqual(profiles, EMB.currentSpectra())
        for s in EMB.currentSpectra():
            self.assertIsInstance(s, SpectralProfile)

        EMB.setCurrentMapSpectraLoading('TOP')
        EMB.loadCurrentMapSpectra(center, mapDock.mapCanvas())
        self.assertEqual(profiles[0:1], EMB.currentSpectra())



if __name__ == '__main__':
    SHOW_GUI = False
    unittest.main()