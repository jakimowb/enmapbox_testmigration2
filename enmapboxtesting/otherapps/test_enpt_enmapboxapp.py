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
from enmapbox import EnMAPBox
from enmapbox.gui.applications import *
from enmapbox.testing import EnMAPBoxTestCase
from enmapbox import DIR_ENMAPBOX
path = os.path.join(DIR_ENMAPBOX, 'apps')
if path not in sys.path:
    sys.path.append(path)

class test_applications(EnMAPBoxTestCase):


    def test_application(self):
        EB = EnMAPBox()

        from enpt_enmapboxapp.enpt_enmapboxapp import EnPTEnMAPBoxApp
        app = [a for a in EB.applicationRegistry.applications() if isinstance(a, EnPTEnMAPBoxApp)]
        self.assertTrue(len(app) == 1, msg='EnPTEnMAPBoxApp was not loaded during EnMAP-Box startup')

        app = app[0]
        self.assertIsInstance(app, EnPTEnMAPBoxApp)
        #app.startGUI()
        self.showGui(EB.ui)


if __name__ == "__main__":

    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)



