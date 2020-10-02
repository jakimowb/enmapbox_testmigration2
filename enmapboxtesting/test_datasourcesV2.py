import unittest
import os
import re
import typing
import xmlrunner
from osgeo import gdal, ogr, osr
from qgis.core import *
from qgis.core import QgsApplication, QgsDataItemProvider, QgsDataCollectionItem, QgsDataItem, \
    QgsRasterLayer, QgsVectorLayer, QgsProject

from qgis.gui import *
from qgis.gui import QgsBrowserGuiModel, QgsBrowserTreeView, QgsBrowserDockWidget
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from enmapbox.gui import SpectralLibrary
from enmapbox.gui.datasourcesV2 import *

class MyTestCase(EnMAPBoxTestCase):

    def printSources(self, sources):
        srcR = [s for s in sources if isinstance(s, QgsRasterLayer)]
        srcV = [s for s in sources if isinstance(s, QgsVectorLayer) and not isinstance(s, SpectralLibrary)]
        srcS = [s for s in sources if isinstance(s, SpectralLibrary)]
        print(f'{len(sources)} sources')
        print(f'{len(srcR)} rasters')
        print(f'{len(srcV)} vectors')
        print(f'{len(srcS)} speclibs')

    def test_Registry(self):
        reg = QgsApplication.dataItemProviderRegistry()

        dataProvider = EnMAPBoxDataItemProvider()
        reg.addProvider(dataProvider)
        #self.assertIsNotNone(reg.provider('PostGIS'))

        m = QgsBrowserGuiModel()
        #m = QgsBrowserModel()
        m.initialize()
        providerNames = []
        for p in QgsApplication.dataItemProviderRegistry().providers():
            self.assertIsInstance(p, QgsDataItemProvider)
            providerNames.append(p.name())
        self.assertIn('EnMAP-Box', providerNames)
        tv = QgsBrowserTreeView()

        #tv.setBrowserModel(m)
        tv.setModel(m)

        sources = []
        def addSource(cls):
            if cls == QgsRasterLayer:
                lyr: QgsRasterLayer = TestObjects.createRasterLayer()
            elif cls == QgsVectorLayer:
                lyr: QgsVectorLayer = TestObjects.createVectorLayer()
            elif cls == SpectralLibrary:
                lyr: SpectralLibrary = TestObjects.createSpectralLibrary()
            else:
                raise NotImplementedError()
            lyr.setName(lyr.id())
            assert lyr.isValid()
            QgsProject.instance().addMapLayer(lyr)
            sources.append(lyr)
            self.printSources(sources)

        def removeSource(cls):
            lyrs = QgsProject.instance().mapLayers().values()
            if cls == QgsRasterLayer:
                lyrs = [l for l in lyrs if isinstance(l, QgsRasterLayer)]
            elif cls == QgsVectorLayer:
                lyrs = [l for l in lyrs if isinstance(l, QgsVectorLayer)]
            elif cls == SpectralLibrary:
                lyrs = [l for l in lyrs if isinstance(l, SpectralLibrary)]
            else:
                raise NotImplementedError()
            if len(lyrs) > 0:
                lyr = lyrs[-1]
                sources.remove(lyr)
                QgsProject.instance().removeMapLayer(lyr)
            self.printSources(sources)

        btnAddVector = QPushButton('Add Vector')
        btnAddVector.clicked.connect(lambda: addSource(QgsVectorLayer))
        btnAddRaster = QPushButton('Add Raster')
        btnAddRaster.clicked.connect(lambda: addSource(QgsRasterLayer))
        btnAddSpeclib = QPushButton('Add Speclib')
        btnAddSpeclib.clicked.connect(lambda: addSource(SpectralLibrary))

        btnDelVector = QPushButton('Remove Vector')
        btnDelVector.clicked.connect(lambda: removeSource(QgsVectorLayer))
        btnDelRaster = QPushButton('Remove Raster')
        btnDelRaster.clicked.connect(lambda: removeSource(QgsRasterLayer))
        btnDelSpeclib = QPushButton('Remove Speclib')
        btnDelSpeclib.clicked.connect(lambda: removeSource(SpectralLibrary))

        grid = QGridLayout()
        grid.addWidget(btnAddVector, 0, 0)
        grid.addWidget(btnAddRaster, 1, 0)
        grid.addWidget(btnAddSpeclib, 2, 0)
        grid.addWidget(btnDelVector, 0, 1)
        grid.addWidget(btnDelRaster, 1, 1)
        grid.addWidget(btnDelSpeclib, 2, 1)
        grid.addWidget(tv, 0, 2, 3, 3)

        w = QWidget()
        w.setWindowTitle('Browser Test')
        w.setLayout(grid)
        w.resize(QSize(400, 400))
        btnAddRaster.clicked.emit()
        w.show()

        btnAddRaster.click()

        self.showGui(tv)
        #QApplication.exec_()

    def test_widget(self):


        m = QgsBrowserGuiModel()
        w = QgsBrowserDockWidget('EXAMPLE', m)

        self.showGui(w)

    def test_printDataItemProviders(self):

        for p in QgsApplication.dataItemProviderRegistry().providers():
            self.assertIsInstance(p, QgsDataItemProvider)
            print(p.name())

    def test_RasterCollectionItem(self):

        item = EnMAPBoxRasterCollectionItem()
        self.assertIsInstance(item, QgsDataCollectionItem)


if __name__ == '__main__':
    unittest.main()
