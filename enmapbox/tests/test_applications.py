# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enmapbox.gui.utils import initQgisApplication
from enmapbox.gui.utils import initQgisApplication
from enmapbox.gui.utils import *
QGIS_APP = initQgisApplication()

from enmapbox import EnMAPBox
import enmapbox.gui
from enmapbox.gui.applications import *
from enmapboxtestdata import enmap, hymap, landcover, speclib
import numpy as np

from enmapbox.gui.utils import TestObjects



class test_applications(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):

        enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = True
        enmapbox.gui.LOAD_INTERNAL_APPS = False
        enmapbox.gui.LOAD_EXTERNAL_APPS = False

    def tearDown(self):
        pass




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
        
        testApp = TestObjects.enmapBoxApplication()

        isOk, errors = EnMAPBoxApplication.checkRequirements(testApp)
        self.assertTrue(isOk)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) == 0)
        self.assertIsInstance(testApp.processingAlgorithms(), list)
        self.assertTrue(len(testApp.processingAlgorithms()) > 0)
        self.assertIsInstance(testApp.menu(QMenu), QMenu)


    def test_applicationRegistry(self):
        EB = EnMAPBox() 
        
        from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
        reg = ApplicationRegistry(EB)
        testApp = TestObjects.enmapBoxApplication()
        self.assertIsInstance(reg.applications(), list)
        self.assertTrue(len(reg.applications()) == 0)
        
        app = TestObjects.enmapBoxApplication()
        self.assertIsInstance(app, EnMAPBoxApplication)
        reg.addApplication(app)
        self.assertTrue(len(reg.applications()) == 1)
        self.assertTrue(len(reg.applications()) == len(reg))

        reg.removeApplication(app)
        self.assertTrue(len(reg.applications()) == 0)

        app2 = TestObjects.enmapBoxApplication()
        reg.addApplication(app2)
        self.assertTrue(len(reg.applications()) == 1, msg='Applications with same name are not allowed to be added twice')

        app2.name = 'TestApp2'
        reg.addApplication(app2)
        self.assertTrue(len(reg.applications()) == 2)

        reg.removeApplication(app2)
        self.assertTrue(len(reg.applications()) == 1, msg='Unable to remove application')


    def test_coreapps(self):

        #test without EnMAPBox
        from metadataeditorapp import MetaDataEditorApp
        enmapbox = EnMAPBox()
        app = MetaDataEditorApp(enmapbox)
        self.assertIsInstance(app, EnMAPBoxApplication)



    def test_enmapbox_start(self):

        enmapbox.gui.LOAD_PROCESSING_FRAMEWORK = True
        enmapbox.gui.LOAD_INTERNAL_APPS = True
        enmapbox.gui.LOAD_EXTERNAL_APPS = True

        EB = EnMAPBox()

        self.assertIsInstance(EB, EnMAPBox)

        # calls all QMenu actions
        def triggerActions(menuItem):
            if isinstance(menuItem, QAction):
                print('Trigger QAction "{}" {}'.format(menuItem.text(), menuItem.toolTip()))
                menuItem.trigger()
            elif isinstance(menuItem, QMenu):
                for a in menuItem.actions():
                    triggerActions(a)


        for w in EB.applicationRegistry.applicationWrapper():
            self.assertIsInstance(w, ApplicationWrapper)

            print('Test QActions from {}...'.format(w.appId))
            #simply call each single QAction


            for menuItem in w.menuItems:
                triggerActions(menuItem)





if __name__ == "__main__":

    unittest.main()



