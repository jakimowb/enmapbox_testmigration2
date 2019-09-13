# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest, os
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()
from enmapboxtestdata import enmap, hires, library
from enmapbox.gui.mapcanvas import *
SHOW_GUI = True and not os.environ.get('CI')

from enmapbox.gui.maplayers import *
from enmapbox.testing import TestObjects
from enmapbox.gui.spectralprofilesources import *
class SpectralProfileSourceTests(unittest.TestCase):

    def test_SpeclibList(self):

        model = SpectralProfileDstListModel()

        sl1 = SpectralLibrary()
        sl1.setName('Speclib 1')
        sl2 = SpectralLibrary()
        sl2.setName('Speclib 2')

        self.assertEqual(len(model), 0)
        model.addSpectralLibraryWidget(sl1)
        model.addSpectralLibraryWidget(sl2)

        self.assertEqual(len(model), 2)
        model.addSpectralLibraryWidget(sl2)
        self.assertEqual(len(model), 2)


        lv = QListView()
        lv.setModel(model)
        lv.show()

        if SHOW_GUI:
            QGIS_APP.exec_()


    def test_SpectralProfileSamplingMode(self):


        lyr = TestObjects.createRasterLayer(nb=5)
        self.assertIsInstance(lyr, QgsRasterLayer)

        pt = SpatialPoint.fromMapLayerCenter(lyr)

        for mode in SpectralProfileSamplingMode:
            self.assertIsInstance(mode, SpectralProfileSamplingMode)
            positions = mode.profilePositions(lyr, pt)

            self.assertIsInstance(positions, list)
            for p in positions:
                self.assertIsInstance(p, SpatialPoint)

            if mode == SpectralProfileSamplingMode.SingleProfile:
                self.assertEqual(len(positions), 1)
                self.assertEqual(positions[0], pt)

            if mode in [SpectralProfileSamplingMode.Sample3x3,
                        SpectralProfileSamplingMode.Sample3x3Mean]:
                self.assertEqual(len(positions), 9)
                self.assertEqual(positions[4], pt)

            if mode in [SpectralProfileSamplingMode.Sample5x5,
                        SpectralProfileSamplingMode.Sample5x5Mean5]:
                self.assertEqual(len(positions), 25)
                self.assertEqual(positions[12], pt)


    def test_loadProfiles(self):

        lyr = TestObjects.createRasterLayer(nb=5)
        self.assertIsInstance(lyr, QgsRasterLayer)

        pt = SpatialPoint.fromMapLayerCenter(lyr)

        samples = []

        for mode in SpectralProfileSamplingMode:
            samples.append(SpectralProfileSourceSample(lyr.source(), lyr.name(), lyr.providerType(), mode))

        qgsTask = QgsTaskMock()
        dump = pickle.dumps((pt, samples))
        dump2 = doLoadSpectralProfiles(qgsTask, pt)

        samples2 = pickle.loads(dump2)
        self.assertIsInstance(samples2, list)
        for s in samples2:
            self.assertIsInstance(s, SpectralProfileSourceSample)

            self.assertTrue(len(s.profiles()) > 0)
            for p in s.profiles():
                self.assertIsInstance(p, SpectralProfile)

            if s.samplingMode() in [SpectralProfileSamplingMode.SingleProfile,
                                    SpectralProfileSamplingMode.Sample3x3Mean,
                                    SpectralProfileSamplingMode.Sample5x5Mean]:
                self.assertTrue(len(s.profiles()) == 1)
                s.profiles()[0].plot()


            if s.samplingMode() == SpectralProfileSamplingMode.Sample3x3:
                self.assertTrue(len(s.profiles()) == 9)

            if s.samplingMode() == SpectralProfileSamplingMode.Sample5x5:
                self.assertTrue(len(s.profiles()) == 25)

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_EnMAPBox(self):
        from qgis.PyQt.QtWidgets import QAction
        action = QAction('test action')
        action.setShortcutVisibleInContextMenu(True)
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox()
        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        enmapBox.loadExampleData()
        enmapBox.setMapTool(MapTools.SpectralProfile)

        enmapBox.createDock('SPECLIB')
        c = enmapBox.mapCanvases()[0]
        enmapBox.loadCurrentMapSpectra(SpatialPoint.fromMapCanvasCenter(c), c)
        if SHOW_GUI:
            QGIS_APP.exec_()


    def test_SpectralProfileBridge(self):

        bridge = SpectralProfileBridge()

        slw1 = SpectralLibraryWidget()
        slw1.speclib().setName('Speclib 1')

        slw2 = SpectralLibraryWidget()
        slw2.speclib().setName('Speclib 2')

        bridge.addDestination(slw1)
        bridge.addDestination(slw2)


        tv = QTableView()

        fm = QSortFilterProxyModel()
        fm.setSourceModel(bridge)
        tv.setModel(fm)

        delegate = SpectralProfileBridgeViewDelegate(tv)
        delegate.setItemDelegates(tv)

        tv.show()
        lyr = TestObjects.createRasterLayer(nb=5)
        src = SpectralProfileSource.fromRasterLayer(lyr)

        rel = SpectralProfileRelation(src, slw1)
        bridge.addProfileRelation(rel)

        pt = SpatialPoint.fromMapLayerCenter(lyr)
        results = bridge.loadProfiles(pt, runAsync=True)

        for r in results:
            self.assertIsInstance(r, SpectralProfileRelation)

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_SpectralProfiledock(self):

        p = SpectralProfileSourcePanel()

        lyr1 = TestObjects.createRasterLayer(nb=5)
        lyr1.setName('source 1')
        lyr2 = TestObjects.createRasterLayer(nb=3)
        lyr2.setName('source 2')

        p.bridge().addRasterLayer(lyr1)
        p.bridge().addRasterLayer(lyr2)
        p.bridge().addRasterLayer(lyr2)
        p.show()

        if True:
            slw1 = SpectralLibraryWidget()
            slw1.speclib().setName('Speclib 1')

            slw2 = SpectralLibraryWidget()
            slw2.speclib().setName('Speclib 2')

            p.bridge().addDestination(slw1)
            p.bridge().addDestination(slw2)


        if SHOW_GUI:
            QGIS_APP.exec_()

if __name__ == "__main__":
    unittest.main()


