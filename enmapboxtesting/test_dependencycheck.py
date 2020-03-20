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

from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *

class test_dependencycheck(EnMAPBoxTestCase):

    def test_gdalissues(self):

        l = checkGDALIssues()
        self.assertIsInstance(l, list)
        for i in l:
            self.assertIsInstance(i, str)

    def test_lookup(self):
        # some python packages have a different name when to be installed with pip
        # addresses https://bitbucket.org/hu-geomatics/enmap-box/issues/307/installation-problem-sklearn

        import enmapbox.dependencycheck
        enmapbox.dependencycheck.PACKAGE_LOOKUP['foobar'] = 'foo-bar'

        info = missingPackageInfo([PIPPackage('foobar')])
        self.assertTrue('foobar' in info)
        self.assertTrue('foo-bar' in info)


    def test_pippackage(self):

        pkg = PIPPackage('gdal')
        self.assertTrue(pkg.isInstalled())
        self.assertIsInstance(pkg.installCommand(), str)
        pkg.installPackage()

        pkg = PIPPackage('foobar')
        self.assertFalse(pkg.isInstalled())
        self.assertIsInstance(pkg.installCommand(), str)
        pkg.installPackage()

    def test_pippackagemodel(self):

        model = PIPPackageInstallerTableModel()
        self.assertTrue(len(model) == 0)

        model.addPackages([PIPPackage('foobar'),
                           PIPPackage('gdal')]
                          )

        self.assertEqual(len(model), 2)
        self.assertEqual(model.rowCount(), 2)

        model.installAll()

        tv = QTableView()
        tv.setModel(model)

        self.showGui(tv)

    def test_PIPInstaller(self):

        pkgs = requiredPackages()
        pkgs.append(PIPPackage('foobar'))
        w = PIPPackageInstaller()
        w.addPackages(pkgs)
       #w.model.installAll()

        self.showGui(w)


if __name__ == "__main__":

    unittest.main()



