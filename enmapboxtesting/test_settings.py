# -*- coding: utf-8 -*-
"""
***************************************************************************
    test_settings
    ---------------------
    Date                 : February 2020
    Copyright            : (C) 2020 by Benjamin Jakimow
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
from unittest import TestCase
from qgis import *
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from enmapbox.testing import EnMAPBoxTestCase
from enmapbox.gui.utils import *
from enmapbox.gui.widgets.models import *
from enmapboxtestdata import *
from enmapbox import EnMAPBox
from enmapbox.gui.settings import *


class TestEnMAPBoxPlugin(EnMAPBoxTestCase):

    def test_loadSettings(self):
        pass
        self.showGui()

    def test_enmapbox_settings(self):


        box = EnMAPBox()
        box.loadExampleData()
        dataSources = box.dataSources()
        n_maps = len(box.mapCanvases())


        proj = QgsProject.instance()
        self.assertIsInstance(proj, QgsProject)
        tmp_path = pathlib.Path(__file__).parents[1] / 'tmp' / 'project.qgs'
        os.makedirs(tmp_path.parent, exist_ok=True)

        box.saveProject(tmp_path)

        box.close()
        self.assertTrue(EnMAPBox.instance() is None)

        box = EnMAPBox()
        self.assertIsInstance(box, EnMAPBox)
        box.addProject(tmp_path.as_posix())

        self.assertEqual(dataSources, box.dataSources())
        self.assertEqual(n_maps, len(box.mapCanvases()))


    def test_SettingsDialog(self):

        d = SettingsDialog()
        self.assertIsInstance(d, SettingsDialog)
        self.showGui(d)

if __name__ == '__main__':

    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
