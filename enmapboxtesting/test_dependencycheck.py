# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import enmapbox, os

__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest, shutil
from collections import namedtuple
from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from enmapbox.dependencycheck import *


class test_dependencycheck(EnMAPBoxTestCase):


    def test_missingPackages(self):

        missing = missingPackages(['sys', 'noneExistingFakePkg'])
        self.assertIsInstance(missing, list)
        self.assertListEqual(missing, ['noneExistingFakePkg'])

    def test_missingPackageInfo(self):
        info1 = missingPackageInfo(['noneExistingFake', 'gdal'])
        self.assertIsInstance(info1, str)
        print(info1)

        info2 = missingPackageInfo([])
        self.assertTrue(info2 == None)

        v = QgsMessageLogViewer()
        v.show()
        v.logMessage(info1, 'TEST', Qgis.Warning)

        self.showGui(v)


if __name__ == "__main__":

    unittest.main()



