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

import unittest, shutil
from collections import namedtuple
from enmapbox.testing import EnMAPBoxTestCase, TestObjects

from enmapbox.gui.utils import *
from enmapbox import EnMAPBox, DIR_ENMAPBOX, DIR_REPO
import enmapbox.gui
from enmapbox.gui.applications import *


from enmapbox import DIR_ENMAPBOX

path = os.path.join(DIR_ENMAPBOX, 'apps')
if path not in sys.path:
    sys.path.append(path)

class test_applications(EnMAPBoxTestCase):

    def test_application(self):
        EB = EnMAPBox()
        EB.ui.hide()

        from lmuvegetationapps.enmapboxintegration import LMU_EnMAPBoxApp

        app = LMU_EnMAPBoxApp(EB)
        app.start_GUI_IVVRM()

        self.showGui()

if __name__ == "__main__":

    unittest.main()



