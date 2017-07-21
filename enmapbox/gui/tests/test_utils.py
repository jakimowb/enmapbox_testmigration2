# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enmapbox.gui.sandbox import initQgisEnvironment
QGIS_APP = initQgisEnvironment()


class testclassData(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        self.w = QMainWindow()
        self.cw = QWidget()
        self.cw.setLayout(QVBoxLayout())
        self.w.setCentralWidget(self.cw)
        self.w.show()
        self.menuBar = self.w.menuBar()
        self.menuA = self.menuBar.addMenu('Menu A')

    def tearDown(self):
        self.w.close()

    def test_appendItemsToMenu(self):
        from enmapbox.gui.utils import appendItemsToMenu

        B = QMenu()
        action = B.addAction('Do something')

        appendItemsToMenu(self.menuA, B)

        self.assertTrue(action in self.menuA.children())

    def test_MimeDataHelper(self):
        class TestClassA(object):

            s = "TEST A"

        class TestClassB(QObject):

            def __init__(self):
                super(TestClassB, self).__init__()
                self.s = 'TEST B A QOBJECT'

        from enmapbox.gui.utils import MimeDataHelper

        oA = TestClassA()
        oB = TestClassB()

        url = 'https://bitbucket.org/hu-geomatics/enmap-box'
        text = 'Lore Ipsum'
        md = QMimeData()
        md.setUrl(url)
        md.setText(text)

        MimeDataHelper.storeObjectReferences(md, [oA, oB])
        mdh = MimeDataHelper(md)
        self.assertTrue(mdh.hasPythonObjects())

        objectList = mdh.pythonObjects()
        self.assertTrue(len(objectList) == 2)
        self.assertIs(objectList[0], oA)
        self.assertIs(objectList[1], oB)


        self.assertTrue(mdh.hasUrls())
        urls = mdh.urls()
        self.assertTrue(len(urls) == 1)
        self.assertTrue(urls[0] == url)

        #todo: check tree mode nodes etc.

if __name__ == "__main__":

    unittest.main()



