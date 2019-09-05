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

        model = SpectralLibraryListModel()

        sl1 = SpectralLibrary()
        sl1.setName('Speclib 1')
        sl2 = SpectralLibrary()
        sl2.setName('Speclib 2')

        self.assertEqual(len(model), 0)
        model.addSpeclib(sl1)
        model.addSpeclib(sl2)

        self.assertEqual(len(model), 2)
        model.addSpeclib(sl2)
        self.assertEqual(len(model), 2)


        lv = QListView()
        lv.setModel(model)
        lv.show()

        if SHOW_GUI:
            QGIS_APP.exec_()

    def test_SpectralProfileBridge(self):

        bridge = SpectralProfileBridge()

        sl1 = SpectralLibrary(name='Speclib 1')
        sl2 = SpectralLibrary(name='Speclib 2')
        bridge.addSpeclib(sl1)
        bridge.addSpeclib(sl2)


        tv = QTableView()

        fm = QSortFilterProxyModel()
        fm.setSourceModel(bridge)
        tv.setModel(fm)

        delegate = SpectralProfileBridgeViewDelegate(tv)
        delegate.setItemDelegates(tv)

        tv.show()

        if SHOW_GUI:
            QGIS_APP.exec_()


if __name__ == "__main__":
    unittest.main()



