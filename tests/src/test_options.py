# -*- coding: utf-8 -*-
"""
***************************************************************************
    test_enMAPBox
    ---------------------
    Date                 : April 2018
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
# noinspection PyPep8Naming


import unittest
import xmlrunner
from unittest import TestCase
from qgis import *
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from enmapbox.testing import EnMAPBoxTestCase
from enmapbox.gui.utils import *
from enmapbox.gui.widgets.models import *
from enmapbox.exampledata import *


class TestEnMAPBoxPlugin(EnMAPBoxTestCase):

    def test_optionmodel(self):
        m = OptionListModel()

        cb = QComboBox()
        cb.setModel(m)
        cb.show()

        sources = [enmap, hires]
        options = [Option(source, os.path.basename(source)) for source in sources]
        m.addOptions(options)

        # m.removeOptions(options)
        self.showGui(cb)


if __name__ == '__main__':

    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
