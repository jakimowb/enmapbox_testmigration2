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
from __future__ import unicode_literals, absolute_import

import unittest
from unittest import TestCase
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.sandbox import initQgisApplication
from enmapbox.gui.utils import *
from enmapbox.gui.enmapboxgui import EnMAPBox

QGIS_APP = initQgisApplication()


from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.outputs import OutputRaster



from processing.core.outputs import OutputRaster

class MyOutputRaster(OutputRaster):

    def __init__(self, name='', description='', ext='bsq'):
        OutputRaster.__init__(self, name, description)
        self.ext = ext

    def getFileFilter(self, alg):
        if self.ext is None:
            return self.tr('ENVI (*.bsq *.bil);;TIFF (*.tif);;All files(*.*)', 'OutputFile')
        else:
            return self.tr('%s files(*.%s)', 'OutputFile') % (self.ext, self.ext)

    def getDefaultFileExtension(self, alg):

        return 'bsq'

class MyGeoAlgorithmus(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'TestAlgorithm'
        self.group = 'TestGroup'
        #self.addParameter(ParameterRaster('infile', 'Test Input Image'))
        self.addOutput(OutputRaster('outfile1', 'Test Output Image'))
        self.addOutput(MyOutputRaster('outfile2', 'Test MyOutput Image'))

    def processAlgorithm(self, progress):
        # map processing framework parameters to that of you algorithm
        infile = self.getParameterValue('infile')
        outfile = self.getOutputValue('outfile')
        outfile2 = self.getOutputValue('outfile2')
        s  =""
        # define
        # todo:

    def getCustomParametersDialog(self):


        from PyQt4.QtGui import QDialog


        d = QDialog()

        return d


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

    def setUpClass(cls):
        cls.EMB = EnMAPBox(None)
        cls.EMB.loadExampleData()
        # self.QGIS_APP.exec_()

    def setUp(self):


        pass

    def tearDown(self):
        self.EMB.close()


    def test_instance(self):
        self.fail()


    def test_initQGISProcessingFramework(self):
        self.fail()

    def test_addApplication(self):
        myApp = TestEnMAPBoxApp(self.EMB)
        self.EMB.addApplication(myApp)

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
        self.fail()

    def test_removeDock(self):
        self.fail()

    def test_isLinkedWithQGIS(self):
        self.fail()

    def test_addSources(self):
        self.fail()

    def test_addSource(self):
        self.fail()

    def test_removeSources(self):
        self.fail()

    def test_removeSource(self):
        self.fail()

    def test_menu(self):
        self.fail()

    def test_run(self):
        self.fail()

    def test_close(self):
        self.fail()

    def test_initQgisInterface(self):
        self.fail()

    def test_mapCanvas(self):
        self.fail()

    def test_loadExampleData(self):
        self.fail()

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

if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication
    app = initQgisApplication()


    if True:
        path = r'/Users/benjamin.jakimow/Repositories/QGIS_Plugins/enmap-box/enmapbox/gui/tests/test_xyz.bil'
        fileFilter = 'ENVI (*.bsq, *.bil);;TIFF (*.tif);; All (*.*)'

        from qgis.gui import QgsEncodingFileDialog
        d = QgsEncodingFileDialog(None, 'Save file', path, fileFilter, None)
        print(d.exec_())
    else:

        emb = EnMAPBox(None)

        myApp = TestEnMAPBoxApp(emb)
        emb.addApplication(myApp)

    app.exec_()


    unittest.main()