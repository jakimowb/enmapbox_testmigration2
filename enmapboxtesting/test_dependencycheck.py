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
import uuid
from collections import namedtuple
from enmapbox.testing import EnMAPBoxTestCase, TestObjects
from enmapbox.dependencycheck import *

from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *

class test_dependencycheck(EnMAPBoxTestCase):

    def setUp(self):
        super().setUp()
        if str(os.environ.get('CI')).lower() in ['1', 'true', 'yes']:
            QTimer.singleShot(2000, QApplication.instance().closeAllWindows)

    def test_gdalissues(self):

        l = checkGDALIssues()
        self.assertIsInstance(l, list)
        for i in l:
            self.assertIsInstance(i, str)

    def test_lookup(self):
        # some python packages have a different name when to be installed with pip
        # addresses https://bitbucket.org/hu-geomatics/enmap-box/issues/307/installation-problem-sklearn

        import enmapbox.dependencycheck
        pipName = self.nonexistingPackageName()
        pyName = pipName.replace('-', '_')
        enmapbox.dependencycheck.PACKAGE_LOOKUP[pyName] = pipName

        info = missingPackageInfo([PIPPackage(pyName)])
        self.assertTrue(pyName in info)
        self.assertTrue(pipName in info)
        del enmapbox.dependencycheck.PACKAGE_LOOKUP[pyName]

    def test_pippackage(self):

        pkg = PIPPackage('gdal', pipCmd='GDAL>=3.0')

        self.assertTrue(pkg.isInstalled())
        self.assertIsInstance(pkg.installCommand(), str)
        pkg.installPackage()

        pkg = PIPPackage(self.nonexistingPackageName())
        self.assertFalse(pkg.isInstalled())
        self.assertIsInstance(pkg.installCommand(), str)
        pkg.installPackage()

        n = self.nonexistingPackageName()

        INSTALLATION_BLOCK[n] = 'reason'
        pkg = PIPPackage(n)

        pkg.installPackage()
        self.assertTrue(pkg.stdoutMsg == '')
        self.assertTrue('reason' in pkg.stderrMsg)

    def test_pippackagemodel(self):

        model = PIPPackageInstallerTableModel()
        self.assertTrue(len(model) == 0)

        model.addPackages([PIPPackage(self.nonexistingPackageName()),
                           PIPPackage('gdal')]
                          )

        self.assertEqual(len(model), 2)
        self.assertEqual(model.rowCount(), 2)

        tv = QTableView()
        tv.setModel(model)

        self.showGui(tv)

    def nonexistingPackageName(self) -> str:
        s = str(uuid.uuid4())
        return 'foobar'+s

    def test_PIPInstaller(self):
        pkgs = [PIPPackage(self.nonexistingPackageName()),
                PIPPackage(self.nonexistingPackageName()),
                PIPPackage(self.nonexistingPackageName())]
        pkgs += requiredPackages()
        w = PIPPackageInstaller()
        w.addPackages(pkgs)
        #w.installAll()
       #w.model.installAll()

        self.showGui(w)

    def test_PIPPackageInfoTask(self):

        required = [PIPPackage(self.nonexistingPackageName())] + requiredPackages()
        AVAILABLE = dict()
        INSTALLED = dict()

        def onAvailableVersion(pkg: str, version: str):
            print('Available {}={}'.format(pkg, version))
            AVAILABLE[pkg] = version

        def onInstalledVersion(pkg: str, version: str):
            print('Installed {}={}'.format(pkg, version))
            INSTALLED[pkg] = version

        def onProgress(p: int):
            print('Progress {}'.format(p))

        def onMessage(msg:str, is_error:bool):
            print(msg)



        task = PIPPackageInfoTask('package info', [p.pipPkgName for p in required])
        task.progressChanged.connect(onProgress)
        task.sigAvailableVersion.connect(onAvailableVersion)
        task.sigInstalledVersion.connect(onInstalledVersion)
        task.sigMessage.connect(onMessage)
        task.run()
        QApplication.processEvents()


    def test_findpython(self):

        p = localPythonExecutable()
        self.assertIsInstance(p, pathlib.Path)
        self.assertTrue(p.is_file())

        import subprocess
        cmd = str(p) + ' --version'

        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
        self.assertTrue(process.stdout.startswith('Python 3.'))


if __name__ == "__main__":

    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)



