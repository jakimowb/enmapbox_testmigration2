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
from qgis.core import QgsProcessingAlgorithm, QgsProject
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()

from enmapbox.gui.utils import *




from qgis.utils import iface

class TestEnMAPBoxPlugin(unittest.TestCase):

    def setUp(self):
        print('START TEST {}'.format(self.id()))
        QgsProject.instance().removeMapLayers(QgsProject.instance().mapLayers().keys())


    def test_loadplugin(self):
        from enmapbox.enmapboxplugin import EnMAPBoxPlugin

        plugin = EnMAPBoxPlugin(iface)
        self.assertIsInstance(plugin, EnMAPBoxPlugin)
        plugin.initGui()

    def test_loadAlgorithmProvider(self):

        #test algos

        import enmapboxgeoalgorithms.algorithms
        exceptions = []
        for algorithm in enmapboxgeoalgorithms.algorithms.ALGORITHMS:
            self.assertIsInstance(algorithm, QgsProcessingAlgorithm)
            algo2 = None

            try:
                algo2 = algorithm.create()
            except Exception as ex:
                exceptions.append((algorithm.name(), ex))


        if len(exceptions) > 0:

            names = '\n'.join([ex[0] for ex in exceptions])

            info = ['Failed to create {} algorithm(s):\n{}\nDETAILS:'.format(len(exceptions), names)]
            for ex in exceptions:
                info.append('Failed Algorithm: {}\nStack trace:\n{}\n'.format(ex[0], str(ex[1])))
            self.fail('\n'.join(info))


        from enmapbox.enmapboxplugin import EnMAPBoxPlugin



        plugin = EnMAPBoxPlugin(iface)
        self.assertIsInstance(plugin, EnMAPBoxPlugin)
        plugin.initGui()
        plugin.unload()

        self.assertTrue(True)


    def test_dependencies(self):

        from enmapbox.dependencycheck import requiredPackages, missingPackages, missingPackageInfo, PIPPackage

        pkgs = requiredPackages()
        for p in pkgs:
            self.assertIsInstance(p, PIPPackage)

        missing = missingPackages()
        self.assertIsInstance(missing, list)
        missing += [PIPPackage('foobar42')]

        info = missingPackageInfo(missing)
        self.assertIsInstance(info, str)
        self.assertTrue('foobar42' in info)
        from enmapbox.enmapboxplugin import EnMAPBoxPlugin

        import qgis.utils
        p = EnMAPBoxPlugin(qgis.utils.iface)
        p.initialDependencyCheck()


if __name__ == '__main__':

    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
