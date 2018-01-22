#!python
# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/api.examples.py

    This file shows a couple of examples how to use the EnMAP-Box API
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


import sys, os
from qgis.core import *


def example1_startEnMAPBoxWithoutQGIS():
    from enmapbox.gui.enmapboxgui import EnMAPBox
    from enmapbox.gui.utils import initQgisApplication

    qgsApp = initQgisApplication()
    enmapBox = EnMAPBox(None)
    enmapBox.openExampleData(mapWindows=1)

    qgsApp.exec_()
    qgsApp.quit()

def example2_connectToRunningEnMAPBox():

    from enmapbox.gui.enmapboxgui import EnMAPBox
    enmapBox = EnMAPBox.instance()
    print(enmapBox)


def example3_DataSourceHandling():

    from enmapbox.gui.enmapboxgui import EnMAPBox
    enmapBox = EnMAPBox.instance()

    #add some data sources
    from enmapboxtestdata import enmap as pathEnMAPImage
    from enmapboxtestdata import landcover as pathVectorFile
    from enmapboxtestdata import speclib as pathSpectralLibrary

    #add a single source
    enmapBox.addSource(pathEnMAPImage)

    #add a list of sources
    enmapBox.addSources([pathVectorFile, pathSpectralLibrary])

    # print all sources
    for source in enmapBox.dataSources():
        print(source)

    # print specific sources only:
    for source in enmapBox.dataSources('RASTER'):
        print(source)

    # remove all data sources
    allSources = enmapBox.dataSources()
    enmapBox.removeSources(allSources)



def example4_createWindows():
    """
    Add new windows to view data
    """
    from enmapbox.gui.enmapboxgui import EnMAPBox
    enmapBox = EnMAPBox.instance()
    enmapBox.createDock('MAP')  # a spatial map
    enmapBox.createDock('SPECLIB') # a spectral library
    enmapBox.createDock('TEXT') # a text editor
    enmapBox.createDock('WEBVIEW') # a browser
    enmapBox.createDock('MIME') # a window to drop mime data


#1. create your own GUI that waits for user input.
from PyQt4.Qt import *
from PyQt4.QtGui import *

class Example5Dialog(QDialog):

    def __init__(self, parent=None):
        super(Example5Dialog, self).__init__(parent=parent)
        enmapBox = EnMAPBox.instance()
        self.enmapBox = enmapBox
        #self.setParent(enmapBox.ui)
        self.btn = QPushButton('Clear')
        self.tb = QPlainTextEdit()
        self.tb.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.label = QLabel('This box shows new added data sources')
        l = QVBoxLayout()
        self.setLayout(l)
        l.addWidget(self.label)
        l.addWidget(self.tb)
        l.addWidget(self.btn)


        self.btn.clicked.connect(self.tb.clear)



        enmapBox.sigDataSourceAdded.connect(self.onSignal)
        enmapBox.sigCurrentLocationChanged.connect(self.onSignal)


    def onSignal(self, src):
        sender = self.sender()

        import datetime
        t = datetime.datetime.now()
        text = self.tb.toPlainText()

        text = '{}\n{} : {}'.format(text, t.time(), src)
        self.tb.setPlainText(text)


def example5_connectWithEnMAPBoxSignals():
    enmapBox = EnMAPBox.instance()

    w = Example5Dialog(parent = enmapBox.ui)
    w.setFixedSize(QSize(600,300))
    w.show()






if __name__ == '__main__':

    #un-comment the example you like to run

    if False:
        example1_startEnMAPBoxWithoutQGIS()
    else:

        # the following 4 lines and the last 2 are not required if the EnMAP-Box was already started,
        # e.g. inside QGIS
        from enmapbox.gui.utils import initQgisApplication
        from enmapbox.gui.enmapboxgui import EnMAPBox
        qgsApp = initQgisApplication()



        enmapBox = EnMAPBox(None)

        example5_connectWithEnMAPBoxSignals()


        #example2_connectToRunningEnMAPBox()
        #example3_DataSourceHandling()
        #example4_createWindows()


        # not required if the GUI Thread is performed by QGIS
        qgsApp.exec_()

