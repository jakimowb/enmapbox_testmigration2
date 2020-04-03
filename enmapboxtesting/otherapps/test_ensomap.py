# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import enmapbox

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from enmapbox import EnMAPBox
from enmapbox.gui.applications import *
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox import DIR_ENMAPBOX
path = os.path.join(DIR_ENMAPBOX, 'apps')
if path not in sys.path:
    sys.path.append(path)

class test_ensomap(EnMAPBoxTestCase):


    def test_imports(self):
        import ensomap
        self.assertTrue(os.path.isfile(ensomap.__file__))
        from ensomap.enmapboxintegration import EnSoMAP
        import hys

        self.assertTrue(os.path.isfile(hys.__file__))

    def test_ENSOMAP_UI(self):
        homedir = os.path.expanduser('~')
        from ensomap.enmapboxintegration import ENSOMAP_UI
        w = ENSOMAP_UI(homedir)
        self.assertIsInstance(w, QWidget)

    def test_EnSOMAP_App(self):

        emb = EnMAPBox(load_core_apps=False, load_other_apps=False)

        from ensomap import enmapboxApplicationFactory

        app = enmapboxApplicationFactory(emb)

        self.assertTrue(isinstance(app, list) or isinstance(app, EnMAPBoxApplication))

    def test_EnMAPBox(self):
        
        emb = EnMAPBox()

        self.assertIsInstance(emb, EnMAPBox)
if __name__ == "__main__":

    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)



