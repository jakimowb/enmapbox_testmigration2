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
from unittest import TestCase
from qgis import *
from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from enmapbox.testing import initQgisApplication, TestObjects
QGIS_APP = initQgisApplication()

from enmapbox.gui.utils import *




from qgis.utils import iface

class TestEnMAPBoxPlugin(unittest.TestCase):


    def test_loadplugin(self):
        from enmapbox.enmapboxplugin import EnMAPBoxPlugin

        plugin = EnMAPBoxPlugin(iface)
        self.assertIsInstance(plugin, EnMAPBoxPlugin)
        plugin.initGui()

    def test_loadAlgorithmProvider(self):

        #test algos

        import enmapboxgeoalgorithms.algorithms
        for algorithm in enmapboxgeoalgorithms.algorithms.ALGORITHMS:
            self.assertIsInstance(algorithm, QgsProcessingAlgorithm)
            algo2 = algorithm.create()
            self.assertIsInstance(algo2, QgsProcessingAlgorithm)

        from enmapbox.enmapboxplugin import EnMAPBoxPlugin



        plugin = EnMAPBoxPlugin(iface)
        self.assertIsInstance(plugin, EnMAPBoxPlugin)
        plugin.initGui()
        plugin.unload()

        self.assertTrue(True)




if __name__ == '__main__':

    unittest.main()