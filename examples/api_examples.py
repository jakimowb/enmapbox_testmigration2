#!python
# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/api.examples.py

    This file shows a couple of examples how to use the EnMAP-Box API
    These examples are used for the API Quick Start in doc/source/APIQuickStart.rst
    ---------------------
    Date                 : January 2018
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

# imports
import sys, os, unittest
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *

# create a QgsApplication instance which emulate the QGIS Desktop Application
from enmapbox.testing import initQgisApplication
qgsApp = initQgisApplication()


class Examples(unittest.TestCase):


    def test_Ex1_StartEnMAPBox(self):

        # start EnMAP-Box instance
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox(None)
        enmapBox.openExampleData(mapWindows=1)

        # access existing EnMAP-Box instance
        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()
        print(enmapBox)

        # load some test data
        enmapBox.openExampleData()

        # close the EnMAP-Box instance
        enmapBox = EnMAPBox.instance()
        enmapBox.close()

        qgsApp.exec_()


    def test_Ex2_DataSources(self):

        from enmapbox import EnMAPBox
        EMB = EnMAPBox(None)


        enmapBox = EnMAPBox.instance()

        # add some data sources
        from enmapboxtestdata import enmap as pathRasterSource
        from enmapboxtestdata import landcover_polygons as pathVectorSource
        from enmapboxtestdata import library as pathSpectralLibrary

        # add a single source
        enmapBox.addSource(pathRasterSource)

        # add a list of sources
        enmapBox.addSources([pathVectorSource, pathSpectralLibrary])

        # add some Web Services
        wmsUri = 'referer=OpenStreetMap%20contributors,%20under%20ODbL&type=xyz&url=http://tiles.wmflabs.org/hikebike/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=17&zmin=1'
        wfsUri = r'restrictToRequestBBOX=''1'' srsname=''EPSG:25833'' typename=''fis:re_postleit'' url=''http://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_postleit'' version=''auto'''
        enmapBox.addSource(wmsUri, name="Open Street Map")
        enmapBox.addSource(wfsUri, name='Berlin PLZ')

        # print all sources
        for source in enmapBox.dataSources():
            print(source)

        # print specific sources only:
        for source in enmapBox.dataSources('RASTER'):
            print(source)

        # remove all data sources
        allSources = enmapBox.dataSources()
        enmapBox.removeSources(allSources)

        qgsApp.exec_()

    def example4_createWindows(self):
        """
        Add new windows to view data
        """
        from enmapbox.gui.enmapboxgui import EnMAPBox
        enmapBox = EnMAPBox(None)

        enmapBox.createDock('MAP')  # a spatial map
        enmapBox.createDock('SPECLIB') # a spectral library
        enmapBox.createDock('TEXT') # a text editor
        enmapBox.createDock('WEBVIEW') # a browser
        enmapBox.createDock('MIME') # a window to drop mime data


        #1. create your own GUI that waits for user input.
        class Example5Dialog(QDialog):
            def __init__(self, parent=None):
                super(Example5Dialog, self).__init__(parent=parent)

                #self.setParent(enmapBox.ui)
                self.btn = QPushButton('Clear')
                self.label = QLabel('This Box will shows data sources newly added to the EnMAP-Box.')
                self.tb = QPlainTextEdit()
                self.tb.setLineWrapMode(QPlainTextEdit.NoWrap)
                self.tb.setPlainText('Click "Project" > "Add example data"\n or add any other data source to the EnMAP-Box')
                l = QVBoxLayout()
                self.setLayout(l)
                l.addWidget(self.label)
                l.addWidget(self.tb)
                l.addWidget(self.btn)


                self.btn.clicked.connect(self.tb.clear)


            def onSignal(self, src):
                sender = self.sender()

                import datetime
                t = datetime.datetime.now()
                text = self.tb.toPlainText()

                text = '{}\n{} : {}'.format(text, t.time(), src)
                self.tb.setPlainText(text)


    def example5_connectWithEnMAPBoxSignals(self):
        """
        This example demonstrates how the Qt Signal-Slot mechanism can be used to react on EnMAP-Box events.
        Read http://doc.qt.io/archives/qt-4.8/signalsandslots.html for details of signals & slots.
        """

        class ExampleDialog(QDialog):
            def __init__(self, parent=None):
                super(ExampleDialog, self).__init__(parent=parent)

                # self.setParent(enmapBox.ui)
                self.btn = QPushButton('Clear')
                self.label = QLabel('This Box will shows data sources newly added to the EnMAP-Box.')
                self.tb = QPlainTextEdit()
                self.tb.setLineWrapMode(QPlainTextEdit.NoWrap)
                self.tb.setPlainText('Click "Project" > "Add example data"\n or add any other data source to the EnMAP-Box')
                l = QVBoxLayout()
                self.setLayout(l)
                l.addWidget(self.label)
                l.addWidget(self.tb)
                l.addWidget(self.btn)

                self.btn.clicked.connect(self.tb.clear)

            def onSignal(self, src):
                import datetime
                t = datetime.datetime.now()
                text = self.tb.toPlainText()
                text = '{}\n{} : {}'.format(text, t.time(), src)
                self.tb.setPlainText(text)

        from enmapbox import EnMAPBox
        enmapBox = EnMAPBox.instance()

        d = ExampleDialog(parent=enmapBox.ui)
        d.setFixedSize(QSize(600, 300))

        #connect different signals to a slot
        enmapBox.sigDataSourceAdded.connect(d.onSignal)
        enmapBox.sigCurrentLocationChanged.connect(d.onSignal)

        d.show()


if __name__ == "__main__":
    unittest.main()


