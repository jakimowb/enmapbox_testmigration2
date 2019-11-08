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

import unittest, shutil, tempfile
from collections import namedtuple
from enmapbox.testing import initQgisApplication, TestObjects

QGIS_APP = initQgisApplication()
SHOW_GUI = False and os.environ.get('CI') is None
from enmapbox.gui.utils import *
from enmapbox import EnMAPBox, DIR_ENMAPBOX, DIR_REPO
import enmapbox.gui
from enmapbox.gui.applications import *

enmapbox.initAll()

DIR_TMP = os.path.join(DIR_REPO, *['tmp', 'tmp_enmapboxApplicationTests'])


class test_applications(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        eb = EnMAPBox.instance()
        if isinstance(eb, EnMAPBox):
            eb.close()
        QApplication.processEvents()

    def tearDown(self):
        eb = EnMAPBox.instance()
        if isinstance(eb, EnMAPBox):
            eb.close()
            QApplication.processEvents()
            EnMAPBox._instance = None



    def createTestData(self)->(str, str, str):
        """
        :return: (path folder, filelist_abs, filelist_rel)
        """

        TESTDATA = namedtuple('TestData', ['validAppDirs','invalidAppDirs','appDirs', 'pathListingAbs','pathListingRel'])


        if os.path.isdir(DIR_TMP):
            shutil.rmtree(DIR_TMP)
        os.makedirs(DIR_TMP, exist_ok=True)

        TESTDATA.invalidAppDirs = []
        TESTDATA.validAppDirs = []

        #1. valid app 1
        pAppDir = os.path.join(DIR_REPO, *['examples','minimumexample'])

        TESTDATA.validAppDirs.append(pAppDir)


        #2. no app 1: empty directory
        pAppDir = os.path.join(DIR_TMP, 'NoApp1')
        os.makedirs(pAppDir)
        TESTDATA.invalidAppDirs.append(pAppDir)

        #3. no app 2: __init__ without factory

        pAppDir = os.path.join(DIR_TMP, 'NoApp2')
        os.makedirs(pAppDir)
        pAppInit = os.path.join(pAppDir, '__init__.py')
        f = open(pAppInit, 'w')
        f.write('import sys')
        f.flush()
        f.close()
        TESTDATA.invalidAppDirs.append(pAppDir)

        TESTDATA.pathListingAbs = os.path.join(DIR_TMP, 'application_abs.txt')
        f = open(TESTDATA.pathListingAbs, 'w')
        for p in TESTDATA.invalidAppDirs + TESTDATA.validAppDirs:
            f.write(p+'\n')
        f.flush()
        f.close()

        TESTDATA.pathListingRel = os.path.join(DIR_TMP, 'application_rel.txt')
        f = open(TESTDATA.pathListingRel, 'w')
        for p in TESTDATA.invalidAppDirs + TESTDATA.validAppDirs:
            f.write(os.path.relpath(p, DIR_TMP)+'\n')
        f.flush()
        f.close()




        return TESTDATA


    def test_application(self):
        EB = EnMAPBox()
        emptyApp = EnMAPBoxApplication(EB)

        isOk, errors = EnMAPBoxApplication.checkRequirements(emptyApp)
        self.assertFalse(isOk)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) > 0)
        self.assertIsInstance(emptyApp.processingAlgorithms(), list)
        self.assertEqual(len(emptyApp.processingAlgorithms()), 0)
        self.assertEqual(emptyApp.menu(QMenu), None)
        
        testApp = TestObjects.enmapboxApplication()

        isOk, errors = EnMAPBoxApplication.checkRequirements(testApp)
        self.assertTrue(isOk)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) == 0)
        self.assertIsInstance(testApp.processingAlgorithms(), list)
        self.assertTrue(len(testApp.processingAlgorithms()) > 0)
        self.assertIsInstance(testApp.menu(QMenu()), QMenu)


    def test_applicationRegistry(self):
        TESTDATA = self.createTestData()

        EB = EnMAPBox()

        reg = ApplicationRegistry(EB)
        testApp = TestObjects.enmapboxApplication()
        self.assertIsInstance(reg.applications(), list)
        self.assertTrue(len(reg.applications()) == 0)
        
        app = TestObjects.enmapboxApplication()
        self.assertIsInstance(app, EnMAPBoxApplication)
        reg.addApplication(app)
        self.assertTrue(len(reg.applications()) == 1)
        self.assertTrue(len(reg.applications()) == len(reg))

        reg.removeApplication(app)
        self.assertTrue(len(reg.applications()) == 0)

        app2 = TestObjects.enmapboxApplication()
        reg.addApplication(app2)
        self.assertTrue(len(reg.applications()) == 1, msg='Applications with same name are not allowed to be added twice')

        app2.name = 'TestApp2'
        reg.addApplication(app2)
        self.assertTrue(len(reg.applications()) == 2)

        reg.removeApplication(app2)
        self.assertTrue(len(reg.applications()) == 1, msg='Unable to remove application')


        #load a folder
        reg = ApplicationRegistry(EB)
        for d in TESTDATA.validAppDirs:
            self.assertTrue(reg.addApplicationFolder(d))
        self.assertEqual(len(reg), len(TESTDATA.validAppDirs))

        reg = ApplicationRegistry(EB)
        for d in TESTDATA.invalidAppDirs:
            self.assertFalse(reg.addApplicationFolder(d))
        self.assertEqual(len(reg), 0)

        reg = ApplicationRegistry(EB)
        reg.addApplicationListing(TESTDATA.pathListingAbs)
        self.assertEqual(len(reg), len(TESTDATA.validAppDirs))


        reg = ApplicationRegistry(EB)
        reg.addApplicationListing(TESTDATA.pathListingRel)
        self.assertEqual(len(reg), len(TESTDATA.validAppDirs))

        reg = ApplicationRegistry(EB)
        reg.addApplicationListing(TESTDATA.pathListingAbs)
        reg.addApplicationListing(TESTDATA.pathListingRel)
        self.assertEqual(len(reg), len(TESTDATA.validAppDirs))

        reg = ApplicationRegistry(EB)
        rootFolder = os.path.dirname(TESTDATA.validAppDirs[0])
        reg.addApplicationFolder(rootFolder, isRootFolder=True)
        self.assertTrue(len(reg) > 0, msg='Failed to add example EnMAPBoxApplication from {}'.format(rootFolder))


    def test_IVVM(self):

        eb = EnMAPBox(None)


        from lmuvegetationapps.IVVRM_GUI import MainUiFunc
        m = MainUiFunc()
        m.show()

        if SHOW_GUI:
            QGIS_APP.exec_()



    def test_externalApp(self):


        EB = EnMAPBox()
        self.assertIsInstance(EB, EnMAPBox)

        pathAppDir = r'C:\Users\geo_beja\Repositories\enmap-box-workshop2019\tutorials\progtut2\exercise3\smallexampleapp'
        if os.path.isdir(pathAppDir):
            reg = ApplicationRegistry(EB)
            reg.addApplicationFolder(pathAppDir)
            self.assertTrue(len(reg) > 0, msg='Failed to add example EnMAPBoxApplication from {}'.format(pathAppDir))

            EB.addApplication(pathAppDir)
            self.assertTrue(len(EB.applicationRegistry) == 1)
            s = ""

    def test_deployed_apps(self):

        pathCoreApps = os.path.join(DIR_ENMAPBOX, 'coreapps')
        pathExternalApps = os.path.join(DIR_ENMAPBOX, 'apps')
        self.assertTrue(os.path.isdir(pathCoreApps))

        EB = EnMAPBox()
        reg = ApplicationRegistry(EB)

        coreAppDirs = []
        externalAppDirs = []

        for d in os.scandir(pathCoreApps):
            if d.is_dir():
                coreAppDirs.append(d.path)

        for d in os.scandir(pathExternalApps):
            if d.is_dir():
                externalAppDirs.append(d.path)



        print('Load APP(s) from {}...'.format(pathExternalApps))
        for d in coreAppDirs + externalAppDirs:
            n1 = len(reg)
            reg.addApplicationFolder(d)
            n2 = len(reg)
            if n1 == n2:
                print('Unable to add EnMAPBoxApplications from {}'.format(d), file=sys.stderr)




    def test_enmapbox_start(self):


        EB = EnMAPBox()

        titles = [m.title() for m in EB.ui.menuBar().children() if isinstance(m, QMenu)]
        print('Menu titles: {}'.format(','.join(titles)))


        # calls all QMenu actions
        def triggerActions(menuItem, prefix=''):
            if isinstance(menuItem, QAction):
                print('Trigger QAction {}"{}" {}'.format(prefix, menuItem.text(), menuItem.toolTip()))
                menuItem.trigger()
            elif isinstance(menuItem, QMenu):
                for a in menuItem.actions():
                    triggerActions(a, prefix='"{}"->'.format(menuItem.title()))

        #test core apps / tools
        if SHOW_GUI:
            for title in ['Tools', 'Applications']:

                print('## TEST QMenu "{}"'.format(title))

                triggerActions(EB.menu(title))



if __name__ == "__main__":

    unittest.main()



