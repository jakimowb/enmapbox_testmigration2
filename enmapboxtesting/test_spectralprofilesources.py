# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'

import unittest, os, random
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.testing import EnMAPBoxTestCase, TestObjects

from enmapboxtestdata import enmap, hires, library
from enmapbox.gui.mapcanvas import *


from enmapbox.testing import TestObjects
from enmapbox.gui.spectralprofilesources import *
from enmapbox import EnMAPBox
class SpectralProfileSourceTests(EnMAPBoxTestCase):


    def test_SpeclibList(self):

        model = SpectralProfileDstListModel()

        slw1 = SpectralLibraryWidget()
        slw1.speclib().setName('Speclib 1')

        slw2 = SpectralLibraryWidget()
        slw2.speclib().setName('Speclib 2')

        self.assertEqual(len(model), 0)
        model.addSpectralLibraryWidget(slw1)
        model.addSpectralLibraryWidget(slw2)

        self.assertEqual(len(model), 2)
        model.addSpectralLibraryWidget(slw2)
        self.assertEqual(len(model), 2)


        lv = QListView()
        lv.setModel(model)
        lv.show()

        self.showGui(lv)


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
                        SpectralProfileSamplingMode.Sample5x5Mean]:
                self.assertEqual(len(positions), 25)
                self.assertEqual(positions[12], pt)


    def test_loadProfiles(self):

        lyr = TestObjects.createRasterLayer(nb=5)
        self.assertIsInstance(lyr, QgsRasterLayer)

        pt = SpatialPoint.fromMapLayerCenter(lyr)
        src = SpectralProfileSource.fromRasterLayer(lyr)
        relations = []

        for mode in SpectralProfileSamplingMode:
            r = SpectralProfileRelation(src, None)
            r.setSamplingMode(mode)
            rw = SpectralProfileRelationWrapper(r)

            relations.append(rw)


        qgsTask = QgsTaskMock()

        task, point, relations = doLoadSpectralProfiles(qgsTask, pt, relations)

        self.assertIsInstance(relations, list)
        for rw in relations:
            self.assertIsInstance(rw, SpectralProfileRelationWrapper)

            self.assertTrue(len(rw.currentProfiles()) > 0)
            for p in rw.currentProfiles():
                self.assertIsInstance(p, SpectralProfile)

            if rw.samplingMode() in [SpectralProfileSamplingMode.SingleProfile,
                                    SpectralProfileSamplingMode.Sample3x3Mean,
                                    SpectralProfileSamplingMode.Sample5x5Mean]:
                self.assertTrue(len(rw.currentProfiles()) == 1)
                #rw.currentProfiles()[0].plot()


            if rw.samplingMode() == SpectralProfileSamplingMode.Sample3x3:
                self.assertTrue(len(rw.currentProfiles()) == 9)

            if rw.samplingMode() == SpectralProfileSamplingMode.Sample5x5:
                self.assertTrue(len(rw.currentProfiles()) == 25)



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

        self.showGui(enmapBox.ui)


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


    def test_SpectralProfiledock(self):

        p = SpectralProfileSourcePanel()

        def addSrc(*args):
            lyr = TestObjects.createRasterLayer()
            p.bridge().addRasterLayer(lyr)

        def delSrc(*args):
            model = p.bridge().dataSourceModel()
            if len(model) > 0:
                model.removeSource(model[-1])

        def addSpeclib(*args):
            model = p.bridge().spectralLibraryModel()
            slw = SpectralLibraryWidget()
            slw.speclib().setName('Speclib {} {}'.format(len(model) + 1, id(slw)))
            slw.show()
            p.bridge().addDestination(slw)

        def delSpeclib(*args):
            model = p.bridge().spectralLibraryModel()
            if len(model) > 0:
                model.removeSpeclib(model[-1])

        w = QWidget()
        btnAddSrc = QPushButton('Add source', parent=w)
        btnAddSrc.clicked.connect(addSrc)
        btnDelSrc = QPushButton('Remove source', parent=w)
        btnDelSrc.clicked.connect(delSrc)
        btnAddDst = QPushButton('Add speclib', parent=w)
        btnAddDst.clicked.connect(addSpeclib)
        btnDelDst = QPushButton('Remove speclib', parent=w)
        btnDelDst.clicked.connect(delSpeclib)

        w.setLayout(QVBoxLayout())

        l = QHBoxLayout()
        for btn in [btnAddSrc, btnAddDst, btnDelSrc, btnDelDst]:
            l.addWidget(btn)
        w.layout().addLayout(l)
        w.layout().addWidget(p)
        w.show()

        p.bridge().dataSourceModel().addSource(SpectralProfileTopLayerSource())
        self.assertEqual(len(p.bridge().dataSourceModel()), 1)
        self.assertEqual(len(p.bridge().spectralLibraryModel()), 0)

        btnAddSrc.clicked.emit()
        btnAddDst.clicked.emit()

        self.assertEqual(len(p.bridge().dataSourceModel()), 2)
        self.assertEqual(len(p.bridge().spectralLibraryModel()), 1)

        btnAddSrc.clicked.emit()
        self.assertEqual(len(p.bridge().dataSourceModel()), 3)
        btnDelSrc.clicked.emit()
        self.assertEqual(len(p.bridge().dataSourceModel()), 2)


        btnAddDst.clicked.emit()
        btnAddSrc.clicked.emit()
        QApplication.processEvents()

        self.showGui(w)

    def test_currentprofiles(self):
        from enmapbox.gui import MapTools
        eb = EnMAPBox()
        eb.loadExampleData()
        eb.setMapTool(MapTools.SpectralProfile)

        c = eb.mapCanvases()[0]
        self.assertIsInstance(c, QgsMapCanvas)
        eb.spectralProfileBridge().setRunAsync(False)
        def randomRasterPosition():
            layer : QgsRasterLayer = random.choice([l for l in c.layers() if isinstance(l, QgsRasterLayer)])
            ext = layer.extent()
            dx = random.uniform(-10, 10) * layer.rasterUnitsPerPixelX()
            dy = random.uniform(-10, 10) * layer.rasterUnitsPerPixelY()
            point = SpatialPoint.fromMapLayerCenter(layer)
            point = SpatialPoint(point.crs(), point.x() + dx, point.y() + dy)
            eb.setCurrentLocation(point, mapCanvas=c)


        self.assertTrue(len(eb.currentSpectra()) == 0)
        randomRasterPosition()
        self.assertTrue(len(eb.currentSpectra()) > 0)

        randomRasterPosition()

        randomRasterPosition()

if __name__ == "__main__":
    unittest.main()



